#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘 Schema

定义仪表盘汇总接口的响应模型，包含统计数据、最近登录、最新公告三部分。
"""

from datetime import datetime

from pydantic import Field

from modules.common.schemas.base import BaseEntity


class DashboardStats(BaseEntity):
    """仪表盘统计数据（4 个核心指标）"""

    user_count: int = Field(default=0, description="用户总数")
    role_count: int = Field(default=0, description="角色总数")
    online_count: int = Field(default=0, description="在线用户数")
    today_login_count: int = Field(default=0, description="今日登录次数")


class DashboardRecentLogin(BaseEntity):
    """最近登录记录条目"""

    username: str = Field(..., description="登录用户名")
    ip: str = Field(default="", description="客户端IP")
    status: bool = Field(..., description="登录状态：True-成功，False-失败")
    login_time: datetime = Field(..., description="登录时间")


class DashboardLatestNotice(BaseEntity):
    """最新公告条目"""

    id: str = Field(..., description="公告ID")
    title: str = Field(..., description="公告标题")
    type: str = Field(..., description="公告类型：announcement/system/operation/approval")
    created_at: datetime = Field(..., description="创建时间")


class DashboardSummary(BaseEntity):
    """仪表盘汇总数据（聚合响应体）"""

    stats: DashboardStats = Field(..., description="统计数据")
    recent_logins: list[DashboardRecentLogin] = Field(default_factory=list, description="最近登录列表")
    latest_notices: list[DashboardLatestNotice] = Field(default_factory=list, description="最新公告列表")
