#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from logging import getLogger
from typing import Callable
from uuid import uuid4
import time

from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.utils.ip_utils import get_real_client_ip
from core.log.request_id_filter import set_request_id

logger = getLogger(__name__)


def _log_request(
    method: str, path: str, status_code: int,
    elapsed_ms: float, client_ip: str, request_id: str,
):
    """同步写审计日志，由 BackgroundTask 在响应发送后调用"""
    logger.info(
        "request completed: method=%s path=%s status=%s elapsed=%.1fms client_ip=%s request_id=%s",
        method, path, status_code, elapsed_ms, client_ip, request_id,
    )


class RequestAuditMiddleware(BaseHTTPMiddleware):
    """写入审计上下文字段，供日志和业务复用。"""

    async def dispatch(self, request: Request, call_next: Callable):
        start = time.monotonic()
        request_id = (
            request.headers.get(settings.TRACE_ID.REQUEST_HEADER_KEY) or uuid4().hex
        )
        client_ip = get_real_client_ip(request)
        request.state.request_id = request_id
        request.state.client_ip = client_ip
        set_request_id(request_id)
        response = await call_next(request)
        elapsed_ms = (time.monotonic() - start) * 1000
        response.headers[settings.TRACE_ID.REQUEST_HEADER_KEY] = request_id

        # 审计日志移到响应发送后执行，不阻塞响应返回
        response.background = BackgroundTask(
            _log_request,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            client_ip,
            request_id,
        )

        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """基于 Content-Length 的请求体大小限制。"""

    # 上传接口豁免路径前缀（使用 UPLOAD_LOCAL.MAX_FILE_SIZE 单独控制）
    _UPLOAD_PATHS = ("/admin/sys/file/upload", "/robot/config/face/upload")

    async def dispatch(self, request: Request, call_next: Callable):
        # 上传接口豁免全局请求体大小限制
        if any(request.url.path.startswith(p) for p in self._UPLOAD_PATHS):
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > settings.SECURITY.MAX_REQUEST_SIZE:
                    return ORJSONResponse(
                        status_code=413,
                        content={
                            "code": 413,
                            "msg": "请求体过大",
                        },
                    )
            except ValueError:
                return ORJSONResponse(
                    status_code=400,
                    content={
                        "code": 400,
                        "msg": "非法 Content-Length",
                    },
                )
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """统一追加安全响应头。"""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault(
            "Referrer-Policy", settings.SECURITY.REFERRER_POLICY
        )
        response.headers.setdefault(
            "Permissions-Policy", settings.SECURITY.PERMISSIONS_POLICY
        )
        response.headers.setdefault(
            "Content-Security-Policy", settings.SECURITY.CSP_POLICY
        )
        if settings.SECURITY.HSTS_ENABLED:
            response.headers.setdefault(
                "Strict-Transport-Security", settings.SECURITY.HSTS_VALUE
            )
        return response
