#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
首页仪表盘接口

提供首页仪表盘汇总数据接口，所有已登录用户可访问（不做 data_scope 过滤）。
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response import ResponseModel, response_base
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.services.sys.dashboard_service import DashboardService
from modules.admin.schemas.sys.dashboard import DashboardSummary

logger = logging.getLogger(__name__)

dashboard_router = APIRouter(prefix="/dashboard", tags=["系统管理/首页仪表盘"])


@dashboard_router.get(
    "/summary",
    response_model=ResponseModel[DashboardSummary],
    summary="获取首页仪表盘汇总数据",
)
async def get_dashboard_summary(
    user=Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    获取首页仪表盘汇总数据。

    返回统计数据（用户总数、角色总数、在线用户数、今日登录次数）
    加最近登录记录与最新公告。结果缓存 60 秒。
    """
    data = await DashboardService.get_summary(db=db)
    return response_base.success(data=data)
