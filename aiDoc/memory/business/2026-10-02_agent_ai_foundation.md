# AI 智能体底座（Agent + MCP 客户端 + 技能包）

## 需求描述

参考 SmileX-Admin-Gin 项目，移植其最核心的差异功能——AI 智能体底座：
模型供应商 → 模型 → Agent 三层 LLM 配置管理、OpenAI 兼容协议 SSE 流式对话 Playground、
function calling（内置工具 + 外部 MCP 服务器远程工具）、提示词技能包注入 system prompt、
多会话管理与 token 用量统计。

## 状态

已完成

## 涉及范围

### 后端（`backend/modules/agent/`，独立大模块，前缀 `/admin/agent`）

- **9 张新表**（迁移 `d2d73eede47a`）：`sys_agent_provider` / `sys_agent_model` / `sys_agent` /
  `sys_agent_conversation` / `sys_agent_conversation_msg` / `sys_agent_usage_log` /
  `sys_mcp_server` / `sys_skill` / `sys_skill_file`。
  tools/skills 为 JSON 文本列（非关系表）；关联全部逻辑引用（应用层 COUNT 预检删除保护）。
- **core 层**：`crypto.py`（域隔离 AES-256-GCM，`key=SHA256(domain+material)`，域前缀
  `smilex-agent:` / `smilex-mcp:`，与 Gin 密文格式互解；material 取 `AGENT.CRYPTO_KEY` 回退
  `JWT.SECRET_KEY`）；`llm_client.py`（零 SDK OpenAI 兼容客户端，httpx 流式 SSE 解析、
  tool_calls 按 index 聚合、`stream_options.include_usage` 末帧用量、120s/10s 超时分层）；
  `tool_registry.py`（内置 now / get_server_status）；`mcp_client.py`（自研 JSON-RPC 2.0 客户端，
  streamable_http + 旧版 SSE 双协议握手）；`mcp_manager.py`（进程内会话池 10min 空闲过期 +
  工具清单缓存 5min TTL）；`chat_stream.py`（SSE 对话编排）。
- **SSE 帧协议**（与 Gin 一致）：`event: meta|delta|tool|error` + 单行 JSON data；
  15s `: ping` 保活（`_KeepAliveIterator` 用 shield 防__anext__被取消）；
  `X-Accel-Buffering: no`。落库时机：上游接受请求后才落 user 消息；流结束（含中断）
  try/finally 聚合落 assistant 消息 + 用量流水。
- **关键防护数值**（照搬 Gin）：工具循环 ≤5 轮；system prompt 60KB 截断；工具结果 8KB 截断；
  本地工具 10s / MCP 工具 60s 超时；单服务工具定义拉取预算 10s；对话限流 20 次/min/用户；
  MCP 测试限流 10 次/min/用户；历史消息 1-50 条、单条 ≤4000 字符、仅 user/assistant 角色
  （防 system 注入）。
- **业务规则**：供应商下有模型禁删、模型被 Agent 引用禁删、MCP/技能被绑定禁删（JSON 列
  LIKE 匹配）；软删事务内唯一列归档 `值#id`；chat 前三级启用校验（Agent→Model→Provider）；
  会话强制 user_id 过滤、不支持跨 Agent 追加；MCP 工具名 `mcp:<code>:<tool>` ↔
  下发函数名 `mcp__<code>__<tool>` resolver 双向映射。
- **配置**：`AGENT` 配置组（CRYPTO_KEY / USAGE_RETENTION_DAYS）；定时任务
  `agent.cleanup_usage`（每日 04:20 按保留期清理用量流水）；错误码 11051-11070；
  i18n zh-CN/en-US 全量（error.agent/mcp_server/skill + agent 模块段）。
- **菜单种子**（迁移 `0006`，照 0004 模式）：「智能体」CATALOG + 6 菜单（providers/agents/
  chat/usage/mcp-servers/skills）+ 27 个 BUTTON 权限码；不分配角色，运维勾选。

### 前端（`frontend/src/views/agent/`）

- 6 页面：providers（密钥掩码 + 连通测试 + 拉上游模型）、agents（模型下拉 + 工具分组多选 +
  技能多选）、chat（Playground：会话侧栏 + markdown-it/highlight.js 渲染 + 工具调用折叠卡片 +
  AbortController 停止）、usage（ECharts 日用量趋势 + 统计卡片）、mcp-servers（双协议 + Token
  掩码 + 握手测试）、skills（主指令 + 附属文件列表编辑）。
- SSE 消费：`service/api/agent.ts` 的 `streamAgentChat`——fetch + ReadableStream 手写解析
  （axios 不支持流式），按空行分帧、event 分发、忽略 `: ping` 注释行。
- 类型：`typings/api/agent.d.ts`（Api.Agent 命名空间）；i18n：route + page.agent 段（zh/en）
  + `app.d.ts` Schema 同步；新依赖 markdown-it + highlight.js。

## 约束与备注

- **MCP 双形态并存**：本模块是「客户端消费侧」（接入外部 MCP 服务器供 Agent 调用工具），
  与既有 `mcp-platform/`（服务端工具托管，`/admin/sys/mcp` 管理）定位互补不冲突；
  前端菜单 `agent_mcp-servers` 与后者区分。
- **索引命名坑**：`sys_agent.model_id` 的自动索引名 `ix_sys_agent_model_id` 与
  `sys_agent_model` 表的 id 索引同名冲突（PG 索引名全库唯一），已显式改名
  `ix_sys_agent_model_ref`（模型 `__table_args__` Index 声明）。
- **流内 DB 会话**：chat_stream 生成器内部经 `db_manager.get_session()` 自管会话，
  不复用 endpoint 的请求级 session（避免流式响应期间依赖注入生命周期问题）。
- alembic autogenerate 会带出历史漂移噪音（removed index/column），迁移文件已手工精简为
  仅含 9 张新表。
