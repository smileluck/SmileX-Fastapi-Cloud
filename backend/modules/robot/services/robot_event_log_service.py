#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人事件日志管理服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime, timezone, timedelta

from database.models.business.robot_event_log import RobotEventLog
from core.exception.errors import NotFoundError
from modules.robot.schemas.robot_event_log import RobotEventLogQueryParams

logger = logging.getLogger(__name__)


class RobotEventLogService:
    """机器人事件日志管理服务类"""

    @staticmethod
    def build_event_log_query(query_params: RobotEventLogQueryParams):
        """构建机器人事件日志查询"""
        conditions = [RobotEventLog.deleted_at.is_(None)]

        if query_params.robot_id:
            conditions.append(RobotEventLog.robot_id == query_params.robot_id)
        if query_params.event_type:
            conditions.append(RobotEventLog.event_type == query_params.event_type)
        if query_params.event_status:
            conditions.append(RobotEventLog.event_status == query_params.event_status)
        if query_params.start_time:
            try:
                dt = datetime.fromisoformat(query_params.start_time)
                start = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(RobotEventLog.created_at >= start)
            except ValueError:
                pass
        if query_params.end_time:
            try:
                dt = datetime.fromisoformat(query_params.end_time)
                end = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
                conditions.append(RobotEventLog.created_at <= end)
            except ValueError:
                pass

        base_query = select(RobotEventLog)
        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(RobotEventLog.created_at.desc())
        return base_query

    @staticmethod
    async def get_log(db: AsyncSession, log_id: int) -> RobotEventLog:
        """获取单条机器人事件日志"""
        result = await db.execute(
            select(RobotEventLog).where(
                and_(RobotEventLog.id == log_id, RobotEventLog.deleted_at.is_(None))
            )
        )
        log = result.scalar_one_or_none()
        if not log:
            raise NotFoundError(msg=f"机器人事件日志 {log_id} 不存在")
        return log

    @staticmethod
    async def batch_delete_logs(db: AsyncSession, log_ids: List[int]) -> int:
        """批量软删除机器人事件日志"""
        result = await db.execute(
            select(RobotEventLog).where(
                and_(RobotEventLog.id.in_(log_ids), RobotEventLog.deleted_at.is_(None))
            )
        )
        logs = result.scalars().all()
        for log in logs:
            log.soft_delete()
        await db.commit()
        return len(logs)

    @staticmethod
    async def clear_logs(db: AsyncSession, days: int = 30) -> int:
        """清理指定天数前的机器人事件日志（软删除）"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        result = await db.execute(
            select(RobotEventLog).where(
                and_(RobotEventLog.created_at < cutoff, RobotEventLog.deleted_at.is_(None))
            )
        )
        logs = result.scalars().all()
        for log in logs:
            log.soft_delete()
        await db.commit()
        return len(logs)
