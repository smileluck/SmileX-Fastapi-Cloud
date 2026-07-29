#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导出模块注册表
每个可导出的业务模块通过 register_export 注册列配置和查询函数
"""
from dataclasses import dataclass
from typing import Callable, Dict, Sequence, Type

from pydantic import BaseModel

from core.utils.excel_export import ExportColumn
from core.i18n import t


@dataclass
class ModuleExportConfig:
    name: str
    module_key: str
    columns: Sequence[ExportColumn]
    build_query_fn: Callable
    query_params_class: Type[BaseModel] | None = None


EXPORT_REGISTRY: Dict[str, ModuleExportConfig] = {}


def register_export(config: ModuleExportConfig):
    EXPORT_REGISTRY[config.module_key] = config


def get_export_config(module_key: str) -> ModuleExportConfig:
    if module_key not in EXPORT_REGISTRY:
        raise ValueError(t("validation.unregistered_export_module", module_key=module_key))
    return EXPORT_REGISTRY[module_key]


# 导入各模块导出配置以触发注册
from . import user_export, role_export, operation_log_export  # noqa: E402, F401
