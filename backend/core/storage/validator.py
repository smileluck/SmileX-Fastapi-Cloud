#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件校验工具
"""
import os
import uuid
from typing import Optional, Tuple

import filetype

from core.exception.errors import RequestError
from core.i18n import t


def validate_file_extension(
    filename: str,
    allowed_extensions: Optional[Tuple[str, ...]] = None,
) -> str:
    """
    校验文件扩展名

    Args:
        filename: 原始文件名
        allowed_extensions: 允许的扩展名白名单 (不含点, 如 ("png", "jpg"))

    Returns:
        扩展名 (不含点, 小写)

    Raises:
        RequestError: 文件扩展名不在白名单中
    """
    ext = os.path.splitext(filename)[1].lstrip(".").lower()
    if not ext:
        raise RequestError(msg=t("storage.file_no_extension"))
    if allowed_extensions and ext not in [e.lower() for e in allowed_extensions]:
        raise RequestError(
            msg=t("storage.unsupported_file_type", ext=ext, allowed=", ".join(allowed_extensions))
        )
    return ext


def validate_file_size(size_bytes: int, max_size: int) -> None:
    """
    校验文件大小

    Args:
        size_bytes: 文件大小 (字节)
        max_size: 最大允许大小 (字节)

    Raises:
        RequestError: 文件大小超过限制
    """
    if size_bytes > max_size:
        max_mb = max_size / (1024 * 1024)
        raise RequestError(msg=t("storage.file_too_large", max=f"{max_mb:.1f}"))


def generate_stored_name(extension: str) -> str:
    """
    生成唯一存储文件名

    Args:
        extension: 文件扩展名 (不含点)

    Returns:
        UUID-based 存储文件名
    """
    return f"{uuid.uuid4().hex}.{extension}"


# filetype 等 magic-number 库检测能力弱的文本/容器类扩展名：
# 检测不到真实类型时，退化为信任扩展名白名单（已由 validate_file_extension 把关）
_TEXT_FALLBACK_EXTS = frozenset({
    "svg", "pdf", "txt", "csv", "json", "xml",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "zip", "rar", "7z", "tar", "gz",
})


def detect_file_type(file_data: bytes) -> Tuple[Optional[str], Optional[str]]:
    """通过 magic bytes 检测文件真实类型。

    Args:
        file_data: 文件二进制内容

    Returns:
        (ext_without_dot, mime)，识别失败返回 (None, None)
    """
    if not file_data:
        return None, None
    kind = filetype.guess(file_data)
    if kind is None:
        return None, None
    return kind.extension, kind.mime


def _mime_compatible(declared: str, real: str) -> bool:
    """声明 MIME 与真实 MIME 是否兼容（容忍 image/jpg ↔ image/jpeg 等常见别名）"""
    norm = lambda m: m.lower().strip().replace("image/jpg", "image/jpeg")
    return norm(declared) == norm(real)


def validate_file_content(
    file_data: bytes,
    declared_ext: str,
    declared_mime: Optional[str] = None,
    *,
    strict_mime: bool = True,
) -> str:
    """扩展名 ↔ 真实类型 ↔ 声明 MIME 三方交叉校验。

    Args:
        file_data: 文件二进制内容
        declared_ext: 声明扩展名（不含点，小写，通常来自 validate_file_extension）
        declared_mime: 客户端声明的 Content-Type
        strict_mime: 是否要求声明 MIME 与检测一致

    Returns:
        可信 MIME 字符串（优先真实检测值）

    Raises:
        RequestError: 真实类型识别失败、扩展名与真实类型不一致、MIME 不匹配
    """
    real_ext, real_mime = detect_file_type(file_data)
    if real_ext is None:
        # 文本/容器类无法用 magic bytes 判定，退化为信任扩展名白名单
        if declared_ext in _TEXT_FALLBACK_EXTS:
            return declared_mime or "application/octet-stream"
        raise RequestError(msg=t("storage.cannot_detect_real_type", ext=declared_ext))
    if real_ext != declared_ext:
        raise RequestError(
            msg=t("storage.ext_mismatch", declared=declared_ext, real=real_ext)
        )
    if (
        strict_mime
        and declared_mime
        and real_mime
        and not _mime_compatible(declared_mime, real_mime)
    ):
        raise RequestError(msg=t("storage.mime_mismatch"))
    return real_mime or declared_mime or "application/octet-stream"
