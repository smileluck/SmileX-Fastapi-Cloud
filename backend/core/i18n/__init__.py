#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
后端 i18n 国际化核心包

对外 API：
    t(key, **kwargs)                 # 按当前请求语言翻译，支持 {name} 占位符
    get_current_language()           # 当前请求语言
    set_current_language(lang)       # 中间件按请求设置
    resolve_language(header, ...)    # 解析 Accept-Language 头
    load_catalogs() / get_catalog()  # 加载 / 获取文案目录
"""
from core.i18n.accept_language import resolve_language
from core.i18n.catalog import (
    get_catalog,
    load_catalogs,
    reload_catalogs,
    supported_locales,
)
from core.i18n.context import (
    get_current_language,
    language_ctx,
    reset_language,
    set_current_language,
)
from core.i18n.translate import t, translate

__all__ = [
    "t",
    "translate",
    "resolve_language",
    "get_current_language",
    "set_current_language",
    "reset_language",
    "language_ctx",
    "get_catalog",
    "load_catalogs",
    "reload_catalogs",
    "supported_locales",
]
