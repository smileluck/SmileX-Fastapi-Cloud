#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
登录日志管理服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, timezone, timedelta

from database.models.sys.login_log import SysLoginLog
from core.exception.errors import NotFoundError
from core.i18n import t
from modules.admin.schemas.sys.login_log import LoginLogQueryParams

logger = logging.getLogger(__name__)


class LoginLogService:
    """登录日志管理服务类"""

    @staticmethod
    async def create_log(
        db: AsyncSession,
        username: str,
        ip: str | None,
        status: bool,
        detail: str | None,
        user_agent: str | None,
    ) -> SysLoginLog:
        """创建登录日志"""
        log = SysLoginLog(
            username=username,
            ip=ip,
            status=status,
            detail=detail,
            user_agent=user_agent,
        )
        db.add(log)
        await db.commit()
        return log

    @staticmethod
    def build_login_log_query(query_params: LoginLogQueryParams):
        """构建登录日志查询"""
        conditions = []

        if query_params.username:
            conditions.append(SysLoginLog.username.like(f"%{query_params.username}%"))
        if query_params.ip:
            conditions.append(SysLoginLog.ip.like(f"%{query_params.ip}%"))
        if query_params.status is not None:
            conditions.append(SysLoginLog.status == query_params.status)
        if query_params.start_time:
            try:
                dt = datetime.fromisoformat(query_params.start_time)
                start = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysLoginLog.login_time >= start)
            except ValueError:
                pass
        if query_params.end_time:
            try:
                dt = datetime.fromisoformat(query_params.end_time)
                end = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(SysLoginLog.login_time <= end)
            except ValueError:
                pass

        conditions.append(SysLoginLog.deleted_at.is_(None))

        base_query = select(SysLoginLog)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(SysLoginLog.login_time.desc())
        return base_query

    @staticmethod
    async def get_log(db: AsyncSession, log_id: int) -> SysLoginLog:
        """获取单条登录日志"""
        result = await db.execute(
            select(SysLoginLog).where(SysLoginLog.id == log_id)
        )
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError(msg=t("login_log.not_found", id=log_id))
        return log

    @staticmethod
    async def batch_delete_logs(db: AsyncSession, log_ids: List[int]) -> int:
        """批量软删除登录日志"""
        result = await db.execute(
            select(SysLoginLog).where(SysLoginLog.id.in_(log_ids))
        )
        logs = result.scalars().all()
        for log in logs:
            log.soft_delete()
        await db.commit()
        return len(logs)

    @staticmethod
    async def clear_logs(db: AsyncSession, days: int = 30) -> int:
        """清理指定天数前的登录日志（软删除）"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            select(SysLoginLog).where(SysLoginLog.login_time < cutoff)
        )
        logs = result.scalars().all()
        for log in logs:
            log.soft_delete()
        await db.commit()
        return len(logs)
