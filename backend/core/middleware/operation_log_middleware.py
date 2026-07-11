#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
操作日志中间件
自动捕获所有 admin 接口的操作日志
"""
import asyncio
import json
import logging
import re
import time
from typing import Callable, Tuple

import jwt
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.config import settings
from core.utils.ip_utils import get_real_client_ip

logger = logging.getLogger(__name__)

MAX_RESPONSE_RESULT_LENGTH = 2000

# 前缀白名单：静态高频轮询接口
WHITELIST_PREFIXES: Tuple[str, ...] = (
    "/admin/auth",
    "/admin/sys/operation-log",
    "/admin/sys/login-log",
    "/admin/sys/monitor",
    "/admin/sys/export/task/list",
    "/docs",
    "/redoc",
    "/openapi.json",
)

# 后缀白名单：预留用于带动态路径参数的高频轮询接口，避免前缀匹配误伤同前缀的增删改接口
# 当前只有列表接口在轮询，故为空；需要时可加入如 "/download" 等固定后缀
WHITELIST_SUFFIXES: Tuple[str, ...] = ()

# 正则白名单：预留用于纯动态路径参数的高频轮询接口
# 当前只有列表接口在轮询，故为空
WHITELIST_PATTERNS: Tuple[re.Pattern, ...] = ()


def _is_whitelisted(path: str) -> bool:
    for prefix in WHITELIST_PREFIXES:
        if path.startswith(prefix):
            return True
    for suffix in WHITELIST_SUFFIXES:
        if path.endswith(suffix):
            return True
    for pattern in WHITELIST_PATTERNS:
        if pattern.match(path):
            return True
    return False


def _decode_jwt_sync(token: str) -> tuple[dict | None, str | None]:
    """同步解析 JWT，供 asyncio.to_thread 调用"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT.SECRET_KEY,
            algorithms=[settings.JWT.ALGORITHM],
            audience=settings.JWT.AUDIENCE,
            options={"verify_exp": True},
        )
        user_id = payload.get("user_id")
        username = payload.get("username")
        return payload, (int(user_id) if user_id else None, username or "unknown")
    except Exception:
        return None, None


async def _extract_user_from_token(request: Request) -> tuple[int | None, str | None]:
    """从 Authorization 头解析 JWT，CPU 密集部分放到线程池"""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        return None, None
    token = auth_header[7:]
    payload, user_info = await asyncio.to_thread(_decode_jwt_sync, token)
    if payload:
        request.state._jwt_payload = payload
        request.state._jwt_raw_token = token
    return user_info or (None, None)


async def _capture_request_body(request: Request) -> str | None:
    """读取请求体并序列化为 JSON 字符串"""
    try:
        body = await request.body()
        if not body:
            params = {}
            if request.query_params:
                params["query"] = dict(request.query_params)
            return json.dumps(params, ensure_ascii=False) if params else None
        params = {"query": dict(request.query_params)} if request.query_params else {}
        try:
            params["body"] = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            params["body"] = body.decode("utf-8", errors="replace")
        return json.dumps(params, ensure_ascii=False)
    except Exception:
        return None


def _read_response_body_fast(response: Response) -> str | None:
    """从已缓冲的响应中快速读取 body"""
    try:
        body = getattr(response, "body", None)
        if body:
            text = body.decode("utf-8", errors="replace") if isinstance(body, bytes) else str(body)
            if len(text) > MAX_RESPONSE_RESULT_LENGTH:
                text = text[:MAX_RESPONSE_RESULT_LENGTH] + "...(truncated)"
            return text
    except Exception:
        pass
    return None


async def _write_operation_log(
    user_id: int | None,
    username: str | None,
    method: str,
    path: str,
    ip: str | None,
    request_params: str | None,
    response_code: int | None,
    response_result: str | None,
    elapsed_ms: float | None,
):
    """异步写入操作日志到数据库，在响应发送后由 BackgroundTask 触发"""
    try:
        from database import get_session
        from database.models.sys.operation_log import SysOperationLog

        async for db in get_session():
            log_entry = SysOperationLog(
                user_id=user_id or 0,
                username=username or "anonymous",
                module=path.split("/")[2] if len(path.split("/")) > 2 else "unknown",
                action=method.lower(),
                description=f"{method} {path}",
                method=method,
                path=path,
                ip=ip,
                request_params=request_params,
                response_code=response_code,
                response_result=response_result,
                elapsed_ms=elapsed_ms,
            )
            db.add(log_entry)
            await db.commit()
    except Exception as e:
        logger.error("写入操作日志失败: %s", e)


class OperationLogMiddleware(BaseHTTPMiddleware):
    """自动记录所有 admin 接口的操作日志"""

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        if not path.startswith("/admin/") or _is_whitelisted(path):
            return await call_next(request)

        start = time.monotonic()

        user_id, username = await _extract_user_from_token(request)
        ip = get_real_client_ip(request)
        request_params = await _capture_request_body(request)

        response = await call_next(request)

        elapsed_ms = (time.monotonic() - start) * 1000

        response_result = _read_response_body_fast(response)

        # 用 BackgroundTask 附加到响应，在响应发送后才写 DB
        response.background = BackgroundTask(
            _write_operation_log,
            user_id=user_id,
            username=username,
            method=request.method,
            path=path,
            ip=ip,
            request_params=request_params,
            response_code=response.status_code,
            response_result=response_result,
            elapsed_ms=elapsed_ms,
        )

        return response
