#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base, ResponsePageDataModel
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scene.services.scene_map_service import SceneMapService
from modules.scene.schemas.scene_map import (
    SceneMapCreate,
    SceneMapUpdate,
    SceneMapQueryParams,
    SceneMapResponseData,
)

scene_map_router = APIRouter(
    prefix="/map",
    tags=["场景管理/场景地图"],
    dependencies=[Depends(current_user)],
)


@scene_map_router.get(
    "/list",
    response_model=ResponsePageModel[SceneMapResponseData],
    summary="获取场景地图列表",
    dependencies=[Depends(require_permission("scene:map:list"))],
)
async def get_map_list(
    query_params: SceneMapQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询场景地图列表（含分组名称）"""
    items, total = await SceneMapService.get_list_with_group_name(db, query_params)

    pages = (total + page_params.page_size - 1) // page_params.page_size
    page_data = ResponsePageDataModel(
        records=items,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
        total_pages=pages,
    )
    return response_base.page(data=page_data)


@scene_map_router.get(
    "/{map_id}",
    response_model=ResponseModel[SceneMapResponseData],
    summary="获取场景地图详情",
    dependencies=[Depends(require_permission("scene:map:detail"))],
)
async def get_map(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取场景地图详情"""
    map_obj = await SceneMapService.get(db, map_id)
    return response_base.success(data=SceneMapResponseData.model_validate(map_obj))


@scene_map_router.post(
    "/add",
    response_model=ResponseModel[SceneMapResponseData],
    summary="创建场景地图",
    dependencies=[Depends(require_permission("scene:map:add"))],
)
async def create_map(
    map_create: SceneMapCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建场景地图"""
    map_obj = await SceneMapService.create(db, map_create)
    await db.commit()
    await db.refresh(map_obj)
    return response_base.success(data=SceneMapResponseData.model_validate(map_obj), msg="创建成功")


@scene_map_router.put(
    "/{map_id}",
    response_model=ResponseModel[SceneMapResponseData],
    summary="更新场景地图",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def update_map(
    map_id: int,
    map_update: SceneMapUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新场景地图"""
    map_obj = await SceneMapService.update(db, map_id, map_update)
    await db.commit()
    await db.refresh(map_obj)
    return response_base.success(data=SceneMapResponseData.model_validate(map_obj), msg="更新成功")


@scene_map_router.delete(
    "/{map_id}",
    response_model=ResponseModel,
    summary="删除场景地图",
    dependencies=[Depends(require_permission("scene:map:delete"))],
)
async def delete_map(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除场景地图"""
    await SceneMapService.delete(db, map_id)
    await db.commit()
    return response_base.success(msg="删除成功")
