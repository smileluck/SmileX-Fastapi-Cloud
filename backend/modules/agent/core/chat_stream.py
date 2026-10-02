#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体 SSE 流式对话编排

帧协议（与 SmileX-Admin-Gin 一致）：
    event: meta  → {agent_id, agent_name, provider_id, model_id, model, conversation_id}
    event: delta → {delta, finish_reason, usage}        （逐 token）
    event: tool  → {tool_calls: [{id, name, arguments, result, error}]}
    event: error → {message}
    注释帧 ": ping" 保活

行为要点：
- 上游接受请求后才落 user 消息（避免上游拒绝时留下孤儿消息）
- 流结束（含中断/出错）时聚合落 assistant 消息，已生成部分照常保存
- 用量在多轮工具循环合并后仅记一条流水
"""
import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import (
    SysAgent,
    SysAgentConversation,
    SysAgentModel,
    SysAgentProvider,
)
from modules.agent.core.llm_client import (
    ChatMessage,
    ChatRequest,
    LLMClient,
    LLMError,
    StreamEvent,
    ToolCall,
    Usage,
)
from modules.agent.core.mcp_manager import get_mcp_manager
from modules.agent.core.tool_registry import TOOL_EXEC_TIMEOUT, get_tool_registry
from modules.agent.services.agent_service import AgentService
from modules.agent.services.conversation_service import ConversationService
from modules.agent.services.provider_service import ProviderService
from modules.agent.services.skill_service import SkillService
from modules.agent.services.usage_service import UsageService

logger = logging.getLogger(__name__)

# 工具循环轮数上限（防死循环）
MAX_TOOL_ROUNDS = 5
# system prompt 总量上限（字节）
SYSTEM_PROMPT_MAX = 60000
# 工具结果回传上限（字节）
TOOL_RESULT_MAX = 8 * 1024
# 单服务 MCP 工具定义拉取预算（秒）
MCP_DEFS_BUDGET = 10.0
# MCP 工具执行超时（秒）
MCP_TOOL_TIMEOUT = 60.0
# SSE 保活间隔（秒）
PING_INTERVAL = 15.0

PING_FRAME = ": ping\n\n"


def sse_frame(event: str, payload: dict[str, Any]) -> str:
    """构造单行 JSON 的具名 SSE 帧"""
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _safe_tool_name(ref: str) -> str:
    """mcp:<code>:<tool> → mcp__<code>__<tool>（OpenAI 函数名不允许冒号）"""
    return ref.replace(":", "_").replace("-", "_")[:64]


def _truncate_result(text: str) -> str:
    """工具结果超长截断（UTF-8 字节口径）"""
    encoded = text.encode("utf-8")
    if len(encoded) <= TOOL_RESULT_MAX:
        return text
    return encoded[:TOOL_RESULT_MAX].decode("utf-8", errors="ignore") + "…（已截断）"


def build_system_prompt(agent: SysAgent, skill_contents: list) -> str:
    """Agent 提示词 + 技能块拼接；总量上限 60KB 截断"""
    parts: list[str] = []
    if agent.system_prompt:
        parts.append(agent.system_prompt)
    for content in skill_contents:
        block = [f"\n\n# 技能：{content.name}"]
        if content.description:
            block.append(content.description)
        block.append(content.instruction)
        for file in content.files:
            block.append(f"\n\n## 附：{file.path}\n{file.content}")
        parts.append("\n".join(block))
    prompt = "".join(parts)
    if len(prompt.encode("utf-8")) > SYSTEM_PROMPT_MAX:
        prompt = prompt.encode("utf-8")[:SYSTEM_PROMPT_MAX].decode("utf-8", errors="ignore")
        logger.warning("智能体 %s system prompt 超限已截断", agent.id)
    return prompt


async def collect_tool_defs(
    db: AsyncSession, agent: SysAgent
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """
    组装下发上游的工具定义。

    返回 (defs, resolver)：resolver 为 下发函数名 → 库存引用名（mcp:<code>:<tool>）反查表。
    内置工具直接命中注册表；MCP 按服务分组共享一次 tools/list，
    单服务预算 10s，超时/失败跳过该服务不阻断对话。
    """
    registry = get_tool_registry()
    defs: list[dict[str, Any]] = []
    resolver: dict[str, str] = {}

    mcp_by_server: dict[str, list[str]] = {}
    for name in AgentService.parse_tools(agent):
        if name.startswith("mcp:"):
            parts = name.split(":", 2)
            if len(parts) == 3:
                mcp_by_server.setdefault(parts[1], []).append(parts[2])
        else:
            tool = registry.find(name)
            if tool is not None:
                func = tool.def_()
                defs.append(
                    {
                        "type": "function",
                        "function": {
                            "name": func.name,
                            "description": func.description,
                            "parameters": func.parameters,
                        },
                    }
                )

    if mcp_by_server:
        manager = get_mcp_manager()
        for server_code, tool_names in mcp_by_server.items():
            try:
                tools, _info = await asyncio.wait_for(
                    manager.get_tools(db, server_code), timeout=MCP_DEFS_BUDGET
                )
            except Exception as exc:
                logger.warning("拉取 MCP 服务 %s 工具定义失败，已跳过: %s", server_code, exc)
                continue
            for info in tools:
                if info.name not in tool_names:
                    continue
                ref = f"mcp:{server_code}:{info.name}"
                safe = _safe_tool_name(ref)
                resolver[safe] = ref
                defs.append(
                    {
                        "type": "function",
                        "function": {
                            "name": safe,
                            "description": info.description,
                            "parameters": info.input_schema or {"type": "object"},
                        },
                    }
                )
    return defs, resolver


async def exec_tool(
    db: AsyncSession, resolver: dict[str, str], name: str, arguments: str
) -> dict[str, str]:
    """执行工具调用：本地注册表优先（10s），MCP 远程次之（60s）；失败不中断流"""
    started = time.monotonic()
    try:
        if name in resolver:
            ref = resolver[name]
            parts = ref.split(":", 2)
            result = await asyncio.wait_for(
                get_mcp_manager().call_tool(db, parts[1], parts[2], arguments),
                timeout=MCP_TOOL_TIMEOUT,
            )
            display_name = ref
        else:
            tool = get_tool_registry().find(name)
            if tool is None:
                return {
                    "id": "",
                    "name": name,
                    "arguments": arguments,
                    "result": "",
                    "error": f"unknown tool: {name}",
                }
            result = await asyncio.wait_for(tool.execute(arguments), timeout=TOOL_EXEC_TIMEOUT)
            display_name = name
        return {
            "id": "",
            "name": display_name,
            "arguments": arguments,
            "result": _truncate_result(result),
            "error": "",
            "latency_ms": int((time.monotonic() - started) * 1000),
        }
    except asyncio.TimeoutError:
        return {"id": "", "name": name, "arguments": arguments, "result": "", "error": "工具执行超时"}
    except Exception as exc:
        return {"id": "", "name": name, "arguments": arguments, "result": "", "error": str(exc)[:300]}


class ChatStreamContext:
    """一次对话的完整上下文（校验通过后组装）"""

    def __init__(
        self,
        agent: SysAgent,
        model: SysAgentModel,
        provider: SysAgentProvider,
        client: LLMClient,
        conversation_id: Optional[int],
    ):
        self.agent = agent
        self.model = model
        self.provider = provider
        self.client = client
        self.conversation_id = conversation_id


async def prepare_chat(
    db: AsyncSession,
    user_id: int,
    agent_id: int,
    conversation_id: Optional[int],
) -> ChatStreamContext:
    """
    对话前校验与上下文组装（Endpoint 阶段调用，失败走统一异常处理）：
    Agent 存在并启用 → Model 存在并启用 → Provider 启用 → 会话归属与绑定校验
    """
    agent = await AgentService.get_agent(db, agent_id)
    if not agent.status:
        raise CustomError(error=CustomErrorCode.AGENT_DISABLED, msg=t("error.agent.disabled"))

    result = await db.execute(
        select(SysAgentModel, SysAgentProvider)
        .join(SysAgentProvider, SysAgentModel.provider_id == SysAgentProvider.id)
        .where(SysAgentModel.id == agent.model_id, SysAgentModel.deleted_at.is_(None))
    )
    row = result.first()
    if row is None:
        raise CustomError(
            error=CustomErrorCode.AGENT_MODEL_NOT_FOUND,
            msg=t("error.agent.model_not_found", id=agent.model_id),
        )
    model, provider = row[0], row[1]
    if not model.status:
        raise CustomError(error=CustomErrorCode.AGENT_MODEL_DISABLED, msg=t("error.agent.model_disabled"))
    if not provider.status:
        raise CustomError(
            error=CustomErrorCode.AGENT_PROVIDER_DISABLED, msg=t("error.agent.provider_disabled")
        )

    if conversation_id:
        await ConversationService.ensure_conversation_agent(db, user_id, conversation_id, agent_id)

    client = ProviderService.build_client(provider)
    return ChatStreamContext(agent, model, provider, client, conversation_id)


class _KeepAliveIterator:
    """包装异步迭代器：读超时时产出哨兵 PING，不取消底层读取任务"""

    PING = object()

    def __init__(self, stream: AsyncIterator[StreamEvent]):
        self._it = stream.__aiter__()
        self._task: Optional[asyncio.Task] = None

    async def __anext__(self) -> Any:
        while True:
            if self._task is None:
                self._task = asyncio.ensure_future(self._it.__anext__())
            try:
                return await asyncio.wait_for(asyncio.shield(self._task), timeout=PING_INTERVAL)
            except asyncio.TimeoutError:
                return self.PING
            except StopAsyncIteration:
                raise
            finally:
                # 正常返回/异常时清理任务句柄；超时路径任务保留继续等
                if self._task is not None and self._task.done():
                    self._task = None


async def stream_chat(
    ctx: ChatStreamContext,
    user_id: int,
    history: list[ChatMessage],
) -> AsyncIterator[str]:
    """
    SSE 流式对话主生成器。

    history 为前端传入的 user/assistant 消息；system 由智能体配置 + 技能注入。
    生成器内部自行管理 DB 会话，流结束（含中断/出错）时保证已生成内容落库。
    """
    from database.db_manager import get_session

    started = time.monotonic()

    # 技能内容加载失败仅跳过，不阻断对话
    skill_contents: list = []
    skill_codes = AgentService.parse_skills(ctx.agent)
    if skill_codes:
        try:
            async for db in get_session():
                skill_contents = await SkillService.get_contents(db, skill_codes)
                break
        except Exception as exc:
            logger.warning("加载智能体 %s 技能失败，已跳过: %s", ctx.agent.id, exc)

    system_prompt = build_system_prompt(ctx.agent, skill_contents)
    messages: list[ChatMessage] = []
    if system_prompt:
        messages.append(ChatMessage(role="system", content=system_prompt))
    messages.extend(history)

    yield sse_frame(
        "meta",
        {
            "agent_id": ctx.agent.id,
            "agent_name": ctx.agent.name,
            "provider_id": ctx.provider.id,
            "model_id": ctx.model.id,
            "model": ctx.model.name,
            "conversation_id": ctx.conversation_id or 0,
        },
    )

    # 工具定义组装（MCP 定义拉取失败跳过）
    defs: list[dict[str, Any]] = []
    resolver: dict[str, str] = {}
    if AgentService.parse_tools(ctx.agent):
        try:
            async for db in get_session():
                defs, resolver = await collect_tool_defs(db, ctx.agent)
                break
        except Exception as exc:
            logger.warning("组装智能体 %s 工具定义失败: %s", ctx.agent.id, exc)

    request = ChatRequest(
        model=ctx.model.name,
        messages=messages,
        temperature=ctx.agent.temperature,
        top_p=ctx.agent.top_p,
        max_tokens=ctx.agent.max_tokens,
        tools=defs,
        stream=True,
    )

    total_usage = Usage()
    assistant_parts: list[str] = []
    last_user_content = next((m.content for m in reversed(history) if m.role == "user"), "")

    try:
        stream = _KeepAliveIterator(ctx.client.stream_completion(request))

        # 推进到首个事件：建立上游连接，失败则发 error 帧且不落 user 消息
        first_event: Optional[StreamEvent] = None
        while first_event is None:
            try:
                event = await stream.__anext__()
            except StopAsyncIteration:
                first_event = StreamEvent(finish_reason="stop")
                break
            if event is _KeepAliveIterator.PING:
                yield PING_FRAME
                continue
            first_event = event

        # 上游已接受请求：落 user 消息
        if ctx.conversation_id:
            try:
                async for db in get_session():
                    conv_result = await db.execute(
                        select(SysAgentConversation).where(
                            SysAgentConversation.id == ctx.conversation_id,
                            SysAgentConversation.user_id == user_id,
                            SysAgentConversation.deleted_at.is_(None),
                        )
                    )
                    conversation = conv_result.scalar_one_or_none()
                    if conversation is not None:
                        await ConversationService.record_user_message(db, conversation, last_user_content)
                    break
            except Exception as exc:
                logger.warning("落 user 消息失败（不阻断对话）: %s", exc)

        async def first_then_stream() -> AsyncIterator[Any]:
            yield first_event
            while True:
                try:
                    yield await stream.__anext__()
                except StopAsyncIteration:
                    return

        async for outcome in run_tool_loop(ctx, request, first_then_stream(), resolver, assistant_parts, total_usage):
            if outcome["type"] == "delta":
                yield sse_frame("delta", outcome["payload"])
            elif outcome["type"] == "tool":
                yield sse_frame("tool", outcome["payload"])
            elif outcome["type"] == "ping":
                yield PING_FRAME

        # 末帧：合并后的 usage 与结束原因
        yield sse_frame(
            "delta",
            {
                "delta": "",
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": total_usage.prompt_tokens,
                    "completion_tokens": total_usage.completion_tokens,
                    "total_tokens": total_usage.total_tokens,
                },
            },
        )
    except LLMError as exc:
        yield sse_frame("error", {"message": str(exc)})
    except asyncio.CancelledError:
        # 客户端断开：已生成部分照常保存（走 finally）
        raise
    except Exception as exc:
        logger.exception("智能体对话流异常")
        yield sse_frame("error", {"message": t("error.agent.upstream_error", detail=str(exc)[:200])})
    finally:
        # 落 assistant 消息与用量流水（中断/出错时已生成部分照常保存）
        if ctx.conversation_id and assistant_parts:
            try:
                async for db in get_session():
                    await ConversationService.append_message(
                        db, ctx.conversation_id, "assistant", "".join(assistant_parts), total_usage.total_tokens
                    )
                    break
            except Exception as exc:
                logger.warning("落 assistant 消息失败（不阻断）: %s", exc)
        if total_usage.total_tokens > 0:
            try:
                async for db in get_session():
                    await UsageService.append_usage(
                        db,
                        agent_id=ctx.agent.id,
                        model_id=ctx.model.id,
                        user_id=user_id,
                        prompt_tokens=total_usage.prompt_tokens,
                        completion_tokens=total_usage.completion_tokens,
                        total_tokens=total_usage.total_tokens,
                        latency_ms=int((time.monotonic() - started) * 1000),
                    )
                    break
            except Exception as exc:
                logger.warning("落用量流水失败（不阻断）: %s", exc)


async def run_tool_loop(
    ctx: ChatStreamContext,
    request: ChatRequest,
    stream: AsyncIterator[Any],
    resolver: dict[str, str],
    assistant_parts: list[str],
    total_usage: Usage,
) -> AsyncIterator[dict[str, Any]]:
    """
    工具调用循环：最多 5 轮。

    每轮流式转发文本增量；usage 累加不转发；模型请求工具时逐个执行（含失败），
    以 tool 事件下发执行结果，并把 assistant(tool_calls) + tool 结果消息 append 回
    messages 续答。多轮合并后的 usage 由外层以单帧下发。
    """
    from database.db_manager import get_session

    current_stream = stream
    for _round in range(MAX_TOOL_ROUNDS):
        content_parts: list[str] = []
        calls: list[ToolCall] = []
        round_usage = Usage()

        async for ev in current_stream:
            if ev is _KeepAliveIterator.PING:
                yield {"type": "ping"}
                continue
            if ev.delta:
                content_parts.append(ev.delta)
                assistant_parts.append(ev.delta)
                yield {"type": "delta", "payload": {"delta": ev.delta}}
            if ev.usage is not None:
                round_usage.prompt_tokens += ev.usage.prompt_tokens
                round_usage.completion_tokens += ev.usage.completion_tokens
                round_usage.total_tokens += ev.usage.total_tokens
            if ev.finish_reason == "tool_calls" and ev.tool_calls:
                calls = ev.tool_calls

        total_usage.prompt_tokens += round_usage.prompt_tokens
        total_usage.completion_tokens += round_usage.completion_tokens
        total_usage.total_tokens += round_usage.total_tokens

        if not calls:
            return

        # 执行本轮全部工具调用（含失败结果，错误也回传模型自查）
        results: list[dict[str, str]] = []
        for call in calls:
            result: dict[str, str]
            try:
                async for db in get_session():
                    result = await exec_tool(db, resolver, call.function.name, call.function.arguments)
                    break
            except Exception as exc:
                result = {
                    "id": call.id,
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                    "result": "",
                    "error": str(exc)[:300],
                }
            result["id"] = call.id
            # 下发名还原为库存引用名（mcp:<code>:<tool>）
            if result["name"] in resolver:
                result["name"] = resolver[result["name"]]
            results.append(result)
        yield {"type": "tool", "payload": {"tool_calls": results}}

        # 把工具交互 append 回消息续答
        request.messages.append(
            ChatMessage(role="assistant", content="".join(content_parts), tool_calls=calls)
        )
        for call, result in zip(calls, results):
            result_text = f"error: {result['error']}" if result.get("error") else result.get("result", "")
            request.messages.append(
                ChatMessage(role="tool", content=result_text, tool_call_id=call.id)
            )

        current_stream = _KeepAliveIterator(ctx.client.stream_completion(request))
