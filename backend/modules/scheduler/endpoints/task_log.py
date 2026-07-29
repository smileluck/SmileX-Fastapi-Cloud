#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base
from core.i18n import t
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scheduler.services.task_log_service import TaskLogService
from modules.scheduler.schemas.task_log import (
    TaskLogQueryParams,
    TaskLogResponse,
    TaskLogDetailResponse,
)

scheduler_log_router = APIRouter(
    prefix="/scheduler-log",
    tags=["系统管理/任务执行日志"],
    dependencies=[Depends(current_user)],
)


@scheduler_log_router.get(
    "/list",
    response_model=ResponsePageModel[TaskLogResponse],
    summary="获取任务执行日志列表",
    dependencies=[Depends(require_permission("sys:scheduler:log:list"))],
)
async def get_log_list(
    query_params: TaskLogQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询任务执行日志"""
    query = TaskLogService.build_log_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=TaskLogResponse,
    )
    return response_base.page(data=page_data)


@scheduler_log_router.get(
    "/{log_id}",
    response_model=ResponseModel[TaskLogDetailResponse],
    summary="获取任务执行日志详情",
    dependencies=[Depends(require_permission("sys:scheduler:log:detail"))],
)
async def get_log(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取任务执行日志详情"""
    log = await TaskLogService.get_log(db, log_id)
    return response_base.success(data=TaskLogDetailResponse.model_validate(log))


@scheduler_log_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量删除任务执行日志",
    dependencies=[Depends(require_permission("sys:scheduler:log:delete"))],
)
async def batch_delete_logs(
    log_ids: list[int],
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量删除任务执行日志"""
    count = await TaskLogService.batch_delete_logs(db, log_ids)
    return response_base.success(data={"deleted": count}, msg=t("common.delete_success"))


@scheduler_log_router.delete(
    "/clear",
    response_model=ResponseModel,
    summary="清理过期任务执行日志",
    dependencies=[Depends(require_permission("sys:scheduler:log:delete"))],
)
async def clear_logs(
    days: int = 30,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """清理指定天数前的任务执行日志"""
    count = await TaskLogService.clear_logs(db, days)
    return response_base.success(data={"deleted": count}, msg=t("scheduler.cleaned_logs", count=count))
