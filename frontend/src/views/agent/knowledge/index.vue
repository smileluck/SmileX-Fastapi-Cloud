<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteKnowledge, fetchGetKnowledgeList, fetchRebuildKnowledge } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import KnowledgeDocsDrawer from './modules/knowledge-docs-drawer.vue';
import KnowledgeOperateDrawer from './modules/knowledge-operate-drawer.vue';
import KnowledgeSearch from './modules/knowledge-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Agent.KnowledgeSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetKnowledgeList(searchParams),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.page = params.page;
    searchParams.page_size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      align: 'center',
      width: 48
    },
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: $t('page.agent.knowledge.name'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'code',
      title: $t('page.agent.knowledge.code'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'embedding_model_name',
      title: $t('page.agent.knowledge.embeddingModel'),
      align: 'center',
      minWidth: 140,
      ellipsis: { tooltip: true },
      render: row => row.embedding_model_name || '-'
    },
    {
      key: 'doc_count',
      title: $t('page.agent.knowledge.docCount'),
      align: 'center',
      width: 90,
      render: row =>
        row.doc_count > 0 ? (
          <NTag size="small" type="info">
            {row.doc_count}
          </NTag>
        ) : (
          '-'
        )
    },
    {
      key: 'chunk_count',
      title: $t('page.agent.knowledge.chunkCount'),
      align: 'center',
      width: 90,
      render: row =>
        row.chunk_count > 0 ? (
          <NTag size="small" type="success">
            {row.chunk_count}
          </NTag>
        ) : (
          '-'
        )
    },
    {
      key: 'status',
      title: $t('page.agent.knowledge.status'),
      align: 'center',
      width: 90,
      render: row => {
        if (row.status === null || row.status === undefined) return null;
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = $t(enableStatusRecord[row.status]);
        return <NTag type={tagMap[row.status]}>{label}</NTag>;
      }
    },
    {
      key: 'updated_at',
      title: $t('page.agent.knowledge.updatedAt'),
      align: 'center',
      minWidth: 160,
      render: row => row.updated_at || '-'
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 220,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('knowledge:edit') && (
            <NButton type="primary" text size="small" onClick={() => openDocs(row)}>
              {$t('page.agent.knowledge.docs')}
            </NButton>
          )}
          {hasAuth('knowledge:edit') && (
            <NPopconfirm onPositiveClick={() => handleRebuild(row.id)}>
              {{
                default: () => $t('page.agent.knowledge.rebuildConfirm'),
                trigger: () => (
                  <NButton type="warning" text size="small">
                    {$t('page.agent.knowledge.rebuild')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          )}
          {hasAuth('knowledge:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('knowledge:delete') && (
            <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
              {{
                default: () => $t('common.confirmDelete'),
                trigger: () => (
                  <NButton type="error" text size="small">
                    {$t('common.delete')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          )}
        </div>
      )
    }
  ]
});

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, checkedRowKeys, onDeleted, onBatchDeleted } =
  useTableOperate(data, 'id', getData);

// 文档管理抽屉
const docsDrawerVisible = ref(false);
const docsRow = ref<Api.Agent.Knowledge | null>(null);

function openDocs(row: Api.Agent.Knowledge) {
  docsRow.value = row;
  docsDrawerVisible.value = true;
}

function onDocsChanged() {
  getData();
}

async function handleRebuild(id: number) {
  const { error } = await fetchRebuildKnowledge(id);
  if (!error) {
    message.success($t('page.agent.knowledge.rebuildStarted'));
    getData();
  }
}

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteKnowledge(Number(id));
    if (error) {
      console.error('Batch delete knowledge failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteKnowledge(id);
  if (!error) {
    onDeleted();
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <KnowledgeSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.agent.knowledge.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="knowledge:add"
          delete-auth="knowledge:delete"
          @add="handleAdd"
          @delete="handleBatchDelete"
          @refresh="getData"
        />
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1300"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <KnowledgeOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
      <KnowledgeDocsDrawer v-model:visible="docsDrawerVisible" :row-data="docsRow" @changed="onDocsChanged" />
    </NCard>
  </div>
</template>

<style scoped></style>
