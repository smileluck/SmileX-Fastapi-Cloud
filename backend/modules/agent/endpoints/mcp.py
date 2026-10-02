#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 服务器接入管理接口（客户端消费侧；与既有 mcp-platform 服务端互补）
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from core.security.rate_limit import enforce_user_limit
from database.db_manager import get_session
from database.models.sys.user import SysUser
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.schemas.mcp_server import (
    McpServerCreate,
    McpServerQueryParams,
    McpServerResponseData,
    McpServerTestResponse,
    McpServerUpdate,
)
from modules.agent.services import McpServerService
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results

logger = logging.getLogger(__name__)

mcp_router = APIRouter(
    prefix="/mcp-servers", tags=["MCP 服务"], dependencies=[Depends(current_user)]
)

# 连通测试限流（次/分钟/用户）
TEST_RATE_LIMIT = 10


def _to_response(server) -> McpServerResponseData:
    """ORM → 响应（补 has_token 派生字段）"""
    data = McpServerResponseData.model_validate(server)
    data.has_token = bool(server.token_enc)
    return data


@mcp_router.get(
    "/list",
    response_model=ResponsePageModel[McpServerResponseData],
    dependencies=[Depends(require_permission("mcp:server:list"))],
)
async def get_mcp_server_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: McpServerQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取 MCP 服务分页列表（Token 仅掩码回显）"""
    logger.info("获取 MCP 服务列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = McpServerService.build_server_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=McpServerResponseData
    )
    for record in page_data.records:
        record.has_token = bool(record.token_mask)
    logger.info("获取 MCP 服务列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[McpServerResponseData](data=page_data)


@mcp_router.get(
    "/{server_id}",
    response_model=ResponseModel[McpServerResponseData],
    dependencies=[Depends(require_permission("mcp:server:list"))],
)
async def get_mcp_server(
    server_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个 MCP 服务"""
    logger.info("获取 MCP 服务请求，ID: %s", server_id)
    server = await McpServerService.get_server(db, server_id)
    return ResponseModel(data=_to_response(server))


@mcp_router.post(
    "/add",
    response_model=ResponseModel[McpServerResponseData],
    dependencies=[Depends(require_permission("mcp:server:add"))],
)
@log_operation(module="mcp_server", action="create", description="创建 MCP 服务")
async def create_mcp_server(
    request: Request,
    server_create: McpServerCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建 MCP 服务（Token 加密落库，响应仅掩码）"""
    logger.info("创建 MCP 服务请求，编码: %s", server_create.code)
    server = await McpServerService.create_server(db, server_create)
    return ResponseModel(data=_to_response(server), msg=t("agent.mcp.create_success"))


@mcp_router.put(
    "/{server_id}",
    response_model=ResponseModel[McpServerResponseData],
    dependencies=[Depends(require_permission("mcp:server:edit"))],
)
@log_operation(module="mcp_server", action="update", description="更新 MCP 服务")
async def update_mcp_server(
    server_id: int,
    request: Request,
    server_update: McpServerUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新 MCP 服务（编码不可改；token 留空=保持不变）"""
    logger.info("更新 MCP 服务请求，ID: %s", server_id)
    server = await McpServerService.update_server(db, server_id, server_update)
    return ResponseModel(data=_to_response(server), msg=t("agent.mcp.update_success"))


@mcp_router.delete(
    "/{server_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("mcp:server:delete"))],
)
@log_operation(module="mcp_server", action="delete", description="删除 MCP 服务")
async def delete_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除 MCP 服务（被智能体工具引用时拒绝）"""
    logger.info("删除 MCP 服务请求，ID: %s", server_id)
    await McpServerService.delete_server(db, server_id)
    return ResponseModel(msg=t("agent.mcp.delete_success"))


@mcp_router.post(
    "/{server_id}/test",
    response_model=ResponseModel[McpServerTestResponse],
    dependencies=[Depends(require_permission("mcp:server:test"))],
)
@log_operation(module="mcp_server", action="test", description="测试 MCP 服务连通性")
async def test_mcp_server(
    server_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    MCP 服务连通测试：真实握手（initialize + tools/list，双协议）。
    失败也是有效结果（ok=false 带原因），接口不报错。
    """
    await enforce_user_limit(user.id, TEST_RATE_LIMIT, window_seconds=60)
    logger.info("测试 MCP 服务连通性，ID: %s", server_id)
    result = await McpServerService.test_server(db, server_id)
    return ResponseModel(data=McpServerTestResponse.model_validate(result))
