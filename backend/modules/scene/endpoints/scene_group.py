#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scene.services.scene_group_service import SceneGroupService
from modules.scene.schemas.scene_group import (
    SceneGroupCreate,
    SceneGroupUpdate,
    SceneGroupQueryParams,
    SceneGroupResponseData,
    SceneGroupTreeResponse,
)

scene_group_router = APIRouter(
    prefix="/group",
    tags=["场景管理/场景分组"],
    dependencies=[Depends(current_user)],
)


@scene_group_router.get(
    "/list",
    response_model=ResponsePageModel[SceneGroupResponseData],
    summary="获取场景分组列表",
    dependencies=[Depends(require_permission("scene:group:list"))],
)
async def get_group_list(
    query_params: SceneGroupQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询场景分组列表"""
    query = SceneGroupService.build_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SceneGroupResponseData,
    )
    return response_base.page(data=page_data)


@scene_group_router.get(
    "/tree",
    response_model=ResponseModel[List[SceneGroupTreeResponse]],
    summary="获取场景分组树形结构",
    dependencies=[Depends(require_permission("scene:group:list"))],
)
async def get_group_tree(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取场景分组树形结构"""
    tree = await SceneGroupService.get_tree(db)
    return response_base.success(data=tree)


@scene_group_router.get(
    "/{group_id}",
    response_model=ResponseModel[SceneGroupResponseData],
    summary="获取场景分组详情",
    dependencies=[Depends(require_permission("scene:group:detail"))],
)
async def get_group(
    group_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取场景分组详情"""
    group = await SceneGroupService.get(db, group_id)
    return response_base.success(data=SceneGroupResponseData.model_validate(group))


@scene_group_router.post(
    "/add",
    response_model=ResponseModel[SceneGroupResponseData],
    summary="创建场景分组",
    dependencies=[Depends(require_permission("scene:group:add"))],
)
async def create_group(
    group_create: SceneGroupCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建场景分组"""
    group = await SceneGroupService.create(db, group_create)
    await db.commit()
    await db.refresh(group)
    return response_base.success(data=SceneGroupResponseData.model_validate(group), msg="创建成功")


@scene_group_router.put(
    "/{group_id}",
    response_model=ResponseModel[SceneGroupResponseData],
    summary="更新场景分组",
    dependencies=[Depends(require_permission("scene:group:edit"))],
)
async def update_group(
    group_id: int,
    group_update: SceneGroupUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新场景分组"""
    group = await SceneGroupService.update(db, group_id, group_update)
    await db.commit()
    await db.refresh(group)
    return response_base.success(data=SceneGroupResponseData.model_validate(group), msg="更新成功")


@scene_group_router.delete(
    "/{group_id}",
    response_model=ResponseModel,
    summary="删除场景分组",
    dependencies=[Depends(require_permission("scene:group:delete"))],
)
async def delete_group(
    group_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除场景分组"""
    await SceneGroupService.delete(db, group_id)
    await db.commit()
    return response_base.success(msg="删除成功")
