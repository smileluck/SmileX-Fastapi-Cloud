#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统管理模块路由聚合
"""
from fastapi import APIRouter
from .config import config_router
from .dept import dept_router
from .merchant import merchant_router
from .dict import dict_router
from .menu import menu_router
from .permission import permission_router
from .role import role_router
from .user import user_router
from .mcp import mcp_router
from .route import route_router
from .operation_log import operation_log_router
from .openapi_log import openapi_log_router
from .login_log import login_log_router
from .export_task import export_router
from .export_template import export_template_router
from .online_user import online_user_router
from .ip_blacklist import ip_blacklist_router
from .notice import notice_router
from .monitor import monitor_router
from .dashboard import dashboard_router
from .file import file_router, preview_router
from modules.scheduler.endpoints.scheduled_task import scheduler_task_router
from modules.scheduler.endpoints.task_log import scheduler_log_router

# 创建系统管理主路由器
sys_router = APIRouter(prefix="/sys", tags=["系统管理"])

# 包含各个子模块路由
sys_router.include_router(config_router)
sys_router.include_router(dept_router)
sys_router.include_router(merchant_router)
sys_router.include_router(dict_router)
sys_router.include_router(menu_router)
sys_router.include_router(permission_router)
sys_router.include_router(role_router)
sys_router.include_router(user_router)
sys_router.include_router(mcp_router)
sys_router.include_router(route_router)
sys_router.include_router(operation_log_router)
sys_router.include_router(openapi_log_router)
sys_router.include_router(login_log_router)
sys_router.include_router(export_router)
sys_router.include_router(export_template_router)
sys_router.include_router(online_user_router)
sys_router.include_router(ip_blacklist_router)
sys_router.include_router(notice_router)
sys_router.include_router(monitor_router)
sys_router.include_router(dashboard_router)
sys_router.include_router(file_router)
sys_router.include_router(preview_router)
sys_router.include_router(scheduler_task_router)
sys_router.include_router(scheduler_log_router)

__all__ = ["sys_router"]
