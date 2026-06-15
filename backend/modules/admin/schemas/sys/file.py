#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件管理 Schema
"""
from datetime import datetime
from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, BeforeValidator
from zoneinfo import ZoneInfo

from app.models.common.base import BaseRespEntity, BaseEntity
from app.models.common.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class SysFileQueryParams(PageRequest):
    """文件查询参数"""

    original_name: Optional[str] = Field(None, description="原始文件名，支持模糊搜索")
    extension: Optional[str] = Field(None, description="文件扩展名")
    storage_platform: Optional[str] = Field(None, description="存储平台")


class SysFileUploadResponse(BaseRespEntity):
    """文件上传响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="文件ID")
    original_name: str = Field(..., description="原始文件名")
    stored_name: str = Field(..., description="存储文件名")
    file_path: str = Field(..., description="存储路径")
    file_size: int = Field(..., description="文件大小(字节)")
    mime_type: str = Field(..., description="MIME类型")
    extension: str = Field(..., description="扩展名")
    storage_platform: str = Field(..., description="存储平台")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="上传时间")


class SysFileListResponse(BaseRespEntity):
    """文件列表响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="文件ID")
    original_name: str = Field(..., description="原始文件名")
    stored_name: str = Field(..., description="存储文件名")
    file_path: str = Field(..., description="存储路径")
    file_size: int = Field(..., description="文件大小(字节)")
    mime_type: str = Field(..., description="MIME类型")
    extension: str = Field(..., description="扩展名")
    storage_platform: str = Field(..., description="存储平台")
    created_by: int = Field(..., description="上传者用户ID")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="上传时间")
