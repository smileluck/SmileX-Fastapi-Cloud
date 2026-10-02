#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自研 MCP 客户端（JSON-RPC 2.0，httpx 实现，零外部 SDK 依赖）

支持两种传输：
- streamable_http（2025-03-26 规范）：单端点 POST，Mcp-Session-Id 会话，
  响应为 JSON 或 text/event-stream（取首帧按 id 匹配）
- sse（旧版 2024-11-05 规范）：GET 事件流长连接，经 endpoint 事件协商消息 POST 端点，
  请求注册 pending future，读循环按 id 路由

握手流程：initialize → notifications/initialized → tools/list / tools/call
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import httpx

logger = logging.getLogger(__name__)

# 建连/请求超时（秒）
MCP_CONNECT_TIMEOUT = 10.0
# 整体握手超时（秒）
MCP_HANDSHAKE_TIMEOUT = 20.0
# 单次工具调用超时（秒）
MCP_CALL_TIMEOUT = 60.0
PROTOCOL_VERSION = "2025-03-26"
CLIENT_INFO = {"name": "smilex-fastapi-cloud", "version": "1.0.0"}

# 自定义头不可覆盖的协议保护头（小写）
PROTECTED_HEADERS = {
    "authorization",
    "content-type",
    "accept",
    "content-length",
    "host",
    "mcp-session-id",
    "cookie",
}


class McpError(Exception):
    """MCP 调用错误（超时/连接失败/协议错误/工具业务失败）"""


@dataclass
class McpToolInfo:
    """远端工具元信息（对外 snake_case）"""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_wire(cls, raw: dict[str, Any]) -> "McpToolInfo":
        return cls(
            name=raw.get("name", ""),
            description=raw.get("description") or "",
            input_schema=raw.get("inputSchema") or {"type": "object"},
        )


@dataclass
class McpServerInfo:
    """initialize 响应中的服务器信息"""

    name: str = ""
    version: str = ""


def _parse_headers(headers_json: Optional[str]) -> dict[str, str]:
    """解析自定义请求头 JSON 数组 [{"key","value"}]，过滤协议保护头"""
    if not headers_json:
        return {}
    try:
        items = json.loads(headers_json)
    except json.JSONDecodeError:
        return {}
    result: dict[str, str] = {}
    if isinstance(items, list):
        for item in items:
            if not isinstance(item, dict):
                continue
            key, value = str(item.get("key", "")).strip(), str(item.get("value", ""))
            if key and key.lower() not in PROTECTED_HEADERS:
                result[key] = value
    return result


def _rpc_request(req_id: int, method: str, params: Optional[dict] = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        payload["params"] = params
    return payload


def _rpc_notification(method: str, params: Optional[dict] = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        payload["params"] = params
    return payload


class _McpClientBase:
    """MCP 客户端基类：维护请求 id 与会话生命周期"""

    def __init__(self, base_url: str, token: str = "", headers: Optional[dict] = None):
        self.base_url = base_url
        self.auth_headers: dict[str, str] = {}
        if token:
            self.auth_headers["Authorization"] = f"Bearer {token}"
        self.custom_headers = headers or {}
        self._next_id = 1
        self.server_info = McpServerInfo()
        self.protocol_version = ""
        self._initialized = False

    def _base_headers(self, accept: str) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": accept,
            **self.auth_headers,
            **self.custom_headers,
        }

    async def initialize(self) -> McpServerInfo:
        """执行 initialize + notifications/initialized 握手"""
        req_id = self._next_id
        self._next_id += 1
        result = await self._request(
            req_id,
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": CLIENT_INFO,
            },
        )
        info = result.get("serverInfo") or {}
        self.server_info = McpServerInfo(
            name=info.get("name", ""), version=info.get("version", "")
        )
        self.protocol_version = result.get("protocolVersion", PROTOCOL_VERSION)
        await self._notify("notifications/initialized")
        self._initialized = True
        return self.server_info

    async def tools_list(self) -> list[McpToolInfo]:
        req_id = self._next_id
        self._next_id += 1
        result = await self._request(req_id, "tools/list", {})
        return [McpToolInfo.from_wire(item) for item in (result.get("tools") or [])]

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """调用远端工具；content 文本拼接，isError=true 视为业务失败"""
        req_id = self._next_id
        self._next_id += 1
        result = await self._request(
            req_id, "tools/call", {"name": name, "arguments": arguments}
        )
        if result.get("isError"):
            texts = [
                item.get("text", "") for item in (result.get("content") or []) if item.get("type") == "text"
            ]
            raise McpError(f"工具执行失败: {''.join(texts) or 'unknown tool error'}")
        texts = [
            item.get("text", "") for item in (result.get("content") or []) if item.get("type") == "text"
        ]
        return "".join(texts)

    async def _request(self, req_id: int, method: str, params: Optional[dict]) -> dict[str, Any]:
        raise NotImplementedError

    async def _notify(self, method: str, params: Optional[dict] = None) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        pass

    async def _extract_result(self, data: dict[str, Any]) -> dict[str, Any]:
        if "error" in data and data["error"]:
            err = data["error"]
            raise McpError(f"MCP 错误 {err.get('code')}: {err.get('message')}")
        return data.get("result") or {}


class StreamableHttpClient(_McpClientBase):
    """streamable_http 传输（2025-03-26 规范）"""

    def __init__(self, base_url: str, token: str = "", headers: Optional[dict] = None):
        super().__init__(base_url, token, headers)
        self.session_id = ""
        self._client: Optional[httpx.AsyncClient] = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(MCP_HANDSHAKE_TIMEOUT, connect=MCP_CONNECT_TIMEOUT)
            )
        return self._client

    async def _post(self, payload: dict[str, Any]) -> httpx.Response:
        headers = self._base_headers("application/json, text/event-stream")
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return await self._ensure_client().post(self.base_url, json=payload, headers=headers)

    async def _request(self, req_id: int, method: str, params: Optional[dict]) -> dict[str, Any]:
        try:
            resp = await self._post(_rpc_request(req_id, method, params))
        except httpx.HTTPError as exc:
            raise McpError(f"连接 MCP 服务器失败: {exc}") from exc
        session_id = resp.headers.get("Mcp-Session-Id")
        if session_id:
            self.session_id = session_id
        if resp.status_code == 202:
            raise McpError("服务端将请求当作通知处理（202），预期响应缺失")
        if resp.status_code != 200:
            body = resp.text[:300]
            raise McpError(f"MCP 服务器返回 HTTP {resp.status_code}: {body}")
        content_type = resp.headers.get("Content-Type", "")
        if "text/event-stream" in content_type:
            data = _match_sse_frame(resp.text, req_id)
            if data is None:
                raise McpError("SSE 响应中未找到匹配请求 id 的帧")
        else:
            try:
                data = resp.json()
            except json.JSONDecodeError as exc:
                raise McpError("MCP 服务器响应不是有效 JSON") from exc
        return await self._extract_result(data)

    async def _notify(self, method: str, params: Optional[dict] = None) -> None:
        try:
            resp = await self._post(_rpc_notification(method, params))
        except httpx.HTTPError as exc:
            raise McpError(f"连接 MCP 服务器失败: {exc}") from exc
        if resp.status_code not in (200, 202):
            raise McpError(f"通知发送失败 HTTP {resp.status_code}")

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


class LegacySseClient(_McpClientBase):
    """旧版 SSE 传输（2024-11-05 规范）：事件流 + 协商消息端点"""

    def __init__(self, base_url: str, token: str = "", headers: Optional[dict] = None):
        super().__init__(base_url, token, headers)
        self._message_url = ""
        self._pending: dict[int, asyncio.Future] = {}
        self._reader_task: Optional[asyncio.Task] = None
        self._client: Optional[httpx.AsyncClient] = None
        self._closed = False

    def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(None, connect=MCP_CONNECT_TIMEOUT)
            )
        return self._client

    async def connect(self) -> None:
        """建立事件流并等待 endpoint 事件协商消息端点"""
        endpoint_future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
        self._reader_task = asyncio.create_task(self._read_loop(endpoint_future))
        try:
            self._message_url = await asyncio.wait_for(endpoint_future, timeout=MCP_HANDSHAKE_TIMEOUT)
        except asyncio.TimeoutError as exc:
            await self.close()
            raise McpError("等待 SSE endpoint 事件超时") from exc

    async def _read_loop(self, endpoint_future: "asyncio.Future[str]") -> None:
        """事件流读循环：endpoint 事件取消息端点；data 帧按 id 路由响应"""
        try:
            async with self._ensure_client().stream(
                "GET",
                self.base_url,
                headers=self._base_headers("text/event-stream"),
            ) as resp:
                if resp.status_code != 200:
                    body = (await resp.aread()).decode("utf-8", errors="replace")[:300]
                    raise McpError(f"MCP 事件流建立失败 HTTP {resp.status_code}: {body}")
                event_name = ""
                async for raw_line in resp.aiter_lines():
                    if self._closed:
                        break
                    line = raw_line.rstrip("\r")
                    if line.startswith("event:"):
                        event_name = line[6:].strip()
                    elif line.startswith("data:"):
                        data_text = line[5:].strip()
                        if event_name == "endpoint" and not endpoint_future.done():
                            resolved = self._resolve_endpoint(data_text)
                            if resolved:
                                endpoint_future.set_result(resolved)
                        else:
                            self._dispatch_response(data_text)
                        event_name = ""
        except McpError:
            if not endpoint_future.done():
                endpoint_future.set_exception(asyncio.CancelledError())
            self._fail_all_pending()
        except Exception as exc:
            if not endpoint_future.done():
                endpoint_future.set_exception(McpError(f"MCP 事件流断开: {exc}"))
            self._fail_all_pending()

    def _resolve_endpoint(self, endpoint: str) -> str:
        """事件流端点可能返回相对路径，基于事件流 URL 解析为绝对地址"""
        if not endpoint:
            return ""
        parsed = urlparse(endpoint)
        if parsed.scheme in ("http", "https"):
            return endpoint
        return urljoin(self.base_url, endpoint)

    def _dispatch_response(self, data_text: str) -> None:
        try:
            data = json.loads(data_text)
        except json.JSONDecodeError:
            return
        req_id = data.get("id")
        future = self._pending.pop(req_id, None) if req_id is not None else None
        if future is not None and not future.done():
            if data.get("error"):
                err = data["error"]
                future.set_exception(McpError(f"MCP 错误 {err.get('code')}: {err.get('message')}"))
            else:
                future.set_result(data.get("result") or {})

    def _fail_all_pending(self) -> None:
        for future in self._pending.values():
            if not future.done():
                future.set_exception(McpError("MCP 事件流已断开"))
        self._pending.clear()

    async def _request(self, req_id: int, method: str, params: Optional[dict]) -> dict[str, Any]:
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        self._pending[req_id] = future
        try:
            resp = await self._ensure_client().post(
                self._message_url,
                json=_rpc_request(req_id, method, params),
                headers=self._base_headers("text/event-stream"),
            )
            if resp.status_code not in (200, 202):
                raise McpError(f"MCP 消息端点返回 HTTP {resp.status_code}")
            result = await asyncio.wait_for(future, timeout=MCP_HANDSHAKE_TIMEOUT)
            return await self._extract_result({"result": result})
        except (httpx.HTTPError, asyncio.TimeoutError) as exc:
            self._pending.pop(req_id, None)
            raise McpError(f"MCP 请求失败: {exc}") from exc

    async def _notify(self, method: str, params: Optional[dict] = None) -> None:
        try:
            resp = await self._ensure_client().post(
                self._message_url,
                json=_rpc_notification(method, params),
                headers=self._base_headers("text/event-stream"),
            )
            if resp.status_code not in (200, 202):
                raise McpError(f"通知发送失败 HTTP {resp.status_code}")
        except httpx.HTTPError as exc:
            raise McpError(f"MCP 请求失败: {exc}") from exc

    async def close(self) -> None:
        self._closed = True
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except (asyncio.CancelledError, Exception):
                pass
            self._reader_task = None
        self._fail_all_pending()
        if self._client is not None:
            await self._client.aclose()
            self._client = None


def _match_sse_frame(text: str, req_id: int) -> Optional[dict[str, Any]]:
    """从 streamable_http 的 SSE 响应体中取第一个匹配请求 id 的 data 帧"""
    data_text = ""
    for line in text.splitlines():
        if line.startswith("data:"):
            data_text = line[5:].strip()
            break
    if not data_text:
        return None
    try:
        data = json.loads(data_text)
    except json.JSONDecodeError:
        return None
    if data.get("id") != req_id:
        return None
    return data


async def handshake_client(
    transport: str, base_url: str, token: str = "", headers: Optional[dict] = None
) -> _McpClientBase:
    """按传输类型创建客户端并完成握手；sse 类型自动 connect 后走统一 initialize"""
    if transport == "sse":
        client = LegacySseClient(base_url, token, headers)
        await client.connect()
    else:
        client = StreamableHttpClient(base_url, token, headers)
    try:
        await client.initialize()
    except Exception:
        await client.close()
        raise
    return client
