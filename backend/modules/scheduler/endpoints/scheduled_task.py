#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, ResponsePageModel, response_base
from core.i18n import t
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.scheduler.services.scheduler_service import SchedulerService
from modules.scheduler.services.task_log_service import TaskLogService
from modules.scheduler.schemas.scheduled_task import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskQueryParams,
    ScheduledTaskResponse,
    CronPreviewRequest,
    CronPreviewResponse,
    RegistryTaskResponse,
)
from modules.scheduler.schemas.task_log import TaskLogQueryParams, TaskLogResponse
from modules.scheduler.core.registry import get_registered_tasks, get_task_params_schema

scheduler_task_router = APIRouter(
    prefix="/scheduler-task",
    tags=["系统管理/定时任务"],
    dependencies=[Depends(current_user)],
)


@scheduler_task_router.get(
    "/list",
    response_model=ResponsePageModel[ScheduledTaskResponse],
    summary="获取定时任务列表",
    dependencies=[Depends(require_permission("sys:scheduler:list"))],
)
async def get_task_list(
    query_params: ScheduledTaskQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询定时任务列表"""
    query = SchedulerService.build_task_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=ScheduledTaskResponse,
    )
    return response_base.page(data=page_data)


@scheduler_task_router.get(
    "/{task_id}",
    response_model=ResponseModel[ScheduledTaskResponse],
    summary="获取定时任务详情",
    dependencies=[Depends(require_permission("sys:scheduler:detail"))],
)
async def get_task(
    task_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取定时任务详情"""
    task = await SchedulerService.get_task(db, task_id)
    return response_base.success(data=ScheduledTaskResponse.model_validate(task))


@scheduler_task_router.post(
    "/add",
    response_model=ResponseModel[ScheduledTaskResponse],
    summary="创建定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:add"))],
)
async def create_task(
    task_create: ScheduledTaskCreate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """创建定时任务"""
    task = await SchedulerService.create_task(db, task_create)
    await db.commit()
    await db.refresh(task)
    return response_base.success(data=ScheduledTaskResponse.model_validate(task), msg=t("common.create_success"))


@scheduler_task_router.put(
    "/{task_id}",
    response_model=ResponseModel[ScheduledTaskResponse],
    summary="更新定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:edit"))],
)
async def update_task(
    task_id: int,
    task_update: ScheduledTaskUpdate,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """更新定时任务"""
    task = await SchedulerService.update_task(db, task_id, task_update)
    await db.commit()
    await db.refresh(task)
    return response_base.success(data=ScheduledTaskResponse.model_validate(task), msg=t("common.update_success"))


@scheduler_task_router.delete(
    "/{task_id}",
    response_model=ResponseModel,
    summary="删除定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:delete"))],
)
async def delete_task(
    task_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除定时任务"""
    await SchedulerService.delete_task(db, task_id)
    await db.commit()
    return response_base.success(msg=t("common.delete_success"))


@scheduler_task_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量删除定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:delete"))],
)
async def batch_delete_tasks(
    task_ids: List[int],
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量删除定时任务"""
    count = 0
    for task_id in task_ids:
        try:
            await SchedulerService.delete_task(db, task_id)
            count += 1
        except Exception:
            pass
    await db.commit()
    return response_base.success(data={"deleted": count}, msg=t("common.delete_success"))


@scheduler_task_router.put(
    "/{task_id}/status",
    response_model=ResponseModel[ScheduledTaskResponse],
    summary="启用/禁用定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:status"))],
)
async def toggle_task_status(
    task_id: int,
    status: bool,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """启用/禁用定时任务"""
    task = await SchedulerService.toggle_status(db, task_id, status)
    await db.commit()
    await db.refresh(task)
    return response_base.success(data=ScheduledTaskResponse.model_validate(task), msg=t("common.status_update_success"))


@scheduler_task_router.post(
    "/{task_id}/trigger",
    response_model=ResponseModel,
    summary="手动触发定时任务",
    dependencies=[Depends(require_permission("sys:scheduler:trigger"))],
)
async def manual_trigger_task(
    task_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """手动触发定时任务"""
    await SchedulerService.manual_trigger(db, task_id)
    await db.commit()
    return response_base.success(msg=t("scheduler.task_triggered"))


@scheduler_task_router.post(
    "/cron-preview",
    response_model=ResponseModel[CronPreviewResponse],
    summary="预览 Cron 表达式",
    dependencies=[Depends(require_permission("sys:scheduler:list"))],
)
async def preview_cron(
    request: CronPreviewRequest,
    user: SysUser = Depends(current_user),
):
    """预览 Cron 表达式接下来 N 次执行时间"""
    times = SchedulerService.preview_cron(request.cron_expression)
    return response_base.success(data=CronPreviewResponse(next_run_times=times))


@scheduler_task_router.get(
    "/registry/list",
    response_model=ResponseModel[list[RegistryTaskResponse]],
    summary="获取装饰器注册的任务列表",
    dependencies=[Depends(require_permission("sys:scheduler:list"))],
)
async def get_registry_tasks(
    user: SysUser = Depends(current_user),
):
    """获取所有通过装饰器注册的任务"""
    registry = get_registered_tasks()
    tasks = [
        RegistryTaskResponse(
            task_key=defn.task_key,
            name=defn.name,
            description=defn.description,
            cron_expression=defn.cron_expression,
            trigger_type=defn.trigger_type,
            trigger_params=defn.trigger_params if defn.trigger_params else None,
            module=defn.module,
            function_path=defn.function_path,
            is_system=defn.is_system,
            timeout=defn.timeout,
            max_retries=defn.max_retries,
            concurrent_policy=defn.concurrent_policy,
            has_params=defn.params_schema is not None,
            task_category=defn.task_category,
        )
        for defn in registry.values()
    ]
    return response_base.success(data=tasks)


@scheduler_task_router.get(
    "/registry/{task_key}/schema",
    response_model=ResponseModel[dict | None],
    summary="获取任务参数 JSON Schema",
    dependencies=[Depends(require_permission("sys:scheduler:list"))],
)
async def get_registry_task_schema(
    task_key: str,
    user: SysUser = Depends(current_user),
):
    """获取指定任务的参数 JSON Schema，无参数任务返回 data=null"""
    schema = get_task_params_schema(task_key)
    return response_base.success(data=schema)


@scheduler_task_router.post(
    "/sync-registry",
    response_model=ResponseModel,
    summary="同步装饰器注册的任务到数据库",
    dependencies=[Depends(require_permission("sys:scheduler:add"))],
)
async def sync_registry(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """将装饰器注册的任务同步到数据库"""
    synced = await SchedulerService.sync_registry_to_db(db)
    await db.commit()
    return response_base.success(data={"synced": synced}, msg=t("scheduler.synced_count", count=len(synced)))
