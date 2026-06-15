#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scene.services.scene_map_object_service import SceneMapObjectService
from modules.scene.schemas.scene_map_object import (
    SceneMapObjectCreate,
    SceneMapObjectUpdate,
    SceneMapObjectResponseData,
)

scene_map_object_router = APIRouter(
    prefix="/map/{map_id}/object",
    tags=["场景管理/地图物体"],
    dependencies=[Depends(current_user)],
)


@scene_map_object_router.get(
    "/list",
    response_model=ResponseModel[List[SceneMapObjectResponseData]],
    summary="获取地图物体列表",
    dependencies=[Depends(require_permission("scene:map:list"))],
)
async def get_object_list(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取指定地图的物体列表"""
    objects = await SceneMapObjectService.get_list(db, map_id)
    data = [SceneMapObjectResponseData.model_validate(o) for o in objects]
    return response_base.success(data=data)


@scene_map_object_router.post(
    "/add",
    response_model=ResponseModel[SceneMapObjectResponseData],
    summary="创建地图物体",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def create_object(
    map_id: int,
    object_create: SceneMapObjectCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建地图物体"""
    # 确保 map_id 与路径参数一致
    object_create.map_id = map_id
    obj = await SceneMapObjectService.create(db, object_create)
    await db.commit()
    await db.refresh(obj)
    return response_base.success(
        data=SceneMapObjectResponseData.model_validate(obj), msg="创建成功"
    )


@scene_map_object_router.put(
    "/{object_id}",
    response_model=ResponseModel[SceneMapObjectResponseData],
    summary="更新地图物体",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def update_object(
    map_id: int,
    object_id: int,
    object_update: SceneMapObjectUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新地图物体"""
    obj = await SceneMapObjectService.update(db, object_id, object_update)
    await db.commit()
    await db.refresh(obj)
    return response_base.success(
        data=SceneMapObjectResponseData.model_validate(obj), msg="更新成功"
    )


@scene_map_object_router.delete(
    "/{object_id}",
    response_model=ResponseModel,
    summary="删除地图物体",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def delete_object(
    map_id: int,
    object_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除地图物体"""
    await SceneMapObjectService.delete(db, object_id)
    await db.commit()
    return response_base.success(msg="删除成功")
