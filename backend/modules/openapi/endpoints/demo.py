#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API 示例接口：用于验证 HMAC 签名鉴权链路是否打通
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from core.response.response_schema import ResponseModel
from modules.openapi.deps import MerchantPrincipal, current_merchant

demo_router = APIRouter(
    prefix="/demo",
    tags=["开放API-示例"],
    dependencies=[Depends(current_merchant)],
)


@demo_router.get("/ping", response_model=ResponseModel)
async def ping(merchant: MerchantPrincipal = Depends(current_merchant)):
    """
    开放API 鉴权连通性测试。

    需携带合法的 X-App-Id / X-Timestamp / X-Nonce / X-Signature 头，
    校验通过后返回商户信息。
    """
    return ResponseModel(
        data={
            "app_id": merchant.app_id,
            "merchant_name": merchant.name,
            "pong": True,
            "server_time": datetime.now(timezone.utc).isoformat(),
        },
        msg="pong",
    )
