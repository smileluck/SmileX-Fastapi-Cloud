<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import {
  fetchDeleteKnowledgeDoc,
  fetchGetKnowledgeDocList,
  fetchReprocessKnowledgeDoc,
  fetchSearchKnowledge,
  fetchUploadKnowledgeDocs
} from '@/service/api';
import { $t } from '@/locales';

defineOptions({
  name: 'KnowledgeDocsDrawer'
});

interface Props {
  rowData?: Api.Agent.Knowledge | null;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', {
  default: false
});

interface Emits {
  (e: 'changed'): void;
}

const emit = defineEmits<Emits>();

const docs = ref<Api.Agent.KnowledgeDoc[]>([]);
const loading = ref(false);
const uploading = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

// 处理中有文档时轮询状态（2s），全部完成后停止并通知父级刷新计数
let pollTimer: ReturnType<typeof setInterval> | null = null;

const docStatusMap: Record<number, { type: NaiveUI.ThemeColor; label: App.I18n.I18nKey }> = {
  0: { type: 'default', label: 'page.agent.knowledge.docStatus.pending' },
  1: { type: 'info', label: 'page.agent.knowledge.docStatus.processing' },
  2: { type: 'success', label: 'page.agent.knowledge.docStatus.completed' },
  3: { type: 'error', label: 'page.agent.knowledge.docStatus.failed' }
};

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

async function loadDocs() {
  if (!props.rowData) return;
  loading.value = true;
  const { data, error } = await fetchGetKnowledgeDocList(props.rowData.id, { page: 1, page_size: 100 });
  loading.value = false;
  if (!error && data) {
    docs.value = data.records || [];
    schedulePoll();
  }
}

function schedulePoll() {
  const processing = docs.value.some(doc => doc.status === 0 || doc.status === 1);
  if (processing && !pollTimer) {
    pollTimer = setInterval(loadDocs, 2000);
  } else if (!processing && pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
    emit('changed');
  }
}

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer);
});

function triggerUpload() {
  fileInput.value?.click();
}

async function handleUpload(event: Event) {
  const input = event.target as HTMLInputElement;
  const files = Array.from(input.files || []);
  input.value = '';
  if (!files.length || !props.rowData) return;
  uploading.value = true;
  const { error } = await fetchUploadKnowledgeDocs(props.rowData.id, files);
  uploading.value = false;
  if (!error) {
    window.$message?.success($t('page.agent.knowledge.doc.uploadSuccess'));
    await loadDocs();
    emit('changed');
  }
}

async function handleDeleteDoc(docId: number) {
  if (!props.rowData) return;
  const { error } = await fetchDeleteKnowledgeDoc(props.rowData.id, docId);
  if (!error) {
    window.$message?.success($t('page.agent.knowledge.doc.deleteSuccess'));
    await loadDocs();
    emit('changed');
  }
}

async function handleReprocess(docId: number) {
  if (!props.rowData) return;
  const { error } = await fetchReprocessKnowledgeDoc(props.rowData.id, docId);
  if (!error) {
    await loadDocs();
  }
}

/** 检索测试 */
const searchQuery = ref('');
const searchTopK = ref(5);
const searchHits = ref<Api.Agent.KnowledgeSearchHit[]>([]);
const searching = ref(false);

async function handleSearch() {
  if (!props.rowData || !searchQuery.value.trim()) return;
  searching.value = true;
  const { data, error } = await fetchSearchKnowledge(props.rowData.id, searchQuery.value.trim(), searchTopK.value);
  searching.value = false;
  if (!error) {
    searchHits.value = data || [];
  }
}

const kbName = computed(() => props.rowData?.name || '');

watch(visible, val => {
  if (val) {
    searchQuery.value = '';
    searchHits.value = [];
    loadDocs();
  } else if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="720">
    <NDrawerContent :title="$t('page.agent.knowledge.doc.title', { name: kbName })" :native-scrollbar="false" closable>
      <div class="flex-col gap-16px">
        <!-- 上传 -->
        <NCard size="small" :bordered="true">
          <div class="flex items-center gap-12px">
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              multiple
              accept=".txt,.md,.pdf,.docx"
              @change="handleUpload"
            />
            <NButton type="primary" :loading="uploading" size="small" @click="triggerUpload">
              {{ $t('page.agent.knowledge.doc.upload') }}
            </NButton>
            <span class="text-12px text-gray-400">{{ $t('page.agent.knowledge.doc.uploadTip') }}</span>
          </div>
        </NCard>

        <!-- 文档列表 -->
        <NCard size="small" :bordered="true" :title="$t('page.agent.knowledge.doc.list')">
          <NSpin :show="loading">
            <div v-if="docs.length === 0 && !loading" class="py-24px text-center text-gray-400">
              {{ $t('page.agent.knowledge.doc.empty') }}
            </div>
            <div
              v-for="doc in docs"
              :key="doc.id"
              class="flex items-start gap-8px border-b border-gray-100 py-8px last:border-none"
            >
              <div class="min-w-0 flex-1">
                <div class="flex items-center gap-8px">
                  <span class="truncate" :title="doc.file_name">{{ doc.file_name }}</span>
                  <NTag size="small" :type="docStatusMap[doc.status]?.type || 'default'">
                    {{ $t(docStatusMap[doc.status]?.label || 'page.agent.knowledge.docStatus.pending') }}
                  </NTag>
                </div>
                <div class="mt-2px text-12px text-gray-400">
                  {{ doc.file_type.toUpperCase() }} · {{ formatSize(doc.file_size) }} ·
                  {{ $t('page.agent.knowledge.doc.chunkCount', { count: doc.chunk_count }) }} ·
                  {{ doc.created_at || '-' }}
                </div>
                <div
                  v-if="doc.status === 3 && doc.error_msg"
                  class="mt-2px truncate text-12px text-error"
                  :title="doc.error_msg"
                >
                  {{ doc.error_msg }}
                </div>
              </div>
              <div class="flex shrink-0 items-center gap-4px">
                <NButton
                  v-if="doc.status === 3 || doc.status === 2"
                  text
                  type="primary"
                  size="small"
                  @click="handleReprocess(doc.id)"
                >
                  {{ $t('page.agent.knowledge.doc.reprocess') }}
                </NButton>
                <NPopconfirm @positive-click="handleDeleteDoc(doc.id)">
                  <template #trigger>
                    <NButton text type="error" size="small">
                      {{ $t('common.delete') }}
                    </NButton>
                  </template>
                  {{ $t('common.confirmDelete') }}
                </NPopconfirm>
              </div>
            </div>
          </NSpin>
        </NCard>

        <!-- 检索测试 -->
        <NCard size="small" :bordered="true" :title="$t('page.agent.knowledge.search.title')">
          <div class="flex items-center gap-8px">
            <NInput
              v-model:value="searchQuery"
              :placeholder="$t('page.agent.knowledge.search.placeholder')"
              class="flex-1"
              @keyup.enter="handleSearch"
            />
            <NInputNumber v-model:value="searchTopK" :min="1" :max="20" size="small" class="w-90px" />
            <NButton type="primary" ghost size="small" :loading="searching" @click="handleSearch">
              {{ $t('common.search') }}
            </NButton>
          </div>
          <div v-if="searchHits.length > 0" class="mt-12px flex-col gap-8px">
            <div v-for="(hit, index) in searchHits" :key="index" class="rounded-4px bg-gray-50 p-8px">
              <div class="mb-4px flex items-center gap-8px text-12px text-gray-500">
                <NTag size="small" type="success">{{ hit.score.toFixed(4) }}</NTag>
                <span>{{ $t('page.agent.knowledge.search.chunkIndex', { index: hit.chunk_index }) }}</span>
              </div>
              <div class="max-h-120px overflow-auto text-13px leading-20px">{{ hit.content }}</div>
            </div>
          </div>
        </NCard>
      </div>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
