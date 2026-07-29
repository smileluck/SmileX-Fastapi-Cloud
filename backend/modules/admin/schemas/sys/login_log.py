#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field

from modules.common.schemas.base import BaseEntity, BoolField


class LoginLogQueryParams(BaseEntity):
    """登录日志查询参数"""

    username: str | None = Field(None, description="登录用户名")
    ip: str | None = Field(None, description="客户端IP")
    status: BoolField = Field(None, description="登录状态")
    start_time: str | None = Field(None, description="开始时间")
    end_time: str | None = Field(None, description="结束时间")


class LoginLogResponse(BaseEntity):
    """登录日志列表响应"""

    id: int
    username: str
    ip: str | None
    status: bool
    detail: str | None
    user_agent: str | None
    login_time: datetime | None
    created_at: datetime | None


class LoginLogDetailResponse(LoginLogResponse):
    """登录日志详情响应"""

    pass
