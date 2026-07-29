#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, Annotated
from zoneinfo import ZoneInfo

from pydantic import Field, BeforeValidator

from modules.common.schemas.base import BaseEntity, OptionalIntField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class OpenapiLogQueryParams(PageRequest):
    """开放API调用日志查询参数"""

    app_id: Optional[str] = Field(None, description="AppId，支持模糊查询")
    path: Optional[str] = Field(None, description="请求路径，支持模糊查询")
    method: Optional[str] = Field(None, description="HTTP方法")
    status_code: OptionalIntField = Field(None, description="HTTP状态码")
    err_code: OptionalIntField = Field(None, description="业务错误码")
    client_ip: Optional[str] = Field(None, description="客户端IP，支持模糊查询")
    request_id: Optional[str] = Field(None, description="请求追踪ID")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


class OpenapiLogResponse(BaseEntity):
    """开放API调用日志响应"""

    model_config = {"from_attributes": True}

    id: int = Field(..., description="日志ID")
    app_id: str = Field(..., description="AppId")
    merchant_name: Optional[str] = Field(None, description="商户名称")
    method: str = Field(..., description="HTTP方法")
    path: str = Field(..., description="请求路径")
    status_code: Optional[int] = Field(None, description="HTTP状态码")
    err_code: Optional[int] = Field(None, description="业务错误码")
    msg: Optional[str] = Field(None, description="响应消息")
    client_ip: Optional[str] = Field(None, description="客户端IP")
    request_id: Optional[str] = Field(None, description="请求追踪ID")
    latency_ms: Optional[int] = Field(None, description="耗时(毫秒)")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(
        None, description="创建时间"
    )
