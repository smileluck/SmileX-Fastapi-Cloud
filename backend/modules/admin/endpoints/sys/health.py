#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
健康检查与就绪探针端点（顶级路由）。

设计说明：
    本端点刻意不使用 ResponseModel 包装、不挂鉴权依赖，并挂在顶级路径（非 /admin、非 /open）。
    原因：
      1. 探针是基础设施语义（供 K8s/nginx/部署脚本探测），需绕过鉴权与业务中间件链路。
      2. 顶级路径天然不受 OperationLogMiddleware（仅作用 /admin/*）与 OpenapiLogMiddleware
         （仅作用 /open/*，强制 HMAC 签名）约束，无需在白名单中维护，最干净。
      3. 与业务响应结构解耦。
    详见 docs/superpowers/specs/2026-05-27-ops-p0-fix-design.md 第 3.2/3.3 节。

路径设计：
    router 直接在 main.py 顶层注册（无 prefix），最终对外路径为：
      - GET /health  存活探针（liveness）
      - GET /ready   就绪探针（readiness）
    与 spec 3.2 节接口契约对齐。
"""
import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.redis import get_redis_client

logger = logging.getLogger(__name__)

# 顶级路由：不挂到 sys_router，直接在 main.py 顶层注册
# 最终对外路径为 /health 与 /ready（脱离 /admin /open 业务前缀）
health_router = APIRouter(tags=["基础设施/健康探针"])


async def _check_db(db: AsyncSession) -> bool:
    """
    检查数据库连接是否可用（执行 SELECT 1）

    Args:
        db: 异步数据库会话

    Returns:
        bool: 连接正常返回 True，异常返回 False
    """
    try:
        result = await db.execute(text("SELECT 1"))
        return result.scalar() == 1
    except Exception as exc:
        # 仅记录 WARNING：就绪检查失败属于基础设施状态波动，不应污染 5xx 错误率统计
        logger.warning("就绪检查 DB 失败: %s", exc)
        return False


async def _check_redis(redis_client) -> bool:
    """
    检查 Redis 连接是否可用（执行 PING）

    Args:
        redis_client: 异步 Redis 客户端

    Returns:
        bool: 连接正常返回 True，异常返回 False
    """
    try:
        pong = await redis_client.ping()
        return bool(pong)
    except Exception as exc:
        logger.warning("就绪检查 Redis 失败: %s", exc)
        return False


@health_router.get(
    "/health",
    summary="存活探针 (liveness)",
    status_code=status.HTTP_200_OK,
)
async def health():
    """
    存活探针：仅判断进程是否存活，不检查外部依赖。

    用于「进程是否需要重启」判断。固定返回 200，不暴露任何内部信息。
    """
    return {"status": "up"}


@health_router.get(
    "/ready",
    summary="就绪探针 (readiness)",
)
async def ready(
    db: AsyncSession = Depends(get_session),
    redis_client=Depends(get_redis_client),
):
    """
    就绪探针：检查 DB 与 Redis 是否就绪。

    用于「是否要接入流量」判断。任一依赖失败返回 HTTP 503。
    响应体仅给出 ok/fail 状态，不暴露错误详情（避免泄漏内部拓扑）。
    """
    db_ok = await _check_db(db)
    redis_ok = await _check_redis(redis_client)
    checks = {
        "db": "ok" if db_ok else "fail",
        "redis": "ok" if redis_ok else "fail",
    }
    ready_ok = db_ok and redis_ok
    return JSONResponse(
        status_code=(
            status.HTTP_200_OK
            if ready_ok
            else status.HTTP_503_SERVICE_UNAVAILABLE
        ),
        content={
            "status": "ready" if ready_ok else "not_ready",
            "checks": checks,
        },
    )
