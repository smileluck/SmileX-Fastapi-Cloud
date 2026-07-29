# SmileX

> 基于 FastAPI + Vue 3 的全栈云服务平台，开箱即用的后台管理系统，覆盖认证授权、权限菜单、系统配置、调度任务、多租户、开放 API 等核心能力。

SmileX 采用前后端分离架构，后端代码位于 [`backend/`](./backend)，前端代码位于 [`frontend/`](./frontend)，并附赠独立的 [MCP 工具平台](./mcp-platform) 与结构化的 [AI 协作文档体系](./AGENTS.md)。

## 目录

- [核心特性](#核心特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [国际化（i18n）](#国际化i18n)
- [MCP 工具平台（可选）](#mcp-工具平台可选)
- [AI 协作文档体系（可选）](#ai-协作文档体系可选)
- [开发指南](#开发指南)
- [部署指南](#部署指南)
- [配置说明](#配置说明)
- [开发规范](#开发规范)
- [贡献与许可](#贡献与许可)

## 核心特性

**后端**
- **统一响应契约**：`{ code, msg, data, request_id, err_code }` + 统一分页 `{ records, page, page_size, total, total_pages }`
- **认证授权**：JWT（access + refresh），基于角色 / 菜单 / 权限码的细粒度访问控制，数据权限（行级可见性）
- **业务模块**：用户 / 角色 / 菜单 / 部门 / 字典 / 配置 / 通知 / 文件 / 操作日志 / 登录日志 / IP 黑名单 / 应用用户 等
- **调度任务**：基于 APScheduler 的可视化定时任务（cron / interval / date），支持注册表自动发现
- **多租户插件**：可选的 `multi_tenant` 插件，JWT 识别租户、strict / optional / 全局三级行级隔离
- **开放 API**：面向第三方系统的 `/open/*` 路由，商户 HMAC-SHA256 签名鉴权 + Nonce 防重放
- **国际化**：后端响应消息按 `Accept-Language` 返回中英文，YAML 文案目录可平滑扩展新语言
- **安全加固**：多维度限流、IP 黑名单自动拉黑、文件上传 magic number 校验、scoped 预览令牌、安全响应头
- **可观测**：按日期滚动日志、`request_id` 全链路追踪、`/health` 与 `/ready` 健康探针

**前端**
- **响应式布局** + **主题系统**（含 NaiveUI 组件级主题定制）
- **动态菜单 / 路由权限**：基于后端权限的前端路由控制
- **国际化**：vue-i18n 中英文切换
- **数据可视化**：ECharts 图表，首页聚合仪表盘
- **异步导出**：导出任务队列 + WebSocket / 轮询状态同步

## 技术栈

### 后端
| 类别 | 选型 |
|---|---|
| 语言 / 框架 | Python **3.11+** / FastAPI |
| 包管理 | uv |
| ORM / 迁移 | SQLAlchemy 2.0（async）/ Alembic |
| 数据库 | PostgreSQL（也支持 MySQL） |
| 缓存 / 限流 | Redis |
| 认证 | PyJWT（JWT） |
| 调度 | APScheduler |
| 数据校验 | Pydantic v2 / pydantic-settings |
| 文档 | Swagger（OpenAPI）内嵌 |

### 前端
| 类别 | 选型 |
|---|---|
| 框架 / 语言 | Vue 3 / TypeScript |
| 构建 / 包管理 | Vite / pnpm |
| 状态管理 | Pinia |
| UI 库 | Naive UI |
| 路由 | Vue Router |
| CSS | UnoCSS |
| 国际化 | vue-i18n |
| 数据请求 | Axios（封装） |

## 项目结构

```
SmileX-Fastapi-Cloud/
├── backend/                    # 后端
│   ├── alembic/                # 数据库迁移脚本
│   ├── config/                 # 日志配置（logging_dev.ini / logging_prod.ini）
│   ├── core/                   # 核心基础设施
│   │   ├── config/             #   配置加载（pydantic-settings 多环境）
│   │   ├── exception/          #   统一异常与全局异常处理器
│   │   ├── health/             #   健康探针（/health /ready）
│   │   ├── i18n/               #   国际化（Accept-Language 解析 + YAML 文案目录）
│   │   ├── log/                #   日志（request_id 过滤、按日期滚动）
│   │   ├── middleware/         #   中间件（上下文 / 限流 / 审计 / 操作日志 …）
│   │   ├── redis/              #   Redis 连接池
│   │   ├── registry/           #   应用装配（中间件 / 异常 / 插件注册）
│   │   ├── response/           #   统一响应结构与状态码
│   │   ├── security/           #   JWT / 限流 / 开放 API 签名
│   │   ├── storage/            #   文件存储（local / oss）
│   │   └── ...
│   ├── database/               # 数据库（models / 连接池 / 工具）
│   │   └── models/             #   模型定义（sys / business）
│   ├── modules/                # 业务模块
│   │   ├── admin/              #   后台管理（endpoints / services / schemas / deps）
│   │   ├── app/                #   移动端 C 端
│   │   ├── common/             #   公共（分页 / 基类 schema）
│   │   ├── openapi/            #   开放 API 示例
│   │   └── scheduler/          #   定时任务
│   ├── plugins/                # 可选插件（multi_tenant 多租户）
│   ├── scripts/                # 运维脚本（create_superuser / reset_admin_password …）
│   ├── main.py                 # 后端入口
│   └── pyproject.toml          # 依赖配置
├── frontend/                   # 前端
│   ├── src/                    # 前端源码（views / store / service / router / locales …）
│   ├── packages/               # 工作区子包（@sa/axios 等）
│   └── package.json
├── mcp-platform/               # 独立 MCP 服务（默认端口 9001）
├── aiDoc/                      # AI 协作分层文档（入口见 aiDoc/README.md）
├── AGENTS.md                   # AI 协作规则（唯一真源，@import 进 CLAUDE.md）
├── CLAUDE.md                   # Claude Code 入口
├── error_codes.md              # 业务错误码表
└── README.md
```

后端分层遵循 `Endpoint -> Service -> Model`，模块统一放在 `backend/modules/<name>/`，含 `endpoints/`、`services/`、`schemas/`、`deps/`。

## 快速开始

### 后端

> 需要 Python 3.11+、uv、PostgreSQL、Redis。

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **创建并激活虚拟环境**
   ```bash
   uv venv
   # Windows: .venv\Scripts\activate
   # macOS / Linux: source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   uv sync
   ```

4. **配置环境变量**
   复制 `.env.dev` 为 `.env`（配置加载顺序：`.env` → `.env.{ENVIR}`，默认 `ENVIR=dev`），按需修改数据库 / Redis / JWT 等配置。

5. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

6. **创建超级用户**
   ```bash
   python scripts/create_superuser.py
   # 忘记密码可执行：python scripts/reset_admin_password.py
   ```

7. **启动后端服务**
   ```bash
   # 开发模式（自动重载）
   python main.py
   # 或
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

启动后访问 Swagger：`http://localhost:8000/docs`。健康探针：`GET /health`、`GET /ready`。

### 前端

1. **进入前端目录**
   ```bash
   cd frontend
   ```
2. **安装依赖**
   ```bash
   pnpm install
   ```
3. **配置环境变量**
   复制 `.env` 为 `.env.local` 并修改 API 地址等配置。
4. **启动开发服务器**
   ```bash
   pnpm dev
   ```

## 国际化（i18n）

前后端均支持中英文，新增语言可平滑扩展。

- **前端**：vue-i18n，文案在 `frontend/src/locales/langs/`，用户切换语言后写入 localStorage。
- **后端**：响应消息按请求头 `Accept-Language` 返回对应语言。前端请求拦截器（`frontend/src/service/request/index.ts`）自动注入 `Accept-Language: <locale>`，后端 `core/i18n/` 解析并翻译 `msg`、异常与校验消息。
- **新增后端文案**：在 `backend/core/i18n/locales/zh-CN.yaml` 与 `en-US.yaml` 同步增删 key，代码中用 `t("ns.key", **kwargs)`（支持 `{name}` 占位符）。
- **新增一种语言**：在 `locales/` 下新增 `<locale>.yaml`，并把该 locale 加入配置 `I18N.SUPPORTED_LANGUAGES`，无需改代码。

跨栈契约详见 [`aiDoc/frontend-backend/boundary.md`](./aiDoc/frontend-backend/boundary.md) 的「国际化」一节。

## MCP 工具平台（可选）

项目内置 MCP（Model Context Protocol）模块，支持工具注册、自动发现、在线创建与测试。两种部署形态：

- **内嵌模式（默认）**：随主应用启动，挂在 `/mcp` 路径下，无需额外操作。
- **独立模式**：独立进程，位于 [`mcp-platform/`](./mcp-platform)，默认监听 `http://127.0.0.1:9001`。
  ```bash
  cd mcp-platform
  uv sync && python run.py
  ```

**后台管理 API**

| 接口 | 路径 | 说明 |
|---|---|---|
| POST | `/admin/sys/mcp/add` | 创建 MCP 工具 |
| POST | `/admin/sys/mcp/list` | 获取已注册工具列表 |
| POST | `/admin/sys/mcp/test` | 测试工具调用 |
| POST | `/admin/sys/mcp/routes` | 获取 MCP 路由信息 |
| POST | `/admin/sys/mcp/status` | 获取 MCP 服务器状态 |
| POST | `/admin/sys/mcp/start` | 启动独立 MCP 服务 |
| POST | `/admin/sys/mcp/stop` | 停止独立 MCP 服务 |

**Claude Code 接入**

1. 启动独立 MCP 服务（见上，端点 `/mcp`）。
2. 在 Claude Code 中执行 `/mcp`，添加 HTTP 类型服务器，URL 填 `http://127.0.0.1:9001/mcp`；或编辑 `~/.claude.json`：
   ```json
   {
     "projects": { "你的项目路径": { "mcpServers": {
       "fastapi": { "type": "http", "url": "http://127.0.0.1:9001/mcp" }
     }}}
   }
   ```
3. 验证：`curl http://127.0.0.1:9001/health` 返回 `{"status":"ok"}` 即正常。

连接后可调用 `system_analyze`、`requirement_analyzer`、`code_review`、`code_execute`、`create_menu`、`list_all_menus`、`assign_menus_to_role`、`create_permission`、`list_all_permissions`、`generate_dictionary`、`query_dictionaries` 等工具。

## AI 协作文档体系（可选）

项目内置结构化 AI 协作文档：根 [`AGENTS.md`](./AGENTS.md)（规则唯一真源）+ [`aiDoc/`](./aiDoc)（分层约束文档），把长期有效的项目上下文从工具私有目录抽离，按主题拆分维护。配套 Claude Code 斜杠命令 `/generate-aidoc` 一键生成或增量维护。

> 与 MCP 一样是**可选**能力，不影响前后端构建与运行。

| 参数 | 行为 |
|---|---|
| （空） | 全量生成：探测项目并生成 / 覆盖所有 aiDoc 文件 |
| `--incremental` | 基于 `git diff` 增量更新受影响文件 |
| `--scope backend` / `frontend` / `relations` / `memory` / `core` | 只重新生成对应范围 |
| `--dry-run` | 只输出探测结果与计划，不写文件 |

加载层级（L0 自动加载 `AGENTS.md` → L1 任务路由 `aiDoc/README.md` → L2 按需深读子文档）见 `AGENTS.md`。

## 开发指南

### 后端
- **新增模块**：在 `modules/<name>/` 下建 `endpoints/`、`services/`、`schemas/`、`deps/`，遵循 `Endpoint -> Service -> Model` 分层；Service 不依赖 FastAPI 请求对象。
- **数据模型**：定义在 `database/models/{sys,business}`。
- **响应消息**：用 `response_base.success/fail/page(...)` 构建统一响应；业务消息走 `core.i18n.t("ns.key")`，避免硬编码中文。
- **错误码**：业务码集中在 `core/response/response_code.py`（`CustomResponseCode` / `CustomErrorCode`），完整码表见 [`error_codes.md`](./error_codes.md)。
- **配置**：`core/config/`（pydantic-settings），支持 `.env` 多环境与 `__` 嵌套覆盖（如 `I18N__DEFAULT_LANGUAGE`）。

### 前端
- **页面**：`src/views/<name>/`；公共组件 `src/components/`。
- **路由**：`src/router/`；状态 `src/store/`（Pinia）；API 封装 `src/service/api/`。
- **国际化**：文案在 `src/locales/langs/`，新增 key 同步 `zh-cn.ts` 与 `en-us.ts`。

## 部署指南

### 后端
1. 服务器安装 Python **3.11+**，使用 `uv sync` 安装依赖。
2. 配置生产环境变量（`ENVIR=prod` + `.env.prod`）。
3. 执行 `alembic upgrade head`。
4. 使用 Gunicorn（见 `gunicorn.conf.py`）或 Uvicorn 启动：
   ```bash
   gunicorn -c gunicorn.conf.py main:app
   ```

### 前端
1. 构建：`pnpm build`。
2. 将 `dist/` 部署到 Nginx 等静态服务器，配置反向代理转发 API 到后端。

## 配置说明

### 后端
- 日志配置：`backend/config/logging_dev.ini`、`logging_prod.ini`。
- 环境变量：`.env`（基础）、`.env.dev` / `.env.test` / `.env.prod`（按 `ENVIR` 覆盖）。
- 关键配置项：数据库 / Redis / JWT / 限流 / 多租户插件开关（`PLUGINS.ENABLED`）/ 国际化（`I18N.*`）等，均支持环境变量覆盖。

### 前端
- 环境变量：`.env`（基础）、`.env.prod`、`.env.test`，本地覆盖用 `.env.local`。

## 开发规范

### 后端
- 遵循 PEP 8；类名大驼峰，函数 / 变量小写下划线。
- 函数与类添加注释；对外接口 Swagger 注释必须与真实行为一致。
- 关键操作记录日志（含 `request_id`）；异常通过统一异常类 + 全局处理器返回。
- 保持统一响应 / 分页结构；跨栈字段名 `snake_case`，`status` 字段 `bool ↔ "1"/"2"` 桥接。

### 前端
- 遵循 ESLint；组件名大驼峰，变量小驼峰，常量全大写下划线。
- 异步操作与 API 调用做错误处理；合理使用计算属性与监听器。

更多分层、命名、契约约束见 [`AGENTS.md`](./AGENTS.md) 与 [`aiDoc/`](./aiDoc)。

## 贡献与许可

- **许可证**：MIT，详见 [`backend/LICENSE`](./backend/LICENSE) 与 [`frontend/LICENSE`](./frontend/LICENSE)。
- **贡献流程**：Fork → 新建特性分支 → 提交 → Push → 发起 Pull Request。
- **反馈**：欢迎通过 Issue 提交问题与建议。

---

**SmileX** — 让云服务更简单，让开发更高效。
