# SmileX 项目

SmileX 是一个基于 FastAPI 和 Vue 的全栈云服务平台，提供完整的前后端解决方案，支持用户认证、权限管理、系统配置等核心功能。

## 项目结构

本项目采用前后端分离架构，后端代码位于 `backend` 目录，前端代码位于 `frontend` 目录。

```
SmileX-Fastapi-Cloud/
├── backend/            # 后端代码
│   ├── app/            # 应用核心模块
│   ├── config/         # 配置文件
│   ├── core/           # 核心功能模块
│   ├── database/       # 数据库相关
│   ├── mcp/            # MCP 工具模块
│   │   ├── registry.py # 工具注册表与自动发现
│   │   ├── server.py   # FastMCP 服务器
│   │   ├── template.py # 工具代码生成器
│   │   ├── standalone.py # 独立进程管理
│   │   └── tools/      # 自动发现的工具目录
│   ├── modules/        # 业务模块
│   ├── scripts/        # 脚本工具
│   ├── main.py         # 后端入口文件
│   └── pyproject.toml  # 项目依赖配置
├── frontend/           # 前端代码
│   ├── packages/       # 前端包
│   ├── public/         # 静态资源
│   ├── src/            # 前端源码
│   ├── index.html      # 前端入口文件
│   └── package.json    # 前端依赖配置
└── README.md           # 项目说明文档
```

## 技术栈

### 后端
- **框架**: FastAPI
- **语言**: Python
- **包管理**: uv
- **数据库**: PostgreSQL (使用 SQLAlchemy ORM)
- **缓存**: Redis
- **认证**: JWT
- **数据库迁移**: Alembic
- **日志**: 自定义日志系统

### 前端
- **框架**: Vue 3
- **语言**: TypeScript
- **构建工具**: Vite
- **包管理**: pnpm
- **状态管理**: Pinia
- **UI 库**: Naive UI
- **路由**: Vue Router
- **CSS 框架**: UnoCSS
- **国际化**: i18n

## 快速开始

### 后端环境搭建

1. **进入后端目录**
   ```bash
   cd backend
   ```

2. **激活虚拟环境**
   ```bash
   ./venv/Scripts/activate.bat
   ```

3. **安装依赖**
   ```bash
   uv add
   ```

4. **配置环境变量**
   复制 `.env.dev` 文件为 `.env` 并修改相关配置

5. **数据库迁移**
   ```bash
   alembic upgrade head
   ```

6. **创建超级用户**
   ```bash
   python scripts/create_superuser.py
   ```

7. **启动后端服务**
   ```bash
   # 开发模式（自动重载）
   python main.py

   # 或使用 uvicorn 直接启动
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **启动 MCP 服务（可选）**

   项目内置了 MCP (Model Context Protocol) 模块，支持工具注册与独立进程部署。

   - **内嵌模式**（默认）：MCP 服务随主应用一起启动，挂载在 `/mcp` 路径下，无需额外操作。
   - **独立模式**：独立的 MCP 服务进程，通过 `mcp-platform/` 目录启动，默认端口 `9001`。

   ```bash
   # MCP 服务随主应用自动启动，无需手动操作
   # 默认配置如下（可在 .env 中覆盖）：
   # MCP__ENABLED=true
   # MCP__NAME=SmileX MCP Server
   # MCP__HOST=127.0.0.1
   # MCP__PORT=9000

   # 独立模式启动：
   cd mcp-platform
   python run.py
   # 默认监听 http://127.0.0.1:9001

   # 也可通过管理 API 启动独立 MCP 进程：
   # POST http://localhost:8000/admin/sys/mcp/start
   ```

   MCP 管理 API 列表：

   | 接口 | 路径 | 说明 |
   |------|------|------|
   | POST | `/admin/sys/mcp/add` | 创建 MCP 工具 |
   | POST | `/admin/sys/mcp/list` | 获取已注册工具列表 |
   | POST | `/admin/sys/mcp/test` | 测试工具调用 |
   | POST | `/admin/sys/mcp/routes` | 获取 MCP 路由信息 |
   | POST | `/admin/sys/mcp/status` | 获取 MCP 服务器状态 |
   | POST | `/admin/sys/mcp/start` | 启动独立 MCP 服务 |
   | POST | `/admin/sys/mcp/stop` | 停止独立 MCP 服务 |

### Claude Code 接入 MCP

本项目支持通过 Claude Code 等 MCP 客户端直接调用后端能力（菜单管理、权限管理、代码审查等）。

1. **启动 MCP 服务**

   确保独立 MCP 服务已启动：

   ```bash
   cd mcp-platform
   python run.py
   ```

   服务启动后默认监听 `http://127.0.0.1:9001`，MCP 协议端点为 `/mcp`。

2. **配置 Claude Code**

   在 Claude Code 中输入 `/mcp` 命令添加 HTTP 类型的 MCP 服务器：

   - **Type**: HTTP
   - **URL**: `http://127.0.0.1:9001/mcp`

   或直接编辑配置文件 `~/.claude.json`（项目级别）：

   ```json
   {
     "projects": {
       "你的项目路径": {
         "mcpServers": {
           "fastapi": {
             "type": "http",
             "url": "http://127.0.0.1:9001/mcp"
           }
         }
       }
     }
   }
   ```

3. **连接验证**

   配置完成后，在 Claude Code 中输入 `/mcp` 查看连接状态，确认状态为已连接。也可通过健康检查接口验证：

   ```bash
   curl http://127.0.0.1:9001/health
   # 返回 {"status": "ok"} 表示服务正常
   ```

4. **可用工具**

   连接成功后，Claude Code 可直接调用以下工具：

   | 工具名称 | 说明 |
   |---------|------|
   | `system_analyze` | 分析系统 |
   | `requirement_analyzer` | 需求分析 |
   | `code_review` | 代码审查 |
   | `code_execute` | 代码执行 |
   | `create_menu` | 创建菜单 |
   | `list_all_menus` | 查询菜单列表 |
   | `assign_menus_to_role` | 为角色分配菜单 |
   | `create_permission` | 创建权限 |
   | `list_all_permissions` | 查询权限列表 |
   | `generate_dictionary` | 生成字典 |
   | `query_dictionaries` | 查询字典 |

### AI 协作文档生成（generate-aidoc，可选）

项目内置了一套结构化的 AI 协作文档体系（根 `AGENTS.MD` + `aiDoc/` 分层文档），把长期有效的项目上下文从工具私有目录中抽离出来，按主题拆分成可维护的约束文档。`generate-aidoc` 是配套的 Claude Code 斜杠命令（`.claude/commands/generate-aidoc.md`），用于一键生成或增量维护这套文档。

> 与 MCP 一样，这是**可选**能力：不使用不影响后端/前端的构建与运行。仅当你想让 AI 协作时自动遵循项目分层、命名、契约约定时才需要。

**何时使用**

- 首次接入 AI 协作，需要生成 `AGENTS.MD` + `aiDoc/` 全套约束文档
- 发生大范围重构后，文档与代码漂移，需要重新同步
- 新增/删除 `aiDoc/` 子文档后，刷新 `aiDoc/README.md` 的路由表与常用入口

**运行模式**

在 Claude Code 中执行 `/generate-aidoc`，可带以下参数：

| 参数 | 行为 |
|---|---|
| （空） | 全量生成：探测项目并生成/覆盖所有 aiDoc 文件 |
| `--incremental` | 增量更新：基于 `git diff` 只更新受影响范围的文件 |
| `--scope backend` / `frontend` / `relations` / `memory` / `core` | 只重新生成对应范围的文件 |
| `--dry-run` | 只输出探测结果与生成计划，不写文件 |

生成的文档分层与加载顺序见 `AGENTS.MD` 的「加载模型」（L0 自动加载 → L1 任务路由 → L2 按需深读）。

### 前端环境搭建

1. **进入前端目录**
   ```bash
   cd frontend
   ```

2. **安装依赖**
   ```bash
   pnpm install
   ```

3. **配置环境变量**
   复制 `.env` 文件为 `.env.local` 并修改相关配置

4. **启动前端开发服务器**
   ```bash
   pnpm dev
   ```

## 核心功能

### 后端核心功能
- **用户认证与授权**: 基于 JWT 的认证系统，支持角色权限管理
- **系统配置管理**: 可配置系统参数，支持多环境配置
- **数据字典管理**: 统一管理系统中的数据字典
- **菜单管理**: 动态生成系统菜单，支持权限控制
- **角色管理**: 基于角色的权限控制系统
- **用户管理**: 完整的用户CRUD操作，支持用户状态管理
- **MCP 工具平台**（可选）: 内置 MCP 服务器，支持工具注册、自动发现、在线创建与测试
- **AI 协作文档体系**（可选）: `AGENTS.MD` + `aiDoc/` 分层约束文档，配套 `generate-aidoc` 命令一键生成与增量维护
- **日志系统**: 完整的日志记录与管理
- **缓存系统**: 基于Redis的缓存实现

### 前端核心功能
- **响应式布局**: 适配不同屏幕尺寸
- **主题系统**: 支持多种主题切换
- **国际化**: 支持中英文切换
- **菜单管理**: 动态生成菜单，支持多级菜单
- **权限控制**: 基于后端权限的前端路由控制
- **数据可视化**: 集成ECharts实现数据图表
- **表单验证**: 完整的表单验证系统
- **文件上传**: 支持文件上传功能

## 开发指南

### 后端开发

1. **模块划分**: 后端按照功能模块划分，每个模块有独立的目录结构
2. **数据库模型**: 数据库模型定义在 `app/models` 目录下
3. **API 路由**: API 路由定义在 `modules` 目录下的对应模块中
4. **业务逻辑**: 业务逻辑封装在 `services` 目录下
5. **配置管理**: 配置文件位于 `config` 目录下，支持多环境配置

### 前端开发

1. **页面划分**: 前端按照页面划分，每个页面有独立的目录结构
2. **组件开发**: 公共组件位于 `components` 目录下
3. **路由配置**: 路由配置位于 `router` 目录下
4. **状态管理**: 状态管理使用 Pinia，定义在 `store` 目录下
5. **API 调用**: API 调用封装在 `service` 目录下

## 部署指南

### 后端部署

1. **环境配置**: 确保服务器安装了 Python 3.9+
2. **依赖安装**: 使用 uv 安装依赖
3. **环境变量**: 配置生产环境的 `.env` 文件
4. **数据库迁移**: 执行数据库迁移
5. **服务启动**: 使用 Gunicorn 或 Uvicorn 启动服务

### 前端部署

1. **构建**: 执行 `pnpm build` 命令构建前端代码
2. **静态文件**: 将构建后的静态文件部署到 Nginx 或其他静态文件服务器
3. **配置**: 配置 Nginx 代理后端 API 请求

## 项目配置

### 后端配置

后端配置文件位于 `backend/config` 目录下，主要配置文件包括：
- `logging_dev.ini`: 开发环境日志配置
- `logging_prod.ini`: 生产环境日志配置

环境变量配置文件包括：
- `.env.dev`: 开发环境变量
- `.env.prod`: 生产环境变量
- `.env.test`: 测试环境变量

### 前端配置

前端配置文件包括：
- `.env`: 基础环境变量
- `.env.prod`: 生产环境变量
- `.env.test`: 测试环境变量

## 开发规范

### 后端开发规范
1. **代码风格**: 遵循 PEP 8 代码风格
2. **命名规范**: 
   - 类名使用大驼峰命名法
   - 函数名使用小写字母加下划线
   - 变量名使用小写字母加下划线
3. **注释规范**: 为函数和类添加详细的注释
4. **错误处理**: 对异常进行捕获和处理
5. **日志记录**: 关键操作添加日志记录

### 前端开发规范
1. **代码风格**: 遵循 ESLint 代码风格
2. **命名规范**: 
   - 组件名使用大驼峰命名法
   - 变量名使用小驼峰命名法
   - 常量名使用全大写加下划线
3. **注释规范**: 为组件和关键函数添加注释
4. **错误处理**: 对异步操作和 API 调用进行错误处理
5. **性能优化**: 合理使用计算属性和监听器，避免不必要的渲染

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎贡献代码，提交 Issue 和 Pull Request。

### 提交代码流程
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 联系方式

- 项目地址: [https://github.com/SmileX/SmileX-Fastapi-Cloud](https://github.com/SmileX/SmileX-Fastapi-Cloud)
- 问题反馈: [https://github.com/SmileX/SmileX-Fastapi-Cloud/issues](https://github.com/SmileX/SmileX-Fastapi-Cloud/issues)

---

**SmileX** - 让云服务更简单，让开发更高效！