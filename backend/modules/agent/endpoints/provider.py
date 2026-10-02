#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模型供应商管理接口
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
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from modules.agent.schemas.provider import (
    AgentConnectTestResponse,
    AgentProviderCreate,
    AgentProviderQueryParams,
    AgentProviderResponseData,
    AgentProviderTestRequest,
    AgentProviderUpdate,
    AgentRemoteModelsResponse,
)
from modules.agent.services import ProviderService

logger = logging.getLogger(__name__)

provider_router = APIRouter(
    prefix="/providers", tags=["模型供应商"], dependencies=[Depends(current_user)]
)


def _to_response(provider) -> AgentProviderResponseData:
    """ORM → 响应（补 has_api_key 派生字段）"""
    data = AgentProviderResponseData.model_validate(provider)
    data.has_api_key = bool(provider.api_key_enc)
    return data


@provider_router.get(
    "/list",
    response_model=ResponsePageModel[AgentProviderResponseData],
    dependencies=[Depends(require_permission("agent:provider:list"))],
)
async def get_provider_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: AgentProviderQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取模型供应商分页列表（API Key 仅掩码回显）"""
    logger.info("获取模型供应商列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = ProviderService.build_provider_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=AgentProviderResponseData
    )
    # has_api_key 为派生字段，统一补齐
    for record in page_data.records:
        record.has_api_key = bool(record.api_key_mask)

    logger.info("获取模型供应商列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[AgentProviderResponseData](data=page_data)


@provider_router.get(
    "/{provider_id}",
    response_model=ResponseModel[AgentProviderResponseData],
    dependencies=[Depends(require_permission("agent:provider:list"))],
)
async def get_provider(
    provider_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个模型供应商"""
    logger.info("获取模型供应商请求，ID: %s", provider_id)
    provider = await ProviderService.get_provider(db, provider_id)
    return ResponseModel(data=_to_response(provider))


@provider_router.post(
    "/add",
    response_model=ResponseModel[AgentProviderResponseData],
    dependencies=[Depends(require_permission("agent:provider:add"))],
)
@log_operation(module="agent_provider", action="create", description="创建模型供应商")
async def create_provider(
    request: Request,
    provider_create: AgentProviderCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建模型供应商（api_key 加密落库，响应仅掩码）"""
    logger.info("创建模型供应商请求，编码: %s", provider_create.code)
    provider = await ProviderService.create_provider(db, provider_create)
    return ResponseModel(data=_to_response(provider), msg=t("agent.provider.create_success"))


@provider_router.put(
    "/{provider_id}",
    response_model=ResponseModel[AgentProviderResponseData],
    dependencies=[Depends(require_permission("agent:provider:edit"))],
)
@log_operation(module="agent_provider", action="update", description="更新模型供应商")
async def update_provider(
    provider_id: int,
    request: Request,
    provider_update: AgentProviderUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新模型供应商（api_key 留空=保持原密钥不变）"""
    logger.info("更新模型供应商请求，ID: %s", provider_id)
    provider = await ProviderService.update_provider(db, provider_id, provider_update)
    return ResponseModel(data=_to_response(provider), msg=t("agent.provider.update_success"))


@provider_router.delete(
    "/{provider_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("agent:provider:delete"))],
)
@log_operation(module="agent_provider", action="delete", description="删除模型供应商")
async def delete_provider(
    provider_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除模型供应商（供应商下存在模型时拒绝）"""
    logger.info("删除模型供应商请求，ID: %s", provider_id)
    await ProviderService.delete_provider(db, provider_id)
    return ResponseModel(msg=t("agent.provider.delete_success"))


@provider_router.post(
    "/{provider_id}/test",
    response_model=ResponseModel[AgentConnectTestResponse],
    dependencies=[Depends(require_permission("agent:provider:test"))],
)
@log_operation(module="agent_provider", action="test", description="测试模型供应商连通性")
async def test_provider(
    provider_id: int,
    request: Request,
    payload: AgentProviderTestRequest,
    db: AsyncSession = Depends(get_session),
):
    """
    供应商连通测试：非流式固定提示词（MaxTokens=64 控制费用）。

    model_id 为 0 时取该供应商下首个启用模型；上游错误以失败结果返回（HTTP 200）。
    """
    logger.info("测试模型供应商连通性，ID: %s", provider_id)
    try:
        _provider, model, result = await ProviderService.test_provider(db, provider_id, payload.model_id)
        data = AgentConnectTestResponse(
            ok=True,
            content=result.content,
            model=result.model or model.name,
            latency_ms=0,
            prompt_tokens=result.usage.prompt_tokens,
            completion_tokens=result.usage.completion_tokens,
        )
    except Exception as exc:
        data = AgentConnectTestResponse(ok=False, error=str(exc)[:300])
    return ResponseModel(data=data)


@provider_router.get(
    "/{provider_id}/remote-models",
    response_model=ResponseModel[AgentRemoteModelsResponse],
    dependencies=[Depends(require_permission("agent:provider:remote-models"))],
)
async def list_remote_models(
    provider_id: int,
    db: AsyncSession = Depends(get_session),
):
    """拉取上游 /models 模型列表（模型录入辅助下拉）"""
    logger.info("拉取上游模型列表，供应商 ID: %s", provider_id)
    models = await ProviderService.list_remote_models(db, provider_id)
    return ResponseModel(data=AgentRemoteModelsResponse(models=models))
