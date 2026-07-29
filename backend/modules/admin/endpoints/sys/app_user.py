#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用用户（AppUser）管理相关接口
供后台运营人员对 C 端应用用户进行增删改查、批量启停与改密。
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.admin.services.sys import AppUserService
from modules.admin.schemas.sys.app_user import (
    AppUserResponseData,
    AppUserListResponse,
    AppUserCreate,
    AppUserUpdate,
    AppUserPasswordUpdate,
    AppUserQueryParams,
    AppUserBatchUpdateStatus,
)

logger = logging.getLogger(__name__)

# 创建应用用户管理路由
app_user_router = APIRouter(
    prefix="/app-user", tags=["应用用户管理"], dependencies=[Depends(current_user)]
)


@app_user_router.get(
    "/list",
    response_model=ResponsePageModel[AppUserListResponse],
    dependencies=[Depends(require_permission("sys:app_user:list"))],
)
async def get_app_user_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: AppUserQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    获取应用用户列表
    """
    logger.info("获取应用用户列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = AppUserService.build_app_user_list_query(query_params)

    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=AppUserListResponse,
    )

    logger.info("获取应用用户列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[AppUserListResponse](data=page_data)


@app_user_router.get(
    "/{user_id}", response_model=ResponseModel[AppUserResponseData]
)
async def get_app_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个应用用户
    """
    logger.info("获取单个应用用户请求，用户ID: %s", user_id)

    user = await AppUserService.get_app_user(db, user_id)
    user_response = AppUserResponseData.model_validate(user)

    logger.info("获取单个应用用户成功，用户ID: %s", user_id)
    return ResponseModel(data=user_response)


@app_user_router.post(
    "/add",
    response_model=ResponseModel[AppUserResponseData],
    dependencies=[Depends(require_permission("sys:app_user:add"))],
)
@log_operation(module="app_user", action="create", description="创建应用用户")
async def create_app_user(
    request: Request,
    user_create: AppUserCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建应用用户
    """
    logger.info("创建应用用户请求，手机号: %s", user_create.phone)

    app_user = await AppUserService.create_app_user(db, user_create)
    user_response = AppUserResponseData.model_validate(app_user)

    logger.info("创建应用用户成功，用户ID: %s", app_user.id)
    return ResponseModel(data=user_response, msg=t("app_user.create_success"))


@app_user_router.put(
    "/{user_id}",
    response_model=ResponseModel[AppUserResponseData],
    dependencies=[Depends(require_permission("sys:app_user:edit"))],
)
@log_operation(module="app_user", action="update", description="更新应用用户")
async def update_app_user(
    user_id: int,
    request: Request,
    user_update: AppUserUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新应用用户
    """
    logger.info("更新应用用户请求，用户ID: %s", user_id)

    app_user = await AppUserService.update_app_user(db, user_id, user_update)
    user_response = AppUserResponseData.model_validate(app_user)

    logger.info("更新应用用户成功，用户ID: %s", user_id)
    return ResponseModel(data=user_response, msg=t("app_user.update_success"))


@app_user_router.delete(
    "/batch",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:app_user:delete"))],
)
@log_operation(module="app_user", action="batch_delete", description="批量删除应用用户")
async def batch_delete_app_users(
    request: Request,
    user_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除应用用户
    """
    logger.info("批量删除应用用户请求，用户ID: %s", user_ids)

    delete_count = await AppUserService.batch_delete_app_users(db, user_ids)

    logger.info("批量删除应用用户成功，共删除 %s 个", delete_count)
    return ResponseModel(
        msg=t("app_user.batch_delete_success", count=delete_count),
        data={"delete_count": delete_count},
    )


@app_user_router.put(
    "/batch/status",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:app_user:edit"))],
)
@log_operation(module="app_user", action="batch_update_status", description="批量更新应用用户状态")
async def batch_update_app_users_status(
    request: Request,
    batch_update: AppUserBatchUpdateStatus,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量更新应用用户状态
    """
    logger.info(
        "批量更新应用用户状态请求，用户ID: %s, 状态: %s",
        batch_update.user_ids,
        batch_update.status,
    )

    update_count = await AppUserService.batch_update_app_users_status(
        db, batch_update.user_ids, batch_update.status
    )

    status_text = t("common.enable") if batch_update.status else t("common.disable")
    logger.info("批量更新应用用户状态成功，共 %s 个被%s", update_count, status_text)
    return ResponseModel(
        msg=t("app_user.batch_status_success", action=status_text, count=update_count),
        data={"update_count": update_count},
    )


@app_user_router.delete(
    "/{user_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:app_user:delete"))],
)
@log_operation(module="app_user", action="delete", description="删除应用用户")
async def delete_app_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除应用用户
    """
    logger.info("删除应用用户请求，用户ID: %s", user_id)

    await AppUserService.delete_app_user(db, user_id)

    logger.info("删除应用用户成功，用户ID: %s", user_id)
    return ResponseModel(msg=t("app_user.delete_success"))


@app_user_router.put(
    "/{user_id}/password",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:app_user:edit"))],
)
@log_operation(module="app_user", action="reset_password", description="重置应用用户密码")
async def change_app_user_password(
    user_id: int,
    request: Request,
    password_update: AppUserPasswordUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    重置应用用户密码（改密后该用户所有设备需重新登录）
    """
    logger.info("重置应用用户密码请求，用户ID: %s", user_id)

    await AppUserService.update_app_user_password(db, user_id, password_update)

    logger.info("重置应用用户密码成功，用户ID: %s", user_id)
    return ResponseModel(msg=t("app_user.password_reset_success"))
