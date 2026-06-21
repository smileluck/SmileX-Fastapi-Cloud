#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通用定时任务集合
这些任务本身在代码里注册一次，但接受运行时参数，前端可基于它们创建多个实例
"""

import asyncio
import ipaddress
import logging
import socket
from typing import Annotated, Literal

import httpx
from pydantic import BaseModel, Field, HttpUrl

from modules.scheduler.core.registry import scheduled_task

logger = logging.getLogger(__name__)


# ============================================================
# Webhook 任务
# ============================================================

_BLOCKED_SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie"}


class WebhookParams(BaseModel):
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"] = "POST"
    url: HttpUrl = Field(..., description="目标 URL")
    headers: dict[str, str] = Field(default_factory=dict, description="自定义请求头")
    body: dict | None = Field(None, description="JSON 请求体")
    timeout_seconds: Annotated[int, Field(ge=1, le=60)] = 30
    expect_status: Annotated[int, Field(ge=100, le=599)] = 200


def _is_private_host(host: str) -> bool:
    """判断主机名是否解析到私网/回环地址（用于 SSRF 防御）"""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = info[4][0]
        try:
            addr = ipaddress.ip_address(ip)
        except ValueError:
            continue
        if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
            return True
    return False


@scheduled_task(
    cron="0 * * * *",
    name="Webhook 请求",
    description="通用 HTTP 调用任务，可由用户实例化",
    task_key="generic.webhook",
    is_system=False,
    params_schema=WebhookParams,
)
async def webhook_task(params: WebhookParams):
    """通用 HTTP 调用任务"""
    safe_headers = {
        k: v for k, v in (params.headers or {}).items()
        if k.lower() not in _BLOCKED_SENSITIVE_HEADERS
    }

    if _is_private_host(params.url.host):
        return {
            "ok": False,
            "error": "目标地址解析到私网/回环，已拒绝",
            "host": params.url.host,
        }

    async with httpx.AsyncClient(timeout=params.timeout_seconds) as client:
        resp = await client.request(
            params.method,
            str(params.url),
            headers=safe_headers,
            json=params.body,
        )

    ok = resp.status_code == params.expect_status
    return {
        "ok": ok,
        "status_code": resp.status_code,
        "body_preview": resp.text[:500],
    }


# ============================================================
# Shell 任务（高危，仅超管可用）
# ============================================================

class ShellParams(BaseModel):
    command: str = Field(..., description="要执行的 Shell 命令")
    cwd: str | None = Field(None, description="工作目录")
    timeout_seconds: Annotated[int, Field(ge=1, le=600)] = 60


@scheduled_task(
    cron="0 * * * *",
    name="Shell 命令",
    description="执行 Shell 命令（高危，仅超管可用）",
    task_key="generic.shell",
    is_system=False,
    params_schema=ShellParams,
)
async def shell_task(params: ShellParams):
    """执行 Shell 命令"""
    proc = await asyncio.create_subprocess_shell(
        params.command,
        cwd=params.cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=params.timeout_seconds
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return {
            "ok": False,
            "error": f"命令执行超时（{params.timeout_seconds}秒）",
            "command": params.command,
        }

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": stdout.decode(errors="replace")[:2000],
        "stderr": stderr.decode(errors="replace")[:2000],
    }


# ============================================================
# SQL 任务（默认只读）
# ============================================================

class SqlParams(BaseModel):
    sql: str = Field(..., description="SQL 语句")
    read_only: bool = Field(True, description="只读模式：仅允许 SELECT")
    limit: Annotated[int, Field(ge=1, le=1000)] = 100


@scheduled_task(
    cron="0 * * * *",
    name="SQL 查询",
    description="执行 SQL 查询任务（默认只读）",
    task_key="generic.sql",
    is_system=False,
    params_schema=SqlParams,
)
async def sql_task(params: SqlParams):
    """执行 SQL 查询"""
    from sqlalchemy import text

    from database.db_manager import get_session

    normalized = params.sql.strip().lower()
    if params.read_only and not normalized.startswith("select"):
        return {
            "ok": False,
            "error": "read_only 模式仅允许 SELECT 语句",
        }

    async for db in get_session():
        try:
            result = await db.execute(text(params.sql))
            if normalized.startswith("select") or normalized.startswith("with"):
                rows = result.mappings().fetchmany(params.limit)
                payload = {
                    "ok": True,
                    "columns": list(rows[0].keys()) if rows else [],
                    "rows": [dict(r) for r in rows],
                    "rowcount": len(rows),
                }
            else:
                await db.commit()
                payload = {"ok": True, "rowcount": result.rowcount}
            return payload
        except Exception as exc:
            await db.rollback()
            return {"ok": False, "error": str(exc)[:2000]}
