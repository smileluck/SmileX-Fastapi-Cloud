#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import NotFoundError, ConflictError, ValidationError
from database.models.sys.scheduled_task import SysScheduledTask
from modules.scheduler.schemas.scheduled_task import (
    ScheduledTaskCreate,
    ScheduledTaskUpdate,
    ScheduledTaskQueryParams,
)
from modules.scheduler.core.registry import get_registered_tasks, get_task_definition, get_task_definition_by_path
from modules.scheduler.core.scheduler import SchedulerManager


def _resolve_definition(task_key: str, function_path: str | None):
    """优先按 task_key 查注册表（专用任务/已实例化的通用任务），否则按 function_path 查"""
    definition = get_task_definition(task_key)
    if definition is not None:
        return definition
    if function_path:
        return get_task_definition_by_path(function_path)
    return None


def _validate_task_params(task_key: str, function_path: str | None, params: dict | None) -> dict | None:
    """根据注册表的 params_schema 校验参数，返回 JSON-safe dict 或 None"""
    definition = _resolve_definition(task_key, function_path)
    if definition is None:
        raise ValidationError(msg=f"任务 '{task_key}' 未在注册表中找到，无法创建")
    if definition.params_schema is None:
        if params:
            raise ValidationError(msg=f"任务 '{task_key}' 不接受参数")
        return None
    try:
        validated = definition.params_schema.model_validate(params or {})
    except Exception as exc:
        raise ValidationError(msg=f"任务参数校验失败: {exc}")
    return validated.model_dump(mode="json")


class SchedulerService:
    """定时任务管理服务"""

    @staticmethod
    def build_task_query(query_params: ScheduledTaskQueryParams):
        """构建定时任务查询"""
        conditions = []
        if query_params.name:
            conditions.append(SysScheduledTask.name.like(f"%{query_params.name}%"))
        if query_params.task_key:
            conditions.append(SysScheduledTask.task_key.like(f"%{query_params.task_key}%"))
        if query_params.status is not None:
            conditions.append(SysScheduledTask.status == query_params.status)
        if query_params.trigger_type:
            conditions.append(SysScheduledTask.trigger_type == query_params.trigger_type)

        stmt = select(SysScheduledTask).where(SysScheduledTask.deleted_at.is_(None))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(SysScheduledTask.created_at.desc())
        return stmt

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> SysScheduledTask:
        """获取单个任务"""
        stmt = select(SysScheduledTask).where(
            SysScheduledTask.id == task_id,
            SysScheduledTask.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError(msg=f"定时任务 {task_id} 不存在")
        return task

    @staticmethod
    async def get_task_by_key(db: AsyncSession, task_key: str) -> SysScheduledTask | None:
        """按 task_key 获取任务"""
        stmt = select(SysScheduledTask).where(
            SysScheduledTask.task_key == task_key,
            SysScheduledTask.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_task(db: AsyncSession, task_create: ScheduledTaskCreate) -> SysScheduledTask:
        """创建定时任务"""
        existing = await SchedulerService.get_task_by_key(db, task_create.task_key)
        if existing:
            raise ConflictError(msg=f"任务标识 '{task_create.task_key}' 已存在")

        definition = _resolve_definition(task_create.task_key, task_create.function_path)
        if definition is None:
            raise ValidationError(msg=f"任务 '{task_create.task_key}' 未在注册表中找到，无法创建")

        params_json = _validate_task_params(task_create.task_key, task_create.function_path, task_create.params)

        task = SysScheduledTask(
            name=task_create.name,
            task_key=task_create.task_key,
            description=task_create.description,
            cron_expression=task_create.cron_expression,
            trigger_type=task_create.trigger_type,
            trigger_params=task_create.trigger_params,
            status=True,
            module=definition.module,
            function_path=definition.function_path,
            timeout=task_create.timeout,
            max_retries=task_create.max_retries,
            concurrent_policy=task_create.concurrent_policy,
            params=params_json,
        )
        db.add(task)
        await db.flush()

        await SchedulerService._sync_job(task, db)
        return task

    @staticmethod
    async def update_task(
        db: AsyncSession, task_id: int, task_update: ScheduledTaskUpdate
    ) -> SysScheduledTask:
        """更新定时任务"""
        task = await SchedulerService.get_task(db, task_id)

        update_data = task_update.model_dump(exclude_unset=True)
        if "params" in update_data:
            update_data["params"] = _validate_task_params(task.task_key, task.function_path, update_data["params"])
        for field, value in update_data.items():
            setattr(task, field, value)

        await db.flush()
        await SchedulerService._sync_job(task, db)
        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> None:
        """删除定时任务"""
        task = await SchedulerService.get_task(db, task_id)
        if task.is_system:
            raise ConflictError(msg="系统任务不可删除")

        from database.utils.timezone import timezone

        task.deleted_at = timezone.now()
        await db.flush()

        manager = SchedulerManager.get_instance()
        manager.remove_task_job(task_id)

    @staticmethod
    async def toggle_status(db: AsyncSession, task_id: int, status: bool) -> SysScheduledTask:
        """启用/禁用任务"""
        task = await SchedulerService.get_task(db, task_id)
        task.status = status
        await db.flush()

        await SchedulerService._sync_job(task, db)
        return task

    @staticmethod
    async def manual_trigger(db: AsyncSession, task_id: int):
        """手动触发任务"""
        task = await SchedulerService.get_task(db, task_id)
        manager = SchedulerManager.get_instance()
        await manager.run_task_now(task, db, triggered_by="manual")
        return task

    @staticmethod
    def preview_cron(cron_expression: str, count: int = 5) -> list[str]:
        """预览 cron 表达式"""
        return SchedulerManager.preview_cron(cron_expression, count)

    @staticmethod
    async def sync_registry_to_db(db: AsyncSession) -> list[str]:
        """将装饰器注册的任务同步到数据库（通用任务模板不同步——它们由用户实例化）"""
        registry = get_registered_tasks()
        synced = []

        for task_key, definition in registry.items():
            if definition.task_category == "generic":
                continue
            existing = await SchedulerService.get_task_by_key(db, task_key)
            if existing:
                existing.name = definition.name
                existing.description = definition.description
                existing.cron_expression = definition.cron_expression
                existing.trigger_type = definition.trigger_type
                existing.module = definition.module
                existing.function_path = definition.function_path
                existing.timeout = definition.timeout
                existing.max_retries = definition.max_retries
                existing.concurrent_policy = definition.concurrent_policy
                existing.is_system = definition.is_system
                if definition.trigger_params:
                    import json
                    existing.trigger_params = json.dumps(definition.trigger_params)
                synced.append(task_key)
            else:
                import json

                task = SysScheduledTask(
                    name=definition.name,
                    task_key=definition.task_key,
                    description=definition.description,
                    cron_expression=definition.cron_expression,
                    trigger_type=definition.trigger_type,
                    trigger_params=json.dumps(definition.trigger_params) if definition.trigger_params else None,
                    status=True,
                    module=definition.module,
                    function_path=definition.function_path,
                    is_system=definition.is_system,
                    timeout=definition.timeout,
                    max_retries=definition.max_retries,
                    concurrent_policy=definition.concurrent_policy,
                )
                db.add(task)
                synced.append(task_key)

        await db.flush()
        return synced

    @staticmethod
    async def _sync_job(task: SysScheduledTask, db: AsyncSession):
        """同步单个任务到调度器"""
        manager = SchedulerManager.get_instance()
        if manager.running:
            await manager.add_task_job(task)
            await db.flush()
        else:
            # 调度器未运行时，用 trigger 计算下次执行时间
            if not task.status:
                task.next_run_at = None
            elif task.trigger_type == "cron" and task.cron_expression:
                next_str = manager.preview_cron(task.cron_expression, count=1)
                if next_str:
                    from datetime import datetime
                    task.next_run_at = datetime.fromisoformat(next_str[0])
                else:
                    task.next_run_at = None
            else:
                task.next_run_at = None
            await db.flush()
