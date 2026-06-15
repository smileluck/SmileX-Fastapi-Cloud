#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务执行服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, Select
from sqlalchemy.orm import noload, selectinload
from typing import List

from database.models.business.task import Task
from database.models.business.task_execution import TaskExecution
from database.models.business.task_point import TaskPoint
from database.models.business.robot import Robot
from database.utils.timezone import timezone
from core.exception.errors import NotFoundError, ConflictError
from modules.task.schemas.task import TaskExecutionQueryParams

logger = logging.getLogger(__name__)


class TaskExecutionService:
    """任务执行服务类"""

    @staticmethod
    async def start_execution(
        db: AsyncSession, task_id: int, robot_ids: List[int], triggered_by: str = "manual"
    ) -> TaskExecution:
        """启动任务执行"""
        try:
            # 获取任务
            result = await db.execute(
                select(Task)
                .options(selectinload(Task.points))
                .where(Task.id == task_id)
                .where(Task.deleted_at.is_(None))
            )
            task_obj = result.unique().scalar_one_or_none()
            if not task_obj:
                raise NotFoundError(msg=f"任务 {task_id} 不存在")

            if task_obj.status == "running":
                raise ConflictError(msg="任务正在执行中，不能重复启动")

            # 更新任务状态
            task_obj.status = "running"

            # 创建执行记录（取第一个机器人作为主执行者）
            robot_id = robot_ids[0] if robot_ids else None
            exec_obj = TaskExecution(
                task_id=task_id,
                task_name=task_obj.name,
                task_type=task_obj.task_type,
                status="running",
                progress=0,
                started_at=timezone.now(),
                robot_id=robot_id,
                triggered_by=triggered_by,
            )
            db.add(exec_obj)

            await db.commit()
            await db.refresh(exec_obj)
            return exec_obj

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("启动任务执行失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def _get_execution(db: AsyncSession, exec_id: int) -> TaskExecution:
        """获取执行记录"""
        result = await db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == exec_id)
            .where(TaskExecution.deleted_at.is_(None))
        )
        exec_obj = result.scalar_one_or_none()
        if not exec_obj:
            raise NotFoundError(msg=f"执行记录 {exec_id} 不存在")
        return exec_obj

    @staticmethod
    async def pause_execution(db: AsyncSession, exec_id: int) -> TaskExecution:
        """暂停执行"""
        try:
            exec_obj = await TaskExecutionService._get_execution(db, exec_id)
            if exec_obj.status != "running":
                raise ConflictError(msg="只有运行中的任务才能暂停")

            exec_obj.status = "paused"

            # 同步更新任务状态
            result = await db.execute(
                select(Task).where(Task.id == exec_obj.task_id)
            )
            task_obj = result.scalar_one_or_none()
            if task_obj:
                task_obj.status = "paused"

            await db.commit()
            await db.refresh(exec_obj)
            return exec_obj

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("暂停任务执行失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def resume_execution(db: AsyncSession, exec_id: int) -> TaskExecution:
        """恢复执行"""
        try:
            exec_obj = await TaskExecutionService._get_execution(db, exec_id)
            if exec_obj.status != "paused":
                raise ConflictError(msg="只有已暂停的任务才能恢复")

            exec_obj.status = "running"

            # 同步更新任务状态
            result = await db.execute(
                select(Task).where(Task.id == exec_obj.task_id)
            )
            task_obj = result.scalar_one_or_none()
            if task_obj:
                task_obj.status = "running"

            await db.commit()
            await db.refresh(exec_obj)
            return exec_obj

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("恢复任务执行失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def stop_execution(db: AsyncSession, exec_id: int) -> TaskExecution:
        """停止执行"""
        try:
            exec_obj = await TaskExecutionService._get_execution(db, exec_id)
            if exec_obj.status not in ("running", "paused"):
                raise ConflictError(msg="只有运行中或已暂停的任务才能停止")

            exec_obj.status = "cancelled"
            exec_obj.ended_at = timezone.now()

            # 重置任务状态
            result = await db.execute(
                select(Task).where(Task.id == exec_obj.task_id)
            )
            task_obj = result.scalar_one_or_none()
            if task_obj:
                task_obj.status = "idle"

            await db.commit()
            await db.refresh(exec_obj)
            return exec_obj

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("停止任务执行失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    def build_active_query() -> Select:
        """构建活跃执行查询"""
        return (
            select(TaskExecution)
            .where(
                TaskExecution.status.in_(["running", "paused"]),
                TaskExecution.deleted_at.is_(None),
            )
            .order_by(TaskExecution.id.desc())
        )

    @staticmethod
    def build_history_query(query_params: TaskExecutionQueryParams) -> Select:
        """构建历史执行查询"""
        base_query = select(TaskExecution).where(
            TaskExecution.status.in_(["completed", "failed", "cancelled"]),
            TaskExecution.deleted_at.is_(None),
        )

        conditions = []
        if query_params.task_name:
            conditions.append(TaskExecution.task_name.contains(query_params.task_name))
        if query_params.status:
            conditions.append(TaskExecution.status == query_params.status)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(TaskExecution.id.desc())
        return base_query

    @staticmethod
    async def get_execution_detail(db: AsyncSession, exec_id: int) -> TaskExecution:
        """获取执行详情（含点位）"""
        result = await db.execute(
            select(TaskExecution)
            .where(TaskExecution.id == exec_id)
            .where(TaskExecution.deleted_at.is_(None))
        )
        exec_obj = result.scalar_one_or_none()
        if not exec_obj:
            raise NotFoundError(msg=f"执行记录 {exec_id} 不存在")

        # 获取关联任务的点位
        task_result = await db.execute(
            select(Task)
            .options(selectinload(Task.points))
            .where(Task.id == exec_obj.task_id)
        )
        task_obj = task_result.unique().scalar_one_or_none()

        # 将点位附加到执行记录（用于响应构建）
        if task_obj:
            exec_obj._task_points = task_obj.points
        else:
            exec_obj._task_points = []

        return exec_obj
