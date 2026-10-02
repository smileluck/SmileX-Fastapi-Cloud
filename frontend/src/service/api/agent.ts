import { getServiceBaseURL } from '@/utils/service';
import { getLocale } from '@/locales';
import { getAuthorization } from '@/service/request/shared';
import { request } from '../request';
import { enableStatusToBoolean } from '@/utils/status';

const isHttpProxy = import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y';
const { baseURL } = getServiceBaseURL(import.meta.env, isHttpProxy);

/**
 * 智能体 SSE 流式对话（fetch + ReadableStream 手写解析，axios 不支持流式响应）。
 *
 * 帧协议：event: meta | delta | tool | error，data 为单行 JSON；
 * 每 15s 可能收到 ": ping" 注释行（忽略）。
 */
export async function streamAgentChat(
  agentId: number,
  payload: { messages: { role: 'user' | 'assistant'; content: string }[]; conversation_id?: number | null },
  handlers: {
    onMeta?: (meta: Api.Agent.ChatMetaFrame) => void;
    onDelta?: (delta: Api.Agent.ChatDeltaFrame) => void;
    onTool?: (tool: Api.Agent.ChatToolFrame) => void;
    onError?: (error: Api.Agent.ChatErrorFrame) => void;
  },
  signal?: AbortSignal
): Promise<void> {
  const response = await fetch(`${baseURL}/admin/agent/chat/agents/${agentId}/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: getAuthorization() || '',
      'Accept-Language': getLocale()
    },
    body: JSON.stringify(payload),
    signal
  });

  if (!response.ok || !response.body) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      message = data?.msg || message;
    } catch {
      // ignore
    }
    handlers.onError?.({ message });
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  const handleFrame = (frameText: string) => {
    // 帧格式：event: <name>\ndata: <json>
    let eventName = '';
    let dataText = '';
    for (const line of frameText.split('\n')) {
      if (line.startsWith('event:')) {
        eventName = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        dataText = line.slice(5).trim();
      }
    }
    if (!eventName || !dataText) return;
    let data: any;
    try {
      data = JSON.parse(dataText);
    } catch {
      return;
    }
    if (eventName === 'meta') handlers.onMeta?.(data);
    else if (eventName === 'delta') handlers.onDelta?.(data);
    else if (eventName === 'tool') handlers.onTool?.(data);
    else if (eventName === 'error') handlers.onError?.(data);
  };

  // 按空行分帧（SSE 规范）
  const processBuffer = (flush = false) => {
    let separator: number;
    // eslint-disable-next-line no-cond-assign
    while ((separator = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, separator);
      buffer = buffer.slice(separator + 2);
      handleFrame(frame);
    }
    if (flush && buffer.trim() && !buffer.trim().startsWith(':')) {
      handleFrame(buffer);
    }
  };

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      processBuffer();
    }
    buffer += decoder.decode();
    processBuffer(true);
  } catch (error: any) {
    if (error?.name !== 'AbortError') {
      handlers.onError?.({ message: error?.message || 'network error' });
    }
  }
}

/** ---- 模型供应商 ---- */
export function fetchGetProviderList(params?: Api.Agent.ProviderSearchParams) {
  return request<Api.Agent.ProviderList>({
    url: '/admin/agent/providers/list',
    method: 'get',
    params
  });
}

export function fetchGetProvider(providerId: number) {
  return request<Api.Agent.Provider>({
    url: `/admin/agent/providers/${providerId}`,
    method: 'get'
  });
}

export function fetchCreateProvider(provider: Api.Agent.ProviderCreate) {
  return request<Api.Agent.Provider>({
    url: '/admin/agent/providers/add',
    method: 'post',
    data: { ...provider, status: enableStatusToBoolean(provider.status) }
  });
}

export function fetchUpdateProvider(providerId: number, provider: Api.Agent.ProviderUpdate) {
  return request<Api.Agent.Provider>({
    url: `/admin/agent/providers/${providerId}`,
    method: 'put',
    data: { ...provider, status: provider.status ? enableStatusToBoolean(provider.status) : undefined }
  });
}

export function fetchDeleteProvider(providerId: number) {
  return request<void>({
    url: `/admin/agent/providers/${providerId}`,
    method: 'delete'
  });
}

export function fetchTestProvider(providerId: number, modelId = 0) {
  return request<Api.Agent.ConnectTestResult>({
    url: `/admin/agent/providers/${providerId}/test`,
    method: 'post',
    data: { model_id: modelId }
  });
}

export function fetchGetProviderRemoteModels(providerId: number) {
  return request<{ models: string[] }>({
    url: `/admin/agent/providers/${providerId}/remote-models`,
    method: 'get'
  });
}

/** ---- 模型 ---- */
export function fetchGetAgentModelList(params?: Api.Agent.ModelSearchParams) {
  return request<Api.Agent.ModelList>({
    url: '/admin/agent/models/list',
    method: 'get',
    params
  });
}

export function fetchCreateAgentModel(model: Api.Agent.ModelCreate) {
  return request<Api.Agent.Model>({
    url: '/admin/agent/models/add',
    method: 'post',
    data: { ...model, status: enableStatusToBoolean(model.status) }
  });
}

export function fetchUpdateAgentModel(modelId: number, model: Api.Agent.ModelUpdate) {
  return request<Api.Agent.Model>({
    url: `/admin/agent/models/${modelId}`,
    method: 'put',
    data: { ...model, status: model.status ? enableStatusToBoolean(model.status) : undefined }
  });
}

export function fetchDeleteAgentModel(modelId: number) {
  return request<void>({
    url: `/admin/agent/models/${modelId}`,
    method: 'delete'
  });
}

export function fetchTestAgentModel(modelId: number) {
  return request<Api.Agent.ConnectTestResult>({
    url: `/admin/agent/models/${modelId}/test`,
    method: 'post'
  });
}

/** ---- 智能体 ---- */
export function fetchGetAgentList(params?: Api.Agent.AgentSearchParams) {
  return request<Api.Agent.AgentList>({
    url: '/admin/agent/agents/list',
    method: 'get',
    params
  });
}

export function fetchGetAllEnabledAgents() {
  return request<Api.Agent.Agent[]>({
    url: '/admin/agent/agents/all',
    method: 'get'
  });
}

export function fetchGetAgent(agentId: number) {
  return request<Api.Agent.Agent>({
    url: `/admin/agent/agents/${agentId}`,
    method: 'get'
  });
}

export function fetchCreateAgent(agent: Api.Agent.AgentCreate) {
  return request<Api.Agent.Agent>({
    url: '/admin/agent/agents/add',
    method: 'post',
    data: { ...agent, status: enableStatusToBoolean(agent.status) }
  });
}

export function fetchUpdateAgent(agentId: number, agent: Api.Agent.AgentUpdate) {
  return request<Api.Agent.Agent>({
    url: `/admin/agent/agents/${agentId}`,
    method: 'put',
    data: { ...agent, status: agent.status ? enableStatusToBoolean(agent.status) : undefined }
  });
}

export function fetchDeleteAgent(agentId: number) {
  return request<void>({
    url: `/admin/agent/agents/${agentId}`,
    method: 'delete'
  });
}

export function fetchGetToolGroups() {
  return request<Api.Agent.ToolGroup[]>({
    url: '/admin/agent/agents/tools/groups',
    method: 'get'
  });
}

/** ---- 会话 ---- */
export function fetchGetConversations(agentId?: number) {
  return request<Api.Agent.Conversation[]>({
    url: '/admin/agent/chat/conversations',
    method: 'get',
    params: agentId ? { agent_id: agentId } : undefined
  });
}

export function fetchCreateConversation(agentId: number) {
  return request<Api.Agent.Conversation>({
    url: '/admin/agent/chat/conversations',
    method: 'post',
    data: { agent_id: agentId }
  });
}

export function fetchGetConversationMessages(conversationId: number) {
  return request<Api.Agent.ConversationMessage[]>({
    url: `/admin/agent/chat/conversations/${conversationId}/messages`,
    method: 'get'
  });
}

export function fetchRenameConversation(conversationId: number, title: string) {
  return request<Api.Agent.Conversation>({
    url: `/admin/agent/chat/conversations/${conversationId}`,
    method: 'put',
    data: { title }
  });
}

export function fetchDeleteConversation(conversationId: number) {
  return request<void>({
    url: `/admin/agent/chat/conversations/${conversationId}`,
    method: 'delete'
  });
}

/** ---- 用量 ---- */
export function fetchGetUsageSummary(days = 7, onlyMine = false) {
  return request<Api.Agent.UsageSummary>({
    url: '/admin/agent/chat/usage',
    method: 'get',
    params: { days, only_mine: onlyMine }
  });
}

/** ---- MCP 服务器 ---- */
export function fetchGetMcpServerList(params?: Api.Agent.McpServerSearchParams) {
  return request<Api.Agent.McpServerList>({
    url: '/admin/agent/mcp-servers/list',
    method: 'get',
    params
  });
}

export function fetchGetMcpServer(serverId: number) {
  return request<Api.Agent.McpServer>({
    url: `/admin/agent/mcp-servers/${serverId}`,
    method: 'get'
  });
}

export function fetchCreateMcpServer(server: Api.Agent.McpServerCreate) {
  return request<Api.Agent.McpServer>({
    url: '/admin/agent/mcp-servers/add',
    method: 'post',
    data: { ...server, status: enableStatusToBoolean(server.status) }
  });
}

export function fetchUpdateMcpServer(serverId: number, server: Api.Agent.McpServerUpdate) {
  return request<Api.Agent.McpServer>({
    url: `/admin/agent/mcp-servers/${serverId}`,
    method: 'put',
    data: { ...server, status: server.status ? enableStatusToBoolean(server.status) : undefined }
  });
}

export function fetchDeleteMcpServer(serverId: number) {
  return request<void>({
    url: `/admin/agent/mcp-servers/${serverId}`,
    method: 'delete'
  });
}

export function fetchTestMcpServer(serverId: number) {
  return request<Api.Agent.McpServerTestResult>({
    url: `/admin/agent/mcp-servers/${serverId}/test`,
    method: 'post'
  });
}

/** ---- 技能 ---- */
export function fetchGetSkillList(params?: Api.Agent.SkillSearchParams) {
  return request<Api.Agent.SkillList>({
    url: '/admin/agent/skills/list',
    method: 'get',
    params
  });
}

export function fetchGetAllEnabledSkills() {
  return request<Api.Agent.Skill[]>({
    url: '/admin/agent/skills/all',
    method: 'get'
  });
}

export function fetchGetSkill(skillId: number) {
  return request<Api.Agent.Skill>({
    url: `/admin/agent/skills/${skillId}`,
    method: 'get'
  });
}

export function fetchCreateSkill(skill: Api.Agent.SkillCreate) {
  return request<Api.Agent.Skill>({
    url: '/admin/agent/skills/add',
    method: 'post',
    data: { ...skill, status: enableStatusToBoolean(skill.status) }
  });
}

export function fetchUpdateSkill(skillId: number, skill: Api.Agent.SkillUpdate) {
  return request<Api.Agent.Skill>({
    url: `/admin/agent/skills/${skillId}`,
    method: 'put',
    data: { ...skill, status: skill.status ? enableStatusToBoolean(skill.status) : undefined }
  });
}

export function fetchDeleteSkill(skillId: number) {
  return request<void>({
    url: `/admin/agent/skills/${skillId}`,
    method: 'delete'
  });
}
