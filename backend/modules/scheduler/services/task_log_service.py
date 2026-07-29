#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone as tz

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import NotFoundError
from core.i18n import t
from database.models.sys.task_log import SysScheduledTaskLog
from modules.scheduler.schemas.task_log import TaskLogQueryParams


class TaskLogService:
    """任务执行日志服务"""

    @staticmethod
    def build_log_query(query_params: TaskLogQueryParams):
        """构建日志查询"""
        conditions = []
        if query_params.task_name:
            conditions.append(SysScheduledTaskLog.task_name.like(f"%{query_params.task_name}%"))
        if query_params.task_id:
            conditions.append(SysScheduledTaskLog.task_id == query_params.task_id)
        if query_params.task_key:
            conditions.append(SysScheduledTaskLog.task_key.like(f"%{query_params.task_key}%"))
        if query_params.status:
            conditions.append(SysScheduledTaskLog.status == query_params.status)
        if query_params.start_time:
            try:
                dt = datetime.fromisoformat(query_params.start_time)
                start = dt.astimezone(tz.utc) if dt.tzinfo else dt.replace(tzinfo=tz.utc)
                conditions.append(SysScheduledTaskLog.start_time >= start)
            except ValueError:
                pass
        if query_params.end_time:
            try:
                dt = datetime.fromisoformat(query_params.end_time)
                end = dt.astimezone(tz.utc) if dt.tzinfo else dt.replace(tzinfo=tz.utc)
                conditions.append(SysScheduledTaskLog.start_time <= end)
            except ValueError:
                pass

        stmt = select(SysScheduledTaskLog).where(SysScheduledTaskLog.deleted_at.is_(None))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(SysScheduledTaskLog.created_at.desc())
        return stmt

    @staticmethod
    async def get_log(db: AsyncSession, log_id: int) -> SysScheduledTaskLog:
        """获取单条日志"""
        stmt = select(SysScheduledTaskLog).where(
            SysScheduledTaskLog.id == log_id,
            SysScheduledTaskLog.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError(msg=t("scheduler.log_not_found", id=log_id))
        return log

    @staticmethod
    async def batch_delete_logs(db: AsyncSession, log_ids: list[int]) -> int:
        """批量删除日志"""
        stmt = delete(SysScheduledTaskLog).where(SysScheduledTaskLog.id.in_(log_ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    @staticmethod
    async def clear_logs(db: AsyncSession, days: int = 30) -> int:
        """清理指定天数前的日志"""
        cutoff = datetime.now(tz.utc) - timedelta(days=days)
        stmt = delete(SysScheduledTaskLog).where(SysScheduledTaskLog.created_at < cutoff)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
