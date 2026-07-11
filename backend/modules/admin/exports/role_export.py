#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.utils.excel_export import ExportColumn
from modules.admin.exports import ModuleExportConfig, register_export
from modules.admin.services.sys import RoleService
from modules.admin.schemas.sys.role import SysRoleQueryParams

_role_columns = [
    ExportColumn("id", "ID", width=20, number_format="0"),
    ExportColumn("name", "角色名", width=20),
    ExportColumn("desc", "描述", width=30),
    ExportColumn("status", "状态", width=10,
                 transform=lambda v: "启用" if v else "禁用"),
    ExportColumn("sort", "排序", width=10, number_format="0"),
    ExportColumn("created_at", "创建时间", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
    ExportColumn("updated_at", "更新时间", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
]

register_export(ModuleExportConfig(
    name="角色列表",
    module_key="role",
    columns=_role_columns,
    build_query_fn=RoleService.build_role_query,
    query_params_class=SysRoleQueryParams,
))
