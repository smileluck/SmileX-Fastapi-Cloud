#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import Field

from modules.common.schemas.base import BaseEntity


class OnlineUserQueryParams(BaseEntity):
    """在线用户查询参数"""

    username: str | None = Field(None, description="用户名筛选")
    ip: str | None = Field(None, description="IP地址筛选")


class OnlineUserResponse(BaseEntity):
    """在线用户列表响应"""

    user_id: int
    username: str | None
    nickname: str | None
    avatar: str | None
    session_id: str
    ip: str | None
    user_agent: str | None
    login_time: str | None


class KickUserRequest(BaseEntity):
    """踢用户下线请求"""

    user_id: int = Field(..., description="用户ID")
    session_id: str = Field(..., description="要踢除的会话ID")


class KickAllRequest(BaseEntity):
    """踢用户所有会话下线请求"""

    user_id: int = Field(..., description="用户ID")
