#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scene.services.scene_map_editor_service import SceneMapEditorService
from modules.scene.schemas.scene_map_editor import (
    EditorSaveRequest,
    EditorMapDataResponse,
    EditorMapAnnotationResponse,
    EditorMapPathResponse,
    EditorMapObjectResponse,
)
from modules.scene.schemas.scene_map import SceneMapResponseData

scene_map_editor_router = APIRouter(
    prefix="/map/{map_id}/editor",
    tags=["场景管理/地图编辑器"],
    dependencies=[Depends(current_user)],
)


@scene_map_editor_router.get(
    "/data",
    response_model=ResponseModel[EditorMapDataResponse],
    summary="获取编辑器完整数据",
    dependencies=[Depends(require_permission("scene:map:list"))],
)
async def get_editor_data(
    map_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取地图编辑器所需的完整数据（地图元数据 + 标注 + 路径 + 物体）"""
    map_obj = await SceneMapEditorService.get_editor_data(db, map_id)

    data = EditorMapDataResponse(
        map=SceneMapResponseData.model_validate(map_obj).model_dump(),
        annotations=[
            EditorMapAnnotationResponse.model_validate(a)
            for a in map_obj.annotations
        ],
        paths=[
            EditorMapPathResponse.model_validate(p)
            for p in map_obj.paths
        ],
        objects=[
            EditorMapObjectResponse.model_validate(o)
            for o in map_obj.objects
        ],
    )
    return response_base.success(data=data)


@scene_map_editor_router.post(
    "/save",
    response_model=ResponseModel,
    summary="批量保存编辑器数据",
    dependencies=[Depends(require_permission("scene:map:edit"))],
)
async def save_editor_data(
    map_id: int,
    save_request: EditorSaveRequest,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量保存编辑器数据（标注、路径、物体的增删改）"""
    await SceneMapEditorService.save_editor_data(db, map_id, save_request)
    await db.commit()
    return response_base.success(msg="保存成功")
