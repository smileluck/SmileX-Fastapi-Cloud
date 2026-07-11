#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.utils.excel_export import ExportColumn
from modules.admin.exports import ModuleExportConfig, register_export
from modules.admin.services.sys.operation_log_service import OperationLogService
from modules.admin.schemas.sys.operation_log import OperationLogQueryParams

_operation_log_columns = [
    ExportColumn("id", "ID", width=20, number_format="0"),
    ExportColumn("user_id", "用户ID", width=15, number_format="0"),
    ExportColumn("username", "用户名", width=20),
    ExportColumn("module", "模块", width=15),
    ExportColumn("action", "操作", width=15),
    ExportColumn("description", "描述", width=30),
    ExportColumn("method", "HTTP方法", width=10),
    ExportColumn("path", "请求路径", width=30),
    ExportColumn("ip", "IP地址", width=18),
    ExportColumn("response_code", "响应码", width=10, number_format="0"),
    ExportColumn("elapsed_ms", "耗时(ms)", width=10, number_format="0.00"),
    ExportColumn("created_at", "操作时间", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
]

register_export(ModuleExportConfig(
    name="操作日志",
    module_key="operation_log",
    columns=_operation_log_columns,
    build_query_fn=OperationLogService.build_operation_log_query,
    query_params_class=OperationLogQueryParams,
))
