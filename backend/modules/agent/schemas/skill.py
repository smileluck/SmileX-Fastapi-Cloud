#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field

from modules.common.schemas.base import BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class SkillFileItem(BaseReqEntity):
    """技能附属文件（整体提交，无独立接口）"""

    path: str = Field(..., description="相对路径（禁绝对路径与 ..）", min_length=1, max_length=128)
    content: str = Field(..., description="文件文本内容", max_length=32768)


class SkillQueryParams(PageRequest):
    """技能查询参数"""

    name: Optional[str] = Field(None, description="技能名称，支持模糊查询")
    code: Optional[str] = Field(None, description="技能编码，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class SkillCreate(BaseReqEntity):
    """技能创建请求（主指令 + 附属文件整体提交）"""

    name: str = Field(..., description="技能名称", min_length=1, max_length=20)
    code: str = Field(..., description="技能编码", min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    description: Optional[str] = Field(None, description="技能描述", max_length=200)
    instruction: str = Field(..., description="主指令（Markdown 提示词）", min_length=1, max_length=8000)
    files: list[SkillFileItem] = Field(default_factory=list, description="附属文件列表", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class SkillUpdate(BaseReqEntity):
    """技能更新请求（编码不可改；全部字段留空=保持原值，files 空数组=清空）"""

    name: Optional[str] = Field(None, description="技能名称", min_length=1, max_length=20)
    description: Optional[str] = Field(None, description="技能描述", max_length=200)
    instruction: Optional[str] = Field(None, description="主指令", min_length=1, max_length=8000)
    files: Optional[list[SkillFileItem]] = Field(None, description="附属文件列表（None=不变，[]=清空）", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class SkillFileResponseData(BaseRespEntity):
    """技能附属文件响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="文件 ID")
    path: str = Field(..., description="相对路径")
    content: str = Field(..., description="文件内容")
    file_size: int = Field(..., description="文件大小（字节）")


class SkillResponseData(BaseRespEntity):
    """技能响应（含附属文件）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="技能 ID")
    name: str = Field(..., description="技能名称")
    code: str = Field(..., description="技能编码")
    description: Optional[str] = Field(None, description="技能描述")
    instruction: str = Field(..., description="主指令")
    files: list[SkillFileResponseData] = Field(default_factory=list, description="附属文件列表")
    file_count: int = Field(0, description="附属文件数量")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")
