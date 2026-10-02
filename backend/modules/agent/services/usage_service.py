#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体 token 用量服务
"""
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from database.models.sys.agent import SysAgentUsageLog
from database.utils.timezone import timezone
from modules.agent.schemas.chat import UsageDailyPoint, UsageSummary

logger = logging.getLogger(__name__)

# 用量统计最大天数
MAX_USAGE_DAYS = 90


class UsageService:
    """智能体用量服务类"""

    @staticmethod
    async def append_usage(
        db: AsyncSession,
        agent_id: int,
        model_id: int,
        user_id: int,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: int,
    ) -> None:
        """落一条用量流水（上游未回 usage 时不调用）；写失败仅告警"""
        log = SysAgentUsageLog(
            agent_id=agent_id,
            model_id=model_id,
            user_id=user_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
        )
        db.add(log)
        await db.commit()

    @staticmethod
    async def get_usage_summary(db: AsyncSession, user_id: Optional[int], days: int = 7) -> UsageSummary:
        """
        用量统计：日聚合趋势 + 汇总。

        按本地时区（Asia/Shanghai）自然日聚合；user_id 非空时仅统计本人。
        """
        days = max(1, min(days, MAX_USAGE_DAYS))
        started = timezone.now() - timedelta(days=days - 1)
        started_local = started.astimezone().replace(hour=0, minute=0, second=0, microsecond=0)

        date_expr = func.to_char(
            func.timezone("Asia/Shanghai", SysAgentUsageLog.created_at), "YYYY-MM-DD"
        )
        query = (
            select(
                date_expr.label("date"),
                func.count().label("calls"),
                func.coalesce(func.sum(SysAgentUsageLog.prompt_tokens), 0).label("prompt_tokens"),
                func.coalesce(func.sum(SysAgentUsageLog.completion_tokens), 0).label("completion_tokens"),
                func.coalesce(func.sum(SysAgentUsageLog.total_tokens), 0).label("total_tokens"),
            )
            .where(SysAgentUsageLog.created_at >= started_local)
            .group_by(date_expr)
            .order_by(date_expr.asc())
        )
        if user_id is not None:
            query = query.where(SysAgentUsageLog.user_id == user_id)

        result = await db.execute(query)
        rows = {row.date: row for row in result.all()}

        # 补齐无数据日期，趋势连续
        trend: list[UsageDailyPoint] = []
        cursor = started_local.date()
        today = timezone.now().astimezone().date()
        while cursor <= today and len(trend) < days:
            key = cursor.isoformat()
            row = rows.get(key)
            trend.append(
                UsageDailyPoint(
                    date=key,
                    calls=row.calls if row else 0,
                    prompt_tokens=row.prompt_tokens if row else 0,
                    completion_tokens=row.completion_tokens if row else 0,
                    total_tokens=row.total_tokens if row else 0,
                )
            )
            cursor += timedelta(days=1)

        return UsageSummary(
            days=days,
            total_calls=sum(p.calls for p in trend),
            total_prompt_tokens=sum(p.prompt_tokens for p in trend),
            total_completion_tokens=sum(p.completion_tokens for p in trend),
            total_tokens=sum(p.total_tokens for p in trend),
            trend=trend,
        )

    @staticmethod
    async def cleanup_expired(db: AsyncSession) -> int:
        """按保留期清理用量流水；0=永久保留（无操作）"""
        retention_days = settings.AGENT.USAGE_RETENTION_DAYS
        if retention_days <= 0:
            return 0
        cutoff = datetime.now(dt_timezone.utc) - timedelta(days=retention_days)
        result = await db.execute(delete(SysAgentUsageLog).where(SysAgentUsageLog.created_at < cutoff))
        await db.commit()
        deleted = result.rowcount or 0
        if deleted:
            logger.info("清理过期智能体用量流水 %s 条（保留 %s 天）", deleted, retention_days)
        return deleted
