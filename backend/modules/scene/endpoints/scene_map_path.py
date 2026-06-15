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
from modules.scene.services.scene_map_path_service import SceneMapPathService
from modules.scene.schemas.scene_map_path import (
    SceneMapPathCreate,
    SceneMapPathUpdate,
    SceneMapPathResponseData,
)

scene_map_path_router = APIRouter(
    prefix="/map/{map_id}/path",
    tags=["场景管理/地图路径"],
    dependencies=[Depends(current_user)],
)


@scene_map_path_router.get(
    "/list",
    response_model=ResponseModel[List[SceneMapPathResponseData]],
    summary="获取地图路径列表",
    dependencies=[Depends(require_permission("scene:map:list"))],
)
async def get_path_list(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取指定地图的路径列表"""
    paths = await SceneMapPathService.get_list(db, map_id)
    data = [SceneMapPathResponseData.model_validate(p) for p in paths]
    return response_base.success(data=data)


@scene_map_path_router.post(
    "/add",
    response_model=ResponseModel[SceneMapPathResponseData],
    summary="创建地图路径",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def create_path(
    map_id: int,
    path_create: SceneMapPathCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建地图路径"""
    path_create.map_id = map_id
    path = await SceneMapPathService.create(db, path_create)
    await db.commit()
    await db.refresh(path)
    return response_base.success(
        data=SceneMapPathResponseData.model_validate(path), msg="创建成功"
    )


@scene_map_path_router.put(
    "/{path_id}",
    response_model=ResponseModel[SceneMapPathResponseData],
    summary="更新地图路径",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def update_path(
    map_id: int,
    path_id: int,
    path_update: SceneMapPathUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新地图路径"""
    path = await SceneMapPathService.update(db, path_id, path_update)
    await db.commit()
    await db.refresh(path)
    return response_base.success(
        data=SceneMapPathResponseData.model_validate(path), msg="更新成功"
    )


@scene_map_path_router.delete(
    "/{path_id}",
    response_model=ResponseModel,
    summary="删除地图路径",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def delete_path(
    map_id: int,
    path_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除地图路径"""
    await SceneMapPathService.delete(db, path_id)
    await db.commit()
    return response_base.success(msg="删除成功")
