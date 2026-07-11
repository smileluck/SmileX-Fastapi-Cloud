#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步导出任务定时调度
通过 APScheduler 每分钟执行一次，处理 pending 任务并清理超时/过期任务
"""

from modules.scheduler.core.registry import scheduled_task
from modules.admin.services.sys.export_task_service import ExportTaskService


@scheduled_task(
    cron="* * * * *",
    name="执行异步导出任务",
    description="每分钟扫描并执行 pending 状态的异步导出任务",
    task_key="system.execute_export_tasks",
    is_system=True,
)
async def execute_export_tasks():
    """执行异步导出任务"""
    from database.db_manager import get_session

    async for db in get_session():
        processed = await ExportTaskService.process_pending_tasks(db)
        return {"processed": processed}


@scheduled_task(
    cron="* * * * *",
    name="清理超时导出任务",
    description="每分钟标记超时导出任务为失败并清理过期 completed/failed 任务",
    task_key="system.cleanup_export_tasks",
    is_system=True,
)
async def cleanup_export_tasks():
    """清理超时与过期导出任务"""
    from database.db_manager import get_session

    async for db in get_session():
        result = await ExportTaskService.timeout_and_cleanup_tasks(db)
        return result
