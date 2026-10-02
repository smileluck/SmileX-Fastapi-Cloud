#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型管理接口
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.schemas.model import (
    AgentModelCreate,
    AgentModelQueryParams,
    AgentModelResponseData,
    AgentModelUpdate,
)
from modules.agent.schemas.provider import AgentConnectTestResponse
from modules.agent.services import ModelService
from modules.agent.utils import paginate_joined
from modules.common.schemas.page import PageRequest, get_page_params

logger = logging.getLogger(__name__)

model_router = APIRouter(
    prefix="/models", tags=["模型管理"], dependencies=[Depends(current_user)]
)


@model_router.get(
    "/list",
    response_model=ResponsePageModel[AgentModelResponseData],
    dependencies=[Depends(require_permission("agent:model:list"))],
)
async def get_model_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: AgentModelQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取模型分页列表（含所属供应商名称）"""
    logger.info("获取模型列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = ModelService.build_model_query(query_params)
    page_data = await paginate_joined(
        db, page_params, query, AgentModelResponseData, ("provider_name",)
    )
    logger.info("获取模型列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[AgentModelResponseData](data=page_data)


@model_router.post(
    "/add",
    response_model=ResponseModel[AgentModelResponseData],
    dependencies=[Depends(require_permission("agent:model:add"))],
)
@log_operation(module="agent_model", action="create", description="创建模型")
async def create_model(
    request: Request,
    model_create: AgentModelCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建模型（同一供应商下模型名唯一）"""
    logger.info("创建模型请求，模型名: %s", model_create.name)
    model = await ModelService.create_model(db, model_create)
    data = AgentModelResponseData.model_validate(model)
    return ResponseModel(data=data, msg=t("agent.model.create_success"))


@model_router.put(
    "/{model_id}",
    response_model=ResponseModel[AgentModelResponseData],
    dependencies=[Depends(require_permission("agent:model:edit"))],
)
@log_operation(module="agent_model", action="update", description="更新模型")
async def update_model(
    model_id: int,
    request: Request,
    model_update: AgentModelUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新模型（供应商不可变更）"""
    logger.info("更新模型请求，ID: %s", model_id)
    model = await ModelService.update_model(db, model_id, model_update)
    return ResponseModel(
        data=AgentModelResponseData.model_validate(model), msg=t("agent.model.update_success")
    )


@model_router.delete(
    "/{model_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("agent:model:delete"))],
)
@log_operation(module="agent_model", action="delete", description="删除模型")
async def delete_model(
    model_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除模型（被智能体引用时拒绝）"""
    logger.info("删除模型请求，ID: %s", model_id)
    await ModelService.delete_model(db, model_id)
    return ResponseModel(msg=t("agent.model.delete_success"))


@model_router.post(
    "/{model_id}/test",
    response_model=ResponseModel[AgentConnectTestResponse],
    dependencies=[Depends(require_permission("agent:model:test"))],
)
@log_operation(module="agent_model", action="test", description="测试模型连通性")
async def test_model(
    model_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """模型连通测试：经所属供应商发起非流式调用（失败以结果返回）"""
    logger.info("测试模型连通性，ID: %s", model_id)
    try:
        model, result = await ModelService.test_model(db, model_id)
        data = AgentConnectTestResponse(
            ok=True,
            content=result.content,
            model=result.model or model.name,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
        )
    except Exception as exc:
        data = AgentConnectTestResponse(ok=False, error=str(exc)[:300])
    return ResponseModel(data=data)
