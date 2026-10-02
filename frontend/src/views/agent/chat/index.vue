<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue';
import MarkdownIt from 'markdown-it';
import hljs from 'highlight.js';
import {
  fetchCreateConversation,
  fetchDeleteConversation,
  fetchGetAllEnabledAgents,
  fetchGetConversationMessages,
  fetchGetConversations,
  fetchRenameConversation,
  streamAgentChat
} from '@/service/api';
import { $t } from '@/locales';

defineOptions({
  name: 'AgentChat'
});

/** markdown 渲染器：默认 html:false 转义内联 HTML，代码块走 highlight.js */
const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch {
        // fallthrough
      }
    }
    return '';
  }
});

interface ToolCallView {
  id: string;
  name: string;
  arguments: string;
  result: string;
  error: string;
}

interface ChatMessageView {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  totalTokens?: number;
  toolCalls?: ToolCallView[];
  streaming?: boolean;
  error?: string;
}

const agents = ref<Api.Agent.Agent[]>([]);
const currentAgentId = ref<number | null>(null);
const conversations = ref<Api.Agent.Conversation[]>([]);
const currentConversationId = ref<number | null>(null);
const messages = ref<ChatMessageView[]>([]);
const inputText = ref('');
const sending = ref(false);
const messageScrollRef = ref<HTMLElement | null>(null);
let abortController: AbortController | null = null;

const currentAgent = computed(() => agents.value.find(a => a.id === currentAgentId.value) || null);

async function loadAgents() {
  const { error, data } = await fetchGetAllEnabledAgents();
  if (!error && data) {
    agents.value = data;
    if (data.length > 0 && !currentAgentId.value) {
      currentAgentId.value = data[0].id;
      await loadConversations();
    }
  }
}

async function loadConversations() {
  const { error, data } = await fetchGetConversations();
  if (!error && data) {
    conversations.value = data;
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messageScrollRef.value) {
      messageScrollRef.value.scrollTop = messageScrollRef.value.scrollHeight;
    }
  });
}

async function handleAgentChange() {
  currentConversationId.value = null;
  messages.value = [];
  await loadConversations();
}

async function handleNewConversation() {
  if (!currentAgentId.value) return;
  const { error, data } = await fetchCreateConversation(currentAgentId.value);
  if (!error && data) {
    conversations.value.unshift(data);
    await openConversation(data.id);
  }
}

async function openConversation(conversationId: number) {
  currentConversationId.value = conversationId;
  messages.value = [];
  const { error, data } = await fetchGetConversationMessages(conversationId);
  if (!error && data) {
    messages.value = data.map(m => ({
      id: `db-${m.id}`,
      role: m.role,
      content: m.content,
      totalTokens: m.total_tokens
    }));
    scrollToBottom();
  }
}

async function handleDeleteConversation(conversationId: number) {
  const { error } = await fetchDeleteConversation(conversationId);
  if (!error) {
    conversations.value = conversations.value.filter(c => c.id !== conversationId);
    if (currentConversationId.value === conversationId) {
      currentConversationId.value = null;
      messages.value = [];
    }
  }
}

async function handleRenameConversation(conversationId: number) {
  const conversation = conversations.value.find(c => c.id === conversationId);
  if (!conversation) return;
  const title = window.prompt($t('page.agent.chat.renamePrompt'), conversation.title || '');
  if (title === null || !title.trim()) return;
  const { error, data } = await fetchRenameConversation(conversationId, title.trim());
  if (!error && data) {
    conversation.title = data.title;
  }
}

function stopStreaming() {
  abortController?.abort();
  abortController = null;
  sending.value = false;
  const last = messages.value[messages.value.length - 1];
  if (last?.streaming) {
    last.streaming = false;
  }
}

async function handleSend() {
  const content = inputText.value.trim();
  if (!content || sending.value || !currentAgentId.value) return;

  // 若当前会话不属于所选 Agent（或不持久化模式），新建会话
  let conversationId = currentConversationId.value;
  const conversation = conversations.value.find(c => c.id === conversationId);
  if (conversation && conversation.agent_id !== currentAgentId.value) {
    conversationId = null;
    currentConversationId.value = null;
  }

  messages.value.push({ id: `u-${Date.now()}`, role: 'user', content });
  const assistantMessage: ChatMessageView = {
    id: `a-${Date.now()}`,
    role: 'assistant',
    content: '',
    toolCalls: [],
    streaming: true
  };
  messages.value.push(assistantMessage);
  inputText.value = '';
  sending.value = true;
  scrollToBottom();

  abortController = new AbortController();

  // 上下文消息（最多 50 条）
  const history = messages.value
    .filter(m => !m.streaming && !m.error)
    .slice(-50)
    .map(m => ({ role: m.role, content: m.content }));

  await streamAgentChat(
    currentAgentId.value,
    {
      messages: history,
      conversation_id: conversationId
    },
    {
      onMeta: meta => {
        if (meta.conversation_id && !currentConversationId.value) {
          currentConversationId.value = meta.conversation_id;
          loadConversations();
        }
      },
      onDelta: delta => {
        if (delta.delta) {
          assistantMessage.content += delta.delta;
          scrollToBottom();
        }
        if (delta.usage?.total_tokens) {
          assistantMessage.totalTokens = delta.usage.total_tokens;
        }
      },
      onTool: tool => {
        assistantMessage.toolCalls = [...(assistantMessage.toolCalls || []), ...tool.tool_calls];
        scrollToBottom();
      },
      onError: error => {
        assistantMessage.error = error.message;
      }
    },
    abortController.signal
  );

  assistantMessage.streaming = false;
  sending.value = false;
  abortController = null;
  scrollToBottom();
}

function renderMarkdown(content: string): string {
  return md.render(content || '');
}

onMounted(() => {
  loadAgents();
});
</script>

<template>
  <div class="min-h-500px h-full flex gap-16px overflow-hidden lt-sm:flex-col">
    <!-- 左侧：Agent 选择 + 会话列表 -->
    <NCard :bordered="false" size="small" class="w-280px shrink-0 card-wrapper lt-sm:w-full">
      <template #header>
        {{ $t('page.agent.chat.conversations') }}
      </template>
      <template #header-extra>
        <NButton size="small" type="primary" ghost :disabled="!currentAgentId" @click="handleNewConversation">
          {{ $t('page.agent.chat.newConversation') }}
        </NButton>
      </template>
      <div class="flex flex-col gap-12px">
        <NSelect
          v-model:value="currentAgentId"
          :options="agents.map(a => ({ label: a.name, value: a.id }))"
          :placeholder="$t('page.agent.chat.selectAgent')"
          @update:value="handleAgentChange"
        />
        <div class="max-h-480px overflow-auto flex flex-col gap-4px">
          <div
            v-for="conversation in conversations.filter(c => !currentAgentId || c.agent_id === currentAgentId)"
            :key="conversation.id"
            class="group cursor-pointer rounded-4px px-8px py-6px transition-colors hover:bg-primary-100"
            :class="{ 'bg-primary-50': currentConversationId === conversation.id }"
            @click="openConversation(conversation.id)"
          >
            <div class="flex items-center justify-between gap-4px">
              <NEllipsis class="flex-1 text-14px">{{ conversation.title || $t('page.agent.chat.untitled') }}</NEllipsis>
              <div class="hidden gap-2px group-hover:flex">
                <NButton text size="tiny" type="primary" @click.stop="handleRenameConversation(conversation.id)">
                  <template #icon>
                    <icon-ant-design:edit-outlined />
                  </template>
                </NButton>
                <NPopconfirm @positive-click="handleDeleteConversation(conversation.id)">
                  <template #trigger>
                    <NButton text size="tiny" type="error" @click.stop>
                      <template #icon>
                        <icon-ant-design:delete-outlined />
                      </template>
                    </NButton>
                  </template>
                  {{ $t('common.confirmDelete') }}
                </NPopconfirm>
              </div>
            </div>
            <div class="text-12px opacity-50">
              {{ conversation.agent_name }} · {{ conversation.last_msg_at || conversation.created_at }}
            </div>
          </div>
          <NEmpty v-if="conversations.length === 0" :description="$t('page.agent.chat.noConversations')" />
        </div>
      </div>
    </NCard>

    <!-- 右侧：消息流 + 输入 -->
    <NCard :bordered="false" size="small" class="flex-1 card-wrapper flex flex-col overflow-hidden">
      <template #header>
        <div class="flex items-center gap-8px">
          <span>{{ currentAgent ? currentAgent.name : $t('page.agent.chat.title') }}</span>
          <NTag v-if="currentAgent?.model_name" size="small" type="info">
            {{ currentAgent.provider_name ? `${currentAgent.provider_name} / ` : '' }}{{ currentAgent.model_name }}
          </NTag>
          <NTag v-if="currentAgent && currentAgent.tools.length > 0" size="small">
            {{ $t('page.agent.agents.tools') }} × {{ currentAgent.tools.length }}
          </NTag>
        </div>
      </template>
      <div ref="messageScrollRef" class="flex-1 overflow-auto pr-8px">
        <NEmpty v-if="messages.length === 0" class="py-80px" :description="$t('page.agent.chat.emptyHint')" />
        <div class="flex flex-col gap-16px py-8px">
          <div v-for="message in messages" :key="message.id" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
            <div
              class="max-w-85% rounded-8px px-12px py-8px"
              :class="message.role === 'user' ? 'bg-primary-100 dark:bg-primary-50' : 'bg-gray-100 dark:bg-dark'"
            >
              <!-- 工具调用折叠卡片 -->
              <NCollapse v-if="message.toolCalls && message.toolCalls.length > 0" class="mb-8px">
                <NCollapseItem :title="$t('page.agent.chat.toolCalls')" name="tools">
                  <div v-for="call in message.toolCalls" :key="call.id + call.name" class="mb-8px flex flex-col gap-2px">
                    <div class="flex items-center gap-8px">
                      <NTag size="small" :type="call.error ? 'error' : 'success'">{{ call.name }}</NTag>
                      <span v-if="call.error" class="text-error text-12px">{{ call.error }}</span>
                    </div>
                    <pre class="bg-gray-800 rounded-4px px-8px py-4px text-12px whitespace-pre-wrap break-all text-white">{{ call.arguments }}</pre>
                    <pre v-if="call.result" class="bg-gray-200 dark:bg-gray-700 rounded-4px px-8px py-4px text-12px whitespace-pre-wrap break-all">{{ call.result }}</pre>
                  </div>
                </NCollapseItem>
              </NCollapse>
              <!-- 消息正文（assistant 走 markdown，user 纯文本） -->
              <div v-if="message.content">
                <div v-if="message.role === 'assistant'" class="markdown-content text-14px break-words" v-html="renderMarkdown(message.content)"></div>
                <div v-else class="whitespace-pre-wrap text-14px">{{ message.content }}</div>
              </div>
              <div v-else-if="message.streaming && !message.toolCalls?.length" class="flex items-center gap-4px text-14px opacity-60">
                <NSpin :size="14" />
                {{ $t('page.agent.chat.thinking') }}
              </div>
              <div v-if="message.error" class="mt-4px text-13px text-error">{{ message.error }}</div>
              <div v-if="message.totalTokens" class="mt-2px text-right text-11px opacity-40">{{ message.totalTokens }} tokens</div>
            </div>
          </div>
        </div>
      </div>
      <div class="border-t-1px border-gray-200 pt-12px dark:border-gray-700">
        <div class="flex items-end gap-8px">
          <NInput
            v-model:value="inputText"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 6 }"
            :placeholder="$t('page.agent.chat.inputPlaceholder')"
            maxlength="4000"
            :disabled="!currentAgentId"
            @keydown.enter.exact.prevent="handleSend"
          />
          <NButton v-if="sending" type="error" @click="stopStreaming">
            {{ $t('page.agent.chat.stop') }}
          </NButton>
          <NButton v-else type="primary" :loading="sending" :disabled="!inputText.trim() || !currentAgentId" @click="handleSend">
            {{ $t('page.agent.chat.send') }}
          </NButton>
        </div>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.markdown-content :deep(pre) {
  background: #282c34;
  color: #abb2bf;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
}

.markdown-content :deep(code) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 13px;
}

.markdown-content :deep(p code) {
  background: rgba(127, 127, 127, 0.15);
  border-radius: 3px;
  padding: 1px 4px;
}

.markdown-content :deep(table) {
  border-collapse: collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid rgba(127, 127, 127, 0.3);
  padding: 4px 8px;
}
</style>
