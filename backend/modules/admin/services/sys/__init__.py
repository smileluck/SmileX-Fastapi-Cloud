#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统管理服务模块
"""
from .config_service import ConfigService
from .data_scope_service import DataScopeService
from .dept_service import DeptService
from .merchant_service import MerchantService
from .dict_service import DictService
from .menu_service import MenuService
from .permission_service import PermissionService
from .role_service import RoleService
from .user_service import UserService
from .mcp_service import MCPService
from .route_service import RouteService
from .operation_log_service import OperationLogService
from .openapi_log_service import OpenapiLogService
from .notice_service import NoticeService
from .monitor_service import MonitorService
from .file_service import FileService

__all__ = [
    "ConfigService",
    "DataScopeService",
    "DeptService",
    "MerchantService",
    "DictService",
    "MenuService",
    "PermissionService",
    "RoleService",
    "UserService",
    "MCPService",
    "RouteService",
    "OperationLogService",
    "OpenapiLogService",
    "NoticeService",
    "MonitorService",
    "FileService",
]
