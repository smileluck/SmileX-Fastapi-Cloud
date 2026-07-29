#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步导出任务管理接口
"""
import logging
import os

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.i18n import t
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from database.models.sys.user import SysUser
from modules.admin.services.sys.export_task_service import ExportTaskService
from modules.admin.schemas.sys.export_task import (
    ExportTaskSubmit,
    ExportTaskResponse,
)

logger = logging.getLogger(__name__)

export_router = APIRouter(prefix="/export", tags=["数据导出"])


@export_router.post(
    "/task",
    response_model=ResponseModel[ExportTaskResponse],
    summary="提交异步导出任务",
)
async def create_export_task(
    submit: ExportTaskSubmit,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    task = await ExportTaskService.submit_task(db, user.id, submit)
    return response_base.success(
        data=ExportTaskResponse.from_orm_with_format(task),
        msg=t("export_task.submitted"),
    )


@export_router.get(
    "/task/list",
    response_model=ResponseModel,
    summary="获取当前用户的导出任务列表",
)
async def get_export_task_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    status: str | None = Query(None, description="任务状态筛选"),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    tasks, total = await ExportTaskService.get_task_list(db, user.id, page, page_size, status)
    items = [ExportTaskResponse.from_orm_with_format(t) for t in tasks]
    total_pages = (total + page_size - 1) // page_size
    return response_base.success(
        data={
            "records": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    )


@export_router.get(
    "/task/{task_id}",
    response_model=ResponseModel[ExportTaskResponse],
    summary="查询导出任务状态",
)
async def get_export_task_status(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    task = await ExportTaskService.get_task(db, task_id)
    return response_base.success(
        data=ExportTaskResponse.from_orm_with_format(task),
    )


@export_router.get(
    "/task/{task_id}/download",
    summary="下载导出文件",
)
async def download_export_file(
    task_id: int,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    file_path = await ExportTaskService.download_file(db, task_id)
    filename = os.path.basename(file_path)
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename,
    )


@export_router.delete(
    "/task/cleanup",
    response_model=ResponseModel,
    summary="清理过期的导出任务和文件",
)
async def cleanup_export_tasks(
    days: int = Query(7, description="清理多少天前的已完成任务"),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    count = await ExportTaskService.cleanup_old_tasks(db, days)
    return response_base.success(
        data={"deleted": count},
        msg=t("export_task.cleaned_expired", count=count),
    )
