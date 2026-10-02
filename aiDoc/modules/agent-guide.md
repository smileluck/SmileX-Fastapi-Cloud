# AI 智能体模块（agent）

## 概述

`backend/modules/agent/` 是参考 SmileX-Admin-Gin 移植的 LLM 底座，提供：模型供应商 → 模型 →
Agent 三层配置管理、OpenAI 兼容协议 SSE 流式对话、function calling（内置工具 + 外部 MCP
服务器远程工具）、提示词技能包、多会话与 token 用量统计。前端页面在 `frontend/src/views/agent/`。

与 MCP 的关系：本模块是**客户端消费侧**（`sys_mcp_server` 记录外部 MCP 服务器接入，Agent
绑定其工具参与对话）；既有 `mcp-platform/` 是**服务端托管侧**（本项目自己提供 MCP 工具给
Claude/Cursor 等客户端），两者互补不冲突。

## 目录结构

```
modules/agent/
├── router.py            # prefix="/admin/agent"，main.py 注册
├── core/
│   ├── crypto.py        # 域隔离 AES-256-GCM（smilex-agent: / smilex-mcp:），与 Gin 密文互解
│   ├── llm_client.py    # OpenAI 兼容客户端（httpx，非流式 + 流式 + ListModels）
│   ├── tool_registry.py # 本地工具注册表（内置 now / get_server_status）
│   ├── mcp_client.py    # JSON-RPC 2.0 客户端（streamable_http + 旧版 SSE 双协议）
│   ├── mcp_manager.py   # 会话池（10min 空闲过期）+ 工具清单缓存（5min TTL）
│   └── chat_stream.py   # SSE 对话编排（消息拼装 + 工具循环 + 落库 + 用量）
├── services/            # 7 个 service（provider/model/agent/skill/mcp_server/conversation/usage）
├── schemas/             # Pydantic schema
├── endpoints/           # provider / model / agent / chat / mcp / skill
└── tasks.py             # agent.cleanup_usage 用量清理定时任务
```

## 数据表（9 张）

| 表 | 说明 | 关键约束 |
|---|---|---|
| sys_agent_provider | 供应商（base_url + api_key 密文/掩码） | code 唯一；下有模型禁删 |
| sys_agent_model | 模型 | (provider_id, name) 唯一；被 Agent 引用禁删 |
| sys_agent | 智能体（tools/skills 为 JSON 文本列） | code 唯一；软删归档 |
| sys_agent_conversation | 会话（本人数据，agent_name 冗余） | 强制 user_id 过滤 |
| sys_agent_conversation_msg | 消息流水 | 随会话物理删除 |
| sys_agent_usage_log | 用量流水 | 按保留期定时清理 |
| sys_mcp_server | 外部 MCP 接入（token 密文/掩码） | code 唯一禁冒号；被工具引用禁删 |
| sys_skill / sys_skill_file | 技能包（主指令 + 附属文件） | files 整体替换；路径正则防穿越 |

## SSE 对话契约（跨栈）

- 端点：`POST /admin/agent/chat/agents/{id}/stream`（StreamingResponse，非统一响应包裹）
- 响应头：`text/event-stream; charset=utf-8`、`Cache-Control: no-cache`、`X-Accel-Buffering: no`
- 帧格式：`event: <name>\ndata: <单行 JSON>\n\n`，事件类型：
  - `meta`（首帧）：agent/model/conversation 信息
  - `delta`：`{delta, finish_reason, usage}` 逐 token；末帧 delta 为空串携带合并 usage
  - `tool`：`{tool_calls: [{id, name, arguments, result, error}]}`（执行后独立帧）
  - `error`：`{message}`（中断）
- 保活：每 15s 一条 `: ping` 注释帧（前端按空行分帧，忽略 `:` 开头行）
- 前端消费：`fetch` + `ReadableStream` 手写解析（axios 不支持流式），`AbortController` 停止
- 请求体：`{messages: [{role: user|assistant, content}], conversation_id?}`；system 由
  Agent 配置注入，前端不可传（防注入）

## 关键防护数值

| 项 | 值 |
|---|---|
| 工具循环轮数上限 | 5 |
| system prompt 总量 | 60KB 截断 |
| 工具结果回传 | 8KB 截断 |
| 本地 / MCP 工具执行超时 | 10s / 60s |
| 单服务 MCP 工具定义拉取预算 | 10s（失败跳过不阻断对话） |
| 对话限流 | 20 次/min/用户 |
| MCP 连通测试限流 | 10 次/min/用户 |
| 历史消息 | 1-50 条，单条 ≤4000 字符 |
| LLM 上游超时 | 总 120s / 建连 10s |

## 工具绑定格式

- 内置工具：注册表名（如 `now`、`get_server_status`）
- MCP 远程工具：库存格式 `mcp:<server_code>:<tool_name>`；下发给上游时转为
  `mcp__<code>__<tool>`（OpenAI 函数名不允许冒号），chat_stream 内用 resolver 字典双向映射，
  不靠字符串拆解

## 配置

```env
# .env.{env}
AGENT__CRYPTO_KEY=            # 密钥加密材料，空则回退 JWT__SECRET_KEY
AGENT__USAGE_RETENTION_DAYS=0 # 用量流水保留天数，0=永久
```

更换回退密钥后旧密文不可解（表现为 decrypt_failed），重新保存密钥即恢复。

## 扩展内置工具

实现 `modules.agent.core.tool_registry.Tool` 子类（`def_()` 返回元信息 + `execute(args_json)`
返回文本），在 `ToolRegistry.__init__` 注册。业务模块也可在运行时调
`get_tool_registry().register(tool)`。
