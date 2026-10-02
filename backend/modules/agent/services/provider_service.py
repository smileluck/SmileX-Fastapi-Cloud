#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型供应商服务
"""
import logging
from typing import Optional, Tuple

from sqlalchemy import and_, func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import SysAgentModel, SysAgentProvider
from modules.agent.core import crypto as agent_crypto
from modules.agent.core.llm_client import ChatMessage, ChatRequest, LLMClient
from modules.agent.schemas.provider import (
    AgentProviderCreate,
    AgentProviderQueryParams,
    AgentProviderUpdate,
)
from modules.agent.utils import archive_and_soft_delete

logger = logging.getLogger(__name__)


class ProviderService:
    """模型供应商服务类"""

    @staticmethod
    def build_provider_query(query_params: AgentProviderQueryParams) -> Select:
        """构建供应商分页查询条件"""
        base_query = select(SysAgentProvider)

        conditions = []
        if query_params.status is not None:
            conditions.append(SysAgentProvider.status == query_params.status)
        if query_params.name:
            conditions.append(SysAgentProvider.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysAgentProvider.code.like(f"%{query_params.code}%"))

        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.order_by(SysAgentProvider.id.desc())

    @staticmethod
    async def get_provider(db: AsyncSession, provider_id: int) -> SysAgentProvider:
        """获取单个供应商，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysAgentProvider).where(
                SysAgentProvider.id == provider_id, SysAgentProvider.deleted_at.is_(None)
            )
        )
        provider = result.scalar_one_or_none()
        if not provider:
            raise NotFoundError(msg=t("error.agent.provider_not_found", id=provider_id))
        return provider

    @staticmethod
    async def _ensure_code_unique(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> None:
        """校验供应商编码唯一（排除自身）"""
        conditions = [
            SysAgentProvider.code == code,
            SysAgentProvider.deleted_at.is_(None),
        ]
        if exclude_id is not None:
            conditions.append(SysAgentProvider.id != exclude_id)
        result = await db.execute(select(SysAgentProvider.id).where(and_(*conditions)))
        if result.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.AGENT_PROVIDER_CODE_EXIST,
                msg=t("error.agent.provider_code_exist", code=code),
            )

    @staticmethod
    async def create_provider(
        db: AsyncSession, payload: AgentProviderCreate
    ) -> SysAgentProvider:
        """创建供应商；api_key 加密落库 + 掩码冗余"""
        logger.info("创建模型供应商，编码: %s", payload.code)
        await ProviderService._ensure_code_unique(db, payload.code)

        api_key_enc = agent_crypto.encrypt_secret(payload.api_key or "")
        provider = SysAgentProvider(
            name=payload.name,
            code=payload.code,
            base_url=payload.base_url,
            api_key_enc=api_key_enc,
            api_key_mask=agent_crypto.mask_secret(payload.api_key or ""),
            protocol=payload.protocol,
            remark=payload.remark,
            status=payload.status,
        )
        db.add(provider)
        await db.commit()
        await db.refresh(provider)
        logger.info("创建模型供应商成功，ID: %s", provider.id)
        return provider

    @staticmethod
    async def update_provider(
        db: AsyncSession, provider_id: int, payload: AgentProviderUpdate
    ) -> SysAgentProvider:
        """更新供应商；api_key 留空=保持原密钥不变"""
        logger.info("更新模型供应商，ID: %s", provider_id)
        provider = await ProviderService.get_provider(db, provider_id)

        update_data = payload.model_dump(exclude_unset=True)
        api_key = update_data.pop("api_key", None)
        for key, value in update_data.items():
            if hasattr(provider, key) and value is not None:
                setattr(provider, key, value)
        if api_key is not None:
            provider.api_key_enc = agent_crypto.encrypt_secret(api_key)
            provider.api_key_mask = agent_crypto.mask_secret(api_key)

        await db.commit()
        await db.refresh(provider)
        logger.info("更新模型供应商成功，ID: %s", provider_id)
        return provider

    @staticmethod
    async def delete_provider(db: AsyncSession, provider_id: int) -> bool:
        """删除供应商；供应商下存在模型时拒绝"""
        logger.info("删除模型供应商，ID: %s", provider_id)
        provider = await ProviderService.get_provider(db, provider_id)

        count_result = await db.execute(
            select(func.count()).select_from(SysAgentModel).where(
                SysAgentModel.provider_id == provider_id,
                SysAgentModel.deleted_at.is_(None),
            )
        )
        if (count_result.scalar() or 0) > 0:
            raise CustomError(
                error=CustomErrorCode.AGENT_PROVIDER_HAS_MODELS,
                msg=t("error.agent.provider_has_models"),
            )

        await archive_and_soft_delete(db, provider, "code")
        logger.info("删除模型供应商成功，ID: %s", provider_id)
        return True

    @staticmethod
    def build_client(provider: SysAgentProvider) -> LLMClient:
        """按供应商配置构造 LLM 客户端（api_key 解密；解密失败抛错提示重新保存）"""
        try:
            api_key = agent_crypto.decrypt_secret(provider.api_key_enc or "")
        except ValueError as exc:
            raise CustomError(
                error=CustomErrorCode.AGENT_DECRYPT_FAILED,
                msg=t("error.agent.decrypt_failed"),
            ) from exc
        return LLMClient(base_url=provider.base_url, api_key=api_key)

    @staticmethod
    async def test_provider(
        db: AsyncSession, provider_id: int, model_id: int
    ) -> Tuple[SysAgentProvider, SysAgentModel, object]:
        """
        供应商连通测试：非流式固定提示词 + MaxTokens=64 控制费用。

        model_id=0 时取该供应商下首个启用模型；不校验供应商启用状态（允许先验证再启用）。
        返回 (provider, model, ChatResult)。
        """
        provider = await ProviderService.get_provider(db, provider_id)
        from modules.agent.services.model_service import ModelService

        if model_id:
            model = await ModelService.get_model(db, model_id)
        else:
            model = await ModelService.get_first_enabled(db, provider_id)
            if model is None:
                raise NotFoundError(msg=t("error.agent.model_not_found", id=0))

        client = ProviderService.build_client(provider)
        result = await client.chat_completion(
            ChatRequest(
                model=model.name,
                messages=[ChatMessage(role="user", content="这是一条连通性测试消息，请直接回复：连接成功")],
                max_tokens=64,
            )
        )
        return provider, model, result

    @staticmethod
    async def list_remote_models(db: AsyncSession, provider_id: int) -> list[str]:
        """拉取上游 /models 模型列表（录入辅助）"""
        provider = await ProviderService.get_provider(db, provider_id)
        client = ProviderService.build_client(provider)
        return await client.list_models()
