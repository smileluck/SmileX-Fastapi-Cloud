#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 管理 Schema
"""
from typing import Optional, List, Any
from pydantic import Field

from modules.common.schemas.base import BaseEntity


class McpToolParamSchema(BaseEntity):
    name: str = Field(..., description="参数名称")
    description: str = Field("", description="参数描述")
    type: str = Field("string", description="参数类型: string/number/boolean/array/object")
    required: bool = Field(True, description="是否必填")
    default: Optional[str] = Field(None, description="默认值")


class McpToolResponseSchema(BaseEntity):
    key: str = Field(..., description="字段名")
    type: str = Field("string", description="字段类型")
    description: str = Field("", description="字段描述")


class AutoMcpToolCreate(BaseEntity):
    name: str = Field(..., description="工具名称", min_length=1, max_length=100)
    description: str = Field(..., description="工具描述")
    params: List[McpToolParamSchema] = Field(default_factory=list, description="工具参数列表")
    response: List[McpToolResponseSchema] = Field(default_factory=list, description="响应字段列表")


class McpToolTestRequest(BaseEntity):
    tool_name: str = Field(..., description="要测试的工具名称")
    arguments: dict = Field(default_factory=dict, description="工具调用参数")


class McpToolInfo(BaseEntity):
    name: str = Field(..., description="工具名称")
    description: str = Field("", description="工具描述")
    params: List[McpToolParamSchema] = Field(default_factory=list, description="参数列表")
    file_path: Optional[str] = Field(None, description="工具文件路径")


class McpServerStatusResponse(BaseEntity):
    running: bool = Field(False, description="是否运行中")
    status: str = Field("stopped", description="状态: running/stopped/starting")
    pid: Optional[int] = Field(None, description="进程PID")
    host: str = Field("127.0.0.1", description="服务地址")
    port: int = Field(9000, description="服务端口")
    started_at: Optional[str] = Field(None, description="启动时间")
