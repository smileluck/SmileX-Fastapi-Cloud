#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
在线用户监控服务
"""
import json
import logging
from datetime import datetime, timezone
from typing import List
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from core.redis import get_redis_util
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from core.security.oauth.user_manager import build_session_key
from database.models.sys.user import SysUser
from modules.common.schemas.page import ResponsePageDataModel
from modules.admin.schemas.sys.online_user import OnlineUserResponse

logger = logging.getLogger(__name__)

SESSION_PREFIX = settings.JWT.SESSION_PREFIX

_SHANGHAI = ZoneInfo("Asia/Shanghai")


def _format_login_time(raw: str | None) -> str:
    if not raw:
        return ""
    try:
        dt = datetime.fromisoformat(raw)
        return dt.astimezone(_SHANGHAI).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return raw


class OnlineUserService:
    """在线用户监控服务"""

    @staticmethod
    async def _collect_online_sessions(role: str = "admin", tenant_id: int | None = None) -> list[dict]:
        """从 Redis 收集所有在线会话信息，支持按 tenant_id 过滤。

        Key 格式：
        - admin: JWT_SESSION:ADMIN:{tenant_id}:{user_id}
        - app:   JWT_SESSION:APP:{user_id}
        """
        redis_util = get_redis_util()
        sessions = []
        role_upper = role.upper()

        # 构建 scan pattern
        if role == "admin" and tenant_id is not None:
            # 精确扫描指定租户
            pattern = f"{SESSION_PREFIX}ADMIN:{tenant_id}:*"
        else:
            # 扫描该 role 下所有 key
            pattern = f"{SESSION_PREFIX}{role_upper}:*"

        async for key in redis_util.scan_iter(match=pattern):
            # 从 key 中提取 user_id（取最后一个冒号后的部分）
            user_id_str = key.rsplit(":", maxsplit=1)[-1]
            try:
                user_id = int(user_id_str)
            except ValueError:
                continue

            all_fields = await redis_util.hgetall(key)
            if not all_fields:
                continue

            for sid, meta_raw in all_fields.items():
                if isinstance(sid, bytes):
                    sid = sid.decode("utf-8")
                if isinstance(meta_raw, bytes):
                    meta_raw = meta_raw.decode("utf-8")
                try:
                    meta = json.loads(meta_raw)
                except (json.JSONDecodeError, TypeError):
                    meta = {"session_id": sid}

                sessions.append({
                    "user_id": user_id,
                    "session_id": sid,
                    "ip": meta.get("ip", ""),
                    "user_agent": meta.get("user_agent", ""),
                    "login_time": _format_login_time(meta.get("login_time")),
                })
        return sessions

    @staticmethod
    async def get_online_user_page(
        db: AsyncSession,
        role: str = "admin",
        username: str | None = None,
        ip: str | None = None,
        page: int = 1,
        page_size: int = 10,
        tenant_id: int | None = None,
    ) -> ResponsePageDataModel:
        """获取在线用户分页列表，支持按租户过滤"""
        sessions = await OnlineUserService._collect_online_sessions(role, tenant_id=tenant_id)

        # 按 user_id 批量查询用户信息
        user_ids = list({s["user_id"] for s in sessions})
        user_map = {}
        if user_ids:
            stmt = select(SysUser).where(SysUser.id.in_(user_ids))
            result = await db.execute(stmt)
            for user in result.scalars().all():
                user_map[user.id] = user

        # 组装响应数据并过滤
        records = []
        for s in sessions:
            user = user_map.get(s["user_id"])
            if not user:
                continue
            if username and username not in (user.username or ""):
                continue
            if ip and ip not in (s.get("ip") or ""):
                continue
            records.append(OnlineUserResponse(
                user_id=user.id,
                username=user.username,
                nickname=user.nickname,
                avatar=user.avatar,
                session_id=s["session_id"],
                ip=s.get("ip", ""),
                user_agent=s.get("user_agent", ""),
                login_time=s.get("login_time", ""),
            ))

        # 按 login_time 降序
        records.sort(key=lambda r: r.login_time or "", reverse=True)

        # 手动分页
        total = len(records)
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        start = (page - 1) * page_size
        page_records = records[start:start + page_size]

        return ResponsePageDataModel(
            records=page_records,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )

    @staticmethod
    async def kick_user(user_id: int, session_id: str, role: str = "admin", tenant_id: int = 0) -> bool:
        """踢除指定会话"""
        redis_key = build_session_key(role, user_id, tenant_id=tenant_id)
        result = await get_redis_util().hdel(redis_key, session_id)
        get_memory_cache().delete(CacheNamespace.SESSION, f"{redis_key}:{session_id}")
        return result > 0

    @staticmethod
    async def kick_all_sessions(user_id: int, role: str = "admin", tenant_id: int = 0) -> int:
        """踢除用户所有会话"""
        redis_key = build_session_key(role, user_id, tenant_id=tenant_id)
        all_fields = await get_redis_util().hgetall(redis_key)
        count = len(all_fields) if all_fields else 0
        await get_redis_util().delete(redis_key)
        get_memory_cache().delete_by_prefix(CacheNamespace.SESSION, f"{redis_key}:")
        return count

    @staticmethod
    async def kick_all_online_users(role: str = "admin") -> int:
        """踢除所有在线用户的所有会话"""
        redis_util = get_redis_util()
        role_upper = role.upper()
        pattern = f"{SESSION_PREFIX}{role_upper}:*"
        count = 0
        async for key in redis_util.scan_iter(match=pattern):
            all_fields = await redis_util.hgetall(key)
            count += len(all_fields) if all_fields else 0
            await redis_util.delete(key)
            get_memory_cache().delete_by_prefix(CacheNamespace.SESSION, f"{key}:")
        return count

    @staticmethod
    async def get_online_count(role: str = "admin") -> int:
        """获取在线用户数（按独立用户计数）"""
        redis_util = get_redis_util()
        role_upper = role.upper()
        pattern = f"{SESSION_PREFIX}{role_upper}:*"
        user_ids = set()
        async for key in redis_util.scan_iter(match=pattern):
            user_id_str = key.rsplit(":", maxsplit=1)[-1]
            try:
                user_ids.add(int(user_id_str))
            except ValueError:
                continue
        return len(user_ids)
