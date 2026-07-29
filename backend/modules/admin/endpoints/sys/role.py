#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
角色管理相关接口
"""
import io
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    ResponsePageDataModel,
)
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from core.utils.excel_export import build_excel_bytes, SYNC_EXPORT_MAX_ROWS
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from modules.admin.exports import get_export_config
from database.models.sys.user import SysUser

from modules.admin.services.sys import RoleService, MenuService
from modules.admin.schemas.sys.role import (
    SysRoleResponseData,
    SysRoleListResponse,
    SysRoleSimpleResponse,
    SysRoleCreate,
    SysRoleUpdate,
    SysRoleQueryParams,
    SysRoleBatchUpdateStatus,
    SysRoleAssignMenu,
)

logger = logging.getLogger(__name__)

# 创建角色管理路由
role_router = APIRouter(
    prefix="/role", tags=["角色管理"], dependencies=[Depends(current_user)]
)


def _build_role_response(role) -> SysRoleResponseData:
    """构建角色响应，从 ORM menus 关系中提取 menu_ids"""
    resp = SysRoleResponseData.model_validate(role)
    resp.menu_ids = [m.id for m in role.menus]
    return resp


@role_router.get("/list", response_model=ResponsePageModel[SysRoleListResponse], dependencies=[Depends(require_permission("sys:role:list"))])
async def get_role_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysRoleQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    获取角色列表
    """
    logger.info("获取角色列表请求")

    # 合并分页参数
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    # 构建查询对象
    query = RoleService.build_role_query(query_params)

    # 使用通用分页方法
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SysRoleListResponse,
    )

    logger.info(f"获取角色列表成功，共 {page_data.total} 条记录")
    return ResponsePageModel[SysRoleListResponse](data=page_data)


@role_router.get("/export", summary="导出角色列表 Excel")
async def export_roles(
    query_params: SysRoleQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    config = get_export_config("role")
    query = config.build_query_fn(query_params).limit(SYNC_EXPORT_MAX_ROWS)
    result = await db.execute(query)
    rows = result.unique().scalars().all()

    excel_bytes = build_excel_bytes(config.columns, rows, sheet_name=config.name)
    filename = f"roles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@role_router.get("/all", response_model=ResponseModel[List[SysRoleSimpleResponse]])
async def get_all_roles(db: AsyncSession = Depends(get_session)):
    """
    获取所有启用的角色
    """
    logger.info("获取所有启用的角色请求")

    roles = await RoleService.get_all_roles(db)
    role_responses = [SysRoleSimpleResponse.model_validate(role) for role in roles]

    logger.info(f"获取所有启用的角色成功，共 {len(role_responses)} 个角色")
    return ResponseModel(data=role_responses)


@role_router.get("/{role_id}", response_model=ResponseModel[SysRoleResponseData])
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个角色
    """
    logger.info(f"获取单个角色请求，角色ID: {role_id}")

    role = await RoleService.get_role(db, role_id)
    role_response = _build_role_response(role)

    logger.info(f"获取单个角色成功，角色ID: {role_id}")
    return ResponseModel(data=role_response)


@role_router.post("/add", response_model=ResponseModel[SysRoleResponseData], dependencies=[Depends(require_permission("sys:role:add"))])
@log_operation(module="role", action="create", description="创建角色")
async def create_role(
    request: Request,
    role_create: SysRoleCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建角色
    """
    logger.info(f"创建角色请求，角色名: {role_create.name}")

    role = await RoleService.create_role(
        db, role_create, is_superuser=user.is_superuser
    )
    role_response = _build_role_response(role)

    logger.info(f"创建角色成功，角色ID: {role.id}")
    return ResponseModel(data=role_response, msg="创建角色成功")


@role_router.put("/{role_id}", response_model=ResponseModel[SysRoleResponseData], dependencies=[Depends(require_permission("sys:role:edit"))])
@log_operation(module="role", action="update", description="更新角色")
async def update_role(
    role_id: int,
    request: Request,
    role_update: SysRoleUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新角色
    """
    logger.info(f"更新角色请求，角色ID: {role_id}")

    role = await RoleService.update_role(
        db, role_id, role_update, is_superuser=user.is_superuser
    )
    role_response = _build_role_response(role)

    logger.info(f"更新角色成功，角色ID: {role_id}")
    return ResponseModel(data=role_response, msg="更新角色成功")


@role_router.post("/{role_id}/menus", response_model=ResponseModel[SysRoleResponseData], dependencies=[Depends(require_permission("sys:role:edit"))])
@log_operation(module="role", action="assign_menu", description="分配菜单权限")
async def assign_menu_to_role(
    role_id: int,
    request: Request,
    assign_in: SysRoleAssignMenu,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    为角色分配菜单权限
    """
    logger.info(
        f"为角色分配菜单权限请求，角色ID: {role_id}, 菜单ID: {assign_in.menu_ids}"
    )

    # 获取当前用户可分配的菜单范围
    permitted_menu_ids = await MenuService.get_user_permitted_menu_ids(db, user)

    role = await RoleService.assign_menu_to_role(
        db, role_id, assign_in.menu_ids,
        is_superuser=user.is_superuser,
        permitted_menu_ids=permitted_menu_ids,
    )
    role_response = _build_role_response(role)

    logger.info(f"为角色分配菜单权限成功，角色ID: {role_id}")
    return ResponseModel(data=role_response, msg="分配菜单权限成功")


@role_router.delete("/batch", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:role:delete"))])
@log_operation(module="role", action="batch_delete", description="批量删除角色")
async def batch_delete_roles(
    request: Request,
    role_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除角色
    """
    logger.info(f"批量删除角色请求，角色ID: {role_ids}")

    delete_count = await RoleService.batch_delete_roles(
        db, role_ids, is_superuser=user.is_superuser
    )

    logger.info(f"批量删除角色成功，共删除 {delete_count} 个角色")
    return ResponseModel(
        msg=f"批量删除成功，共删除 {delete_count} 个角色",
        data={"delete_count": delete_count},
    )


@role_router.put("/batch/status", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:role:edit"))])
@log_operation(module="role", action="batch_update_status", description="批量更新角色状态")
async def batch_update_roles_status(
    request: Request,
    batch_update: SysRoleBatchUpdateStatus,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量更新角色状态
    """
    logger.info(
        f"批量更新角色状态请求，角色ID: {batch_update.role_ids}, 状态: {batch_update.status}"
    )

    update_count = await RoleService.batch_update_roles_status(
        db, batch_update.role_ids, batch_update.status, is_superuser=user.is_superuser
    )

    status_text = "启用" if batch_update.status else "禁用"
    logger.info(f"批量更新角色状态成功，共 {update_count} 个角色被{status_text}")
    return ResponseModel(
        msg=f"批量{status_text}成功，共 {update_count} 个角色",
        data={"update_count": update_count},
    )


@role_router.delete("/{role_id}", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:role:delete"))])
@log_operation(module="role", action="delete", description="删除角色")
async def delete_role(
    role_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除角色
    """
    logger.info(f"删除角色请求，角色ID: {role_id}")

    await RoleService.delete_role(db, role_id, is_superuser=user.is_superuser)

    logger.info(f"删除角色成功，角色ID: {role_id}")
    return ResponseModel(msg="删除角色成功")
