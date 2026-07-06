---
description: 分析项目代码库并生成 AGENTS.MD + aiDoc/ 分层约束文档体系
---

# 项目约束文档生成器

你是项目约束文档生成器。你的任务是分析当前项目的代码库，然后按照 aiDoc 标准结构生成一套完整的 AI 协作约束文档。

用户提示：$ARGUMENTS

---

## 运行模式

根据 `$ARGUMENTS` 解析运行模式：

| 参数 | 行为 |
|---|---|
| （空） | 全量生成：探测项目并生成/覆盖所有 aiDoc 文件 |
| `--incremental` | 增量更新：读取已有 aiDoc，对比代码变化，只更新过时的文件 |
| `--scope backend` | 只重新生成 `modules/backend-layer-rules.md`、`examples/backend/` 等后端相关文件 |
| `--scope frontend` | 只重新生成 `frontend-backend/frontend-rules.md`、`frontend-backend/frontend-utils.md`、`examples/frontend/` |
| `--scope relations` | 只重新生成 `relations/` 下 3 个文件 |
| `--scope memory` | 只重新生成 `memory/` 下文件 |
| `--scope core` | 只重新生成 `AGENTS.MD` + `aiDoc/README.md`（加载契约与路由层） |
| `--dry-run` | 只输出阶段 1 探测结果和生成计划，不写文件 |

**增量更新规则**（`--incremental` 时适用）：
- 每个文件头部维护 `<!-- last-updated: YYYY-MM-DD -->` 注释
- 先读取已有 aiDoc 文件，再用 `git diff` 判断自上次更新以来哪些代码目录有变化
- 只重新生成受影响范围内的文件
- 用户手动调优过的内容（非 AI 生成标记）应尽量保留
- 路由表是跨文件元数据：若 `aiDoc/` 下新增/删除文件，即便老文件 last-updated 未变，也必须重生成 `aiDoc/README.md` 的「常用入口」与任务路由表
- AGENTS.md 调用逻辑同步：「高层速查（任务族→aiDoc 区域）」与「何时重新生成 aiDoc」两节属于调用逻辑层。只要 `aiDoc/` 下区域（modules/、frontend-backend/、examples/、relations/、memory/ 等）有增删，即便 AGENTS.md 自身 last-updated 未变，也必须同步这两节

---

## 执行流程

严格按照以下三个阶段执行。每个阶段完成后向用户简要报告进度。

### 阶段 1：项目探测

#### 1.1 项目结构探测

- 列出根目录下的顶层目录和关键文件
- 识别是否有前端/后端/全栈目录分离
- 扫描每个顶层目录的子目录结构（深度 2-3 层即可）

#### 1.2 技术栈识别

读取以下文件（如存在）提取技术栈信息：

- `package.json` / `pnpm-workspace.yaml` / `lerna.json` → 前端依赖和脚本
- `pyproject.toml` / `requirements.txt` / `Pipfile` / `setup.py` → Python 后端依赖
- `go.mod` / `go.sum` → Go 后端依赖
- `pom.xml` / `build.gradle` → Java 后端依赖
- `Cargo.toml` → Rust 后端依赖
- `.nvmrc` / `.node-version` / `.python-version` → 运行时版本
- `Dockerfile` / `docker-compose.yml` → 部署配置

**框架识别策略**：优先从依赖列表自动匹配，而非硬编码特征。扫描 `dependencies`/`devDependencies`/`install_requires` 中是否包含以下关键词：

| 依赖关键词 | 框架/技术 |
|---|---|
| `fastapi`, `uvicorn` | FastAPI |
| `django` | Django |
| `flask` | Flask |
| `hono` | Hono |
| `fastify` | Fastify |
| `express`, `koa`, `nestjs` | Node.js 后端 |
| `gin`, `gorm`, `fiber` | Go (Gin/Fiber) |
| `spring-boot` | Spring Boot |
| `actix`, `axum` | Rust (Actix/Axum) |
| `vue`, `vite` + `.vue` | Vue |
| `react`, `.jsx`/`.tsx` | React |
| `angular` | Angular |
| `svelte`, `@sveltejs` | Svelte/SvelteKit |
| `next` | Next.js |
| `nuxt` | Nuxt |

未覆盖的框架通过依赖名 + 目录结构综合判断。

#### 1.3 代码模式探测

- 后端：读取 2-3 个典型的 endpoint/controller、service、model 文件，识别分层模式
- 前端：读取 2-3 个典型的页面组件、API 封装、状态管理文件，识别组件模式
- 识别响应/请求的统一格式（如果有）
- 识别认证/鉴权机制
- 识别数据库访问模式（ORM 原生/sqlalchemy/typeorm/gorm/prisma 等）

**示例模块选择策略**（优先级从高到低）：

1. CRUD 完整的模块：同时拥有 model + schema + service + endpoint
2. 最近修改的模块：更能反映当前代码风格（用 `git log --format="" --name-only` 辅助判断）
3. 特性丰富的模块：包含分页、认证、关联关系等特性，覆盖面更广

#### 1.4 项目类型判定

根据探测结果，判定项目类型：

- **fullstack**：同时有前后端代码
- **backend-only**：仅有后端代码
- **frontend-only**：仅有前端代码

### 阶段 2：按模板生成文件

根据阶段 1 的探测结果，按以下顺序生成文件。

**自适应规则**：
- **backend-only**：跳过 `frontend-backend/frontend-rules.md`、`frontend-backend/frontend-utils.md`、`examples/frontend/`，`boundary.md` 改为 API 接口契约
- **frontend-only**：跳过 `modules/backend-layer-rules.md`、`examples/backend/`，`boundary.md` 改为 API 消费契约
- **fullstack**：生成全部文件

**并行生成**：同一并行组内的文件可以同时生成，组间按顺序执行。

| 顺序 | 并行组 | 文件 |
|---|---|---|
| 1 | — | `AGENTS.MD` |
| 2 | — | `aiDoc/README.md` |
| 3 | A | `aiDoc/relations/repo-profile.md`、`aiDoc/relations/development-workflow.md`、`aiDoc/relations/system-map.md` |
| 4 | B | `aiDoc/modules/backend-layer-rules.md`、`aiDoc/modules/module-development.md` |
| 5 | C | `aiDoc/frontend-backend/boundary.md`、`aiDoc/frontend-backend/frontend-rules.md`、`aiDoc/frontend-backend/frontend-utils.md` |
| 6 | D | `aiDoc/examples/backend/*.md`（model、schema、service、endpoint、router） |
| 7 | D | `aiDoc/examples/frontend/*.md`（api、view、utils-usage） |
| 8 | E | `aiDoc/examples/README.md` |
| 9 | F | `aiDoc/memory/` 全部文件 |

`--scope` 模式下只生成对应范围的并行组。

每生成一个并行组后，向用户简要报告进度。

---

#### 文件 1：`AGENTS.MD`

项目根目录的 AI 协作规则唯一真源。

内容要求：

```markdown
<!-- last-updated: YYYY-MM-DD -->
# AGENTS.MD

## 目的

本文件是本仓库内 AI 协作规则的唯一真源，只承载所有 AI 必须始终知道的最小高层规则。细节按任务路由到 `aiDoc/`。

## 加载模型

- **L0 自动加载**：根 `CLAUDE.md` 通过 `@AGENTS.md` 在每次会话自动 import 本文件。本文件不展开细节、不列文档清单。
- **L1 任务路由**：`aiDoc/README.md` 是文档索引 + "任务→必读文档"路由表的唯一真源。接到任务先查路由表，决定本次读哪些子文档。
- **L2 按需深读**：路由表指向的 `aiDoc/` 具体子文档。
- **冲突优先级**（仓库内任务）：`AGENTS.MD` > `aiDoc/README.md` > aiDoc 子文档 > 工具适配文件。

## 各工具加载方式

| 工具 | 加载方式 |
|---|---|
| Claude Code | 根 `CLAUDE.md @AGENTS.md` 原生 import；`.claude/commands/` 只放项目命令，不生成规则适配文件 |
| Trae | `.trae/rules/project_rules.md` 薄适配层指向 `AGENTS.MD` |
| Cursor / Codex / 其他 | 若不支持 `@import`，参照 `.trae` 模式新建薄适配文件，只写入口指针，不复制规则正文 |

任何工具的私有目录都不应保存项目级规则副本。

## 仓库概览

[根据探测结果列出根目录和关键子目录的职责。工具目录（.claude/.trae 等）不在本节列，其加载方式见上表]

## 工程规则

### 架构
[根据实际分层模式填写，如 Endpoint -> Service -> Model]

### 前后端协作 / API 契约
[根据实际响应格式和约定填写]

### 模块与目录
[根据实际目录结构填写]

### 示例文档
[固定文本：aiDoc/examples/ 是讲解型示例层]

### 记忆规则
[固定文本：long-term/ 稳定偏好，business/ 每次业务需求]

### 文档维护
[固定文本：高层规则在 AGENTS.MD，细节在 aiDoc/；AGENTS.MD 只保留「任务族→aiDoc 区域」的高层速查指针（见「文档索引与任务路由」），「任务→必读文档」详细路由表唯一维护于 aiDoc/README.md，不在 AGENTS.MD 罗列完整清单，避免双份维护导致口径漂移]

### 代码读取约束
[固定文本：不读 node_modules/、.venv/、__pycache__/、vendor/ 等]

## 文档索引与任务路由

### 高层速查（任务族 → aiDoc 区域）

[固定结构，按粗粒度任务族指向 aiDoc 区域，每族一行，不展开到具体文件。根据项目实际存在的 aiDoc 区域调整。示例：

| 任务族 | 优先查阅区域 |
|---|---|
| 后端模块/接口开发 | `aiDoc/modules/`、`aiDoc/examples/backend/` |
| 前端页面/功能开发 | `aiDoc/frontend-backend/`、`aiDoc/examples/frontend/` |
| 前后端契约/字段对接 | `aiDoc/frontend-backend/boundary.md` |
| 仓库结构/技术栈/流程 | `aiDoc/relations/` |
| 业务需求记录 | `aiDoc/memory/business/` |

只做高层指向；详细到具体文件的「任务→必读文档」路由表见下方。]

### 详细路由

「任务→必读文档」详细路由表、常用入口字典统一维护在 `aiDoc/README.md`。本文件只放高层速查，避免双份维护导致口径漂移。冲突时以本文件为准。

## 何时重新生成 aiDoc（调用 generate-aidoc）

[固定文本：出现以下情况时调用 `.claude/commands/generate-aidoc.md` 重新生成或增量更新文档体系：
- 架构较大变化：分层调整、新增/删除顶层目录、技术栈替换
- 新增/删除后端模块或前端页面，导致 `aiDoc/modules/`、`aiDoc/examples/`、`aiDoc/relations/system-map.md` 与代码脱节
- `aiDoc/` 子文档新增/删除，导致 `aiDoc/README.md` 详细路由表与本文件高层速查失效
- 路由表或示例与真实代码明显漂移

小改动（单接口、单页面调整）无需整体重生成，用 `--incremental` 或 `--scope <area>` 局部更新即可。生成后必须按命令末尾的验证步骤核验索引与路径一致性。]
```

---

#### 文件 2：`aiDoc/README.md`

文档索引和使用指南。

内容要求：

```markdown
<!-- last-updated: YYYY-MM-DD -->
# aiDoc

aiDoc/ 是本仓库的结构化 AI 文档层，用于把长期有效的项目上下文从工具目录中抽离出来，并按主题拆分成可维护的约束文档。

## 使用方式

1. `AGENTS.MD` 已随根 `CLAUDE.md @AGENTS.md` 自动加载（L0），始终生效
2. 接到任务先查本文件「任务→必读文档」路由表，确定必读（L1）
3. 不清楚某个文档讲什么时，再翻「常用入口」字典（L1）
4. 按路由表打开 `aiDoc/` 下具体子文档深读（L2）

不再把项目级规则复制到工具私有目录；Claude Code 走 `@import`，Trae 等走薄适配指针（见 `AGENTS.MD` 的「各工具加载方式」）。

## 目录说明

- relations/: 仓库结构、技术栈、依赖关系、开发流程
- modules/: 后端分层规则、模块职责
- frontend-backend/: 前后端契约、前端规范、工具函数复用规则（如适用）
- examples/: 讲解型示例
- memory/: AI 记忆层

## 常用入口

[每个文件一行描述：文档路径 + 一句话用途，作为"按文档查字典"的索引]

## 任务→必读文档 路由表

[按任务类型给出必读文档列表，路径相对 aiDoc/。示例行：

| 任务类型 | 必读文档 |
|---|---|
| 新建后端模块 / 接口 | modules/module-development.md、modules/backend-layer-rules.md、examples/backend/* |
| 新建前端页面 / 功能 | frontend-backend/frontend-rules.md、frontend-backend/frontend-utils.md、examples/frontend/* |
| 前后端契约 / 字段对接 | frontend-backend/boundary.md |
| 用户提出新业务需求 | memory/business/TEMPLATE.md、memory/project-memory.md（必更新索引） |

根据项目实际存在的 aiDoc 子文档补全所有任务类型。]

## 维护原则

- 稳定规则放这里，不放到工具私有目录里
- 临时会话草稿不要入库
- 项目级规则先写进 AGENTS.MD，细节拆到 aiDoc/
- 新增/删除 aiDoc/ 子文档时，必须同步更新本文件「常用入口」与任务路由表，否则等于未入库
```

---

#### 文件 3：`aiDoc/relations/repo-profile.md`

项目定位与技术栈。

内容要求：

- **项目定位**：根据 package.json/pyproject.toml 的 name/description、README.md、用户提示推断
- **后端技术栈**：列出语言、框架、ORM、数据库、缓存、迁移工具、认证方式等
- **前端技术栈**：列出框架、构建工具、UI 库、状态管理、路由、样式方案等
- **包管理**：uv/pip/npm/pnpm/yarn/go mod 等
- **核心特性**：表格列出项目特有的关键特性（统一响应格式、ID 策略、认证方式等）

---

#### 文件 4：`aiDoc/relations/development-workflow.md`

开发流程与提交规范。

内容要求：

- **推荐开发顺序**：根据实际分层设计开发步骤
- **前后端协作**：后端先接口、前端并行、联调验证
- **分支策略**：main/develop/feature/hotfix
- **提交规范**：type(scope): description 格式
- **环境与依赖**：具体的安装、启动、迁移命令
- **API 文档**：Swagger/ReDoc 地址（如有）

---

#### 文件 5：`aiDoc/relations/system-map.md`

系统架构与组件关系。

内容要求：

- **根目录职责**：表格列出每个顶层目录的用途
- **后端分层关系**：根据实际分层模式绘制（如 Router → Controller → Service → Model）
- **核心基础设施**：表格列出基础设施目录及其职责
- **前端数据流**（如有前端）：API 封装 → 状态管理 → 路由 → 视图 → 类型声明
- **模块对应关系**：后端模块 ↔ 前端页面的映射
- **配置文件**：列出关键配置文件及其用途

---

#### 文件 6：`aiDoc/modules/backend-layer-rules.md`（有后端时生成）

后端分层约束。

内容要求：

- **总原则**：严格分层，不跨层调用
- **Model 层**：基类继承、字段声明方式、表名规则、存放位置
- **Schema/DTO 层**：请求/响应基类、序列化规则、验证方式
- **Service 层**：纯业务逻辑、方法签名模式、异常处理、查询优化
- **Controller/Endpoint 层**：参数提取、响应格式化、分页处理
- **Router 层**：路由注册方式
- **错误码分配**（如有）：列出已使用的错误码范围
- **所有规则必须引用实际代码中的类名和文件路径**

---

#### 文件 7：`aiDoc/modules/module-development.md`（有后端时生成）

模块开发指南。

内容要求：

- **新建后端模块**：完整步骤（创建目录 → 定义模型 → Schema → Service → Endpoint → Router → 注册 → 迁移）
- **新建前端功能**（如有前端）：完整步骤（定义类型 → API 函数 → i18n → 页面 → 生成路由）
- **设计原则**：自包含、遵循现有模式
- **引用真实的参考文件路径**

---

#### 文件 8：`aiDoc/frontend-backend/boundary.md`（前后端项目适用）

前后端边界与数据契约。

内容要求：

- **责任边界**：后端/前端各自的职责表格
- **统一响应结构**：根据实际代码填写 JSON 结构和字段说明
- **统一分页结构**（如有）：字段说明
- **字段命名规范**：snake_case / camelCase
- **关键类型桥接**：如果有特殊类型转换（如 bool ↔ string），必须详细说明转换流程和涉及的代码位置
- **时间字段**（如有特殊处理）：格式和时区
- **变更规则**和**完成前检查清单**

---

#### 文件 9：`aiDoc/frontend-backend/frontend-rules.md`（有前端时生成）

前端开发规范。

内容要求：

- **基础规则**：HTTP 请求方式、状态管理、路由
- **命名规范**：文件、组件、变量、API 函数的命名约定表格
- **TypeScript/类型要求**（如适用）
- **组件规范**：公共组件/页面组件的位置、Props 定义方式
- **页面规范**：新增页面必须完成的步骤
- **样式规范**：CSS 方案优先级
- **国际化规范**（如有 i18n）
- **环境变量**
- **常用脚本命令**：表格列出
- **代码注释要求**

---

#### 文件 10：`aiDoc/frontend-backend/frontend-utils.md`（有前端时生成）

前端工具函数复用规则。

内容要求：

- **核心原则**：先查现有工具，不重复造轮子
- **关键工具**：列出 src/utils/ 或类似目录下的工具函数，说明用途
- **工作区子包**（如有 monorepo）：列出每个包的职责
- **强制使用场景清单**：表格列出场景和必须使用的工具

---

#### 文件 11：`aiDoc/examples/README.md`

```markdown
# 示例层

aiDoc/examples/ 是讲解型示例层，告诉 AI 每一层应该按什么标准组织和书写。

## 用途

- 示例不是要求逐字复制，而是展示项目标准的代码组织方式
- 当 AI 需要新增某一层文件时，应先阅读对应示例

## 后端开发阅读顺序
[列出后端示例文件]

## 前端开发阅读顺序（如有前端）
[列出前端示例文件]

## 原则

- 仓库真实代码与示例不一致时，以真实代码为准，并更新示例
```

---

#### 文件 12-16：`aiDoc/examples/backend/*.md`（有后端时生成）

为后端的每一层生成一个示例文件：

- `model-example.md`：ORM 模型示例（展示基类继承、字段声明、关联关系）
- `schema-example.md` 或 `dto-example.md`：请求/响应 Schema 示例
- `service-example.md`：Service 层示例（展示方法签名、异常处理）
- `endpoint-example.md` 或 `controller-example.md`：API 端点示例
- `router-example.md`：路由注册示例

每个示例文件格式：

```markdown
<!-- last-updated: YYYY-MM-DD -->
# [层名]示例

## 用途
[说明这个示例展示什么]

## 核心原则
[2-3 条关键规则]

## 示例
[从项目中读取的真实代码示例，去除敏感信息]

## 关键点
[解释示例中的关键设计决策]

## 真实参考文件
- [实际文件路径]
```

**重要**：示例代码必须从项目实际代码中提取，而非凭空编写。如果项目中没有足够的示例代码，基于探测到的模式编写符合项目风格的代码。

---

#### 文件 17-19：`aiDoc/examples/frontend/*.md`（有前端时生成）

- `api-example.md`：API 封装示例
- `view-example.md`：页面组件示例
- `utils-usage-example.md`：工具函数使用示例

格式与后端示例一致。

---

#### 文件 20-24：`aiDoc/memory/` 记忆层

`memory/README.md`：

```markdown
# 记忆层

aiDoc/memory/ 是 AI 的记忆层。

## 目录说明

- long-term/: 长期稳定的用户偏好、协作方式
- business/: 每次用户提出的业务需求记录

## 使用规则

- 用户提出业务需求时，AI 必须新增或更新一条 business/ 记忆
- 沉淀为稳定模式时，提炼到 long-term/
- 临时草稿不入库
```

`memory/project-memory.md`：

```markdown
# 项目记忆索引

## 长期记忆
暂无。

## 业务需求记忆
暂无。

## 维护说明
- 新增记忆时创建文件并更新此索引
- 过时记忆及时清理
```

`memory/long-term/README.md`：

```markdown
# 长期记忆

存放跨任务、跨会话长期有效的用户偏好和协作约束。

## 规则

- 只记录经过多次验证的稳定模式
- 每条记忆包含：规则描述、适用场景、来源
- 过时记忆及时删除
```

`memory/business/README.md`：

```markdown
# 业务需求记忆

存放每次用户提出的业务需求记录。

## 规则

- 用户提出业务需求时，必须新增或更新一条记录
- 使用 TEMPLATE.md 作为新记录模板
- 记录完成后在 project-memory.md 中更新索引

## 需求索引
暂无。
```

`memory/business/TEMPLATE.md`：

```markdown
# 业务需求模板

## 需求描述
<!-- 简要描述需求内容 -->

## 状态
<!-- 待开发 / 开发中 / 已完成 / 已取消 -->

## 涉及范围

### 后端
<!-- 涉及的模块、模型、接口 -->

### 前端
<!-- 涉及的页面、组件、API -->

## 约束与备注
<!-- 特殊的业务规则、限制条件 -->

## 相关文件
<!-- 列出涉及的关键文件路径 -->

## 记录日期
<!-- YYYY-MM-DD -->
```

---

### 阶段 3：工具加载适配

不是每个工具目录都要适配文件——先按工具是否支持 `@import` 分流。原则：规则正文只在 `AGENTS.MD` 与 `aiDoc/`，工具目录只承载该工具的原生加载入口与命令。

#### 3.1 支持 `@import` 的工具（Claude Code 等）

无需生成适配文件。只需确保根 `CLAUDE.md` 含一行 `@AGENTS.md`：
- `.claude/` 目录只放 `commands/`（项目命令），**不生成**规则适配文件
- 若根 `CLAUDE.md` 缺失或不含 `@AGENTS.md`，补一行即可

#### 3.2 不支持 `@import` 的工具（Trae / Cursor / Codex / Copilot 等）

仅对**实际存在**的工具目录生成/更新薄适配文件（不要为不存在的工具硬造目录）。逐个检查已知目录是否存在：`.trae/rules/`、`.cursor/rules/`、`.codex/`、`.github/copilot-instructions.md`、`.windsurf/`、`.aider/`，只对探测到的目录处理。

> 禁止用 `ls -d .*/` 扫描后给每个 `.` 目录都写适配文件——那会诱导生成冗余副本，违反"规则正文单一真源"。

薄适配文件模板（内容只写入口指针，**不含规则正文**）：

```markdown
---
tool: [trae/cursor/codex/copilot/windsurf/aider]
role: compatibility-adapter
canonical_source: /AGENTS.MD
structured_context: /aiDoc
---

# [工具名] 规则适配层

本文件只用于兼容 [工具名] 现有的自动加载路径。

## 真实规则入口

1. /AGENTS.MD
2. /aiDoc/README.md（含"任务→必读文档"路由表，先查表再深读）
3. 路由表指向的 /aiDoc/ 子文档

## 适配层约束

- 不要在这里扩写项目级规则
- 项目级规则变更时，先更新 /AGENTS.MD 与 /aiDoc/，本文件无需改
- 工具目录只保留薄适配层职责
```

#### 3.3 登记到 AGENTS.MD

生成/更新适配文件后，在 `AGENTS.MD` 的「各工具加载方式」表登记该工具的路径与加载方式，保持该表是工具适配状态的唯一索引。

---

## 写作风格要求

所有文档必须遵循以下风格：

1. **简洁指令性语言**：使用"必须"/"应该"/"禁止"，无填充文本
2. **精确路径引用**：每个规则引用实际文件路径和类名/函数名（如 `app/models/common/page.py:PageRequest`）
3. **清晰 Markdown 层次**：使用 `##`/`###` 组织，善用表格
4. **文档间交叉引用**：引用其他 aiDoc 文件时使用相对路径
5. **中文为主**：代码标识符和技术术语保持英文
6. **内容来源真实**：所有技术细节必须来自实际代码探测，不可凭空编造

## 生成完成后的验证

生成全部文件后，**实际执行**以下验证步骤：

### 自动验证（必须执行）

1. **索引完整性**：读取生成的 `aiDoc/README.md`，从「常用入口」与「任务→必读文档」路由表提取所有 aiDoc 路径，用 Glob 逐一确认文件存在（AGENTS.MD 不再列文档索引）
2. **路径真实性**：用 Grep 搜索所有生成文件中引用的代码路径（如 `app/models/xxx.py`），确认引用的文件存在
3. **符号一致性**：用 Grep 搜索 boundary.md 中引用的类名/函数名（如 `PageRequest`、`ResponseModel`），确认在代码中确实存在
4. **示例参考有效性**：提取所有示例文件的"真实参考文件"路径，用 Glob 确认存在
5. **AGENTS.md 调用逻辑同步**：确认 AGENTS.md「高层速查」表覆盖的 aiDoc 区域与实际生成的 `aiDoc/` 子目录一致；确认「何时重新生成 aiDoc」小节存在且触发条件完整

### 报告输出

向用户输出以下内容：

```
## 验证结果

### 通过
- [x] 索引完整性：N/N 文件已索引（基于 aiDoc/README.md 路由表与常用入口）
- [x] 路径真实性：N/N 路径有效
- [x] 符号一致性：N/N 符号已验证
- [x] 示例参考：N/N 参考文件存在
- [x] AGENTS.md 调用逻辑：高层速查表与 aiDoc/ 区域一致，何时重新生成小节存在

### 失败（如有）
- [ ] 路径不存在：xxx
- [ ] 符号未找到：xxx

## 生成文件清单
[列出所有生成/更新的文件及大小]
```
