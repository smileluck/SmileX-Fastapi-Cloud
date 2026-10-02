#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field, field_validator

from modules.common.schemas.base import BaseEntity, BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class McpHeaderItem(BaseEntity):
    """自定义请求头项"""

    key: str = Field(..., description="请求头名称", min_length=1, max_length=64)
    value: str = Field("", description="请求头值", max_length=512)


class McpServerQueryParams(PageRequest):
    """MCP 服务查询参数"""

    name: Optional[str] = Field(None, description="服务名称，支持模糊查询")
    code: Optional[str] = Field(None, description="服务编码，支持模糊查询")
    transport: Optional[str] = Field(None, description="传输协议：streamable_http / sse")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class McpServerCreate(BaseReqEntity):
    """MCP 服务创建请求"""

    name: str = Field(..., description="服务名称", min_length=1, max_length=20)
    code: str = Field(..., description="服务编码（禁用冒号）", min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    transport: str = Field("streamable_http", description="传输协议：streamable_http / sse")
    base_url: str = Field(..., description="消息端点 / 事件流端点地址", min_length=1, max_length=255)
    token: Optional[str] = Field(None, description="鉴权 Token（留空=不鉴权；仅写入链路出现明文）", max_length=512)
    headers: list[McpHeaderItem] = Field(default_factory=list, description="自定义请求头", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class McpServerUpdate(BaseReqEntity):
    """MCP 服务更新请求（编码不可改；token 留空=保持不变）"""

    name: Optional[str] = Field(None, description="服务名称", min_length=1, max_length=20)
    transport: Optional[str] = Field(None, description="传输协议：streamable_http / sse")
    base_url: Optional[str] = Field(None, description="端点地址", min_length=1, max_length=255)
    token: Optional[str] = Field(None, description="新鉴权 Token（留空=保持不变）", max_length=512)
    headers: Optional[list[McpHeaderItem]] = Field(None, description="自定义请求头（None=不变，[]=清空）", max_length=10)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class McpServerResponseData(BaseRespEntity):
    """MCP 服务响应（token 仅回显掩码）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="服务 ID")
    name: str = Field(..., description="服务名称")
    code: str = Field(..., description="服务编码")
    transport: str = Field(..., description="传输协议")
    base_url: str = Field(..., description="端点地址")
    token_mask: Optional[str] = Field(None, description="Token 掩码")
    has_token: bool = Field(False, description="是否已配置 Token")
    headers: list[McpHeaderItem] = Field(default_factory=list, description="自定义请求头")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")

    @field_validator("headers", mode="before")
    @classmethod
    def _parse_headers_column(cls, v):
        """ORM JSON 文本列（str）→ 请求头列表"""
        if isinstance(v, str):
            try:
                items = json.loads(v) if v else []
            except json.JSONDecodeError:
                items = []
            return [
                {"key": item.get("key", ""), "value": item.get("value", "")}
                for item in items
                if isinstance(item, dict) and item.get("key")
            ]
        return v or []


class McpServerTestResponse(BaseEntity):
    """MCP 服务连通测试结果（失败也是有效结果，不抛错）"""

    ok: bool = Field(..., description="是否成功")
    server_name: Optional[str] = Field(None, description="远端服务器名称")
    server_version: Optional[str] = Field(None, description="远端服务器版本")
    protocol_version: Optional[str] = Field(None, description="协商的协议版本")
    tool_count: Optional[int] = Field(None, description="发现的工具数量")
    latency_ms: int = Field(0, description="耗时（毫秒）")
    error: Optional[str] = Field(None, description="失败原因")
