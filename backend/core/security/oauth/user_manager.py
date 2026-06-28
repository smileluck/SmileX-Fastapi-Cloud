#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from core.config import settings
from core.redis import get_redis_util
from core.security.oauth.jwt import JWTAuthManager
from core.utils.session_utils import generate_session_id
from datetime import datetime, timezone
from typing import Optional

import logging

logger = logging.getLogger(__name__)


def build_session_key(role: str, user_id: int, tenant_id: int = 0) -> str:
    """构建 Redis session key。

    - admin: JWT_SESSION:ADMIN:{tenant_id}:{user_id}
    - app:   JWT_SESSION:APP:{user_id}
    """
    prefix = settings.JWT.SESSION_PREFIX
    if role == "admin":
        return f"{prefix}ADMIN:{tenant_id}:{user_id}"
    return f"{prefix}{role.upper()}:{user_id}"


def build_session_key_legacy(role: str, user_id: int) -> str:
    """构建旧格式 Redis session key（兼容过渡期）"""
    return settings.JWT.SESSION_PREFIX + role + str(user_id)


class BaseUserManager:
    """
    基础用户管理器类
    包含所有服务共享的用户管理功能
    """

    jwt_manager: JWTAuthManager

    def __init__(self):
        self.jwt_manager = JWTAuthManager()

    @staticmethod
    async def _evict_duplicate_sessions(redis_key: str, ip: str, user_agent: str) -> None:
        """删除同 user_id+tenant_id 下 IP 和 UA 完全相同的旧 session。

        防止同一浏览器反复登录堆积大量 session，污染在线用户列表。

        - 仅当 ip 和 user_agent 都非空时才执行，避免误伤未传 IP/UA 的调用方
          （如 app 端登录默认传空字符串，那种情况下保持原有"允许多 session"语义）
        - 跨 tenant_id 的 redis_key 不受影响（每个 tenant_id 一个独立 key）
        """
        if not ip or not user_agent:
            return
        redis_util = get_redis_util()
        all_fields = await redis_util.hgetall(redis_key)
        if not all_fields:
            return
        stale_sids: list[str] = []
        for sid, meta_raw in all_fields.items():
            if isinstance(sid, bytes):
                sid = sid.decode("utf-8")
            if isinstance(meta_raw, bytes):
                meta_raw = meta_raw.decode("utf-8")
            try:
                meta = json.loads(meta_raw)
            except (json.JSONDecodeError, TypeError):
                continue
            if meta.get("ip") == ip and meta.get("user_agent") == user_agent:
                stale_sids.append(sid)
        if stale_sids:
            await redis_util.hdel(redis_key, *stale_sids)

    async def create_token(
        self,
        user_id: int,
        user_role: str = "app",
        session_id: str = None,
        username: str = None,
        ip: str = "",
        user_agent: str = "",
        tenant_id: int = 0,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        access_lifetime: Optional[int] = None,
    ):
        """
        创建token，使用 Redis Hash 存储会话元数据以支持多会话追踪
        """
        new_session = False
        if session_id is None:
            session_id = generate_session_id(user_id)
            new_session = True
        token_data = {"id": user_id, "session_id": session_id, "role": user_role, "username": username}
        extra_claims = {}
        if tenant_id:
            extra_claims["tenant_id"] = str(tenant_id)

        if new_session:
            redis_key = build_session_key(user_role, user_id, tenant_id=tenant_id)

            # 清理旧格式 key（兼容过渡）
            legacy_key = build_session_key_legacy(user_role, user_id)
            await get_redis_util().delete(legacy_key)

            # 清理同用户其他 tenant_id 的旧 key（仅 admin）
            if user_role == "admin" and tenant_id != 0:
                old_key = build_session_key(user_role, user_id, tenant_id=0)
                if old_key != redis_key:
                    await get_redis_util().delete(old_key)

            # 清理同 IP+UA 的旧 session，防止同浏览器反复登录堆积
            await self._evict_duplicate_sessions(redis_key, ip, user_agent)

            session_meta = json.dumps({
                "session_id": session_id,
                "login_time": datetime.now(timezone.utc).isoformat(),
                "ip": ip,
                "user_agent": user_agent,
            })
            await get_redis_util().hset(redis_key, session_id, session_meta)
            await get_redis_util().expire(redis_key, settings.JWT.REFRESH_LIFETIME)

        tokens = JWTAuthManager.create_tokens(
            token_data,
            extra_claims=extra_claims if extra_claims else None,
            secret_key=secret_key,
            algorithm=algorithm,
            access_lifetime=access_lifetime,
        )
        return tokens


base_user_manager = BaseUserManager()
