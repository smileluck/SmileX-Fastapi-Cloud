#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field

from modules.common.schemas.base import BaseReqEntity, BaseRespEntity, OptionalIntField


class OperationLogQueryParams(BaseReqEntity):
    """操作日志查询参数"""

    module: str | None = Field(None, description="操作模块")
    action: str | None = Field(None, description="操作类型")
    user_id: OptionalIntField = Field(None, description="操作人ID")
    username: str | None = Field(None, description="操作人用户名")
    start_time: str | None = Field(None, description="开始时间")
    end_time: str | None = Field(None, description="结束时间")


class OperationLogResponse(BaseRespEntity):
    """操作日志列表响应"""

    id: int
    user_id: int
    username: str
    module: str
    action: str
    description: str | None
    method: str | None
    path: str | None
    ip: str | None
    response_code: int | None
    elapsed_ms: float | None
    created_at: datetime | None


class OperationLogDetailResponse(BaseRespEntity):
    """操作日志详情响应（含请求参数和响应结果）"""

    id: int
    user_id: int
    username: str
    module: str
    action: str
    description: str | None
    method: str | None
    path: str | None
    ip: str | None
    response_code: int | None
    elapsed_ms: float | None
    request_params: str | None
    response_result: str | None
    created_at: datetime | None
