#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""限流与 IP 黑名单 Redis 工具。

提供两类能力：
1. 端点级显式限流：`limit_by_ip` / `check_rate_limit`（供已有登录等场景调用）
2. 中间件层多维度限流和黑名单短路：`enforce_rate_limit` / `is_ip_blocked`
   等高阶函数，被 `RateLimitMiddleware` 使用。
"""
import asyncio
from logging import getLogger
from typing import Optional

from fastapi import HTTPException, Request

from core.config import settings
from core.i18n import t
from core.redis import RedisPool
from core.security.rate_limit_config import RateLimitConfigProvider
from core.utils.ip_utils import get_real_client_ip
from core.utils.memory_cache import get_memory_cache, CacheNamespace

logger = getLogger(__name__)


BLACKLIST_KEY_PREFIX = "blacklist:ip:"
RATE_LIMIT_KEY_PREFIX = "ratelimit:"
LOGIN_FAIL_KEY_PREFIX = "ratelimit:login:fail:"

LUA_INCR_EXPIRE = """
local c = redis.call('INCR', KEYS[1])
if c == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return c
"""


def _blacklist_key(ip: str) -> str:
    return f"{BLACKLIST_KEY_PREFIX}{ip}"


def _login_fail_key(ip: str) -> str:
    return f"{LOGIN_FAIL_KEY_PREFIX}{ip}"


async def check_rate_limit(
    key: str,
    limit: int,
    window_seconds: int,
    block_message: str,
) -> None:
    """基于 Redis Lua 脚本的固定窗口限流（INCR + EXPIRE 原子操作）。"""
    redis_client = RedisPool.get_client()
    current = await redis_client.eval(LUA_INCR_EXPIRE, 1, key, window_seconds)
    if current > limit:
        ttl = await redis_client.ttl(key)
        logger.warning("限流触发 key=%s count=%s ttl=%s", key, current, ttl)
        raise HTTPException(
            status_code=429,
            detail=t("rate_limit.blocked_retry", message=block_message, ttl=max(ttl, 1)),
        )


async def limit_by_ip(
    request: Request,
    action: str,
    limit: int,
    window_seconds: int,
    scope: str = "global",
    extra_suffix: Optional[str] = None,
) -> None:
    client_ip = get_real_client_ip(request)
    suffix = f":{extra_suffix}" if extra_suffix else ""
    key = f"{RATE_LIMIT_KEY_PREFIX}{scope}:{action}:ip:{client_ip}{suffix}"
    await check_rate_limit(
        key=key,
        limit=limit,
        window_seconds=window_seconds,
        block_message=t("error.rate_limit_exceeded"),
    )


# ---------------------------------------------------------------------------
# 黑名单
# ---------------------------------------------------------------------------


async def is_ip_blocked(ip: str) -> bool:
    """检查 IP 是否在 Redis 黑名单中。使用 stale-while-revalidate 策略避免 Redis 回源阻塞。"""
    if not ip:
        return False
    _cache = get_memory_cache()
    cached, is_stale = _cache.get_stale(CacheNamespace.IP_BLACKLIST, ip)
    if cached is not None:
        if is_stale:
            asyncio.ensure_future(_refresh_ip_blocklist(ip))
        return cached
    redis_client = RedisPool.get_client()
    exists = await redis_client.exists(_blacklist_key(ip))
    result = bool(exists)
    _cache.set(CacheNamespace.IP_BLACKLIST, ip, result, ttl=10)
    return result


async def _refresh_ip_blocklist(ip: str) -> None:
    """后台刷新单个 IP 的黑名单缓存。"""
    try:
        redis_client = RedisPool.get_client()
        exists = await redis_client.exists(_blacklist_key(ip))
        _cache = get_memory_cache()
        _cache.set(CacheNamespace.IP_BLACKLIST, ip, bool(exists), ttl=10)
    except Exception:
        logger.debug("后台刷新 IP 黑名单缓存失败 ip=%s", ip, exc_info=True)


async def add_ip_to_redis_blacklist(
    ip: str,
    ttl_seconds: Optional[int] = None,
    reason: str = "",
) -> None:
    """写入 Redis 黑名单。永久黑名单也会带兜底 TTL，到期由后台 warmup 重新加载。"""
    if not ip:
        return
    redis_client = RedisPool.get_client()
    effective_ttl = ttl_seconds if ttl_seconds and ttl_seconds > 0 else await RateLimitConfigProvider.get(
        "rate_limit.blacklist_redis_ttl", settings.RATE_LIMIT.BLACKLIST_REDIS_TTL
    )
    await redis_client.set(_blacklist_key(ip), reason or "1", ex=effective_ttl)


async def remove_ip_from_redis_blacklist(ip: str) -> None:
    if not ip:
        return
    redis_client = RedisPool.get_client()
    await redis_client.delete(_blacklist_key(ip))


# ---------------------------------------------------------------------------
# 登录失败计数
# ---------------------------------------------------------------------------


async def incr_login_failure(ip: str) -> int:
    """登录失败 +1，返回当前计数。窗口由 LOGIN_FAIL_WINDOW 控制。"""
    if not ip:
        return 0
    redis_client = RedisPool.get_client()
    key = _login_fail_key(ip)
    window = await RateLimitConfigProvider.get(
        "rate_limit.login_fail_window", settings.RATE_LIMIT.LOGIN_FAIL_WINDOW
    )
    count = await redis_client.eval(LUA_INCR_EXPIRE, 1, key, window)
    return int(count)


async def clear_login_failure(ip: str) -> None:
    if not ip:
        return
    redis_client = RedisPool.get_client()
    await redis_client.delete(_login_fail_key(ip))


# ---------------------------------------------------------------------------
# 多维度限流（供中间件调用）
# ---------------------------------------------------------------------------


class RateLimitExceeded(Exception):
    """限流触发的领域异常。中间件捕获后转换为 429 ORJSONResponse。"""

    def __init__(self, reason: str, retry_after: int):
        super().__init__(reason)
        self.reason = reason
        self.retry_after = max(retry_after, 1)


async def _incr_window(key: str, limit: int, window_seconds: int, dim: str) -> None:
    redis_client = RedisPool.get_client()
    current = await redis_client.eval(LUA_INCR_EXPIRE, 1, key, window_seconds)
    if current > limit:
        ttl = await redis_client.ttl(key)
        logger.warning("middleware 限流 dim=%s key=%s count=%s ttl=%s", dim, key, current, ttl)
        raise RateLimitExceeded(reason=t("rate_limit.dim_exceeded", dim=dim), retry_after=ttl)


async def enforce_ip_limit(ip: str, limit: int, window_seconds: int = 60) -> None:
    if not ip or limit <= 0:
        return
    key = f"{RATE_LIMIT_KEY_PREFIX}ip:{ip}"
    await _incr_window(key, limit, window_seconds, "ip")


async def enforce_user_limit(user_id: int, limit: int, window_seconds: int = 60) -> None:
    if not user_id or limit <= 0:
        return
    key = f"{RATE_LIMIT_KEY_PREFIX}user:{user_id}"
    await _incr_window(key, limit, window_seconds, "user")


async def enforce_path_limit(method: str, path: str, ip: str, limit: int, window_seconds: int = 60) -> None:
    if not ip or limit <= 0:
        return
    key = f"{RATE_LIMIT_KEY_PREFIX}path:{method}:{path}:ip:{ip}"
    await _incr_window(key, limit, window_seconds, "path")
