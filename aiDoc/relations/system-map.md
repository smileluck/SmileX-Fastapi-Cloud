# 系统架构与组件关系

## 根目录职责

| 目录 | 职责 |
|------|------|
| `backend/` | FastAPI 应用，含模型、核心基础设施、业务模块 |
| `frontend/` | Vue 3 应用，含工作区子包和页面组件 |
| `aiDoc/` | AI 协作文档层 |
| `.trae/`、`.claude/`、`.cursor/` | 工具兼容适配层（不放项目规则） |

## 后端分层关系

```
main.py                            # 应用入口，注册路由、中间件、生命周期
  └─ modules/<name>/router.py      # 模块路由注册
       └─ endpoints/               # API 端点层（HTTP 参数提取、响应格式化）
            └─ services/           # 业务服务层（纯业务逻辑，不依赖 HTTP）
                 └─ database/models/ # ORM 模型层（SQLAlchemy 数据映射）
                      ├─ sys/      # 系统模型（用户、角色、权限、菜单、字典、配置）
                      ├─ business/ # 业务模型
                      └─ base.py   # 公共基类（Base、DataClassBase、Mixin）
```

### MCP 工具平台 `mcp/`

| 目录/文件 | 职责 |
|-----------|------|
| `mcp/server.py` | FastMCP 服务器创建与 ASGI 挂载 |
| `mcp/registry.py` | 工具注册表 + `@register_tool` 装饰器 + 自动发现 |
| `mcp/context.py` | 鉴权上下文（`contextvars` 传播） |
| `mcp/http_client.py` | 上游 HTTP 客户端（工具回调主应用 API） |
| `mcp/result.py` | 结果辅助函数（`text_result`、`text_result_with_json`、`text_result_error`） |
| `mcp/template.py` | 工具代码模板生成器 |
| `mcp/standalone.py` | 独立进程管理（启动/停止/健康检查） |
| `mcp/tools/` | 工具实现目录（自动发现） |

详细使用指南见 `aiDoc/modules/mcp-guide.md`。

### 核心基础设施 `core/`

| 目录 | 职责 |
|------|------|
| `config/` | 配置管理（pydantic-settings + .env） |
| `response/` | 统一响应模型（`ResponseModel`、`ResponsePageModel`、错误码） |
| `exception/` | 自定义异常（`CustomError`、`NotFoundError`、`ConflictError` 等） |
| `security/` | 安全认证（JWT、密码哈希、限流、输入消毒） |
| `redis/` | Redis 连接管理 |
| `log/` | 日志系统 |
| `middleware/` | 中间件（请求追踪等） |
| `health/` | 健康检查 |
| `registry/` | 注册机制 |
| `utils/` | 工具函数 |

### 数据库层 `database/`

| 目录/文件 | 职责 |
|-----------|------|
| `__init__.py` | 统一导出接口（ORM 基类、管理器、工具函数） |
| `config.py` | 数据库配置（`DatabaseModel`、`DatabaseType`、驱动枚举） |
| `db_manager.py` | 数据库连接池管理 |
| `models/base.py` | ORM 基类（`MappedBase`、`DataClassBase`、`Base`、`LogicMixin`、`DateTimeMixin`、`UserMixin`） |
| `models/sys/` | 系统模型（用户、角色、权限、菜单、字典、配置等） |
| `models/business/` | 业务模型 |
| `models/dataclasses.py` | 数据类（`IpInfo`、`AccessToken`、`RefreshToken` 等） |
| `manager/async_manager.py` | 异步数据库管理器（`get_session`、`get_session_cr`） |
| `manager/sync_manager.py` | 同步数据库管理器 |
| `plugins/setup_database.py` | 数据库插件（软删除自动过滤等） |
| `utils/snowflake.py` | 雪花 ID 生成 |
| `utils/str_utils.py` | 字符串工具（`camel_to_snake` 等） |
| `utils/timezone.py` | 时区工具 |
| `utils/url_builder.py` | 数据库 URL 构建器 |

### Pydantic Schema 基类 `modules/common/schemas/`

| 文件 | 职责 |
|------|------|
| `base.py` | Pydantic 基类（`BaseEntity`、`BaseReqEntity`、`BaseRespEntity`、`BoolField`） |
| `page.py` | 分页基类（`PageRequest`、`get_page_params`、`get_paginated_results`） |
| `mixin.py` | Schema Mixin |

## 前端数据流

```
src/service/api/          # API 调用封装（fetch 前缀函数）
  └─ @sa/axios            # HTTP 请求库封装（packages/axios/）
src/store/                # Pinia 全局状态管理
src/router/               # 路由配置与守卫
src/views/                # 页面组件
  ├─ manage/              # 系统管理页面（对应后端 admin 模块）
  ├─ log/                 # 日志管理页面（登录日志、操作日志）
  └─ <feature>/           # 业务页面
src/typings/api/          # TypeScript 类型声明（与后端 Schema 对应）
src/locales/langs/        # 国际化（zh-cn.ts、en-us.ts）
```

### 工作区子包 `packages/`

| 包名 | 职责 |
|------|------|
| `@sa/axios` | Axios 请求封装 |
| `@sa/hooks` | Vue 组合式函数 |
| `@sa/materials` | UI 组件库 |
| `@sa/utils` | 工具函数（crypto、nanoid、klona、storage） |
| `@sa/color` | 颜色工具 |
| `@sa/uno-preset` | UnoCSS 预设 |
| `@sa/alova` | Alova 请求库封装 |
| `@sa/scripts` | 构建与开发脚本 |

## 模块对应关系

| 后端模块 | 前端页面 |
|----------|----------|
| `backend/modules/admin/` | `frontend/src/views/manage/` |
| `backend/modules/admin/endpoints/sys/login_log.py` | `frontend/src/views/log/login-log/` |
| `backend/modules/admin/endpoints/sys/operation_log.py` | `frontend/src/views/log/operation-log/` |
| `backend/modules/app/` | `frontend/src/views/`（应用页面） |

## 配置文件

| 文件 | 说明 |
|------|------|
| `backend/.env` | 后端环境变量 |
| `backend/pyproject.toml` | Python 项目配置与依赖 |
| `backend/config/logging_dev.ini` | 开发环境日志配置 |
| `backend/config/logging_prod.ini` | 生产环境日志配置 |
| `frontend/.env` | 前端环境变量（`VITE_*` 前缀） |
| `frontend/package.json` | 前端依赖与脚本 |
| `frontend/vite.config.ts` | Vite 构建配置 |
| `frontend/uno.config.ts` | UnoCSS 配置 |
