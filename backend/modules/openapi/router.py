#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API 路由聚合（前缀 /open）

该模块下的接口面向第三方系统，使用商户 app_id/app_secret 的 HMAC 签名鉴权，
不经过后台管理员的 JWT 鉴权与操作日志中间件（后者只作用于 /admin/*）。
"""
from fastapi import APIRouter

from .endpoints import demo_router

open_router = APIRouter(prefix="/open", tags=["开放API"])
open_router.include_router(demo_router)

__all__ = ["open_router"]
