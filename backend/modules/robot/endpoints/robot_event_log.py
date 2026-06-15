#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人事件日志管理接口
"""
import logging
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from database.models.business.robot import Robot
from modules.robot.services.robot_event_log_service import RobotEventLogService
from modules.robot.schemas.robot_event_log import (
    RobotEventLogQueryParams,
    RobotEventLogResponse,
    RobotEventLogDetailResponse,
)

logger = logging.getLogger(__name__)

robot_event_log_router = APIRouter(
    prefix="/event-log", tags=["机器人/事件日志"], dependencies=[Depends(current_user)]
)


async def _fill_robot_names(db: AsyncSession, records: list) -> None:
    """批量填充机器人名称"""
    if not records:
        return

    robot_ids = {record.robot_id for record in records}
    result = await db.execute(select(Robot).where(Robot.id.in_(robot_ids)))
    robot_map = {r.id: r.name for r in result.scalars().all()}

    for record in records:
        record.robot_name = robot_map.get(record.robot_id)


@robot_event_log_router.get(
    "/list",
    response_model=ResponsePageModel[RobotEventLogResponse],
    summary="获取机器人事件日志列表",
    dependencies=[Depends(require_permission("robot:event-log:list"))],
)
async def get_event_log_list(
    query_params: RobotEventLogQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询机器人事件日志列表"""
    query = RobotEventLogService.build_event_log_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=RobotEventLogResponse,
    )
    if page_data.records:
        await _fill_robot_names(db, page_data.records)
    return response_base.page(data=page_data)


@robot_event_log_router.get(
    "/{log_id}",
    response_model=ResponseModel[RobotEventLogDetailResponse],
    summary="获取机器人事件日志详情",
)
async def get_event_log_detail(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取单条机器人事件日志详情"""
    log = await RobotEventLogService.get_log(db, log_id)
    response_data = RobotEventLogDetailResponse.model_validate(log)
    robot_ids = {response_data.robot_id}
    result = await db.execute(select(Robot).where(Robot.id.in_(robot_ids)))
    robot_map = {r.id: r.name for r in result.scalars().all()}
    response_data.robot_name = robot_map.get(response_data.robot_id)
    return response_base.success(data=response_data, msg="获取机器人事件日志详情成功")


@robot_event_log_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量删除机器人事件日志",
    dependencies=[Depends(require_permission("robot:event-log:delete"))],
)
async def batch_delete_logs(
    log_ids: List[int] = ...,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量删除机器人事件日志"""
    count = await RobotEventLogService.batch_delete_logs(db, log_ids)
    return response_base.success(data={"deleted": count}, msg="批量删除成功")


@robot_event_log_router.delete(
    "/clear",
    response_model=ResponseModel,
    summary="清理过期机器人事件日志",
    dependencies=[Depends(require_permission("robot:event-log:delete"))],
)
async def clear_logs(
    days: int = Query(30, description="清理多少天前的日志"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """清理指定天数前的机器人事件日志"""
    count = await RobotEventLogService.clear_logs(db, days)
    return response_base.success(data={"deleted": count}, msg=f"已清理 {days} 天前的日志")


@robot_event_log_router.delete(
    "/{log_id}",
    response_model=ResponseModel,
    summary="删除单条机器人事件日志",
    dependencies=[Depends(require_permission("robot:event-log:delete"))],
)
async def delete_log(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除单条机器人事件日志"""
    count = await RobotEventLogService.batch_delete_logs(db, [log_id])
    return response_base.success(data={"deleted": count}, msg="删除成功")
