#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型管理服务
"""
import logging
from typing import Optional, Tuple

from sqlalchemy import and_, func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import SysAgent, SysAgentModel, SysAgentProvider
from modules.agent.core.llm_client import ChatMessage, ChatRequest
from modules.agent.schemas.model import (
    AgentModelCreate,
    AgentModelQueryParams,
    AgentModelUpdate,
)
from modules.agent.services.provider_service import ProviderService
from modules.agent.utils import archive_and_soft_delete

logger = logging.getLogger(__name__)


class ModelService:
    """模型管理服务类"""

    @staticmethod
    def build_model_query(query_params: AgentModelQueryParams) -> Select:
        """构建模型分页查询条件（联查供应商名称）"""
        base_query = select(SysAgentModel, SysAgentProvider.name).join(
            SysAgentProvider,
            SysAgentModel.provider_id == SysAgentProvider.id,
            isouter=True,
        )

        conditions = [SysAgentModel.deleted_at.is_(None)]
        if query_params.provider_id is not None:
            conditions.append(SysAgentModel.provider_id == query_params.provider_id)
        if query_params.status is not None:
            conditions.append(SysAgentModel.status == query_params.status)
        if query_params.name:
            conditions.append(SysAgentModel.name.like(f"%{query_params.name}%"))

        return (
            base_query.where(and_(*conditions))
            .order_by(SysAgentModel.provider_id.asc(), SysAgentModel.name.asc())
        )

    @staticmethod
    async def get_model(db: AsyncSession, model_id: int) -> SysAgentModel:
        """获取单个模型，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysAgentModel).where(
                SysAgentModel.id == model_id, SysAgentModel.deleted_at.is_(None)
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            raise NotFoundError(msg=t("error.agent.model_not_found", id=model_id))
        return model

    @staticmethod
    async def get_first_enabled(db: AsyncSession, provider_id: int) -> Optional[SysAgentModel]:
        """取供应商下首个启用模型（id 最小）"""
        result = await db.execute(
            select(SysAgentModel)
            .where(
                SysAgentModel.provider_id == provider_id,
                SysAgentModel.status.is_(True),
                SysAgentModel.deleted_at.is_(None),
            )
            .order_by(SysAgentModel.id.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_model(db: AsyncSession, payload: AgentModelCreate) -> SysAgentModel:
        """创建模型；校验供应商存在 + (provider_id, name) 复合唯一"""
        logger.info("创建模型，供应商 ID: %s，模型名: %s", payload.provider_id, payload.name)
        await ProviderService.get_provider(db, payload.provider_id)

        existing = await db.execute(
            select(SysAgentModel.id).where(
                SysAgentModel.provider_id == payload.provider_id,
                SysAgentModel.name == payload.name,
                SysAgentModel.deleted_at.is_(None),
            )
        )
        if existing.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.AGENT_MODEL_EXIST,
                msg=t("error.agent.model_exist", name=payload.name),
            )

        model = SysAgentModel(
            provider_id=payload.provider_id,
            name=payload.name,
            display_name=payload.display_name,
            context_window=payload.context_window,
            max_output=payload.max_output,
            supports_tools=payload.supports_tools,
            input_price=payload.input_price,
            output_price=payload.output_price,
            remark=payload.remark,
            status=payload.status,
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)
        logger.info("创建模型成功，ID: %s", model.id)
        return model

    @staticmethod
    async def update_model(
        db: AsyncSession, model_id: int, payload: AgentModelUpdate
    ) -> SysAgentModel:
        """更新模型（供应商不可变更）"""
        logger.info("更新模型，ID: %s", model_id)
        model = await ModelService.get_model(db, model_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("provider_id", None)
        for key, value in update_data.items():
            if hasattr(model, key) and value is not None:
                setattr(model, key, value)

        await db.commit()
        await db.refresh(model)
        logger.info("更新模型成功，ID: %s", model_id)
        return model

    @staticmethod
    async def delete_model(db: AsyncSession, model_id: int) -> bool:
        """删除模型；被智能体引用时拒绝"""
        logger.info("删除模型，ID: %s", model_id)
        model = await ModelService.get_model(db, model_id)

        count_result = await db.execute(
            select(func.count()).select_from(SysAgent).where(
                SysAgent.model_id == model_id,
                SysAgent.deleted_at.is_(None),
            )
        )
        if (count_result.scalar() or 0) > 0:
            raise CustomError(
                error=CustomErrorCode.AGENT_MODEL_IN_USE,
                msg=t("error.agent.model_in_use"),
            )

        await archive_and_soft_delete(
            db, model, "name"
        )
        logger.info("删除模型成功，ID: %s", model_id)
        return True

    @staticmethod
    async def test_model(db: AsyncSession, model_id: int) -> Tuple[SysAgentModel, object]:
        """模型连通测试：经所属供应商发起非流式调用"""
        model = await ModelService.get_model(db, model_id)
        provider = await ProviderService.get_provider(db, model.provider_id)

        client = ProviderService.build_client(provider)
        result = await client.chat_completion(
            ChatRequest(
                model=model.name,
                messages=[ChatMessage(role="user", content="这是一条连通性测试消息，请直接回复：连接成功")],
                max_tokens=64,
            )
        )
        return model, result

    @staticmethod
    async def list_enabled(db: AsyncSession) -> list[SysAgentModel]:
        """全部启用模型（Agent 表单下拉数据源）"""
        result = await db.execute(
            select(SysAgentModel)
            .where(SysAgentModel.status.is_(True), SysAgentModel.deleted_at.is_(None))
            .order_by(SysAgentModel.provider_id.asc(), SysAgentModel.name.asc())
        )
        return list(result.scalars().all())
