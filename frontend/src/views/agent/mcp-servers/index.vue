<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteMcpServer, fetchGetMcpServerList, fetchTestMcpServer } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import McpServerOperateDrawer from './modules/mcp-server-operate-drawer.vue';
import McpServerSearch from './modules/mcp-server-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Agent.McpServerSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null,
  transport: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetMcpServerList(searchParams),
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
      title: $t('page.agent.mcpServers.name'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'code',
      title: $t('page.agent.mcpServers.code'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'transport',
      title: $t('page.agent.mcpServers.transport'),
      align: 'center',
      width: 140,
      render: row => (
        <NTag size="small" type={row.transport === 'sse' ? 'warning' : 'info'}>
          {row.transport}
        </NTag>
      )
    },
    {
      key: 'base_url',
      title: $t('page.agent.mcpServers.baseUrl'),
      align: 'center',
      minWidth: 220,
      ellipsis: { tooltip: true }
    },
    {
      key: 'token_mask',
      title: $t('page.agent.mcpServers.token'),
      align: 'center',
      minWidth: 120,
      render: row => row.token_mask || '-'
    },
    {
      key: 'status',
      title: $t('page.agent.mcpServers.status'),
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
      minWidth: 170,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('mcp:server:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('mcp:server:test') && (
            <NButton type="info" text size="small" onClick={() => handleTest(row.id)}>
              {$t('page.agent.mcpServers.test')}
            </NButton>
          )}
          {hasAuth('mcp:server:delete') && (
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
    const { error } = await fetchDeleteMcpServer(Number(id));
    if (error) {
      console.error('Batch delete MCP servers failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteMcpServer(id);
  if (!error) {
    onDeleted();
  }
}

async function handleTest(id: number) {
  message.loading($t('page.agent.mcpServers.testing'));
  const { error, data: result } = await fetchTestMcpServer(id);
  if (!error && result) {
    if (result.ok) {
      message.success(
        `${result.server_name || ''} v${result.server_version || '?'} · ${result.protocol_version || ''} · ${result.tool_count ?? 0} ${$t('page.agent.mcpServers.toolsCount')} (${result.latency_ms}ms)`
      );
    } else {
      message.error(`${$t('page.agent.mcpServers.testFailed')}: ${result.error || 'unknown'}`);
    }
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <McpServerSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.agent.mcpServers.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="mcp:server:add"
          delete-auth="mcp:server:delete"
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
      <McpServerOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData" @submitted="getDataByPage" />
    </NCard>
  </div>
</template>

<style scoped></style>
