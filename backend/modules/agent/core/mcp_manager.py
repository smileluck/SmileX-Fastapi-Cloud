#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 连接管理器（进程内单例）

- 活跃会话池：空闲 10 分钟过期，get 时惰性清理；配置变更 drop 失效
- 工具清单缓存：TTL 5 分钟；Agent 表单分组与对话前工具定义拉取共用
- 工具调用：tools/call，参数须为 JSON 对象，60s 超时
"""
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.sys.mcp_server import SysMcpServer
from modules.agent.core import crypto as agent_crypto
from modules.agent.core.mcp_client import (
    MCP_CALL_TIMEOUT,
    McpError,
    McpServerInfo,
    McpToolInfo,
    _McpClientBase,
    _parse_headers,
    handshake_client,
)

logger = logging.getLogger(__name__)

# 活跃会话空闲过期（秒）
SESSION_IDLE_TTL = 600.0
# 工具清单缓存 TTL（秒）
TOOLS_CACHE_TTL = 300.0


@dataclass
class _SessionEntry:
    client: _McpClientBase
    last_used: float = field(default_factory=time.monotonic)


@dataclass
class _ToolsCacheEntry:
    tools: list[McpToolInfo]
    server_info: McpServerInfo
    expires_at: float


class McpManager:
    """MCP 会话池与工具缓存（进程内单例）"""

    def __init__(self) -> None:
        self._sessions: dict[str, _SessionEntry] = {}
        self._tools_cache: dict[str, _ToolsCacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def drop(self, code: str) -> None:
        """失效指定服务的会话与缓存（配置变更/删除时调用）"""
        entry = self._sessions.pop(code, None)
        if entry is not None:
            # 关闭交给事件循环，不阻塞调用方
            asyncio.ensure_future(entry.client.close())
        self._tools_cache.pop(code, None)

    def drop_all(self) -> None:
        for code in list(self._sessions):
            self.drop(code)

    async def _session_for(self, server: SysMcpServer) -> _McpClientBase:
        """取或建指定服务的活跃会话；空闲过期后重建"""
        self._cleanup_idle()
        entry = self._sessions.get(server.code)
        if entry is not None:
            entry.last_used = time.monotonic()
            return entry.client

        lock = self._locks.setdefault(server.code, asyncio.Lock())
        async with lock:
            if server.code in self._sessions:
                entry = self._sessions[server.code]
                entry.last_used = time.monotonic()
                return entry.client

            token = ""
            if server.token_enc:
                token = agent_crypto.decrypt_secret(server.token_enc, agent_crypto.MCP_DOMAIN)
            client = await handshake_client(
                transport=server.transport,
                base_url=server.base_url,
                token=token,
                headers=_parse_headers(server.headers),
            )
            self._sessions[server.code] = _SessionEntry(client=client)
            return client

    def _cleanup_idle(self) -> None:
        """惰性清理空闲超时的会话"""
        now = time.monotonic()
        expired = [
            code for code, entry in self._sessions.items() if now - entry.last_used > SESSION_IDLE_TTL
        ]
        for code in expired:
            entry = self._sessions.pop(code)
            asyncio.ensure_future(entry.client.close())
            self._tools_cache.pop(code, None)

    async def get_tools(self, db: AsyncSession, code: str) -> tuple[list[McpToolInfo], McpServerInfo]:
        """获取指定服务的工具清单（带 5 分钟缓存）；服务不存在/禁用抛 McpError"""
        cached = self._tools_cache.get(code)
        if cached is not None and cached.expires_at > time.monotonic():
            return cached.tools, cached.server_info

        result = await db.execute(
            select(SysMcpServer).where(
                SysMcpServer.code == code, SysMcpServer.deleted_at.is_(None)
            )
        )
        server = result.scalar_one_or_none()
        if server is None:
            raise McpError(f"MCP 服务 {code} 不存在")
        if not server.status:
            raise McpError(f"MCP 服务 {code} 已禁用")

        client = await self._session_for(server)
        tools = await client.tools_list()
        self._tools_cache[code] = _ToolsCacheEntry(
            tools=tools,
            server_info=client.server_info,
            expires_at=time.monotonic() + TOOLS_CACHE_TTL,
        )
        return tools, client.server_info

    async def call_tool(self, db: AsyncSession, code: str, tool: str, arguments_json: str) -> str:
        """调用远端工具；arguments_json 须为 JSON 对象文本，60s 超时"""
        try:
            arguments = json.loads(arguments_json) if arguments_json else {}
        except json.JSONDecodeError as exc:
            raise McpError("工具调用参数不是有效 JSON") from exc
        if not isinstance(arguments, dict):
            raise McpError("工具调用参数必须是 JSON 对象")

        client = await self._session_for_cached(code, db)
        try:
            return await asyncio.wait_for(client.call_tool(tool, arguments), timeout=MCP_CALL_TIMEOUT)
        except asyncio.TimeoutError as exc:
            raise McpError(f"工具执行超时（>{MCP_CALL_TIMEOUT:.0f}s）") from exc

    async def _session_for_cached(self, code: str, db: AsyncSession) -> _McpClientBase:
        """按 code 取会话（优先复用，未命中查库重建）"""
        self._cleanup_idle()
        entry = self._sessions.get(code)
        if entry is not None:
            entry.last_used = time.monotonic()
            return entry.client

        result = await db.execute(
            select(SysMcpServer).where(
                SysMcpServer.code == code, SysMcpServer.deleted_at.is_(None)
            )
        )
        server = result.scalar_one_or_none()
        if server is None:
            raise McpError(f"MCP 服务 {code} 不存在")
        return await self._session_for(server)

    async def test_server(self, server: SysMcpServer) -> dict[str, Any]:
        """
        连通测试：全新客户端握手 + tools/list，返回测试结果（失败也是有效结果）。
        不复用会话池；成功后顺手刷新工具缓存。
        """
        token = ""
        if server.token_enc:
            token = agent_crypto.decrypt_secret(server.token_enc, agent_crypto.MCP_DOMAIN)
        started = time.monotonic()
        payload: dict[str, Any] = {"ok": False}
        try:
            client = await handshake_client(
                transport=server.transport,
                base_url=server.base_url,
                token=token,
                headers=_parse_headers(server.headers),
            )
            try:
                tools = await client.tools_list()
                payload.update(
                    ok=True,
                    server_name=client.server_info.name,
                    server_version=client.server_info.version,
                    protocol_version=client.protocol_version,
                    tool_count=len(tools),
                )
                self._tools_cache[server.code] = _ToolsCacheEntry(
                    tools=tools,
                    server_info=client.server_info,
                    expires_at=time.monotonic() + TOOLS_CACHE_TTL,
                )
            finally:
                await client.close()
        except Exception as exc:
            payload["error"] = str(exc)[:300]
        payload["latency_ms"] = int((time.monotonic() - started) * 1000)
        return payload


_manager: Optional[McpManager] = None


def get_mcp_manager() -> McpManager:
    """获取进程内 MCP 管理器单例"""
    global _manager
    if _manager is None:
        _manager = McpManager()
    return _manager
