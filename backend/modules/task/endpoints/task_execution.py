#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务执行控制接口
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

from modules.task.services.task_execution_service import TaskExecutionService
from modules.task.schemas.task import (
    TaskExecutionQueryParams,
    TaskExecutionResponseData,
    TaskExecutionDetailResponseData,
    TaskPointResponse,
)

logger = logging.getLogger(__name__)

task_execution_router = APIRouter(
    prefix="/execution", tags=["任务执行"], dependencies=[Depends(current_user)]
)


async def _build_execution_response(exec_obj, db: AsyncSession = None) -> TaskExecutionResponseData:
    """构建执行记录响应"""
    data = TaskExecutionResponseData.model_validate(exec_obj)

    # 获取机器人名称
    if exec_obj.robot_id and db:
        robot_result = await db.execute(
            select(Robot.name).where(Robot.id == exec_obj.robot_id)
        )
        data.robot_name = robot_result.scalar_one_or_none()

    return data


@task_execution_router.post(
    "/{task_id}/start",
    response_model=ResponseModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:execution:start"))],
)
@log_operation(module="task", action="start", description="启动任务")
async def start_task_execution(
    task_id: int,
    request: Request,
    robot_ids: List[int] = [],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """启动任务执行"""
    try:
        exec_obj = await TaskExecutionService.start_execution(db, task_id, robot_ids)
        response_data = await _build_execution_response(exec_obj, db)
        return response_base.success(data=response_data, msg="任务已启动")

    except Exception as e:
        logger.error("启动任务执行失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.post(
    "/{exec_id}/pause",
    response_model=ResponseModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:execution:control"))],
)
async def pause_execution(
    exec_id: int,
    db: AsyncSession = Depends(get_session),
):
    """暂停执行"""
    try:
        exec_obj = await TaskExecutionService.pause_execution(db, exec_id)
        response_data = await _build_execution_response(exec_obj, db)
        return response_base.success(data=response_data, msg="任务已暂停")

    except Exception as e:
        logger.error("暂停任务执行失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.post(
    "/{exec_id}/resume",
    response_model=ResponseModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:execution:control"))],
)
async def resume_execution(
    exec_id: int,
    db: AsyncSession = Depends(get_session),
):
    """恢复执行"""
    try:
        exec_obj = await TaskExecutionService.resume_execution(db, exec_id)
        response_data = await _build_execution_response(exec_obj, db)
        return response_base.success(data=response_data, msg="任务已恢复")

    except Exception as e:
        logger.error("恢复任务执行失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.post(
    "/{exec_id}/stop",
    response_model=ResponseModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:execution:control"))],
)
@log_operation(module="task", action="stop", description="停止任务")
async def stop_execution(
    exec_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """停止执行"""
    try:
        exec_obj = await TaskExecutionService.stop_execution(db, exec_id)
        response_data = await _build_execution_response(exec_obj, db)
        return response_base.success(data=response_data, msg="任务已停止")

    except Exception as e:
        logger.error("停止任务执行失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.get(
    "/active",
    response_model=ResponsePageModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:list"))],
)
async def get_active_executions(
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """获取活跃执行列表"""
    try:
        query = TaskExecutionService.build_active_query()
        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=TaskExecutionResponseData,
        )

        # 补充机器人名称
        if page_data.records:
            for record in page_data.records:
                if record.robot_id:
                    robot_result = await db.execute(
                        select(Robot.name).where(Robot.id == record.robot_id)
                    )
                    record.robot_name = robot_result.scalar_one_or_none()

        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取活跃执行列表失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.get(
    "/history",
    response_model=ResponsePageModel[TaskExecutionResponseData],
    dependencies=[Depends(require_permission("task:list"))],
)
async def get_execution_history(
    query_params: TaskExecutionQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """获取历史执行记录"""
    try:
        query = TaskExecutionService.build_history_query(query_params)
        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=TaskExecutionResponseData,
        )

        # 补充机器人名称
        if page_data.records:
            for record in page_data.records:
                if record.robot_id:
                    robot_result = await db.execute(
                        select(Robot.name).where(Robot.id == record.robot_id)
                    )
                    record.robot_name = robot_result.scalar_one_or_none()

        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取历史执行记录失败: %s", str(e), exc_info=True)
        raise


@task_execution_router.get(
    "/detail/{exec_id}",
    response_model=ResponseModel[TaskExecutionDetailResponseData],
)
async def get_execution_detail(
    exec_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取执行详情"""
    try:
        exec_obj = await TaskExecutionService.get_execution_detail(db, exec_id)
        data = await _build_execution_response(exec_obj, db)

        # 构建详情响应
        detail_data = TaskExecutionDetailResponseData(**data.model_dump())

        # 获取关联点位
        if hasattr(exec_obj, '_task_points'):
            detail_data.points = [TaskPointResponse.model_validate(p) for p in exec_obj._task_points]

        return response_base.success(data=detail_data)

    except Exception as e:
        logger.error("获取执行详情失败: %s", str(e), exc_info=True)
        raise
