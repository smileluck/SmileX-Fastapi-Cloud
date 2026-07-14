#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户管理相关接口
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
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from app.models.common.base import BoolField
from core.decorators.operation_log import log_operation
from core.utils.excel_export import build_excel_bytes, SYNC_EXPORT_MAX_ROWS
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from modules.admin.exports import get_export_config
from database.models.sys.user import SysUser

from modules.admin.services.sys import UserService, DataScopeService
from modules.admin.schemas.sys.user import (
    SysUserResponseData,
    SysUserListResponse,
    SysUserCreate,
    SysUserUpdate,
    SysUserPasswordUpdate,
    SysUserQueryParams,
    SysUserBatchUpdateStatus,
)

logger = logging.getLogger(__name__)

# 创建用户管理路由
user_router = APIRouter(
    prefix="/user", tags=["用户管理"], dependencies=[Depends(current_user)]
)


@user_router.get("/list", response_model=ResponsePageModel[SysUserListResponse], dependencies=[Depends(require_permission("sys:user:list"))])
async def get_user_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysUserQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    获取用户列表
    """
    logger.info("获取用户列表请求")

    # 合并分页参数和查询参数
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    # 计算数据权限范围（None=不限，超管/ALL；SELF 走 current_user_id 过滤）
    scope = await DataScopeService.get_effective_scope(db, user)
    permitted_dept_ids = await DataScopeService.get_permitted_dept_ids(db, user, scope)

    # 构建查询对象（build_user_list_query 已 selectinload 角色，供列表响应回填）
    query = UserService.build_user_list_query(
        query_params,
        data_scope=scope,
        permitted_dept_ids=permitted_dept_ids,
        current_user_id=user.id,
    )

    # 使用通用分页方法
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SysUserListResponse,
    )

    logger.info(f"获取用户列表成功，共 {page_data.total} 条记录")
    return ResponsePageModel[SysUserListResponse](data=page_data)


@user_router.get("/export", summary="导出用户列表 Excel")
async def export_users(
    query_params: SysUserQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    config = get_export_config("user")
    query = config.build_query_fn(query_params).limit(SYNC_EXPORT_MAX_ROWS)
    result = await db.execute(query)
    rows = result.unique().scalars().all()

    excel_bytes = build_excel_bytes(config.columns, rows, sheet_name=config.name)
    filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@user_router.get("/{user_id}", response_model=ResponseModel[SysUserResponseData])
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个用户
    """
    logger.info(f"获取单个用户请求，用户ID: {user_id}")

    user = await UserService.get_user(db, user_id)
    user_response = SysUserResponseData.model_validate(user)

    logger.info(f"获取单个用户成功，用户ID: {user_id}")
    return ResponseModel(data=user_response)


@user_router.post("/add", response_model=ResponseModel[SysUserResponseData], dependencies=[Depends(require_permission("sys:user:add"))])
@log_operation(module="user", action="create", description="创建用户")
async def create_user(
    request: Request,
    user_create: SysUserCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建用户
    """
    logger.info(f"创建用户请求，用户名: {user_create.username}")

    user = await UserService.create_user(db, user_create)
    user_response = SysUserResponseData.model_validate(user)

    logger.info(f"创建用户成功，用户ID: {user.id}")
    return ResponseModel(data=user_response, msg="创建用户成功")


@user_router.put("/{user_id}", response_model=ResponseModel[SysUserResponseData], dependencies=[Depends(require_permission("sys:user:edit"))])
@log_operation(module="user", action="update", description="更新用户")
async def update_user(
    user_id: int,
    request: Request,
    user_update: SysUserUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新用户
    """
    logger.info(f"更新用户请求，用户ID: {user_id}")

    user = await UserService.update_user(db, user_id, user_update)
    user_response = SysUserResponseData.model_validate(user)

    logger.info(f"更新用户成功，用户ID: {user_id}")
    return ResponseModel(data=user_response, msg="更新用户成功")


@user_router.post("/{user_id}/roles", response_model=ResponseModel[SysUserResponseData], dependencies=[Depends(require_permission("sys:user:edit"))])
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    为用户分配角色
    """
    logger.info(f"为用户分配角色请求，用户ID: {user_id}, 角色ID: {role_ids}")

    user = await UserService.assign_roles_to_user(db, user_id, role_ids)
    user_response = SysUserResponseData.model_validate(user)

    logger.info(f"为用户分配角色成功，用户ID: {user_id}")
    return ResponseModel(data=user_response, msg="分配角色成功")


@user_router.delete("/batch", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:user:delete"))])
@log_operation(module="user", action="batch_delete", description="批量删除用户")
async def batch_delete_users(
    request: Request,
    user_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除用户
    """
    logger.info(f"批量删除用户请求，用户ID: {user_ids}")

    delete_count = await UserService.batch_delete_users(db, user_ids)

    logger.info(f"批量删除用户成功，共删除 {delete_count} 个用户")
    return ResponseModel(
        msg=f"批量删除成功，共删除 {delete_count} 个用户",
        data={"delete_count": delete_count},
    )


@user_router.put("/batch/status", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:user:edit"))])
@log_operation(module="user", action="batch_update_status", description="批量更新用户状态")
async def batch_update_users_status(
    request: Request,
    batch_update: SysUserBatchUpdateStatus,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量更新用户状态
    """
    logger.info(
        f"批量更新用户状态请求，用户ID: {batch_update.user_ids}, 状态: {batch_update.status}"
    )

    update_count = await UserService.batch_update_users_status(
        db, batch_update.user_ids, batch_update.status
    )

    status_text = "启用" if batch_update.status else "禁用"
    logger.info(f"批量更新用户状态成功，共 {update_count} 个用户被{status_text}")
    return ResponseModel(
        msg=f"批量{status_text}成功，共 {update_count} 个用户",
        data={"update_count": update_count},
    )


@user_router.delete("/{user_id}", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:user:delete"))])
@log_operation(module="user", action="delete", description="删除用户")
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除用户
    """
    logger.info(f"删除用户请求，用户ID: {user_id}")

    await UserService.delete_user(db, user_id)

    logger.info(f"删除用户成功，用户ID: {user_id}")
    return ResponseModel(msg="删除用户成功")


@user_router.put("/{user_id}/password", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:user:edit"))])
@log_operation(module="user", action="change_password", description="修改用户密码")
async def change_user_password(
    user_id: int,
    request: Request,
    password_update: SysUserPasswordUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    修改用户密码
    """
    logger.info(f"修改用户密码请求，用户ID: {user_id}")

    await UserService.update_user_password(db, user_id, password_update)

    logger.info(f"修改用户密码成功，用户ID: {user_id}")
    return ResponseModel(msg="密码修改成功")
