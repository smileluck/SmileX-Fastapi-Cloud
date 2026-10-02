#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 智能体模块定时任务
"""

from modules.scheduler.core.registry import scheduled_task


@scheduled_task(
    cron="20 4 * * *",
    name="清理过期智能体用量流水",
    description="按保留期（AGENT.USAGE_RETENTION_DAYS，0=永久）清理智能体 token 用量流水",
    task_key="agent.cleanup_usage",
    is_system=True,
)
async def cleanup_agent_usage():
    """清理过期智能体用量流水"""
    from database.db_manager import get_session
    from modules.agent.services.usage_service import UsageService

    total = 0
    async for db in get_session():
        total = await UsageService.cleanup_expired(db)
        break
    return {"deleted": total}
