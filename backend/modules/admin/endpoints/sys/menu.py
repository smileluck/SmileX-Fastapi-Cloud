#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单管理相关接口
"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.i18n import t
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    ResponsePageDataModel,
    response_base,
)
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.admin.services.sys import MenuService
from modules.admin.schemas.sys.menu import (
    SysMenuResponseData,
    SysMenuTreeResponse,
    SysMenuCreate,
    SysMenuUpdate,
    SysMenuQueryParams,
    SysMenuTreeQuery,
    SysMenuBatchUpdateStatus,
)
from database.models.sys.menu import MenuType

logger = logging.getLogger(__name__)

# 页面组件列表（模拟前端的视图组件）
PAGE_COMPONENTS = [
    "403",
    "404",
    "500",
    "iframe-page",
    "login",
    "home",
    "manage_config",
    "manage_dict",
    "manage_menu",
    "manage_role",
    "manage_user-detail",
    "manage_user",
    "log_login-log",
    "log_operation-log",
    "monitor",
]


# 创建菜单管理路由
menu_router = APIRouter(
    prefix="/menu", tags=["菜单管理"], dependencies=[Depends(current_user)]
)


@menu_router.get("/pages", response_model=ResponseModel[List[str]])
async def get_all_pages():
    """
    获取所有页面组件列表
    """
    logger.info("获取所有页面组件列表")
    return ResponseModel(data=PAGE_COMPONENTS)


@menu_router.get("/list", response_model=ResponsePageModel[SysMenuResponseData], dependencies=[Depends(require_permission("sys:menu:list"))])
async def get_menu_list(
    query_params: SysMenuQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取菜单列表（分页）
    """
    logger.info("获取菜单列表请求")

    # 合并分页参数
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    # 构建查询对象
    query = MenuService.build_menu_query(query_params)

    # 使用通用分页方法
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SysMenuResponseData,
    )

    logger.info(f"获取菜单列表成功，共 {page_data.total} 条记录")
    return response_base.page(data=page_data)


@menu_router.get("/list-tree", response_model=ResponseModel[List[SysMenuResponseData]], dependencies=[Depends(require_permission("sys:menu:list"))])
async def get_menu_list_tree(
    db: AsyncSession = Depends(get_session),
):
    """
    获取菜单树形列表（包含完整菜单信息）
    """
    logger.info("获取菜单树形列表请求")

    menu_tree = await MenuService.build_menu_tree_list(db)

    logger.info(f"获取菜单树形列表成功")
    return ResponseModel(data=menu_tree)


@menu_router.get("/tree", response_model=ResponseModel[List[SysMenuTreeResponse]], dependencies=[Depends(require_permission("sys:menu:list"))])
async def get_menu_tree(
    query_params: SysMenuTreeQuery = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    获取菜单树结构
    """
    logger.info("获取菜单树结构请求")

    menu_tree = await MenuService.get_menu_tree(db, status=query_params.status)

    logger.info(f"获取菜单树结构成功，共 {len(menu_tree)} 个根菜单")
    return ResponseModel(data=menu_tree)


@menu_router.get("/assign-tree", response_model=ResponseModel[List[SysMenuTreeResponse]])
async def get_assign_menu_tree(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    获取当前用户可分配的菜单权限树（含按钮）。
    用于角色权限分配时，只展示当前用户自身拥有的菜单和按钮。
    """
    logger.info(f"获取用户可分配菜单树，用户ID: {user.id}")

    menu_tree = await MenuService.get_user_assign_menu_tree(db, user)

    logger.info(f"获取用户可分配菜单树成功，共 {len(menu_tree)} 个根菜单")
    return ResponseModel(data=menu_tree)


@menu_router.get(
    "/user-menus", response_model=ResponseModel[List[SysMenuTreeResponse]]
)
async def get_user_menus(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    获取当前用户的菜单权限树
    根据当前用户角色返回可访问的菜单树结构
    """
    logger.info(f"获取用户菜单权限树请求，用户ID: {user.id}")

    menu_tree = await MenuService.get_user_menu_tree(db, user)

    logger.info(f"获取用户菜单权限树成功，共 {len(menu_tree)} 个根菜单")
    return ResponseModel(data=menu_tree)


@menu_router.get("/{menu_id}", response_model=ResponseModel[SysMenuResponseData])
async def get_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个菜单
    """
    logger.info(f"获取单个菜单请求，菜单ID: {menu_id}")

    menu = await MenuService.get_menu(db, menu_id)
    menu_response = SysMenuResponseData.model_validate(menu)

    logger.info(f"获取单个菜单成功，菜单ID: {menu_id}")
    return ResponseModel(data=menu_response)


@menu_router.post("/add", response_model=ResponseModel[SysMenuResponseData], dependencies=[Depends(require_permission("sys:menu:add"))])
@log_operation(module="menu", action="create", description="创建菜单")
async def create_menu(
    request: Request,
    menu_create: SysMenuCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建菜单
    """
    logger.info(f"创建菜单请求，菜单名称: {menu_create.name}")

    menu = await MenuService.create_menu(db, menu_create, is_superuser=user.is_superuser)
    menu_response = SysMenuResponseData.model_validate(menu)

    logger.info(f"创建菜单成功，菜单ID: {menu.id}")
    return ResponseModel(data=menu_response, msg=t("menu.create_success"))


@menu_router.put("/{menu_id}", response_model=ResponseModel[SysMenuResponseData], dependencies=[Depends(require_permission("sys:menu:edit"))])
@log_operation(module="menu", action="update", description="更新菜单")
async def update_menu(
    menu_id: int,
    request: Request,
    menu_update: SysMenuUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新菜单
    """
    logger.info(f"更新菜单请求，菜单ID: {menu_id}")

    menu = await MenuService.update_menu(db, menu_id, menu_update, is_superuser=user.is_superuser)
    menu_response = SysMenuResponseData.model_validate(menu)

    logger.info(f"更新菜单成功，菜单ID: {menu_id}")
    return ResponseModel(data=menu_response, msg=t("menu.update_success"))


@menu_router.delete("/batch/delete", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:menu:delete"))])
@log_operation(module="menu", action="batch_delete", description="批量删除菜单")
async def batch_delete_menus(
    request: Request,
    menu_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除菜单
    """
    logger.info(f"批量删除菜单请求，菜单ID: {menu_ids}")

    delete_count = await MenuService.batch_delete_menus(db, menu_ids, is_superuser=user.is_superuser)

    logger.info(f"批量删除菜单成功，共删除 {delete_count} 个菜单")
    return ResponseModel(
        msg=t("menu.batch_delete_success", count=delete_count),
        data={"delete_count": delete_count},
    )


@menu_router.put("/batch/status", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:menu:edit"))])
@log_operation(module="menu", action="batch_update_status", description="批量更新菜单状态")
async def batch_update_menus_status(
    request: Request,
    batch_update: SysMenuBatchUpdateStatus,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量更新菜单状态
    """
    logger.info(
        f"批量更新菜单状态请求，菜单ID: {batch_update.menu_ids}, 状态: {batch_update.status}"
    )

    update_count = await MenuService.batch_update_menus_status(
        db, batch_update.menu_ids, batch_update.status, is_superuser=user.is_superuser
    )

    status_text = t("common.enable") if batch_update.status else t("common.disable")
    logger.info(f"批量更新菜单状态成功，共 {update_count} 个菜单被{status_text}")
    return ResponseModel(
        msg=t("menu.batch_status_success", action=status_text, count=update_count),
        data={"update_count": update_count},
    )


@menu_router.delete("/{menu_id}", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:menu:delete"))])
@log_operation(module="menu", action="delete", description="删除菜单")
async def delete_menu(
    menu_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除菜单
    """
    logger.info(f"删除菜单请求，菜单ID: {menu_id}")

    await MenuService.delete_menu(db, menu_id, is_superuser=user.is_superuser)

    logger.info(f"删除菜单成功，菜单ID: {menu_id}")
    return ResponseModel(msg=t("menu.delete_success"))
