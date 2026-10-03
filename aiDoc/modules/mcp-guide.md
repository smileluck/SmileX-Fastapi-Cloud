<!-- last-updated: 2026-05-21 -->
# MCP 使用指南

## 概述

本项目集成了 MCP（Model Context Protocol）工具平台，支持 AI 助手通过标准化协议调用后端工具。提供两种部署模式：内嵌模式（默认）和独立模式。

## 架构

```
AI 客户端（Claude / Cursor / Trae 等）
        │
        │ MCP 协议（Streamable HTTP）
        ▼
  /mcp 端点（FastMCP）
        │
        ├── 工具发现与注册（registry.py）
        ├── 鉴权上下文传播（context.py）
        ├── 上游 HTTP 回调（http_client.py）
        └── 工具实现（mcp/tools/*.py）
```

## 目录结构

```
backend/mcp/
├── __init__.py          # 包标记
├── registry.py          # 工具注册表 + @register_tool 装饰器 + 自动发现
├── server.py            # FastMCP 服务器创建与 ASGI 挂载
├── context.py           # 鉴权上下文（contextvars 传播）
├── http_client.py       # 上游 HTTP 客户端（工具回调主应用 API）
├── result.py            # 结果辅助函数
├── template.py          # 工具代码模板生成器
├── standalone.py        # 独立进程管理
└── tools/               # 工具实现目录
    └── __init__.py
```

## 配置

定义于 `core/config/settings_model.py:MCPModel`，通过环境变量或 `.env` 文件配置：

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| `ENABLED` | `MCP_ENABLED` | `True` | 是否启用 MCP 模块 |
| `NAME` | `MCP_NAME` | `"SmileX MCP Server"` | MCP 服务器名称 |
| `VERSION` | `MCP_VERSION` | `"1.0.0"` | 版本号 |
| `HOST` | `MCP_HOST` | `"127.0.0.1"` | 独立服务监听地址 |
| `PORT` | `MCP_PORT` | `9000` | 独立服务监听端口 |
| `UPSTREAM_BASE_URL` | `MCP_UPSTREAM_BASE_URL` | `"http://127.0.0.1:8000"` | 主应用 URL（工具回调用） |
| `AUTH_HEADER` | `MCP_AUTH_HEADER` | `"Authorization"` | 鉴权 Header 名称 |
| `REQUEST_TIMEOUT` | `MCP_REQUEST_TIMEOUT` | `30` | HTTP 请求超时（秒） |
| `PROCESS_META_FILE` | `MCP_PROCESS_META_FILE` | `"mcp_process.json"` | 进程元数据文件路径 |

禁用 MCP：在 `.env` 中设置 `MCP_ENABLED=false`。

## 部署模式

### 内嵌模式（默认）

MCP 作为 FastAPI 应用的子应用挂载，共享同一进程。

- 挂载路径：`/mcp`
- 启动方式：随主应用自动启动
- 适用场景：开发环境、小规模部署

启动代码在 `main.py`：
```python
if settings.MCP.ENABLED:
    from mcp.server import create_mcp_server
    mcp_server = create_mcp_server()
    app.mount("/mcp", mcp_server.streamable_http_app())
```

### 独立模式

MCP 作为独立子进程运行，通过管理接口控制生命周期。

- 默认地址：`http://127.0.0.1:9000`
- 适用场景：生产环境、需要隔离 MCP 工具的资源消耗
- 管理接口通过 `POST /admin/mcp/start`、`POST /admin/mcp/stop`、`POST /admin/mcp/status` 控制

## 创建 MCP 工具

### 方式一：通过模板自动生成

调用管理接口 `POST /admin/mcp/add`，传入工具定义：

```json
{
  "name": "query-user",
  "description": "根据用户名查询用户信息",
  "params": [
    { "name": "username", "description": "用户名", "type": "string", "required": true },
    { "name": "page", "description": "页码", "type": "number", "required": false, "default": 1 }
  ],
  "response": [
    { "key": "id", "type": "number", "description": "用户ID" },
    { "key": "username", "type": "string", "description": "用户名" }
  ]
}
```

系统会在 `mcp/tools/` 目录自动生成 `query_user.py` 文件，包含完整的工具类框架。生成后需要编辑 `handle()` 方法实现业务逻辑。

### 方式二：手动编写

在 `mcp/tools/` 目录下创建新文件，按以下模板编写：

```python
from mcp.registry import register_tool, ToolParam
from mcp.context import McpContext
from mcp.result import text_result, text_result_with_json, text_result_error
from mcp.types import TextContent


@register_tool
class QueryUser:
    @classmethod
    def tool_name(cls) -> str:
        return "query-user"

    @classmethod
    def tool_description(cls) -> str:
        return "根据用户名查询用户信息"

    @classmethod
    def tool_params(cls) -> list[ToolParam]:
        return [
            ToolParam(name="username", description="用户名", type="string", required=True),
        ]

    async def handle(self, arguments: dict, context: McpContext) -> list[TextContent]:
        username = arguments.get("username")
        # 实现业务逻辑
        # 可使用 McpHttpClient 回调主应用 API
        result = {"username": username, "id": 123}
        return text_result_with_json(result)
```

### 工具注册机制

1. 使用 `@register_tool` 装饰器标记工具类
2. 工具类必须实现 `McpTool` 协议的四个方法：`tool_name()`、`tool_description()`、`tool_params()`、`handle()`
3. 服务器启动时通过 `discover_tools()` 自动扫描 `mcp/tools/` 目录下的所有模块
4. 已注册工具可通过 `POST /admin/mcp/list` 查看

### 参数类型

| type 值 | Python 类型 | 说明 |
|---------|------------|------|
| `string` | `str` | 字符串 |
| `number` | `float` | 数值 |
| `boolean` | `bool` | 布尔值 |
| `array` | `list` | 数组 |
| `object` | `dict` | 对象 |

## 结果返回

使用 `mcp/result.py` 中的辅助函数构建返回值：

```python
from mcp.result import text_result, text_result_with_json, text_result_error

# 纯文本
return text_result("操作成功")

# JSON 格式（推荐）
return text_result_with_json({"id": 1, "name": "test"})

# 错误信息
return text_result_error("用户不存在")
```

## 鉴权与上下文

### 请求上下文

MCP 通过 `contextvars` 在异步调用链中传递鉴权信息：

- AI 客户端请求时携带 `x-token` 或 `Authorization` Header
- `McpContext.from_headers()` 自动提取 Token
- 工具的 `handle()` 方法通过 `context` 参数获取 Token

### 回调主应用

工具如需调用主应用 API，使用 `McpHttpClient`（`mcp/http_client.py`）：

```python
from mcp.http_client import McpHttpClient

class MyTool:
    async def handle(self, arguments: dict, context: McpContext) -> list[TextContent]:
        client = McpHttpClient()
        # 自动携带当前请求的鉴权 Token
        result = await client.get("/admin/sys/user/list", params={"page": 1})
        return text_result_with_json(result)
```

`McpHttpClient` 自动：
- 从 `mcp_request_ctx` 获取当前请求的 Token
- 拼接 `UPSTREAM_BASE_URL` 前缀
- 设置鉴权 Header

## 管理接口

所有管理接口路径前缀为 `/admin/mcp`：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/mcp/add` | POST | 从模板创建工具 |
| `/admin/mcp/list` | POST | 获取已注册工具列表 |
| `/admin/mcp/routes` | POST | 获取 MCP 路由信息 |
| `/admin/mcp/test` | POST | 测试工具执行 |
| `/admin/mcp/status` | POST | 获取服务器状态 |
| `/admin/mcp/start` | POST | 启动独立服务 |
| `/admin/mcp/stop` | POST | 停止独立服务 |

### 测试工具

```json
POST /admin/mcp/test
{
  "tool_name": "query-user",
  "arguments": { "username": "admin" }
}
```

## 新增工具的完整流程

1. 在 `mcp/tools/` 目录创建工具文件（手动或通过模板 API）
2. 实现 `McpTool` 协议的四个方法
3. 编辑 `handle()` 方法实现业务逻辑
4. 重启应用（内嵌模式）或调用 `POST /admin/mcp/start`（独立模式）
5. 调用 `POST /admin/mcp/list` 验证工具已注册
6. 调用 `POST /admin/mcp/test` 测试工具执行
7. 在 AI 客户端中配置 MCP 服务地址

## 时间参数规范

MCP 工具如需接收时间参数，遵循项目统一的时间格式约定（详见 `aiDoc/frontend-backend/boundary.md`）：

- **入参格式**：ISO 8601 带时区偏移，如 `2026-05-21T16:39:23+08:00`
- **解析方式**：
  ```python
  dt = datetime.fromisoformat(time_str)
  result = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
  ```
- **禁止**：直接对带时区偏移的字符串使用 `.replace(tzinfo=timezone.utc)`

## 相关文件

| 文件 | 职责 |
|------|------|
| `backend/mcp/registry.py` | 工具注册表、自动发现、`McpTool` 协议 |
| `backend/mcp/server.py` | FastMCP 服务器创建 |
| `backend/mcp/context.py` | 鉴权上下文 |
| `backend/mcp/http_client.py` | 上游 HTTP 客户端 |
| `backend/mcp/result.py` | 结果辅助函数 |
| `backend/mcp/template.py` | 工具代码生成器 |
| `backend/mcp/standalone.py` | 独立进程管理 |
| `backend/mcp/tools/` | 工具实现目录 |
| `backend/modules/admin/endpoints/sys/mcp.py` | 管理接口 |
| `backend/modules/admin/services/sys/mcp_service.py` | 管理服务层 |
| `backend/modules/admin/schemas/sys/mcp.py` | 管理 Schema |
| `backend/core/config/settings_model.py` | MCP 配置模型 |

## 日志模块

系统提供登录日志和操作日志两个模块，前端搜索表单已统一为标准折叠网格布局（`NCollapse` + `NGrid` + `NFormItemGi`）。

### 后端 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/admin/login-log/list` | GET | 分页查询登录日志 |
| `/admin/login-log/batch/delete` | DELETE | 批量删除登录日志 |
| `/admin/login-log/clear` | DELETE | 清理过期登录日志（默认 30 天） |
| `/admin/login-log/{log_id}` | GET/DELETE | 查看/删除单条登录日志 |
| `/admin/operation-log/list` | GET | 分页查询操作日志 |
| `/admin/operation-log/export` | GET | 导出操作日志 |
| `/admin/operation-log/batch/delete` | DELETE | 批量删除操作日志 |
| `/admin/operation-log/clear` | DELETE | 清理过期操作日志（默认 30 天） |
| `/admin/operation-log/{log_id}` | GET/DELETE | 查看/删除单条操作日志 |

### 前端组件

| 组件 | 路径 |
|------|------|
| 登录日志列表 | `frontend/src/views/log/login-log/index.vue` |
| 登录日志搜索 | `frontend/src/views/log/login-log/modules/login-log-search.vue` |
| 操作日志列表 | `frontend/src/views/log/operation-log/index.vue` |
| 操作日志搜索 | `frontend/src/views/log/operation-log/modules/operation-log-search.vue` |
| 操作日志详情 | `frontend/src/views/log/operation-log/modules/operation-log-detail-drawer.vue` |
