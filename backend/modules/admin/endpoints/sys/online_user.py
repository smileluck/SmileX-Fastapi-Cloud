#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
在线用户监控接口
"""
import logging

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.i18n import t
from core.response import ResponseModel, ResponsePageModel, response_base
from modules.common.schemas.page import PageRequest, get_page_params
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.admin.services.sys.online_user_service import OnlineUserService
from modules.admin.schemas.sys.online_user import (
    OnlineUserQueryParams,
    OnlineUserResponse,
    KickUserRequest,
    KickAllRequest,
)

logger = logging.getLogger(__name__)

online_user_router = APIRouter(prefix="/online-user", tags=["系统管理/在线用户"])


@online_user_router.get(
    "/list",
    response_model=ResponsePageModel[OnlineUserResponse],
    summary="获取在线用户列表",
    dependencies=[Depends(require_permission("sys:online:list"))],
)
async def get_online_users(
    query_params: OnlineUserQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询当前在线用户列表"""
    # 从租户上下文获取 tenant_id（多租户插件启用时自动注入）
    tenant_id = None
    try:
        from plugins.multi_tenant.deps.tenant_context import get_current_tenant_id
        tenant_id = get_current_tenant_id()
    except ImportError:
        pass

    page_data = await OnlineUserService.get_online_user_page(
        db=db,
        username=query_params.username,
        ip=query_params.ip,
        page=page_params.page,
        page_size=page_params.page_size,
        tenant_id=tenant_id,
    )
    return response_base.page(data=page_data)


@online_user_router.post(
    "/kick",
    response_model=ResponseModel,
    summary="踢用户下线",
    dependencies=[Depends(require_permission("sys:online:kick"))],
)
async def kick_user(
    kick_req: KickUserRequest = Body(..., description="踢用户请求"),
    user: SysUser = Depends(current_user),
):
    """踢除指定用户的指定会话"""
    success = await OnlineUserService.kick_user(
        user_id=kick_req.user_id,
        session_id=kick_req.session_id,
    )
    if not success:
        return response_base.success(msg=t("online_user.session_not_found"))
    return response_base.success(msg=t("online_user.kicked"))


@online_user_router.post(
    "/kick-all",
    response_model=ResponseModel,
    summary="踢用户所有设备下线",
    dependencies=[Depends(require_permission("sys:online:kick"))],
)
async def kick_all_sessions(
    kick_req: KickAllRequest = Body(..., description="踢所有会话请求"),
    user: SysUser = Depends(current_user),
):
    """踢除指定用户的所有会话"""
    count = await OnlineUserService.kick_all_sessions(
        user_id=kick_req.user_id,
    )
    return response_base.success(
        data={"sessions_removed": count},
        msg=t("online_user.kicked_count", count=count),
    )


@online_user_router.post(
    "/kick-all-online",
    response_model=ResponseModel,
    summary="踢所有在线用户下线",
    dependencies=[Depends(require_permission("sys:online:kick"))],
)
async def kick_all_online_users(
    user: SysUser = Depends(current_user),
):
    """踢除所有在线用户的所有会话"""
    count = await OnlineUserService.kick_all_online_users()
    return response_base.success(
        data={"sessions_removed": count},
        msg=t("online_user.kicked_count", count=count),
    )


@online_user_router.get(
    "/count",
    response_model=ResponseModel[int],
    summary="获取在线用户数",
    dependencies=[Depends(require_permission("sys:online:list"))],
)
async def get_online_count(
    user: SysUser = Depends(current_user),
):
    """获取当前在线用户总数"""
    count = await OnlineUserService.get_online_count()
    return response_base.success(data=count)
