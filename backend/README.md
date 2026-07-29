# SmileX Cloud · Backend

基于 FastAPI 构建的云服务平台后端，提供认证授权、权限菜单、系统配置、调度任务、多租户、开放 API 等能力。对应前端见 [`../frontend`](../frontend)，独立 MCP 服务见 [`../mcp-platform`](../mcp-platform)。

## 技术栈

| 类别 | 选型 |
|---|---|
| 语言 / 框架 | Python **3.11+** / FastAPI |
| 包管理 | uv |
| ORM / 迁移 | SQLAlchemy 2.0（async）/ Alembic |
| 数据库 | PostgreSQL（asyncpg）/ 也支持 MySQL（aiomysql） |
| 缓存 / 限流 | Redis |
| 认证 | PyJWT（JWT access + refresh） |
| 调度 | APScheduler |
| 校验 / 配置 | Pydantic v2 / pydantic-settings |
| 文案目录 | PyYAML（i18n） |
| 服务器 | Uvicorn（开发）/ Gunicorn（生产） |

## 目录结构

```
backend/
├── alembic/                # 数据库迁移脚本
├── config/                 # 日志配置（logging_dev.ini / logging_prod.ini）
├── core/                   # 核心基础设施
│   ├── config/             #   配置加载（pydantic-settings，多环境）
│   ├── exception/          #   统一异常类与全局异常处理器
│   ├── health/             #   健康探针（/health /ready）
│   ├── i18n/               #   国际化（Accept-Language + YAML 文案目录）
│   ├── log/                #   日志（request_id 过滤、按日期滚动）
│   ├── middleware/         #   中间件（上下文 / 限流 / 审计 / 操作日志 / 安全头 …）
│   ├── models/             #   基础模型 mixin
│   ├── redis/              #   Redis 连接池
│   ├── registry/           #   应用装配（中间件 / 异常 / 插件注册）
│   ├── response/           #   统一响应结构与状态码枚举
│   ├── security/           #   JWT / 限流 / 开放 API HMAC 签名
│   ├── storage/            #   文件存储（local / oss）
│   └── utils/              #   工具函数
├── database/               # 数据库层
│   ├── models/             #   ORM 模型（sys / business）
│   ├── manager/            #   同步 / 异步连接池
│   └── utils/              #   雪花 ID / URL 构建等
├── modules/                # 业务模块
│   ├── admin/              #   后台管理（endpoints / services / schemas / deps）
│   ├── app/                #   移动端 C 端
│   ├── common/             #   公共（分页 / 基类 schema）
│   ├── openapi/            #   开放 API 示例
│   └── scheduler/          #   定时任务
├── plugins/                # 可选插件（multi_tenant 多租户）
├── scripts/                # 运维脚本（create_superuser / reset_admin_password …）
├── static/                 # 静态资源
├── uploads/                # 本地上传目录
├── main.py                 # 应用入口
├── gunicorn.conf.py        # Gunicorn 生产配置
├── pyproject.toml          # 依赖配置
└── .env / .env.dev / .env.test / .env.prod
```

模块分层统一遵循 **`Endpoint -> Service -> Model`**：Endpoint 处理 HTTP 与参数，Service 承载业务逻辑（不依赖 FastAPI 请求对象），Model 定义数据。

## 快速开始

> 依赖：Python 3.11+、uv、PostgreSQL、Redis。

```bash
# 1. 进入目录、创建虚拟环境、安装依赖
cd backend
uv venv
uv sync                      # Windows 激活: .venv\Scripts\activate

# 2. 配置环境变量（加载顺序 .env -> .env.{ENVIR}，默认 ENVIR=dev）
cp .env.dev .env             # 按需修改 DB / Redis / JWT 等

# 3. 数据库迁移 + 创建超管
alembic upgrade head
python scripts/create_superuser.py
# 忘记密码: python scripts/reset_admin_password.py

# 4. 启动
python main.py               # 或 uvicorn main:app --reload --port 8000
```

启动后：
- Swagger：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`
- 健康探针：`GET /health`（liveness）、`GET /ready`（readiness，检查 DB+Redis）

## 核心能力

### 统一响应与错误码
- 普通响应：`{ code, msg, data, request_id, err_code }`；分页：`{ records, page, page_size, total, total_pages }`
- 用 `response_base.success / fail / page(...)` 构建；业务码集中在 `core/response/response_code.py`（`CustomResponseCode` / `CustomErrorCode`），完整码表见 [`../error_codes.md`](../error_codes.md)

### 国际化（i18n）
- 响应消息按请求头 `Accept-Language` 返回中英文；前端拦截器自动注入
- 文案目录：`core/i18n/locales/{zh-CN,en-US}.yaml`，代码用 `t("ns.key", **kwargs)`（支持 `{name}` 占位符）
- 新增语言：加 `<locale>.yaml` + 追加 `I18N.SUPPORTED_LANGUAGES`

### 调度任务
- 基于 APScheduler 的可视化定时任务（cron / interval / date），`modules/scheduler/` 提供 REST 管理与注册表自动发现

### 多租户（可选插件）
- `plugins/multi_tenant/`：JWT 识别租户，strict / optional / 全局三级行级隔离；在 `.env` 通过 `PLUGINS.ENABLED` 启用

### 开放 API
- `/open/*` 面向第三方，商户 HMAC-SHA256 签名 + Nonce 防重放（`core/security/openapi/`）；后台商户管理在 `/admin/sys/merchant/*`

### 安全
- 多维度限流（IP / 用户 / 路径）+ IP 黑名单自动拉黑、文件上传 magic number 校验、scoped 预览令牌、安全响应头

## MCP 工具平台（可选）

内置 MCP（Model Context Protocol）模块，支持工具注册、自动发现、在线创建与测试。

- **内嵌模式（默认）**：随主应用启动，挂在 `/mcp`，无需额外操作
- **独立模式**：[`../mcp-platform`](../mcp-platform)，默认 `http://127.0.0.1:9001`

`.env` 配置（`MCP__` 前缀）：

```bash
MCP__ENABLED=true
MCP__NAME=SmileX MCP Server
MCP__HOST=127.0.0.1
MCP__PORT=9000                          # 后端 MCP 模块独立服务端口
MCP__UPSTREAM_BASE_URL=http://127.0.0.1:8000
```

管理 API：

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/admin/sys/mcp/add` | 创建 MCP 工具 |
| POST | `/admin/sys/mcp/list` | 获取已注册工具列表 |
| POST | `/admin/sys/mcp/test` | 测试工具调用 |
| POST | `/admin/sys/mcp/routes` | 获取 MCP 路由信息 |
| POST | `/admin/sys/mcp/status` | 获取 MCP 服务器状态 |
| POST | `/admin/sys/mcp/start` | 启动独立 MCP 服务 |
| POST | `/admin/sys/mcp/stop` | 停止独立 MCP 服务 |

## 数据库迁移

> 使用 `uv` 时在命令前加 `uv run`。

```bash
alembic revision --autogenerate -m "描述"   # 生成迁移
alembic upgrade head                        # 应用
alembic downgrade -1                        # 回退一版
alembic history                             # 历史
```

## 部署

```bash
# 生产（Gunicorn，配置见 gunicorn.conf.py）
gunicorn -c gunicorn.conf.py main:app
```

环境：`ENVIR=prod` + `.env.prod`，先 `alembic upgrade head` 再启动。

## 配置

- 环境变量：`.env`（基础）+ `.env.dev` / `.env.test` / `.env.prod`（按 `ENVIR` 覆盖）
- 嵌套项用 `__` 分隔覆盖，如 `I18N__DEFAULT_LANGUAGE=en-US`、`MCP__ENABLED=false`
- 关键配置组：`DATABASE` / `REDIS` / `JWT` / `SECURITY` / `RATE_LIMIT` / `PLUGINS` / `I18N` / `MCP` / `OPEN_API`

## 开发规范

- 遵循 PEP 8；类名大驼峰，函数 / 变量小写下划线
- 对外接口 Swagger 注释必须与真实行为一致；Service 不依赖 FastAPI 请求对象
- 关键操作记录日志（含 `request_id`）；异常通过统一异常类 + 全局处理器返回
- 业务消息走 `t("ns.key")`，避免硬编码中文；跨栈字段 `snake_case`，`status` 字段 `bool ↔ "1"/"2"` 桥接

更多分层、命名、契约约束见 [`../AGENTS.md`](../AGENTS.md) 与 [`../aiDoc/`](../aiDoc)。

## 许可证

MIT，详见 [LICENSE](LICENSE)。
