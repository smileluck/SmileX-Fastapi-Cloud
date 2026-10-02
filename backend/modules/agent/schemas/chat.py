#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field

from modules.common.schemas.base import BaseEntity, BaseReqEntity, BaseRespEntity


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class ChatMessageInput(BaseReqEntity):
    """对话输入消息（仅允许 user/assistant 角色，system 由智能体配置注入）"""

    role: str = Field(..., description="消息角色：user / assistant", pattern=r"^(user|assistant)$")
    content: str = Field(..., description="消息内容", min_length=1, max_length=4000)


class AgentChatRequest(BaseEntity):
    """智能体对话请求（SSE 流式响应）"""

    messages: list[ChatMessageInput] = Field(..., description="对话消息（1-50 条，最后一条须为 user）", min_length=1, max_length=50)
    conversation_id: Optional[int] = Field(None, description="会话 ID（可选：持久化会话；为空则不落库）", gt=0)


class ConversationCreate(BaseEntity):
    """会话创建请求"""

    agent_id: int = Field(..., description="智能体 ID", gt=0)


class ConversationRename(BaseReqEntity):
    """会话重命名请求"""

    title: str = Field(..., description="新标题", min_length=1, max_length=64)


class ConversationResponseData(BaseRespEntity):
    """会话响应（本人数据）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="会话 ID")
    agent_id: int = Field(..., description="智能体 ID")
    agent_name: str = Field(..., description="智能体名称（冗余）")
    title: str = Field(..., description="会话标题")
    last_msg_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="最近消息时间")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")


class ConversationMessageResponseData(BaseRespEntity):
    """会话消息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="消息 ID")
    conversation_id: int = Field(..., description="所属会话 ID")
    role: str = Field(..., description="消息角色：user / assistant")
    content: str = Field(..., description="消息内容")
    total_tokens: int = Field(0, description="assistant 消息的总 token 数")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")


class UsageDailyPoint(BaseEntity):
    """用量日聚合点"""

    date: str = Field(..., description="日期（YYYY-MM-DD）")
    calls: int = Field(0, description="调用次数")
    prompt_tokens: int = Field(0, description="输入 token 合计")
    completion_tokens: int = Field(0, description="输出 token 合计")
    total_tokens: int = Field(0, description="总 token 合计")


class UsageSummary(BaseEntity):
    """用量统计汇总"""

    days: int = Field(..., description="统计天数")
    total_calls: int = Field(0, description="总调用次数")
    total_prompt_tokens: int = Field(0, description="输入 token 合计")
    total_completion_tokens: int = Field(0, description="输出 token 合计")
    total_tokens: int = Field(0, description="总 token 合计")
    trend: list[UsageDailyPoint] = Field(default_factory=list, description="日用量趋势")
