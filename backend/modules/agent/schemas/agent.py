#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field, field_validator

from modules.common.schemas.base import BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


def _parse_json_str_list(v):
    """ORM JSON 文本列（str）→ list[str]"""
    from modules.agent.utils import load_str_list

    if isinstance(v, str):
        return load_str_list(v)
    return v or []


class AgentQueryParams(PageRequest):
    """智能体查询参数"""

    name: Optional[str] = Field(None, description="智能体名称，支持模糊查询")
    code: Optional[str] = Field(None, description="智能体编码，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentCreate(BaseReqEntity):
    """智能体创建请求"""

    name: str = Field(..., description="智能体名称", min_length=1, max_length=20)
    code: str = Field(..., description="智能体编码", min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    model_id: int = Field(..., description="绑定模型 ID", gt=0)
    system_prompt: Optional[str] = Field(None, description="系统提示词", max_length=4000)
    temperature: float = Field(0.0, description="温度（0-2，0=未设置）", ge=0, le=2)
    top_p: float = Field(0.0, description="Top-P（0-1，0=未设置）", ge=0, le=1)
    max_tokens: int = Field(0, description="单次最大输出（token，0=上游默认）", ge=0, le=131072)
    tools: list[str] = Field(default_factory=list, description="绑定的工具名列表（内置名或 mcp:<code>:<tool>）", max_length=10)
    skills: list[str] = Field(default_factory=list, description="绑定的技能编码列表", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class AgentUpdate(BaseReqEntity):
    """智能体更新请求（编码不可改；全部字段留空=保持原值，空数组=清空）"""

    name: Optional[str] = Field(None, description="智能体名称", min_length=1, max_length=20)
    model_id: Optional[int] = Field(None, description="绑定模型 ID", gt=0)
    system_prompt: Optional[str] = Field(None, description="系统提示词", max_length=4000)
    temperature: Optional[float] = Field(None, description="温度", ge=0, le=2)
    top_p: Optional[float] = Field(None, description="Top-P", ge=0, le=1)
    max_tokens: Optional[int] = Field(None, description="单次最大输出（token）", ge=0, le=131072)
    tools: Optional[list[str]] = Field(None, description="绑定的工具名列表（None=不变，[] =清空）", max_length=10)
    skills: Optional[list[str]] = Field(None, description="绑定的技能编码列表（None=不变，[]=清空）", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentResponseData(BaseRespEntity):
    """智能体响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="智能体 ID")
    name: str = Field(..., description="智能体名称")
    code: str = Field(..., description="智能体编码")
    model_id: int = Field(..., description="绑定模型 ID")
    model_name: Optional[str] = Field(None, description="绑定模型名称（联查填充）")
    provider_name: Optional[str] = Field(None, description="模型所属供应商名称（联查填充）")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    temperature: float = Field(..., description="温度")
    top_p: float = Field(..., description="Top-P")
    max_tokens: int = Field(..., description="单次最大输出")
    tools: list[str] = Field(default_factory=list, description="绑定的工具名列表")
    skills: list[str] = Field(default_factory=list, description="绑定的技能编码列表")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")

    @field_validator("tools", "skills", mode="before")
    @classmethod
    def _parse_tool_columns(cls, v):
        return _parse_json_str_list(v)


class ToolGroupItem(BaseReqEntity):
    """可绑定工具分组项（Agent 表单数据源）"""

    name: str = Field(..., description="工具名（内置名或 mcp:<code>:<tool>）")
    description: str = Field("", description="工具描述")


class ToolGroup(BaseReqEntity):
    """工具分组：内置 / 各 MCP 服务"""

    group: str = Field(..., description="分组标识：builtin 或 MCP 服务编码")
    label: str = Field(..., description="分组展示名")
    tools: list[ToolGroupItem] = Field(default_factory=list, description="分组内工具列表")
