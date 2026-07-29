#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限管理相关接口
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.i18n import t
from core.response.response_schema import ResponseModel
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from database.models.sys.user import SysUser

from modules.admin.services.sys import PermissionService
from modules.admin.schemas.sys.permission import (
    SysPermissionQueryParams,
    SysPermissionCreate,
    SysPermissionUpdate,
    SysPermissionResponse,
)

# 创建权限管理路由
permission_router = APIRouter(prefix="/permission", tags=["权限管理"])


@permission_router.get("/list", response_model=ResponseModel[List[SysPermissionResponse]])
async def get_permission_list(
    query_params: SysPermissionQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    获取权限列表
    """
    permissions = await PermissionService.get_permission_list(
        db, query_params.category, query_params.status
    )
    return ResponseModel(data=permissions)


@permission_router.post("/add", response_model=ResponseModel[SysPermissionResponse])
@log_operation(module="permission", action="create", description="创建权限")
async def create_permission(
    request: Request,
    permission_in: SysPermissionCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建权限
    """
    permission = await PermissionService.create_permission(db, permission_in)
    return ResponseModel(data=SysPermissionResponse.model_validate(permission), msg=t("common.create_success"))


@permission_router.put("/{permission_id}", response_model=ResponseModel[SysPermissionResponse])
@log_operation(module="permission", action="update", description="更新权限")
async def update_permission(
    permission_id: int,
    request: Request,
    permission_in: SysPermissionUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新权限
    """
    permission = await PermissionService.update_permission(
        db, permission_id, permission_in
    )
    return ResponseModel(data=SysPermissionResponse.model_validate(permission), msg=t("common.update_success"))


@permission_router.delete("/{permission_id}", response_model=ResponseModel)
@log_operation(module="permission", action="delete", description="删除权限")
async def delete_permission(
    permission_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除权限
    """
    await PermissionService.delete_permission(db, permission_id)
    return ResponseModel(msg=t("common.delete_success"))
