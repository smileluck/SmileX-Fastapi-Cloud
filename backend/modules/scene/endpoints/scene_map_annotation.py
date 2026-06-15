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
from modules.scene.services.scene_map_annotation_service import SceneMapAnnotationService
from modules.scene.schemas.scene_map_annotation import (
    SceneMapAnnotationCreate,
    SceneMapAnnotationUpdate,
    SceneMapAnnotationResponseData,
)

scene_map_annotation_router = APIRouter(
    prefix="/map/{map_id}/annotation",
    tags=["场景管理/地图标注"],
    dependencies=[Depends(current_user)],
)


@scene_map_annotation_router.get(
    "/list",
    response_model=ResponseModel[List[SceneMapAnnotationResponseData]],
    summary="获取地图标注列表",
    dependencies=[Depends(require_permission("scene:map:list"))],
)
async def get_annotation_list(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取指定地图的标注列表"""
    annotations = await SceneMapAnnotationService.get_list(db, map_id)
    data = [SceneMapAnnotationResponseData.model_validate(a) for a in annotations]
    return response_base.success(data=data)


@scene_map_annotation_router.post(
    "/add",
    response_model=ResponseModel[SceneMapAnnotationResponseData],
    summary="创建地图标注",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def create_annotation(
    map_id: int,
    annotation_create: SceneMapAnnotationCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建地图标注"""
    # 确保 map_id 与路径参数一致
    annotation_create.map_id = map_id
    annotation = await SceneMapAnnotationService.create(db, annotation_create)
    await db.commit()
    await db.refresh(annotation)
    return response_base.success(
        data=SceneMapAnnotationResponseData.model_validate(annotation), msg="创建成功"
    )


@scene_map_annotation_router.put(
    "/{annotation_id}",
    response_model=ResponseModel[SceneMapAnnotationResponseData],
    summary="更新地图标注",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def update_annotation(
    map_id: int,
    annotation_id: int,
    annotation_update: SceneMapAnnotationUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新地图标注"""
    annotation = await SceneMapAnnotationService.update(db, annotation_id, annotation_update)
    await db.commit()
    await db.refresh(annotation)
    return response_base.success(
        data=SceneMapAnnotationResponseData.model_validate(annotation), msg="更新成功"
    )


@scene_map_annotation_router.delete(
    "/{annotation_id}",
    response_model=ResponseModel,
    summary="删除地图标注",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def delete_annotation(
    map_id: int,
    annotation_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除地图标注"""
    await SceneMapAnnotationService.delete(db, annotation_id)
    await db.commit()
    return response_base.success(msg="删除成功")
