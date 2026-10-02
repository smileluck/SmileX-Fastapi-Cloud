#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenAI 兼容协议 LLM 客户端（零 SDK 依赖，httpx 实现）

- 超时分层：整体 120s（含流式读 body）、建连 10s 快速失败（base_url 填错时快速报错而非干等）
- 流式：stream_options.include_usage 请求上游在末帧回吐 usage；tool_calls 分片按 index 聚合
- 错误映射：超时 / 连接失败 / 上游 HTTP 错误 三类，均以 LLMError 抛出
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional

import httpx

logger = logging.getLogger(__name__)

# 整体请求超时（秒）：覆盖 TCP/TLS/读写，更长生成靠前端停止按钮取消流
LLM_TOTAL_TIMEOUT = 120.0
# 建连超时（秒）：base_url 错误时快速失败
LLM_CONNECT_TIMEOUT = 10.0
# SSE 单行读取上限（字节）
SSE_LINE_LIMIT = 1024 * 1024


class LLMError(Exception):
    """LLM 上游调用错误（message 已本地化，可直接透传给前端 error 帧）"""


@dataclass
class Usage:
    """token 用量（上游响应 usage 字段）"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class FunctionCall:
    name: str = ""
    arguments: str = ""


@dataclass
class ToolCall:
    """上游返回的工具调用请求（流式分片聚合结果）"""

    id: str = ""
    function: FunctionCall = field(default_factory=FunctionCall)


@dataclass
class StreamEvent:
    """流式对话单帧事件"""

    delta: str = ""
    finish_reason: Optional[str] = None
    usage: Optional[Usage] = None
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class ChatMessage:
    """对话消息（system 由后端拼装，tool 结果以 role=tool 回传）"""

    role: str  # system | user | assistant | tool
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""

    def to_wire(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        return payload


@dataclass
class ChatRequest:
    """一次对话请求参数"""

    model: str
    messages: list[ChatMessage]
    temperature: float = 0.0
    top_p: float = 0.0
    max_tokens: int = 0
    tools: list[dict[str, Any]] = field(default_factory=list)
    stream: bool = False


@dataclass
class ChatResult:
    """非流式对话结果"""

    content: str
    model: str
    usage: Usage
    tool_calls: list[ToolCall] = field(default_factory=list)


def _wrap_error(exc: Exception) -> LLMError:
    """将 httpx 异常映射为用户可读的 LLMError"""
    if isinstance(exc, httpx.TimeoutException):
        return LLMError("上游响应超时")
    if isinstance(exc, httpx.ConnectError):
        return LLMError("无法连接上游服务，请检查 Base URL")
    if isinstance(exc, LLMError):
        return exc
    return LLMError(f"上游调用失败: {exc}")


def _parse_upstream_error_body(text: str) -> str:
    """解析上游错误体（兼容 error.message 与顶层 message 两种格式），兜底截 300 字节"""
    try:
        data = json.loads(text)
        msg = (data.get("error") or {}).get("message") or data.get("message")
        if msg:
            return str(msg)[:300]
    except Exception:
        pass
    return text[:300] if text else "unknown error"


class LLMClient:
    """OpenAI 兼容协议客户端（一个实例对应一个供应商配置）"""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._timeout = httpx.Timeout(
            LLM_TOTAL_TIMEOUT, connect=LLM_CONNECT_TIMEOUT
        )

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_payload(self, req: ChatRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": req.model,
            "messages": [m.to_wire() for m in req.messages],
        }
        if req.temperature > 0:
            payload["temperature"] = req.temperature
        if req.top_p > 0:
            payload["top_p"] = req.top_p
        if req.max_tokens > 0:
            payload["max_tokens"] = req.max_tokens
        if req.tools:
            payload["tools"] = req.tools
        if req.stream:
            payload["stream"] = True
            payload["stream_options"] = {"include_usage": True}
        return payload

    async def chat_completion(self, req: ChatRequest) -> ChatResult:
        """非流式对话（连通测试 / 无工具场景）"""
        payload = self._build_payload(req)
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self._headers(),
                )
        except Exception as exc:
            raise _wrap_error(exc) from exc
        if resp.status_code != 200:
            raise LLMError(f"上游返回 HTTP {resp.status_code}: {_parse_upstream_error_body(resp.text)}")
        data = resp.json()
        usage_raw = data.get("usage") or {}
        usage = Usage(
            prompt_tokens=usage_raw.get("prompt_tokens", 0),
            completion_tokens=usage_raw.get("completion_tokens", 0),
            total_tokens=usage_raw.get("total_tokens", 0),
        )
        content = ""
        tool_calls: list[ToolCall] = []
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            content = message.get("content") or ""
            for tc in message.get("tool_calls") or []:
                func = tc.get("function") or {}
                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", ""),
                        function=FunctionCall(
                            name=func.get("name", ""), arguments=func.get("arguments", "")
                        ),
                    )
                )
        return ChatResult(content=content, model=data.get("model", req.model), usage=usage, tool_calls=tool_calls)

    async def stream_completion(self, req: ChatRequest) -> AsyncIterator[StreamEvent]:
        """
        流式对话：逐 token 产出 StreamEvent。

        - delta.content 增量透传
        - tool_calls 分片按 index 聚合，到 finish_reason == "tool_calls" 时以完整调用整体下发
        - usage 仅出现在末帧（依赖 stream_options.include_usage）
        - 解析失败的帧跳过不中断
        """
        payload = self._build_payload(req)
        pending: dict[int, ToolCall] = {}

        try:
            client = httpx.AsyncClient(timeout=self._timeout)
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={
                        **self._headers(),
                        "Accept": "text/event-stream",
                    },
                ) as resp:
                    if resp.status_code != 200:
                        body = (await resp.aread()).decode("utf-8", errors="replace")
                        raise LLMError(
                            f"上游返回 HTTP {resp.status_code}: {_parse_upstream_error_body(body)}"
                        )
                    async for line in resp.aiter_lines():
                        event = self._parse_sse_line(line, pending)
                        if event is not None:
                            yield event
            finally:
                await client.aclose()
        except LLMError:
            raise
        except Exception as exc:
            raise _wrap_error(exc) from exc

    @staticmethod
    def _parse_sse_line(line: str, pending: dict[int, ToolCall]) -> Optional[StreamEvent]:
        """解析单行 SSE；返回 None 表示跳过（注释行/空行/[DONE]/解析失败）"""
        if not line.startswith("data:"):
            return None
        data_text = line[5:].strip()
        if not data_text or data_text == "[DONE]":
            return None
        try:
            chunk = json.loads(data_text)
        except json.JSONDecodeError:
            return None

        event = StreamEvent()
        usage_raw = chunk.get("usage")
        if usage_raw:
            event.usage = Usage(
                prompt_tokens=usage_raw.get("prompt_tokens", 0),
                completion_tokens=usage_raw.get("completion_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
            )
        choices = chunk.get("choices") or []
        if choices:
            choice = choices[0]
            delta = choice.get("delta") or {}
            event.delta = delta.get("content") or ""
            event.finish_reason = choice.get("finish_reason")
            for tc in delta.get("tool_calls") or []:
                index = tc.get("index", 0)
                call = pending.get(index)
                if call is None:
                    call = ToolCall()
                    pending[index] = call
                if tc.get("id"):
                    call.id = tc["id"]
                func = tc.get("function") or {}
                if func.get("name"):
                    call.function.name += func["name"]
                call.function.arguments += func.get("arguments") or ""
            if event.finish_reason == "tool_calls":
                # 按 index 排序、过滤无名调用，聚合完成后整体下发
                event.tool_calls = [
                    pending[k] for k in sorted(pending) if pending[k].function.name
                ]
                pending.clear()
        return event

    async def list_models(self) -> list[str]:
        """拉取上游 /models 模型 ID 列表（升序去重），作为模型录入辅助"""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(f"{self.base_url}/models", headers=self._headers())
        except Exception as exc:
            raise _wrap_error(exc) from exc
        if resp.status_code != 200:
            raise LLMError(f"上游返回 HTTP {resp.status_code}: {_parse_upstream_error_body(resp.text)}")
        data = resp.json()
        ids = sorted({item.get("id") for item in (data.get("data") or []) if item.get("id")})
        return ids
