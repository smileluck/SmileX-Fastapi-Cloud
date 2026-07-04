# aiDoc

`aiDoc/` 是本仓库的结构化 AI 文档层，用于把长期有效的项目上下文从工具目录中抽离出来，并按主题拆分成可维护的约束文档。

## 使用方式

1. `AGENTS.MD` 已随根 `CLAUDE.md @AGENTS.md` 自动加载（L0），始终生效
2. 接到任务先查本文件的「任务→必读文档」路由表，确定必读（L1）
3. 不清楚某个文档讲什么时，再翻「常用入口」字典（L1）
4. 按路由表打开 `aiDoc/` 下具体子文档深读（L2）

不再把项目级规则复制到工具私有目录；Claude Code 走 `@import`，Trae 等走薄适配指针（见 `AGENTS.MD` 的「各工具加载方式」）。

> 路由表 = 按任务导航；常用入口 = 按文档查字典。两者分工，避免维护漂移。

## 目录说明

- `relations/`: 仓库结构、技术栈、依赖关系、开发流程
- `modules/`: 后端分层规则、模块职责
- `frontend-backend/`: 前后端契约、前端规范、工具函数复用规则
- `examples/`: 讲解型示例，告诉 AI 每一层应该按什么标准组织和书写
- `memory/`: AI 记忆层，拆分为长期记忆与业务记忆

## 常用入口

- `relations/repo-profile.md`: 项目定位、技术栈、核心特性
- `relations/development-workflow.md`: 开发流程、分支与提交规范
- `relations/system-map.md`: 系统架构与组件关系
- `modules/backend-layer-rules.md`: 后端分层、统一响应、错误码约束
- `modules/module-development.md`: 后端/前端模块开发流程
- `modules/mcp-guide.md`: MCP 工具平台使用指南（部署模式、工具开发、管理接口）
- `modules/plugin-development.md`: 插件开发与管理指南（生命周期、CLI、多租户集成）
- `frontend-backend/boundary.md`: 前后端契约与字段类型约束
- `frontend-backend/frontend-rules.md`: 前端代码、状态、路由、样式规范
- `frontend-backend/frontend-utils.md`: 工具函数的强制复用规则
- `examples/README.md`: 示例层总入口
- `memory/project-memory.md`: 记忆层总入口
- `memory/long-term/`: 长期记忆
- `memory/business/`: 业务需求记忆

## 任务→必读文档 路由表

接到任务先按本表确定必读，再按需扩展（路径相对 `aiDoc/`）：

| 任务类型 | 必读文档 |
|---|---|
| 新建后端模块 / 新增后端接口 | `modules/module-development.md`、`modules/backend-layer-rules.md`、`examples/backend/*` |
| 新建前端页面 / 前端功能 | `modules/module-development.md`（前端部分）、`frontend-backend/frontend-rules.md`、`frontend-backend/frontend-utils.md`、`examples/frontend/*` |
| 前后端契约变更 / 字段对接 | `frontend-backend/boundary.md`、`modules/backend-layer-rules.md`（响应/分页结构） |
| MCP 工具开发 / 调用 | `modules/mcp-guide.md` |
| 插件开发 / 多租户 | `modules/plugin-development.md`、`relations/system-map.md` |
| 项目结构 / 技术栈 / 依赖答疑 | `relations/repo-profile.md`、`relations/system-map.md` |
| 开发流程 / 提交规范 / 分支 | `relations/development-workflow.md` |
| 数据库迁移 / 模型变更 | `modules/backend-layer-rules.md`（Model 层）、`relations/development-workflow.md`（迁移命令） |
| 工具函数复用 / 不重复造轮子 | `frontend-backend/frontend-utils.md`、`examples/frontend/utils-usage-example.md` |
| 看示例 / 不确定如何组织某层代码 | `examples/README.md` + 对应 `examples/backend/*` 或 `examples/frontend/*` |
| 用户提出新业务需求（任意） | `memory/business/TEMPLATE.md`、`memory/project-memory.md`（必更新索引） |
| 跨任务长期偏好沉淀 | `memory/long-term/README.md` |
| 权限 / 数据范围 / 多租户相关 | `modules/plugin-development.md`、`frontend-backend/boundary.md`（status 桥接）、`memory/business/` 中相关历史记录 |

## 维护原则

- 稳定规则放这里，不放到工具私有目录里
- 临时会话草稿不要入库，只有变成长期知识时才记录
- 适用于所有 AI 的项目级规则，先写进 `AGENTS.MD`
- 细节说明再拆到 `aiDoc/` 对应子目录
- 新增/删除 `aiDoc/` 子文档时，必须同步更新本文件「常用入口」与路由表，否则等于未入库
- 只要用户提出业务需求，就要同步更新 `memory/business/`
