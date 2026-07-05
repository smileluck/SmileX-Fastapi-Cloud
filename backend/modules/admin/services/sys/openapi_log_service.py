#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API调用日志服务
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import and_, delete, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import NotFoundError
from database.models.sys.openapi_log import SysOpenapiLog
from modules.admin.schemas.sys.openapi_log import OpenapiLogQueryParams

logger = logging.getLogger(__name__)


class OpenapiLogService:
    """开放API调用日志服务"""

    @staticmethod
    def build_openapi_log_query(query_params: OpenapiLogQueryParams) -> Select:
        """构建开放API调用日志查询（列表与导出共用）"""
        conditions = []

        if query_params.app_id:
            conditions.append(SysOpenapiLog.app_id.like(f"%{query_params.app_id}%"))
        if query_params.path:
            conditions.append(SysOpenapiLog.path.like(f"%{query_params.path}%"))
        if query_params.method:
            conditions.append(SysOpenapiLog.method == query_params.method.upper())
        if query_params.status_code is not None:
            conditions.append(SysOpenapiLog.status_code == query_params.status_code)
        if query_params.err_code is not None:
            conditions.append(SysOpenapiLog.err_code == query_params.err_code)
        if query_params.client_ip:
            conditions.append(SysOpenapiLog.client_ip.like(f"%{query_params.client_ip}%"))
        if query_params.request_id:
            conditions.append(SysOpenapiLog.request_id == query_params.request_id)
        if query_params.start_time:
            try:
                dt = datetime.fromisoformat(query_params.start_time)
                start = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysOpenapiLog.created_at >= start)
            except ValueError:
                pass
        if query_params.end_time:
            try:
                dt = datetime.fromisoformat(query_params.end_time)
                end = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysOpenapiLog.created_at <= end)
            except ValueError:
                pass

        base_query = select(SysOpenapiLog)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.order_by(SysOpenapiLog.created_at.desc())

    @staticmethod
    async def get_log(db: AsyncSession, log_id: int) -> SysOpenapiLog:
        """获取单条开放API调用日志"""
        result = await db.execute(select(SysOpenapiLog).where(SysOpenapiLog.id == log_id))
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError(msg=f"开放API调用日志 {log_id} 不存在")
        return log

    @staticmethod
    async def batch_delete_logs(db: AsyncSession, log_ids: List[int]) -> int:
        """批量删除开放API调用日志"""
        stmt = delete(SysOpenapiLog).where(SysOpenapiLog.id.in_(log_ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    @staticmethod
    async def clear_logs(db: AsyncSession, days: int = 30) -> int:
        """清理指定天数前的开放API调用日志"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = delete(SysOpenapiLog).where(SysOpenapiLog.created_at < cutoff)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
