#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Function calling 工具注册表

- Tool 抽象：Def() 输出 OpenAI functions 元信息，Execute(args_json) 执行并返回文本
- 注册表：进程内单例，重名/空名跳过注册；MCP 远程工具在对话编排时动态合入
"""
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import psutil

# 本地工具执行超时（秒）；MCP 远程工具超时见 mcp_manager
TOOL_EXEC_TIMEOUT = 10.0


@dataclass
class ToolFunc:
    """下发上游的工具元信息"""

    name: str
    description: str
    parameters: dict[str, Any]


@dataclass
class ToolDef:
    """OpenAI functions 格式的工具定义"""

    type: str = "function"
    function: Optional[ToolFunc] = None

    def to_wire(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "function": {
                "name": self.function.name,
                "description": self.function.description,
                "parameters": self.function.parameters,
            },
        }


class Tool(ABC):
    """本地工具抽象基类"""

    @abstractmethod
    def def_(self) -> ToolFunc:
        """工具元信息（名称/描述/参数 JSON Schema）"""

    @abstractmethod
    async def execute(self, args: str) -> str:
        """执行工具调用；args 为上游给出的原始 JSON 字符串"""


class NowTool(Tool):
    """内置工具：服务器当前时间"""

    def def_(self) -> ToolFunc:
        return ToolFunc(
            name="now",
            description="获取服务器当前时间（含时区）",
            parameters={"type": "object", "properties": {}},
        )

    async def execute(self, args: str) -> str:
        from database.utils.timezone import timezone

        return timezone.now().strftime("%Y-%m-%d %H:%M:%S %z")


class ServerStatusTool(Tool):
    """内置工具：服务器运行状态摘要（CPU / 内存 / 磁盘）"""

    def def_(self) -> ToolFunc:
        return ToolFunc(
            name="get_server_status",
            description="获取服务器运行状态：CPU 占用率、内存占用率、各分区磁盘占用",
            parameters={"type": "object", "properties": {}},
        )

    async def execute(self, args: str) -> str:
        mem = psutil.virtual_memory()
        parts = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                parts.append(
                    {"mount": part.mountpoint, "percent": round(usage.percent, 1)}
                )
            except (PermissionError, OSError):
                continue
        return json.dumps(
            {
                "cpu_percent": round(psutil.cpu_percent(interval=1), 1),
                "mem_percent": round(mem.percent, 1),
                "mem_used_gb": round(mem.used / 1024**3, 1),
                "mem_total_gb": round(mem.total / 1024**3, 1),
                "disks": parts,
            },
            ensure_ascii=False,
        )


class ToolRegistry:
    """本地工具注册表"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}
        for tool in (NowTool(), ServerStatusTool()):
            self.register(tool)

    def register(self, tool: Tool) -> None:
        """注册工具；重名或空名跳过"""
        name = tool.def_().name
        if not name or name in self._tools:
            return
        self._tools[name] = tool

    def names(self) -> list[str]:
        """全部已注册工具名（排序稳定）"""
        return sorted(self._tools)

    def defs(self) -> list[dict[str, Any]]:
        """全部工具的 OpenAI functions 定义"""
        return [
            ToolDef(function=self._tools[name].def_()).to_wire()
            for name in sorted(self._tools)
        ]

    def find(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)


# 进程内全局注册表
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """获取进程内工具注册表单例"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
