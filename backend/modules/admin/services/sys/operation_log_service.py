#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
操作日志管理服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List
from datetime import datetime, timezone

from database.models.sys.operation_log import SysOperationLog
from core.exception.errors import NotFoundError
from modules.admin.schemas.sys.operation_log import OperationLogQueryParams

logger = logging.getLogger(__name__)


class OperationLogService:
    """操作日志管理服务类"""

    @staticmethod
    def build_operation_log_query(query_params: OperationLogQueryParams):
        """构建操作日志查询（供导出和列表共用）"""
        conditions = []

        if query_params.module:
            conditions.append(SysOperationLog.module == query_params.module)
        if query_params.action:
            conditions.append(SysOperationLog.action == query_params.action)
        if query_params.user_id:
            conditions.append(SysOperationLog.user_id == query_params.user_id)
        if query_params.username:
            conditions.append(
                SysOperationLog.username.like(f"%{query_params.username}%")
            )
        if query_params.start_time:
            try:
                dt = datetime.fromisoformat(query_params.start_time)
                start = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysOperationLog.created_at >= start)
            except ValueError:
                pass
        if query_params.end_time:
            try:
                dt = datetime.fromisoformat(query_params.end_time)
                end = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysOperationLog.created_at <= end)
            except ValueError:
                pass

        base_query = select(SysOperationLog)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.where(SysOperationLog.deleted_at.is_(None))
        base_query = base_query.order_by(SysOperationLog.created_at.desc())
        return base_query

    @staticmethod
    async def get_log(db: AsyncSession, log_id: int) -> SysOperationLog:
        """获取单条操作日志"""
        result = await db.execute(
            select(SysOperationLog).where(SysOperationLog.id == log_id)
        )
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError(msg=f"操作日志 {log_id} 不存在")
        return log

    @staticmethod
    async def batch_delete_logs(
        db: AsyncSession, log_ids: List[int]
    ) -> int:
        """批量删除操作日志"""
        stmt = delete(SysOperationLog).where(SysOperationLog.id.in_(log_ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    @staticmethod
    async def clear_logs(db: AsyncSession, days: int = 30) -> int:
        """清理指定天数前的操作日志"""
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(SysOperationLog).where(SysOperationLog.created_at < cutoff)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
