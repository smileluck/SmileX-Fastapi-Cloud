/**
 * Namespace Agent
 *
 * 智能体（AI 底座）模块：backend api module "agent"
 */
declare namespace Api {
  namespace Agent {
    type CommonSearchParams = Pick<Common.PaginatingCommonParams, 'page' | 'page_size'>;

    /** 模型供应商 */
    interface Provider {
      id: number;
      name: string;
      code: string;
      base_url: string;
      api_key_mask: string | null;
      has_api_key: boolean;
      protocol: string;
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    type ProviderSearchParams = CommonType.RecordNullable<
      Pick<Provider, 'name' | 'code' | 'status'> & CommonSearchParams
    >;

    type ProviderList = Common.PaginatingQueryRecord<Provider>;

    interface ProviderCreate {
      name: string;
      code: string;
      base_url: string;
      api_key?: string;
      protocol?: string;
      remark?: string;
      status: Common.EnableStatus;
    }

    interface ProviderUpdate {
      name?: string;
      base_url?: string;
      api_key?: string;
      protocol?: string;
      remark?: string;
      status?: Common.EnableStatus;
    }

    /** 模型 */
    interface Model {
      id: number;
      provider_id: number;
      provider_name?: string | null;
      name: string;
      model_type: ModelType;
      display_name: string | null;
      context_window: number;
      max_output: number;
      supports_tools: boolean;
      input_price: number;
      output_price: number;
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    /** 模型类型：chat-对话 / embedding-向量化 / rerank-重排 */
    type ModelType = 'chat' | 'embedding' | 'rerank';

    type ModelSearchParams = CommonType.RecordNullable<
      Pick<Model, 'provider_id' | 'name' | 'status'> & CommonSearchParams
    >;

    type ModelList = Common.PaginatingQueryRecord<Model>;

    interface ModelCreate {
      provider_id: number;
      name: string;
      model_type?: ModelType;
      display_name?: string;
      context_window?: number;
      max_output?: number;
      supports_tools?: boolean;
      input_price?: number;
      output_price?: number;
      remark?: string;
      status: Common.EnableStatus;
    }

    interface ModelUpdate {
      model_type?: ModelType;
      display_name?: string;
      context_window?: number;
      max_output?: number;
      supports_tools?: boolean;
      input_price?: number;
      output_price?: number;
      remark?: string;
      status?: Common.EnableStatus;
    }

    /** 智能体 */
    interface Agent {
      id: number;
      name: string;
      code: string;
      model_id: number;
      model_name?: string | null;
      provider_name?: string | null;
      system_prompt: string | null;
      temperature: number;
      top_p: number;
      max_tokens: number;
      tools: string[];
      skills: string[];
      knowledge_ids: number[];
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    type AgentSearchParams = CommonType.RecordNullable<Pick<Agent, 'name' | 'code' | 'status'> & CommonSearchParams>;

    type AgentList = Common.PaginatingQueryRecord<Agent>;

    interface AgentCreate {
      name: string;
      code: string;
      model_id: number;
      system_prompt?: string;
      temperature?: number;
      top_p?: number;
      max_tokens?: number;
      tools?: string[];
      skills?: string[];
      knowledge_ids?: number[];
      remark?: string;
      status: Common.EnableStatus;
    }

    interface AgentUpdate {
      name?: string;
      model_id?: number;
      system_prompt?: string;
      temperature?: number;
      top_p?: number;
      max_tokens?: number;
      tools?: string[];
      skills?: string[];
      knowledge_ids?: number[];
      remark?: string;
      status?: Common.EnableStatus;
    }

    /** 工具分组（Agent 表单数据源） */
    interface ToolGroup {
      group: string;
      label: string;
      tools: { name: string; description: string }[];
    }

    /** 会话 */
    interface Conversation {
      id: number;
      agent_id: number;
      agent_name: string;
      title: string;
      last_msg_at: string | null;
      created_at: string | null;
    }

    interface ConversationMessage {
      id: number;
      conversation_id: number;
      role: 'user' | 'assistant';
      content: string;
      total_tokens: number;
      created_at: string | null;
    }

    /** 用量统计 */
    interface UsageDailyPoint {
      date: string;
      calls: number;
      prompt_tokens: number;
      completion_tokens: number;
      total_tokens: number;
    }

    interface UsageSummary {
      days: number;
      total_calls: number;
      total_prompt_tokens: number;
      total_completion_tokens: number;
      total_tokens: number;
      trend: UsageDailyPoint[];
    }

    /** MCP 服务器 */
    interface McpServer {
      id: number;
      name: string;
      code: string;
      transport: 'streamable_http' | 'sse';
      base_url: string;
      token_mask: string | null;
      has_token: boolean;
      headers: { key: string; value: string }[];
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    type McpServerSearchParams = CommonType.RecordNullable<
      Pick<McpServer, 'name' | 'code' | 'transport' | 'status'> & CommonSearchParams
    >;

    type McpServerList = Common.PaginatingQueryRecord<McpServer>;

    interface McpServerCreate {
      name: string;
      code: string;
      transport: string;
      base_url: string;
      token?: string;
      headers?: { key: string; value: string }[];
      remark?: string;
      status: Common.EnableStatus;
    }

    interface McpServerUpdate {
      name?: string;
      transport?: string;
      base_url?: string;
      token?: string;
      headers?: { key: string; value: string }[];
      remark?: string;
      status?: Common.EnableStatus;
    }

    interface McpServerTestResult {
      server_id: number;
      server_code: string;
      ok: boolean;
      server_name?: string | null;
      server_version?: string | null;
      protocol_version?: string | null;
      tool_count?: number | null;
      latency_ms: number;
      error?: string | null;
    }

    /** 技能 */
    interface Skill {
      id: number;
      name: string;
      code: string;
      description: string | null;
      instruction: string;
      files: SkillFile[];
      file_count: number;
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    interface SkillFile {
      id: number;
      path: string;
      content: string;
      file_size: number;
    }

    type SkillSearchParams = CommonType.RecordNullable<Pick<Skill, 'name' | 'code' | 'status'> & CommonSearchParams>;

    type SkillList = Common.PaginatingQueryRecord<Skill>;

    interface SkillCreate {
      name: string;
      code: string;
      description?: string;
      instruction: string;
      files?: { path: string; content: string }[];
      remark?: string;
      status: Common.EnableStatus;
    }

    interface SkillUpdate {
      name?: string;
      description?: string;
      instruction?: string;
      files?: { path: string; content: string }[];
      remark?: string;
      status?: Common.EnableStatus;
    }

    /** 连通测试结果（供应商/模型共用） */
    interface ConnectTestResult {
      ok: boolean;
      content?: string | null;
      model?: string | null;
      latency_ms: number;
      prompt_tokens: number;
      completion_tokens: number;
      error?: string | null;
    }

    /** 知识库 */
    interface Knowledge {
      id: number;
      name: string;
      code: string;
      description: string | null;
      embedding_model_id: number;
      embedding_model_name?: string | null;
      doc_count: number;
      chunk_count: number;
      remark: string | null;
      status: Common.EnableStatus;
      created_at: string | null;
      updated_at: string | null;
    }

    type KnowledgeSearchParams = CommonType.RecordNullable<
      Pick<Knowledge, 'name' | 'code' | 'status'> & CommonSearchParams
    >;

    type KnowledgeList = Common.PaginatingQueryRecord<Knowledge>;

    interface KnowledgeCreate {
      name: string;
      code: string;
      description?: string;
      embedding_model_id: number;
      remark?: string;
      status: Common.EnableStatus;
    }

    interface KnowledgeUpdate {
      name?: string;
      description?: string;
      remark?: string;
      status?: Common.EnableStatus;
    }

    /** 知识库文档处理状态：0-待处理 1-处理中 2-完成 3-失败 */
    type KnowledgeDocStatus = 0 | 1 | 2 | 3;

    interface KnowledgeDoc {
      id: number;
      knowledge_id: number;
      file_name: string;
      file_type: string;
      file_size: number;
      char_count: number;
      chunk_count: number;
      status: KnowledgeDocStatus;
      error_msg: string | null;
      created_at: string | null;
    }

    type KnowledgeDocSearchParams = CommonType.RecordNullable<
      { file_name?: string; status?: KnowledgeDocStatus } & CommonSearchParams
    >;

    type KnowledgeDocList = Common.PaginatingQueryRecord<KnowledgeDoc>;

    /** 检索测试命中 */
    interface KnowledgeSearchHit {
      kb_id: number;
      kb_name: string;
      doc_id: number;
      chunk_index: number;
      content: string;
      score: number;
    }

    /** SSE 对话帧：meta */
    interface ChatMetaFrame {
      agent_id: number;
      agent_name: string;
      provider_id: number;
      model_id: number;
      model: string;
      conversation_id: number;
    }

    /** SSE 对话帧：delta */
    interface ChatDeltaFrame {
      delta: string;
      finish_reason?: string | null;
      usage?: {
        prompt_tokens: number;
        completion_tokens: number;
        total_tokens: number;
      } | null;
    }

    /** SSE 对话帧：tool */
    interface ChatToolFrame {
      tool_calls: {
        id: string;
        name: string;
        arguments: string;
        result: string;
        error: string;
        latency_ms?: number;
      }[];
    }

    /** SSE 对话帧：error */
    interface ChatErrorFrame {
      message: string;
    }
  }
}
