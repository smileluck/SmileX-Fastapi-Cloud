#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""限流与 IP 黑名单中间件。

执行顺序（在 setup_registry 中靠后注册 = 实际执行靠前）：
    RequestContextMiddleware -> RateLimitMiddleware -> OperationLogMiddleware -> ...

逻辑：
    1. 命中白名单前缀 / 白名单 IP / 配置关闭 -> 直接放行
    2. 命中 IP 黑名单 -> 直接 429
    3. 解析 JWT 拿 user_id（可选，沿用 operation_log_middleware 的方式）
    4. 顺序检查：全局 IP -> 用户 -> 路径细粒度
"""
import asyncio
import logging
from typing import Callable, Optional

import jwt
from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.i18n import t
from core.security.rate_limit import (
    RateLimitExceeded,
    enforce_ip_limit,
    enforce_path_limit,
    enforce_user_limit,
    is_ip_blocked,
)
from core.security.rate_limit_config import RateLimitConfigProvider
from core.utils.ip_utils import get_real_client_ip

logger = logging.getLogger(__name__)


async def _is_whitelisted_path(path: str) -> bool:
    prefixes = await RateLimitConfigProvider.get(
        "rate_limit.whitelist_path_prefixes",
        list(settings.RATE_LIMIT.WHITELIST_PATH_PREFIXES),
    )
    for prefix in prefixes:
        if path.startswith(prefix):
            return True
    return False


def _extract_user_id(request: Request) -> Optional[int]:
    """优先复用 operation_log_middleware 已经写入的 payload，避免重复解析 JWT。"""
    cached = getattr(request.state, "_jwt_payload", None)
    if cached and cached.get("user_id"):
        try:
            return int(cached["user_id"])
        except (TypeError, ValueError):
            return None

    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    try:
        payload = jwt.decode(
            token,
            settings.JWT.SECRET_KEY,
            algorithms=[settings.JWT.ALGORITHM],
            audience=settings.JWT.AUDIENCE,
            options={"verify_exp": True},
        )
        request.state._jwt_payload = payload
        request.state._jwt_raw_token = token
        user_id = payload.get("user_id")
        if user_id:
            return int(user_id)
    except Exception:
        return None
    return None


async def _match_path_rule(path: str, method: str):
    """匹配第一条命中的 PATH_RULES 规则。"""
    rules = await RateLimitConfigProvider.get(
        "rate_limit.path_rules",
        [r.model_dump() for r in settings.RATE_LIMIT.PATH_RULES],
    )
    for rule in rules:
        rule_path = rule.get("path", rule.get("PATH", ""))
        rule_method = rule.get("method", rule.get("METHOD", "*"))
        if not path.startswith(rule_path):
            continue
        if rule_method != "*" and rule_method.upper() != method.upper():
            continue
        return rule
    return None


def _build_429_response(request_id: str, reason: str, retry_after: int) -> ORJSONResponse:
    """返回对齐 ResponseModel 结构的 429 响应。"""
    body = {
        "code": 429,
        "msg": reason,
        "data": None,
        "request_id": request_id,
        "err_code": 10901,
    }
    resp = ORJSONResponse(status_code=429, content=body)
    resp.headers["Retry-After"] = str(retry_after)
    return resp


def _build_blocked_response(request_id: str) -> ORJSONResponse:
    body = {
        "code": 429,
        "msg": t("rate_limit.ip_blocked_contact"),
        "data": None,
        "request_id": request_id,
        "err_code": 10902,
    }
    resp = ORJSONResponse(status_code=429, content=body)
    resp.headers["Retry-After"] = "3600"
    return resp


class RateLimitMiddleware(BaseHTTPMiddleware):
    """多维度限流 + IP 黑名单。"""

    async def dispatch(self, request: Request, call_next: Callable):
        enabled = await RateLimitConfigProvider.get(
            "rate_limit.enabled", settings.RATE_LIMIT.ENABLED
        )
        if not enabled:
            return await call_next(request)

        path = request.url.path
        if await _is_whitelisted_path(path):
            return await call_next(request)

        client_ip = getattr(request.state, "client_ip", "") or get_real_client_ip(request)
        whitelist_ips = await RateLimitConfigProvider.get(
            "rate_limit.whitelist_ips", list(settings.RATE_LIMIT.WHITELIST_IPS)
        )
        if client_ip and client_ip in whitelist_ips:
            return await call_next(request)

        request_id = getattr(request.state, "request_id", "") or ""

        try:
            # 黑名单短路：单独检查，命中直接返回
            if client_ip and await is_ip_blocked(client_ip):
                logger.warning("IP 命中黑名单 ip=%s path=%s", client_ip, path)
                return _build_blocked_response(request_id)

            # 并行读取所有限流配置
            config_keys = ["rate_limit.ip_per_minute", "rate_limit.user_per_minute"]
            config_defaults = [settings.RATE_LIMIT.IP_PER_MINUTE, settings.RATE_LIMIT.USER_PER_MINUTE]
            configs = await asyncio.gather(
                *(RateLimitConfigProvider.get(k, d) for k, d in zip(config_keys, config_defaults))
            )
            ip_per_minute, user_per_minute = configs

            # 构建并行限流任务
            tasks = []
            if client_ip:
                tasks.append(enforce_ip_limit(client_ip, ip_per_minute, 60))

            user_id = _extract_user_id(request)
            if user_id:
                tasks.append(enforce_user_limit(user_id, user_per_minute, 60))

            rule = await _match_path_rule(path, request.method)
            if rule and client_ip:
                tasks.append(enforce_path_limit(
                    method=request.method,
                    path=rule.get("path", rule.get("PATH", "")),
                    ip=client_ip,
                    limit=rule.get("per_minute", rule.get("PER_MINUTE", 60)),
                    window_seconds=60,
                ))

            if tasks:
                await asyncio.gather(*tasks)
        except RateLimitExceeded as exc:
            return _build_429_response(request_id, exc.reason, exc.retry_after)
        except Exception as exc:  # Redis 故障等 -> 失败放行，避免阻塞业务
            logger.error("限流中间件异常，放行请求 path=%s err=%s", path, exc)
            return await call_next(request)

        return await call_next(request)
