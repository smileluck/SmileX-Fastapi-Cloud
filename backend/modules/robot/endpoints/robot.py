#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人管理相关接口
"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import noload

from database.db_manager import get_session
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    response_base,
)
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from database.models.business.robot import Robot
from database.models.business.robot_model import RobotModel
from database.models.business.scene_map import SceneMap

from modules.robot.services.robot_service import RobotService
from modules.robot.services.robot_schema_service import RobotSchemaService
from modules.robot.schemas.robot import (
    RobotCreate,
    RobotUpdate,
    RobotQueryParams,
    RobotResponseData,
)

logger = logging.getLogger(__name__)

robot_router = APIRouter(
    prefix="/manage", tags=["机器人管理"], dependencies=[Depends(current_user)]
)


async def _fill_robot_names(db: AsyncSession, records: list[RobotResponseData]) -> None:
    if not records:
        return

    model_ids = {record.model_id for record in records}
    model_result = await db.execute(select(RobotModel).where(RobotModel.id.in_(model_ids)))
    model_map = {model.id: model.name for model in model_result.scalars().all()}

    map_ids = {record.map_id for record in records if record.map_id is not None}
    map_map = {}
    if map_ids:
        map_result = await db.execute(select(SceneMap).where(SceneMap.id.in_(map_ids)))
        map_map = {scene_map.id: scene_map.name for scene_map in map_result.scalars().all()}

    for record in records:
        record.model_name = model_map.get(record.model_id)
        if record.map_id is not None:
            record.map_name = map_map.get(record.map_id)


@robot_router.get(
    "/list",
    response_model=ResponsePageModel[RobotResponseData],
    dependencies=[Depends(require_permission("robot:manage:list"))],
)
async def get_robot_list(
    query_params: RobotQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取机器人列表（分页）
    """
    try:
        logger.info("获取机器人列表接口被调用")

        await RobotSchemaService.ensure_robot_map_binding(db)
        query = RobotService.build_query(query_params)

        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=RobotResponseData,
        )

        await _fill_robot_names(db, page_data.records)

        logger.info("获取机器人列表接口成功，共 %d 条记录", page_data.total)
        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取机器人列表接口失败: %s", str(e), exc_info=True)
        raise


@robot_router.get(
    "/{robot_id}",
    response_model=ResponseModel[RobotResponseData],
)
async def get_robot(
    robot_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个机器人
    """
    try:
        logger.info("获取机器人详情接口被调用，机器人ID: %d", robot_id)

        await RobotSchemaService.ensure_robot_map_binding(db)
        robot_obj = await RobotService.get(db, robot_id)
        response_data = RobotResponseData.model_validate(robot_obj)
        await _fill_robot_names(db, [response_data])

        logger.info("获取机器人详情接口成功，机器人ID: %d", robot_id)
        return response_base.success(data=response_data)

    except Exception as e:
        logger.error("获取机器人详情接口失败: %s", str(e), exc_info=True)
        raise


@robot_router.post(
    "/add",
    response_model=ResponseModel[RobotResponseData],
    dependencies=[Depends(require_permission("robot:manage:add"))],
)
@log_operation(module="robot", action="create", description="创建机器人")
async def create_robot(
    request: Request,
    robot_in: RobotCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建机器人
    """
    try:
        logger.info("创建机器人接口被调用")

        await RobotSchemaService.ensure_robot_map_binding(db)
        robot_obj = await RobotService.create(db, robot_in)
        response_data = RobotResponseData.model_validate(robot_obj)
        await _fill_robot_names(db, [response_data])

        logger.info("创建机器人接口成功，机器人ID: %d", robot_obj.id)
        return response_base.success(data=response_data, msg="创建成功")

    except Exception as e:
        logger.error("创建机器人接口失败: %s", str(e), exc_info=True)
        raise


@robot_router.put(
    "/{robot_id}",
    response_model=ResponseModel[RobotResponseData],
    dependencies=[Depends(require_permission("robot:manage:edit"))],
)
@log_operation(module="robot", action="update", description="更新机器人")
async def update_robot(
    robot_id: int,
    request: Request,
    robot_in: RobotUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新机器人
    """
    try:
        logger.info("更新机器人接口被调用，机器人ID: %d", robot_id)

        await RobotSchemaService.ensure_robot_map_binding(db)
        robot_obj = await RobotService.update(db, robot_id, robot_in)
        response_data = RobotResponseData.model_validate(robot_obj)
        await _fill_robot_names(db, [response_data])

        logger.info("更新机器人接口成功，机器人ID: %d", robot_id)
        return response_base.success(data=response_data, msg="更新成功")

    except Exception as e:
        logger.error("更新机器人接口失败: %s", str(e), exc_info=True)
        raise


@robot_router.delete(
    "/{robot_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("robot:manage:delete"))],
)
@log_operation(module="robot", action="delete", description="删除机器人")
async def delete_robot(
    robot_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除机器人
    """
    try:
        logger.info("删除机器人接口被调用，机器人ID: %d", robot_id)

        await RobotService.delete(db, robot_id)

        logger.info("删除机器人接口成功，机器人ID: %d", robot_id)
        return response_base.success(msg="删除成功")

    except Exception as e:
        logger.error("删除机器人接口失败: %s", str(e), exc_info=True)
        raise
