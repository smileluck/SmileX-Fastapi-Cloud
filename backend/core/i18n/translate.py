#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译核心

translate(locale, key, **kwargs):
    1. 在请求语言中查 key
    2. 缺失则回退到 FALLBACK_LANGUAGE
    3. 再缺失回退到 DEFAULT_LANGUAGE
    4. 仍缺失则返回原始 key 字符串（永不抛异常）

动态字段插入使用 {name} 命名占位符，借助 _SafeDict，
缺占位符时原样保留 {name}、多余 kwargs 静默忽略，模板格式错误时退回原文。
"""
from logging import getLogger
from typing import List

from core.config import settings
from core.i18n.catalog import get_catalog
from core.i18n.context import get_current_language

logger = getLogger(__name__)


class _SafeDict(dict):
    """format_map 用的安全字典：缺失占位符原样保留，便于译员排查"""

    def __missing__(self, key):  # type: ignore[override]
        return "{" + key + "}"


def _fallback_chain(locale: str) -> List[str]:
    """构造去重后的回退语言链：locale -> FALLBACK -> DEFAULT"""
    chain: List[str] = []
    for loc in (locale, settings.I18N.FALLBACK_LANGUAGE, settings.I18N.DEFAULT_LANGUAGE):
        if loc and loc not in chain:
            chain.append(loc)
    return chain


def translate(locale: str, key: str, **kwargs) -> str:
    """按语言查 key 并做占位符替换；任何异常都不向外抛"""
    catalog = get_catalog()
    for loc in _fallback_chain(locale):
        bundle = catalog.get(loc)
        if bundle and key in bundle:
            template = bundle[key]
            if not kwargs:
                return template
            try:
                return template.format_map(_SafeDict(kwargs))
            except (IndexError, ValueError):
                return template
    # 完全缺失：dev 环境打 warning 便于补 key
    if settings.ENVIR == "dev":
        logger.warning("i18n 缺少文案 key=%s locale=%s", key, locale)
    return key


def t(key: str, **kwargs) -> str:
    """取当前请求语言翻译 key（最常用的对外 API）"""
    return translate(get_current_language(), key, **kwargs)
