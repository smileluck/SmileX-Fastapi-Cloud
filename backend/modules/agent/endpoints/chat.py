#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体对话（SSE 流式）+ 会话管理 + 用量统计接口
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.i18n import t
from core.response.response_schema import ResponseModel
from core.security.rate_limit import enforce_user_limit
from database.db_manager import get_session
from database.models.sys.user import SysUser
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.core.chat_stream import prepare_chat, stream_chat
from modules.agent.core.llm_client import ChatMessage
from modules.agent.schemas.chat import (
    AgentChatRequest,
    ConversationCreate,
    ConversationMessageResponseData,
    ConversationRename,
    ConversationResponseData,
    UsageSummary,
)
from modules.agent.services import AgentService, ConversationService, UsageService

logger = logging.getLogger(__name__)

chat_router = APIRouter(
    prefix="/chat", tags=["智能体对话"], dependencies=[Depends(current_user)]
)

# 对话按用户限流（次/分钟）
CHAT_RATE_LIMIT = 20

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",  # nginx 反代禁缓冲
}


@chat_router.post(
    "/agents/{agent_id}/stream",
    dependencies=[Depends(require_permission("agent:chat"))],
)
async def chat_stream(
    agent_id: int,
    payload: AgentChatRequest,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    智能体 SSE 流式对话。

    帧协议：event: meta | delta | tool | error，data 为单行 JSON；
    每 15s 发送 ": ping" 注释帧保活；conversation_id 非空时消息持久化。
    """
    # 按用户限流（Redis 固定窗口）
    await enforce_user_limit(user.id, CHAT_RATE_LIMIT, window_seconds=60)

    # 对话前校验：Agent/模型/供应商启用状态 + 会话归属（失败走统一异常处理）
    ctx = await prepare_chat(db, user.id, agent_id, payload.conversation_id)

    history = [ChatMessage(role=m.role, content=m.content) for m in payload.messages]
    return StreamingResponse(
        stream_chat(ctx, user.id, history),
        media_type="text/event-stream; charset=utf-8",
        headers=SSE_HEADERS,
    )


@chat_router.get(
    "/conversations",
    response_model=ResponseModel[list[ConversationResponseData]],
    dependencies=[Depends(require_permission("agent:conversation:list"))],
)
async def list_conversations(
    agent_id: Optional[int] = Query(None, description="按智能体过滤"),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """获取本人的会话列表（按最近消息排序）"""
    query = ConversationService.build_conversation_query(user.id, agent_id)
    result = await db.execute(query.limit(200))
    conversations = result.scalars().all()
    return ResponseModel(
        data=[ConversationResponseData.model_validate(c) for c in conversations]
    )


@chat_router.post(
    "/conversations",
    response_model=ResponseModel[ConversationResponseData],
    dependencies=[Depends(require_permission("agent:conversation:create"))],
)
async def create_conversation(
    payload: ConversationCreate,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """为指定智能体创建空会话"""
    agent = await AgentService.get_agent(db, payload.agent_id)
    conversation = await ConversationService.create_conversation(db, user.id, agent)
    return ResponseModel(
        data=ConversationResponseData.model_validate(conversation),
        msg=t("agent.conversation.create_success"),
    )


@chat_router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ResponseModel[list[ConversationMessageResponseData]],
    dependencies=[Depends(require_permission("agent:conversation:list"))],
)
async def list_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """获取会话历史消息（时间正序；本人会话）"""
    messages = await ConversationService.list_messages(db, user.id, conversation_id)
    return ResponseModel(
        data=[ConversationMessageResponseData.model_validate(m) for m in messages]
    )


@chat_router.put(
    "/conversations/{conversation_id}",
    response_model=ResponseModel[ConversationResponseData],
    dependencies=[Depends(require_permission("agent:conversation:update"))],
)
async def rename_conversation(
    conversation_id: int,
    payload: ConversationRename,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """重命名本人会话"""
    conversation = await ConversationService.rename_conversation(
        db, user.id, conversation_id, payload.title
    )
    return ResponseModel(
        data=ConversationResponseData.model_validate(conversation),
        msg=t("agent.conversation.rename_success"),
    )


@chat_router.delete(
    "/conversations/{conversation_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("agent:conversation:delete"))],
)
@log_operation(module="agent_conversation", action="delete", description="删除智能体会话")
async def delete_conversation(
    conversation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """删除本人会话（连同全部消息物理删除）"""
    await ConversationService.delete_conversation(db, user.id, conversation_id)
    return ResponseModel(msg=t("agent.conversation.delete_success"))


@chat_router.get(
    "/usage",
    response_model=ResponseModel[UsageSummary],
    dependencies=[Depends(require_permission("agent:usage"))],
)
async def get_usage(
    days: int = Query(7, ge=1, le=90, description="统计天数（1-90）"),
    only_mine: bool = Query(False, description="True=仅统计本人用量"),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """token 用量统计：日聚合趋势 + 汇总"""
    summary = await UsageService.get_usage_summary(
        db, user.id if only_mine else None, days=days
    )
    return ResponseModel(data=summary)
