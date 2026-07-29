#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译文案目录加载

启动时（首次访问）将 locales/*.yaml 读取为内存扁平字典：
    { locale: { "dotted.key": "模板字符串" } }

嵌套 YAML 会被拍平为点号拼接的 key，例如：
    error:
      user:
        not_found: "用户不存在"
    => { "error.user.not_found": "用户不存在" }

catalog 全程只读，加载一次后并发访问安全。
"""
from pathlib import Path
from typing import Dict, List

import yaml

_LOCALES_DIR = Path(__file__).parent / "locales"
_catalog: Dict[str, Dict[str, str]] | None = None


def _flatten(data: Dict, prefix: str = "") -> Dict[str, str]:
    """把嵌套 dict 拍平为 dotted key -> 字符串"""
    result: Dict[str, str] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            result.update(_flatten(value, full_key))
        else:
            result[full_key] = "" if value is None else str(value)
    return result


def load_catalogs(locales_dir: Path = _LOCALES_DIR) -> Dict[str, Dict[str, str]]:
    """加载所有 locale YAML 文件，返回 {locale: {key: template}}"""
    catalog: Dict[str, Dict[str, str]] = {}
    if not locales_dir.exists():
        return catalog
    for file_path in sorted(locales_dir.glob("*.yaml")):
        with open(file_path, "r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp) or {}
        catalog[file_path.stem] = _flatten(data)
    return catalog


def get_catalog() -> Dict[str, Dict[str, str]]:
    """获取目录（首次访问时懒加载）"""
    global _catalog
    if _catalog is None:
        _catalog = load_catalogs()
    return _catalog


def supported_locales() -> List[str]:
    """返回当前已加载的所有 locale（文件名 stem）"""
    return list(get_catalog().keys())


def reload_catalogs() -> Dict[str, Dict[str, str]]:
    """强制重新加载目录（测试 / 热更新用）"""
    global _catalog
    _catalog = load_catalogs()
    return _catalog
