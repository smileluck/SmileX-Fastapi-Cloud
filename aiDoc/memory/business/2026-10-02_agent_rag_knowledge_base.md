<!-- last-updated: 2026-10-02 -->
# Agent RAG 知识库

## 需求描述

为 AI 智能体模块新增 RAG 知识库能力：管理员创建知识库、上传文档（解析 → 切片 → 向量化 → 入库），
Agent 绑定知识库后在对话时自动检索相关知识并注入上下文。明确要求：**初期轻便**（不引入重型基础设施，
优先 pgvector + 复用现有 LLM 客户端/APScheduler/三层配置）、**后续可扩展升级**（存储/解析/切片/检索
分层抽象，可演进到混合检索、rerank、外挂向量库）。明确不走 SFT 微调路线。

## 状态

已完成开发（后端 + 前端 + 迁移 b9cd09e3fcc6 已落库；待 Qdrant 部署联调）

## 涉及范围

### 后端

- `modules/agent/`：新增 knowledge 相关 endpoints/services/schemas、core 下新增
  解析/切片/向量存储(Qdrant httpx 直调)/检索组件、`llm_client.py` 扩展 embeddings 接口
- `database/models/sys/`：新增 sys_agent_knowledge / sys_agent_knowledge_doc /
  sys_agent_knowledge_chunk 三表（chunk 不存向量，仅元数据）；sys_agent_model 加 model_type
  （chat/embedding/rerank）；sys_agent 加 knowledge_ids
- `chat_stream.py`：build_system_prompt 注入检索结果
- 依赖：pypdf、python-docx；部署侧 +1 Qdrant 服务（单二进制 systemd 或 docker）
- 对账定时任务挂 agent/tasks.py

### 前端

- `views/agent/knowledge/`：知识库管理页（列表 + 文档上传 + 状态轮询 + 检索测试）
- Agent 编辑页：知识库多选绑定
- 模型管理页：model_type 区分 chat/embedding/rerank

## 约束与备注

- **向量存储选型定稿 Qdrant（轻量独立向量库，httpx 直调 REST 零 SDK）**，评审过程：
  pgvector 方案（零新服务但绑定 PG、需一次定维度迁移）→ 用户倾向独立向量库 → 折中轻量方案。
  排除嵌入式（Chroma embedded/LanceDB/sqlite-vec，Gunicorn 多 worker 并发不安全）与重型
  （Milvus 依赖 etcd/MinIO）；Qdrant 每知识库一 collection（kb_{id}，不同库可用不同 embedding
  模型，删库=drop collection），point id=chunk 雪花 ID，payload 存 doc_id/kb_id/chunk_index/content
- 双写一致性：chunk 元数据与状态机在 PG，向量在 Qdrant；幂等重跑（重处理前按 doc_id 清残留）、
  删除顺序先 Qdrant 后 PG、APScheduler 对账兜底（PG 为准）
- 文档处理为状态机（pending/processing/completed/failed），初期 asyncio.create_task
  后台处理，不上 Celery；僵尸 processing 超时复位
- 检索结果注入 system prompt（query 取最后一条 user 消息），受现有 60KB 截断保护；
  阶段 2 预留工具式检索（search_knowledge）与 SSE citation 帧
- embedding 模型复用 provider/model 三层配置，以 model_type 区分用途；知识库级锁定
  embedding 模型，换模型走全量 rebuild

## 相关文件

- `backend/modules/agent/`（现有底座）
- `aiDoc/modules/agent-guide.md`
- 设计方案见本记忆「设计方案」节（待实现后回填 aiDoc/modules/agent-guide.md）

## 记录日期

2026-10-02
