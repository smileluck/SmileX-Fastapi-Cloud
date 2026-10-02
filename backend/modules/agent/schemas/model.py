#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field

from modules.common.schemas.base import BaseEntity, BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class AgentModelQueryParams(PageRequest):
    """模型查询参数"""

    provider_id: Optional[int] = Field(None, description="供应商 ID 精确过滤")
    name: Optional[str] = Field(None, description="模型名称，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentModelCreate(BaseReqEntity):
    """模型创建请求"""

    provider_id: int = Field(..., description="所属供应商 ID", gt=0)
    name: str = Field(..., description="模型名称（上游模型 ID）", min_length=1, max_length=128)
    display_name: Optional[str] = Field(None, description="展示名称", max_length=64)
    context_window: int = Field(0, description="上下文窗口（token，0=未知）", ge=0)
    max_output: int = Field(0, description="单次最大输出（token，0=上游默认）", ge=0)
    supports_tools: bool = Field(False, description="是否支持工具调用")
    input_price: float = Field(0.0, description="每千 token 输入单价（0=未设置）", ge=0)
    output_price: float = Field(0.0, description="每千 token 输出单价（0=未设置）", ge=0)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class AgentModelUpdate(BaseReqEntity):
    """模型更新请求（供应商不可变更；全部字段留空=保持原值）"""

    display_name: Optional[str] = Field(None, description="展示名称", max_length=64)
    context_window: Optional[int] = Field(None, description="上下文窗口（token）", ge=0)
    max_output: Optional[int] = Field(None, description="单次最大输出（token）", ge=0)
    supports_tools: Optional[bool] = Field(None, description="是否支持工具调用")
    input_price: Optional[float] = Field(None, description="每千 token 输入单价", ge=0)
    output_price: Optional[float] = Field(None, description="每千 token 输出单价", ge=0)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentModelResponseData(BaseRespEntity):
    """模型响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="模型 ID")
    provider_id: int = Field(..., description="所属供应商 ID")
    provider_name: Optional[str] = Field(None, description="所属供应商名称（联查填充）")
    name: str = Field(..., description="模型名称")
    display_name: Optional[str] = Field(None, description="展示名称")
    context_window: int = Field(..., description="上下文窗口")
    max_output: int = Field(..., description="单次最大输出")
    supports_tools: bool = Field(..., description="是否支持工具调用")
    input_price: float = Field(..., description="输入单价")
    output_price: float = Field(..., description="输出单价")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")


class AgentModelBrief(BaseEntity):
    """模型简要信息（Agent 表单下拉）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="模型 ID")
    provider_id: int = Field(..., description="供应商 ID")
    name: str = Field(..., description="模型名称")
    display_name: Optional[str] = Field(None, description="展示名称")
    status: bool = Field(..., description="状态")
