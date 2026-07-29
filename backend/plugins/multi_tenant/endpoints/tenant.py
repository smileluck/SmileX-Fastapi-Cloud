#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""租户管理接口"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.response.response_schema import ResponseModel, ResponsePageModel
from modules.common.schemas.page import get_page_params, get_paginated_results, PageRequest
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from plugins.multi_tenant.services.tenant_service import TenantService
from plugins.multi_tenant.schemas.tenant import (
    TenantCreate,
    TenantUpdate,
    TenantQueryParams,
    TenantResponse,
    TenantListResponse,
    TenantAssignUser,
    TenantUserInfo,
    TenantConfigResponse,
    TenantConfigUpdate,
)

logger = logging.getLogger(__name__)

tenant_router = APIRouter(
    prefix="/tenant",
    tags=["租户管理"],
    dependencies=[Depends(current_user)],
)


@tenant_router.get(
    "/list",
    response_model=ResponsePageModel[TenantListResponse],
    dependencies=[Depends(require_permission("tenant:tenant:list"))],
)
async def get_tenant_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: TenantQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取租户列表"""
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size
    query = TenantService.build_tenant_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=TenantListResponse
    )
    return ResponsePageModel[TenantListResponse](data=page_data)


@tenant_router.get(
    "/all",
    response_model=ResponseModel[List[TenantListResponse]],
)
async def get_all_tenants(
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """获取当前用户可用的所有租户"""
    tenants = await TenantService.get_user_tenants(db, user.id)
    tenant_list = [TenantListResponse.model_validate(t) for t in tenants]
    return ResponseModel(data=tenant_list)


@tenant_router.get(
    "/{tenant_id}",
    response_model=ResponseModel[TenantResponse],
    dependencies=[Depends(require_permission("tenant:tenant:detail"))],
)
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取租户详情"""
    tenant = await TenantService.get_tenant(db, tenant_id)
    return ResponseModel(data=TenantResponse.model_validate(tenant))


@tenant_router.post(
    "/add",
    response_model=ResponseModel[TenantResponse],
    dependencies=[Depends(require_permission("tenant:tenant:add"))],
)
async def create_tenant(
    tenant_create: TenantCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建租户"""
    tenant = await TenantService.create_tenant(db, tenant_create)
    return ResponseModel(data=TenantResponse.model_validate(tenant), msg="创建租户成功")


@tenant_router.put(
    "/{tenant_id}",
    response_model=ResponseModel[TenantResponse],
    dependencies=[Depends(require_permission("tenant:tenant:edit"))],
)
async def update_tenant(
    tenant_id: int,
    tenant_update: TenantUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新租户"""
    tenant = await TenantService.update_tenant(db, tenant_id, tenant_update)
    return ResponseModel(data=TenantResponse.model_validate(tenant), msg="更新租户成功")


@tenant_router.delete(
    "/{tenant_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("tenant:tenant:delete"))],
)
async def delete_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_session),
):
    """删除租户"""
    await TenantService.delete_tenant(db, tenant_id)
    return ResponseModel(msg="删除租户成功")


@tenant_router.put(
    "/{tenant_id}/status",
    response_model=ResponseModel[TenantResponse],
    dependencies=[Depends(require_permission("tenant:tenant:status"))],
)
async def update_tenant_status(
    tenant_id: int,
    status: bool,
    db: AsyncSession = Depends(get_session),
):
    """更新租户状态"""
    tenant = await TenantService.update_status(db, tenant_id, status)
    return ResponseModel(data=TenantResponse.model_validate(tenant), msg="更新状态成功")


@tenant_router.get(
    "/{tenant_id}/config",
    response_model=ResponseModel[TenantConfigResponse],
    dependencies=[Depends(require_permission("tenant:tenant:config"))],
)
async def get_tenant_config(
    tenant_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取租户配置"""
    config = await TenantService.get_tenant_config(db, tenant_id)
    return ResponseModel(data=config)


@tenant_router.put(
    "/{tenant_id}/config",
    response_model=ResponseModel[TenantConfigResponse],
    dependencies=[Depends(require_permission("tenant:tenant:config"))],
)
async def update_tenant_config(
    tenant_id: int,
    config_update: TenantConfigUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新租户配置"""
    config = await TenantService.update_tenant_config(db, tenant_id, config_update)
    return ResponseModel(data=config, msg="更新租户配置成功")


@tenant_router.get(
    "/{tenant_id}/users",
    response_model=ResponseModel[List[TenantUserInfo]],
    dependencies=[Depends(require_permission("tenant:tenant:users"))],
)
async def get_tenant_users(
    tenant_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取租户用户列表"""
    users = await TenantService.get_tenant_users(db, tenant_id)
    return ResponseModel(data=[TenantUserInfo.model_validate(u) for u in users])


@tenant_router.post(
    "/{tenant_id}/users",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("tenant:tenant:assign"))],
)
async def assign_user_to_tenant(
    tenant_id: int,
    assign_in: TenantAssignUser,
    db: AsyncSession = Depends(get_session),
):
    """分配用户到租户"""
    await TenantService.assign_user(db, tenant_id, assign_in.user_id, assign_in.role)
    return ResponseModel(msg="分配用户成功")


@tenant_router.delete(
    "/{tenant_id}/users/{user_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("tenant:tenant:remove"))],
)
async def remove_user_from_tenant(
    tenant_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    """从租户移除用户"""
    await TenantService.remove_user(db, tenant_id, user_id)
    return ResponseModel(msg="移除用户成功")
