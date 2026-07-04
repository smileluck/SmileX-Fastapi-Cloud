# AGENTS.MD

## 目的

本文件是本仓库内 AI 协作规则的唯一真源，只承载所有 AI 必须始终知道的最小高层规则。细节按任务路由到 `aiDoc/`。

## 加载模型

本仓库的 AI 上下文分三层加载：

- **L0 自动加载**：根 `CLAUDE.md` 通过 `@AGENTS.md` 在每次会话自动 import 本文件。本文件刻意不展开细节、不列文档清单。
- **L1 任务路由**：`aiDoc/README.md` 是文档索引 + "任务→必读文档"路由表的唯一真源。接到任务先查路由表，决定本次读哪些子文档。
- **L2 按需深读**：路由表指向的 `aiDoc/` 具体子文档。

**冲突优先级**（仓库内任务）：`AGENTS.MD` > `aiDoc/README.md` > aiDoc 子文档 > 工具适配文件。根 `CLAUDE.md` 中除 `@AGENTS.md` import 外的内容属用户全局偏好；与 `AGENTS.MD` 冲突时，仓库内任务以 `AGENTS.MD` 为准。

## 各工具加载方式

| 工具 | 加载方式 |
|---|---|
| Claude Code | 根 `CLAUDE.md @AGENTS.md` 原生 import；`.claude/commands/` 只放项目命令，不生成规则适配文件 |
| Trae | `.trae/rules/project_rules.md` 薄适配层指向 `AGENTS.MD` |
| Cursor / Codex / 其他 | 若不支持 `@import`，参照 `.trae` 模式新建薄适配文件，只写入口指针，不复制规则正文 |

任何工具的私有目录都不应保存项目级规则副本——规则正文只在 `AGENTS.MD` 与 `aiDoc/`。

## 仓库概览

- `backend/`: Python 3.11+ FastAPI + SQLAlchemy 2.0 后端
- `frontend/`: Vue 3 + Vite + NaiveUI 前端
- `aiDoc/`: AI 协作文档层（按任务路由加载，入口见 `aiDoc/README.md`）

各 AI 工具目录（`.claude/`、`.trae/` 等）的加载方式见上文「各工具加载方式」。

## 工程规则

### 架构

- 保持现有后端分层：`Endpoint -> Service -> Model`
- Endpoint 层处理 HTTP 相关逻辑，Service 层不要依赖 FastAPI 请求对象
- 对外接口的 Swagger 注释必须和真实行为保持一致
- 优先沿用项目现有模式，不做无关的大改

### 前后端协作

- 明确请求与响应契约
- 保持统一响应结构：`{ code, msg, data, request_id, err_code }`
- 保持统一分页结构：`{ records, page, page_size, total, total_pages }`
- 前后端字段名和数据类型保持一致
- Status 字段桥接：后端 `bool` → 前端 `"1"` / `"2"` 字符串
- 涉及跨栈边界变更时，同步更新 `aiDoc/frontend-backend/`

### 模块与目录

- 后端模块放在 `backend/modules/<name>/`，含 `endpoints/`、`services/`、`schemas/`、`deps/`
- 前端页面放在 `frontend/src/views/<name>/`
- 稳定的模块职责、入口和边界说明放到 `aiDoc/modules/`

### 示例文档

- `aiDoc/examples/` 是讲解型示例层
- 示例文档不是要求逐字复制，而是告诉 AI 该如何按项目标准组织代码
- 当 AI 需要新增某一层文件时，应先阅读对应示例，再开始实现

### 记忆规则

- `aiDoc/memory/long-term/` 用于记录长期稳定的用户偏好、协作方式和跨任务约束
- `aiDoc/memory/business/` 用于记录每次用户提出的业务需求
- 这里的"业务需求"指新增或修改模块、接口、页面、流程、业务规则等项目需求
- 当用户提出业务需求时，AI 必须新增或更新一条 `business` 记忆，并同步更新需求索引
- 当某条业务需求沉淀成长期稳定偏好时，再提炼到 `long-term`

### 文档维护

- `AGENTS.MD` 只保留高层、稳定、跨任务的规则
- 细节上下文写入 `aiDoc/`
- 结构关系放在 `aiDoc/relations/`
- 示例写法放在 `aiDoc/examples/`
- 长期记忆与业务记忆放在 `aiDoc/memory/`
- "任务→必读文档"路由表唯一维护于 `aiDoc/README.md`，不在 `AGENTS.MD` 罗列文档清单
- 若项目级 AI 规则发生变化，先改 `AGENTS.MD`，再按需更新「各工具加载方式」

### 代码读取约束

- 无论什么情况，都不要直接读取 `node_modules/`、`.venv/`、`__pycache__/` 中的代码
- 如需了解第三方库行为，优先查看项目源码中的调用方式、锁文件、配置文件、官方文档或包的公开类型/说明文件

## 文档索引与任务路由

详细索引、常用入口与"任务→必读文档"路由表，统一维护在 `aiDoc/README.md`。本文件不再罗列，避免双份维护导致口径漂移。冲突时以本文件为准。

