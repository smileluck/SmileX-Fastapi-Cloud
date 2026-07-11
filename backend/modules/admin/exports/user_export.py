#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core.utils.excel_export import ExportColumn
from modules.admin.exports import ModuleExportConfig, register_export
from modules.admin.services.sys import UserService
from modules.admin.schemas.sys.user import SysUserQueryParams

_user_columns = [
    ExportColumn("id", "ID", width=20, number_format="0"),
    ExportColumn("username", "用户名", width=20),
    ExportColumn("nickname", "昵称", width=20),
    ExportColumn("email", "邮箱", width=25),
    ExportColumn("phone", "手机号", width=15),
    ExportColumn("status", "状态", width=10,
                 transform=lambda v: "启用" if v else "禁用"),
    ExportColumn("is_superuser", "超级管理员", width=10,
                 transform=lambda v: "是" if v else "否"),
    ExportColumn("roles", "角色", width=30,
                 transform=lambda roles: ", ".join(r.name for r in roles) if roles else ""),
    ExportColumn("last_login_at", "最后登录", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
    ExportColumn("last_login_ip", "最后登录IP", width=18),
    ExportColumn("created_at", "创建时间", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
    ExportColumn("updated_at", "更新时间", width=22,
                 transform=lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else ""),
]

register_export(ModuleExportConfig(
    name="用户列表",
    module_key="user",
    columns=_user_columns,
    build_query_fn=UserService.build_user_query,
    query_params_class=SysUserQueryParams,
))
