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


class AgentProviderQueryParams(PageRequest):
    """模型供应商查询参数"""

    name: Optional[str] = Field(None, description="供应商名称，支持模糊查询")
    code: Optional[str] = Field(None, description="供应商编码，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentProviderCreate(BaseReqEntity):
    """模型供应商创建请求（api_key 留空=不配置，适配本地无鉴权服务）"""

    name: str = Field(..., description="供应商名称", min_length=1, max_length=20)
    code: str = Field(..., description="供应商编码", min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    base_url: str = Field(..., description="OpenAI 兼容 API 基础地址", min_length=1, max_length=255)
    api_key: Optional[str] = Field(None, description="API Key（留空=不配置；仅写入链路出现明文）", max_length=512)
    protocol: str = Field("openai", description="调用协议", max_length=32)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class AgentProviderUpdate(BaseReqEntity):
    """模型供应商更新请求（api_key 留空=保持原密钥不变）"""

    name: Optional[str] = Field(None, description="供应商名称", min_length=1, max_length=20)
    base_url: Optional[str] = Field(None, description="OpenAI 兼容 API 基础地址", min_length=1, max_length=255)
    api_key: Optional[str] = Field(None, description="新 API Key（留空=保持不变）", max_length=512)
    protocol: Optional[str] = Field(None, description="调用协议", max_length=32)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class AgentProviderResponseData(BaseRespEntity):
    """模型供应商响应（api_key 仅回显掩码，永不返回明文/密文）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="供应商 ID")
    name: str = Field(..., description="供应商名称")
    code: str = Field(..., description="供应商编码")
    base_url: str = Field(..., description="OpenAI 兼容 API 基础地址")
    api_key_mask: Optional[str] = Field(None, description="API Key 掩码")
    has_api_key: bool = Field(False, description="是否已配置 API Key")
    protocol: str = Field(..., description="调用协议")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")


class AgentProviderTestRequest(BaseEntity):
    """供应商连通测试请求"""

    model_id: int = Field(0, description="测试使用的模型 ID（0=取该供应商下首个启用模型）")


class AgentConnectTestResponse(BaseEntity):
    """连通测试结果（供应商/模型共用）"""

    ok: bool = Field(..., description="是否成功")
    content: Optional[str] = Field(None, description="模型回复内容")
    model: Optional[str] = Field(None, description="实际使用的模型")
    latency_ms: int = Field(0, description="耗时（毫秒）")
    prompt_tokens: int = Field(0, description="输入 token 数")
    completion_tokens: int = Field(0, description="输出 token 数")
    error: Optional[str] = Field(None, description="失败原因")


class AgentRemoteModelsResponse(BaseEntity):
    """上游模型列表响应"""

    models: list[str] = Field(default_factory=list, description="上游模型 ID 列表（升序去重）")
