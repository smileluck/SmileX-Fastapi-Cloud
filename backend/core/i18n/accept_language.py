#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Accept-Language 头解析与语言匹配（RFC 7231 质量值）

纯函数、无第三方依赖。示例：
    resolve_language("en-US,en;q=0.9,zh-CN;q=0.8", ["zh-CN", "en-US"], "zh-CN") -> "en-US"
    resolve_language("zh", ["zh-CN", "en-US"], "zh-CN") -> "zh-CN"
    resolve_language(None, ["zh-CN", "en-US"], "zh-CN") -> "zh-CN"
"""
from typing import List, Optional


def _normalize(tag: str) -> str:
    """归一化语言标签：小写、下划线转连字符"""
    return tag.strip().lower().replace("_", "-")


def _parse(header: str) -> List[tuple]:
    """解析 Accept-Language 头为 [(tag, q), ...]，按 q 降序、原序稳定排序"""
    candidates = []
    for idx, part in enumerate(header.split(",")):
        part = part.strip()
        if not part or part == "*":
            continue
        tag = part
        q = 1.0
        if ";" in part:
            tag, _, params = part.partition(";")
            tag = tag.strip()
            for p in params.split(";"):
                p = p.strip()
                if p.startswith("q="):
                    try:
                        q = float(p[2:])
                    except ValueError:
                        q = 1.0
        tag = tag.strip()
        if not tag or q <= 0:
            continue
        candidates.append((tag, q, idx))
    # 按 q 降序，q 相同时保持头部出现的顺序
    candidates.sort(key=lambda x: (-x[1], x[2]))
    return [(tag, q) for tag, q, _ in candidates]


def resolve_language(
    header: Optional[str], supported: List[str], default: str
) -> str:
    """
    根据 Accept-Language 头从 supported 中选出最佳语言。

    匹配优先级：精确 > 主语言前缀（zh 匹配 zh-CN，en 匹配 en-US，双向）。
    无任何匹配时返回 default。
    """
    if not header:
        return default

    supported_norm = [(_normalize(s), s) for s in supported]
    supported_primary = [(sn.split("-")[0], s) for sn, s in supported_norm]

    for tag, _q in _parse(header):
        n = _normalize(tag)
        p = n.split("-")[0]
        # 1. 精确匹配
        for sn, original in supported_norm:
            if n == sn:
                return original
        # 2. 主语言前缀匹配（双向：请求 zh 命中 zh-CN；请求 zh-TW 也命中 zh-CN）
        for sp, original in supported_primary:
            if p == sp:
                return original

    return default
