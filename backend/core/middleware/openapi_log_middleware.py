#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API调用日志中间件

记录每一次 /open/* 请求：AppId、HTTP 方法、路径、状态码、业务 err_code、
客户端 IP、request_id、耗时、商户名（冗余）。鉴权失败也记录，便于安全审计。

写入采用 BackgroundTask（响应发出后才落库），不阻塞响应。
"""
import json
import logging
import time
from typing import Any

from starlette.background import BackgroundTask
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from core.security.openapi import HEADER_APP_ID
from core.utils.ip_utils import get_real_client_ip
from core.utils.track_id import get_request_trace_id

logger = logging.getLogger(__name__)

_MAX_MSG_LENGTH = 255


def _parse_response(body: Any) -> tuple[int | None, str | None]:
    """从响应 body 中解析 err_code 与 msg（容错）"""
    if not body:
        return None, None
    try:
        if isinstance(body, (bytes, bytearray)):
            text = body.decode("utf-8", errors="replace")
        else:
            text = str(body)
        data = json.loads(text)
        if isinstance(data, dict):
            err_code = data.get("err_code")
            msg = data.get("msg")
            if isinstance(err_code, str) and err_code.isdigit():
                err_code = int(err_code)
            if isinstance(msg, str) and len(msg) > _MAX_MSG_LENGTH:
                msg = msg[:_MAX_MSG_LENGTH]
            return (err_code if isinstance(err_code, int) else None), msg
    except Exception:
        return None, None
    return None, None


async def _write_openapi_log(
    app_id: str,
    method: str,
    path: str,
    merchant_name: str | None,
    status_code: int | None,
    err_code: int | None,
    msg: str | None,
    client_ip: str | None,
    request_id: str | None,
    latency_ms: int | None,
) -> None:
    """响应发出后异步写入开放API调用日志"""
    try:
        from database import get_session
        from database.models.sys.openapi_log import SysOpenapiLog

        async for db in get_session():
            log_entry = SysOpenapiLog(
                app_id=app_id or "unknown",
                method=method,
                path=path,
                merchant_name=merchant_name,
                status_code=status_code,
                err_code=err_code,
                msg=msg,
                client_ip=client_ip,
                request_id=request_id,
                latency_ms=latency_ms,
            )
            db.add(log_entry)
            await db.commit()
    except Exception as exc:
        logger.error("写入开放API调用日志失败: %s", exc)


async def _resolve_merchant_name(app_id: str) -> str | None:
    """尽量从缓存取商户名（命中则无 DB 查询；鉴权失败的 app_id 返回 None）"""
    if not app_id:
        return None
    try:
        from database import get_session
        from modules.admin.services.sys import MerchantService

        async for db in get_session():
            info = await MerchantService.get_active_by_app_id_cached(db, app_id)
            return info.get("name") if info else None
    except Exception:
        return None


class OpenapiLogMiddleware(BaseHTTPMiddleware):
    """记录 /open/* 调用日志"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if not path.startswith("/open/"):
            return await call_next(request)

        app_id = request.headers.get(HEADER_APP_ID) or ""
        client_ip = get_real_client_ip(request)
        request_id = get_request_trace_id(request)

        start = time.monotonic()
        response = await call_next(request)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        # BaseHTTPMiddleware 默认拿到的是流式响应，需要缓冲出 body 才能解析 err_code/msg；
        # 缓冲后再重新打包成 Response 返回给客户端（/open 响应都是小 JSON，开销可忽略）
        try:
            chunks: list[bytes] = []
            async for chunk in response.body_iterator:
                if isinstance(chunk, str):
                    chunk = chunk.encode("utf-8")
                chunks.append(chunk)
            body_bytes = b"".join(chunks)
            err_code, msg = _parse_response(body_bytes)
            response = StarletteResponse(
                content=body_bytes,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )
        except Exception:
            err_code, msg = None, None

        # 写日志放在响应发出之后（BackgroundTask）；商户名异步解析，失败不影响主流程
        async def _enrich_and_write() -> None:
            merchant_name = await _resolve_merchant_name(app_id)
            await _write_openapi_log(
                app_id=app_id,
                method=request.method,
                path=path,
                merchant_name=merchant_name,
                status_code=response.status_code,
                err_code=err_code,
                msg=msg,
                client_ip=client_ip,
                request_id=request_id,
                latency_ms=elapsed_ms,
            )

        response.background = BackgroundTask(_enrich_and_write)
        return response
