<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteAgent, fetchGetAgentList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import AgentOperateDrawer from './modules/agent-operate-drawer.vue';
import AgentSearch from './modules/agent-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Agent.AgentSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetAgentList(searchParams),
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
      title: $t('page.agent.agents.name'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'code',
      title: $t('page.agent.agents.code'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'model_name',
      title: $t('page.agent.agents.model'),
      align: 'center',
      minWidth: 160,
      render: row =>
        row.model_name ? `${row.provider_name ? `${row.provider_name} / ` : ''}${row.model_name}` : '-'
    },
    {
      key: 'tools',
      title: $t('page.agent.agents.tools'),
      align: 'center',
      minWidth: 140,
      render: row =>
        row.tools.length > 0 ? (
          <NTag size="small" type="info">
            {row.tools.length}
          </NTag>
        ) : (
          '-'
        )
    },
    {
      key: 'skills',
      title: $t('page.agent.agents.skills'),
      align: 'center',
      minWidth: 120,
      render: row =>
        row.skills.length > 0 ? (
          <NTag size="small" type="success">
            {row.skills.length}
          </NTag>
        ) : (
          '-'
        )
    },
    {
      key: 'temperature',
      title: $t('page.agent.agents.temperature'),
      align: 'center',
      width: 100,
      render: row => (row.temperature > 0 ? row.temperature : '-')
    },
    {
      key: 'status',
      title: $t('page.agent.agents.status'),
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
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 140,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('agent:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('agent:delete') && (
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

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteAgent(Number(id));
    if (error) {
      console.error('Batch delete agents failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteAgent(id);
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
    <AgentSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.agent.agents.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="agent:add"
          delete-auth="agent:delete"
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
        :scroll-x="1200"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <AgentOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData" @submitted="getDataByPage" />
    </NCard>
  </div>
</template>

<style scoped></style>
