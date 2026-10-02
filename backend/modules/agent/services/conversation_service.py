#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体会话服务（本人数据）
"""
import logging
from typing import Optional

from sqlalchemy import delete, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import NotFoundError, CustomError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import SysAgent, SysAgentConversation, SysAgentConversationMsg
from database.utils.timezone import timezone

logger = logging.getLogger(__name__)

# 默认标题取首条用户消息前 N 字符（字符级截断防中文乱码）
DEFAULT_TITLE_PREFIX_LEN = 20


class ConversationService:
    """智能体会话服务类"""

    @staticmethod
    def build_conversation_query(user_id: int, agent_id: Optional[int] = None) -> Select:
        """构建本人会话查询（强制 user_id 过滤）"""
        base_query = select(SysAgentConversation).where(
            SysAgentConversation.user_id == user_id,
            SysAgentConversation.deleted_at.is_(None),
        )
        if agent_id is not None:
            base_query = base_query.where(SysAgentConversation.agent_id == agent_id)
        return base_query.order_by(
            SysAgentConversation.last_msg_at.desc().nullslast(),
            SysAgentConversation.id.desc(),
        )

    @staticmethod
    async def find_conversation(
        db: AsyncSession, user_id: int, conversation_id: int
    ) -> SysAgentConversation:
        """按本人过滤查找会话；他人会话与本不存在统一 NotFound（不泄露存在性）"""
        result = await db.execute(
            select(SysAgentConversation).where(
                SysAgentConversation.id == conversation_id,
                SysAgentConversation.user_id == user_id,
                SysAgentConversation.deleted_at.is_(None),
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise NotFoundError(msg=t("error.agent.conversation_not_found", id=conversation_id))
        return conversation

    @staticmethod
    async def create_conversation(
        db: AsyncSession, user_id: int, agent: SysAgent
    ) -> SysAgentConversation:
        """为指定智能体创建空会话"""
        conversation = SysAgentConversation(
            user_id=user_id,
            agent_id=agent.id,
            agent_name=agent.name,
            title=t("agent.default_conversation_title"),
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def rename_conversation(
        db: AsyncSession, user_id: int, conversation_id: int, title: str
    ) -> SysAgentConversation:
        """重命名本人会话"""
        conversation = await ConversationService.find_conversation(db, user_id, conversation_id)
        conversation.title = title
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def delete_conversation(db: AsyncSession, user_id: int, conversation_id: int) -> bool:
        """删除本人会话：软删会话 + 物理删除其全部消息"""
        logger.info("删除会话，ID: %s，用户: %s", conversation_id, user_id)
        conversation = await ConversationService.find_conversation(db, user_id, conversation_id)
        await db.execute(
            delete(SysAgentConversationMsg).where(
                SysAgentConversationMsg.conversation_id == conversation_id
            )
        )
        conversation.soft_delete()
        await db.commit()
        logger.info("删除会话成功，ID: %s", conversation_id)
        return True

    @staticmethod
    async def list_messages(
        db: AsyncSession, user_id: int, conversation_id: int
    ) -> list[SysAgentConversationMsg]:
        """按时间正序列出会话消息（本人会话校验）"""
        await ConversationService.find_conversation(db, user_id, conversation_id)
        result = await db.execute(
            select(SysAgentConversationMsg)
            .where(SysAgentConversationMsg.conversation_id == conversation_id)
            .order_by(SysAgentConversationMsg.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def ensure_conversation_agent(
        db: AsyncSession, user_id: int, conversation_id: int, agent_id: int
    ) -> SysAgentConversation:
        """会话归属与智能体绑定校验（不允许跨 Agent 追加）"""
        conversation = await ConversationService.find_conversation(db, user_id, conversation_id)
        if conversation.agent_id != agent_id:
            raise CustomError(
                error=CustomErrorCode.AGENT_CONVERSATION_AGENT_MISMATCH,
                msg=t("error.agent.conversation_agent_mismatch"),
            )
        return conversation

    @staticmethod
    async def record_user_message(
        db: AsyncSession, conversation: SysAgentConversation, content: str
    ) -> SysAgentConversationMsg:
        """
        落 user 消息并刷新会话元数据。

        调用时机：上游接受请求之后（避免上游拒绝时留下孤儿消息）；
        会话尚无有效标题时用首条消息前 20 字符改写默认标题。
        """
        message = SysAgentConversationMsg(
            conversation_id=conversation.id,
            role="user",
            content=content,
        )
        db.add(message)
        conversation.last_msg_at = timezone.now()
        if not conversation.title or conversation.title == t("agent.default_conversation_title"):
            conversation.title = content[:DEFAULT_TITLE_PREFIX_LEN] or t("agent.default_conversation_title")
        await db.commit()
        return message

    @staticmethod
    async def append_message(
        db: AsyncSession, conversation_id: int, role: str, content: str, total_tokens: int = 0
    ) -> SysAgentConversationMsg:
        """追加消息（assistant 消息落库，流结束后调用）；DB 写失败仅告警不阻断"""
        message = SysAgentConversationMsg(
            conversation_id=conversation_id,
            role=role,
            content=content,
            total_tokens=total_tokens,
        )
        db.add(message)
        await db.commit()
        return message
