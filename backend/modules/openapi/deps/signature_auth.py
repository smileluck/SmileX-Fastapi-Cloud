#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API HMAC 签名鉴权依赖

用法：在开放接口上声明 dependencies=[Depends(current_merchant)]，
      或在签名中通过 merchant: MerchantPrincipal = Depends(current_merchant) 取用。
"""
import time
from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exception.errors import OpenApiError
from core.redis import RedisPool
from core.response.response_code import CustomErrorCode
from core.security.openapi import (
    HEADER_APP_ID,
    HEADER_NONCE,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    build_canonical_string,
    compute_signature,
    decrypt_secret,
    is_valid_nonce,
    verify_signature,
)
from database.db_manager import get_session
from modules.admin.services.sys import MerchantService


@dataclass
class MerchantPrincipal:
    """鉴权通过后的商户主体（不携带任何密钥信息）"""

    id: int
    name: str
    app_id: str
    status: bool


async def current_merchant(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> MerchantPrincipal:
    """
    校验 HMAC 签名并返回商户主体。

    校验顺序：请求头完整性 → 时间戳窗口 → nonce 合法性 → nonce 防重放
              → 商户存在性 → 商户启用状态 → 签名一致性
    """
    app_id = request.headers.get(HEADER_APP_ID)
    timestamp = request.headers.get(HEADER_TIMESTAMP)
    nonce = request.headers.get(HEADER_NONCE)
    signature = request.headers.get(HEADER_SIGNATURE)

    # 1. 请求头完整性
    if not (app_id and timestamp and nonce and signature):
        raise OpenApiError(error=CustomErrorCode.OPEN_API_MISSING_HEADER)

    # 2. 时间戳窗口
    try:
        ts_value = int(timestamp)
    except (TypeError, ValueError):
        raise OpenApiError(error=CustomErrorCode.OPEN_API_TIMESTAMP_EXPIRED)

    now_ts = int(time.time())
    tolerance = settings.OPEN_API.TIMESTAMP_TOLERANCE_SECONDS
    if abs(now_ts - ts_value) > tolerance:
        raise OpenApiError(error=CustomErrorCode.OPEN_API_TIMESTAMP_EXPIRED)

    # 3. nonce 合法性
    if not is_valid_nonce(nonce):
        raise OpenApiError(error=CustomErrorCode.OPEN_API_INVALID_NONCE)

    # 4. nonce 防重放（Redis 原子 SET NX + EX）
    nonce_key = f"openapi:nonce:{app_id}:{nonce}"
    client = RedisPool.get_client()
    acquired = await client.set(
        nonce_key, "1", ex=settings.OPEN_API.NONCE_TTL, nx=True
    )
    if not acquired:
        raise OpenApiError(error=CustomErrorCode.OPEN_API_NONCE_REPLAY)

    # 5. 商户存在性
    merchant_info = await MerchantService.get_active_by_app_id_cached(db, app_id)
    if merchant_info is None:
        raise OpenApiError(error=CustomErrorCode.OPEN_API_MERCHANT_NOT_FOUND)

    # 6. 商户启用状态
    if not merchant_info.get("status"):
        raise OpenApiError(error=CustomErrorCode.OPEN_API_MERCHANT_DISABLED)

    # 7. 签名一致性
    body_bytes = await request.body()
    canonical = build_canonical_string(
        method=request.method,
        path=request.url.path,
        body_bytes=body_bytes,
        timestamp=timestamp,
        nonce=nonce,
        app_id=app_id,
    )
    app_secret = decrypt_secret(merchant_info["app_secret_encrypted"])
    expected = compute_signature(canonical, app_secret)
    if not verify_signature(expected, signature):
        raise OpenApiError(error=CustomErrorCode.OPEN_API_SIGNATURE_INVALID)

    return MerchantPrincipal(
        id=merchant_info["id"],
        name=merchant_info["name"],
        app_id=merchant_info["app_id"],
        status=merchant_info["status"],
    )
