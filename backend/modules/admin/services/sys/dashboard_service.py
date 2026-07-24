#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘聚合服务

聚合用户、角色、在线用户、登录日志、公告等数据，供首页仪表盘展示。
所有子查询独立 try-except，单个失败不影响其他字段返回（优雅降级）。
结果用 Redis 缓存 60 秒，减少高频首页访问对数据库的压力。
"""

import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import get_redis_util
from database.models.sys.user import SysUser
from database.models.sys.role import SysRole
from database.models.sys.login_log import SysLoginLog
from database.models.sys.notice import SysNotice
from database.utils.timezone import timezone
from modules.admin.services.sys.online_user_service import OnlineUserService
from modules.admin.schemas.sys.dashboard import (
    DashboardStats,
    DashboardRecentLogin,
    DashboardLatestNotice,
    DashboardSummary,
)

logger = logging.getLogger(__name__)

# Redis 缓存配置
_CACHE_KEY = "dashboard:summary"
_CACHE_TTL = 60  # 秒，首页高频访问，缓存 1 分钟

# 查询条数限制
_RECENT_LOGIN_LIMIT = 10
_LATEST_NOTICE_LIMIT = 5


class DashboardService:
    """首页仪表盘聚合服务"""

    @staticmethod
    async def get_summary(db: AsyncSession) -> DashboardSummary:
        """
        获取仪表盘汇总数据（带 60 秒 Redis 缓存）。

        :param db: 异步数据库会话
        :return: 仪表盘汇总数据
        """
        redis_util = get_redis_util()

        # 尝试读取缓存
        try:
            cached = await redis_util.get(_CACHE_KEY)
            if cached:
                return DashboardSummary.model_validate_json(cached)
        except Exception as exc:
            logger.warning("读取仪表盘缓存失败: %s", exc)

        # 缓存未命中，执行聚合查询
        stats = await DashboardService._get_stats(db)
        recent_logins = await DashboardService._get_recent_logins(db)
        latest_notices = await DashboardService._get_latest_notices(db)

        summary = DashboardSummary(
            stats=stats,
            recent_logins=recent_logins,
            latest_notices=latest_notices,
        )

        # 写入缓存
        try:
            await redis_util.set(_CACHE_KEY, summary.model_dump_json(), expire=_CACHE_TTL)
        except Exception as exc:
            logger.warning("写入仪表盘缓存失败: %s", exc)

        return summary

    @staticmethod
    async def _get_stats(db: AsyncSession) -> DashboardStats:
        """
        获取统计数据（4 个核心指标）。

        每个字段独立 try-except，单个查询失败时该字段返回 0，
        不影响其他字段返回（优雅降级）。

        :param db: 异步数据库会话
        :return: 统计数据
        """
        user_count = 0
        role_count = 0
        online_count = 0
        today_login_count = 0

        # 用户总数（排除软删除）
        try:
            result = await db.execute(
                select(func.count(SysUser.id)).where(SysUser.deleted_at.is_(None))
            )
            user_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询用户总数失败: %s", exc)

        # 角色总数（排除软删除）
        try:
            result = await db.execute(
                select(func.count(SysRole.id)).where(SysRole.deleted_at.is_(None))
            )
            role_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询角色总数失败: %s", exc)

        # 在线用户数（Redis 会话 key 计数，复用现有服务）
        try:
            online_count = await OnlineUserService.get_online_count(role="admin")
        except Exception as exc:
            logger.warning("仪表盘查询在线用户数失败: %s", exc)

        # 今日登录次数（Asia/Shanghai 当日 00:00 起算）
        try:
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            result = await db.execute(
                select(func.count(SysLoginLog.id)).where(
                    SysLoginLog.login_time >= today_start
                )
            )
            today_login_count = result.scalar() or 0
        except Exception as exc:
            logger.warning("仪表盘查询今日登录数失败: %s", exc)

        return DashboardStats(
            user_count=user_count,
            role_count=role_count,
            online_count=online_count,
            today_login_count=today_login_count,
        )

    @staticmethod
    async def _get_recent_logins(db: AsyncSession) -> list[DashboardRecentLogin]:
        """
        获取最近 10 条登录记录（按时间倒序）。

        :param db: 异步数据库会话
        :return: 最近登录记录列表，查询失败时返回空列表
        """
        try:
            result = await db.execute(
                select(SysLoginLog)
                .order_by(SysLoginLog.login_time.desc())
                .limit(_RECENT_LOGIN_LIMIT)
            )
            logs = result.scalars().all()
            return [
                DashboardRecentLogin(
                    username=log.username,
                    ip=log.ip or "",
                    status=log.status,
                    login_time=log.login_time,
                )
                for log in logs
            ]
        except Exception as exc:
            logger.warning("仪表盘查询最近登录失败: %s", exc)
            return []

    @staticmethod
    async def _get_latest_notices(db: AsyncSession) -> list[DashboardLatestNotice]:
        """
        获取最新 5 条已发布公告（按创建时间倒序）。

        :param db: 异步数据库会话
        :return: 最新公告列表，查询失败时返回空列表
        """
        try:
            result = await db.execute(
                select(SysNotice)
                .where(SysNotice.status.is_(True))
                .order_by(SysNotice.created_at.desc())
                .limit(_LATEST_NOTICE_LIMIT)
            )
            notices = result.scalars().all()
            return [
                DashboardLatestNotice(
                    id=str(notice.id),
                    title=notice.title,
                    type=notice.type,
                    created_at=notice.created_at,
                )
                for notice in notices
            ]
        except Exception as exc:
            logger.warning("仪表盘查询最新公告失败: %s", exc)
            return []
