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


@scheduled_task(
    cron="*/10 * * * *",
    name="知识库向量对账",
    description="复位处理超时文档；比对 PG 切片账目与 Qdrant 点数，偏差文档自动重跑（Qdrant 异常跳过本轮）",
    task_key="agent.knowledge_reconcile",
    is_system=True,
)
async def reconcile_agent_knowledge():
    """知识库向量对账（自愈）"""
    from database.db_manager import get_session
    from modules.agent.services.knowledge_service import KnowledgeService

    summary = {"reprocessed": 0}
    async for db in get_session():
        summary = await KnowledgeService.reconcile(db)
        break
    return summary
