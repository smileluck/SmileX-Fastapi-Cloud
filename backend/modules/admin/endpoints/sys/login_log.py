#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
登录日志管理接口
"""
import logging
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.admin.services.sys.login_log_service import LoginLogService
from modules.admin.schemas.sys.login_log import (
    LoginLogQueryParams,
    LoginLogResponse,
    LoginLogDetailResponse,
)

logger = logging.getLogger(__name__)

login_log_router = APIRouter(prefix="/login-log", tags=["系统管理/登录日志"])


@login_log_router.get(
    "/list",
    response_model=ResponsePageModel[LoginLogResponse],
    summary="获取登录日志列表",
    dependencies=[Depends(require_permission("sys:log:list"))],
)
async def get_log_list(
    query_params: LoginLogQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询登录日志列表"""
    query = LoginLogService.build_login_log_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=LoginLogResponse,
    )
    return response_base.page(data=page_data)


@login_log_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量删除登录日志",
    dependencies=[Depends(require_permission("sys:log:delete"))],
)
async def batch_delete_logs(
    log_ids: List[int] = Body(..., description="日志ID列表"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量软删除登录日志"""
    count = await LoginLogService.batch_delete_logs(db, log_ids)
    return response_base.success(data={"deleted": count}, msg="批量删除成功")


@login_log_router.delete(
    "/clear",
    response_model=ResponseModel,
    summary="清理过期登录日志",
    dependencies=[Depends(require_permission("sys:log:delete"))],
)
async def clear_logs(
    days: int = Query(30, description="清理多少天前的日志"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """清理指定天数前的登录日志"""
    count = await LoginLogService.clear_logs(db, days)
    return response_base.success(
        data={"deleted": count}, msg=f"已清理 {days} 天前的日志"
    )


@login_log_router.get(
    "/{log_id}",
    response_model=ResponseModel[LoginLogDetailResponse],
    summary="获取登录日志详情",
)
async def get_log_detail(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取单条登录日志详情"""
    log = await LoginLogService.get_log(db, log_id)
    return response_base.success(
        data=LoginLogDetailResponse.model_validate(log),
        msg="获取登录日志详情成功",
    )


@login_log_router.delete(
    "/{log_id}",
    response_model=ResponseModel,
    summary="删除单条登录日志",
    dependencies=[Depends(require_permission("sys:log:delete"))],
)
async def delete_log(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """软删除单条登录日志"""
    count = await LoginLogService.batch_delete_logs(db, [log_id])
    return response_base.success(data={"deleted": count}, msg="删除成功")
