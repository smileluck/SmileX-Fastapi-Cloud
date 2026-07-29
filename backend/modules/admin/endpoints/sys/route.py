#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
动态路由相关接口
"""
import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.i18n import t
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from database.models.sys.user import SysUser
from modules.admin.services.sys.route_service import RouteService
from modules.admin.schemas.sys.route import (
    MenuRouteResponse,
    UserRouteResponse,
)

logger = logging.getLogger(__name__)

route_router = APIRouter(prefix="/route", tags=["系统管理/动态路由"])


@route_router.get(
    "/getConstantRoutes",
    response_model=ResponseModel[list[MenuRouteResponse]],
    summary="获取常量路由",
    description="获取不需要权限控制的常量路由（登录页、错误页等）",
)
async def get_constant_routes():
    routes = await RouteService.get_constant_routes()
    return response_base.success(data=routes, msg=t("route.constant_success"))


@route_router.get(
    "/getPermissions",
    response_model=ResponseModel[UserRouteResponse],
    summary="获取当前用户路由与按钮权限",
    description="根据当前登录用户的角色，返回可用的路由树及按钮权限标识列表",
)
async def get_permissions(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await RouteService.get_user_routes(db, user)
    return response_base.success(data=result, msg=t("route.user_permission_success"))


@route_router.get(
    "/isRouteExist",
    response_model=ResponseModel[bool],
    summary="检查路由是否存在",
)
async def is_route_exist(
    routeName: str = Query(..., description="路由名称"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    exists = await RouteService.is_route_exist(db, routeName)
    return response_base.success(data=exists)
