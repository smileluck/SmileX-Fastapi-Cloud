<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import {
  fetchDeleteProvider,
  fetchGetProviderList,
  fetchGetProviderRemoteModels,
  fetchTestProvider
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import ProviderOperateDrawer from './modules/provider-operate-drawer.vue';
import ProviderSearch from './modules/provider-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Agent.ProviderSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetProviderList(searchParams),
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
      title: $t('page.agent.providers.name'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'code',
      title: $t('page.agent.providers.code'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'base_url',
      title: $t('page.agent.providers.baseUrl'),
      align: 'center',
      minWidth: 220,
      ellipsis: { tooltip: true }
    },
    {
      key: 'api_key_mask',
      title: $t('page.agent.providers.apiKey'),
      align: 'center',
      minWidth: 130,
      render: row => row.api_key_mask || $t('page.agent.providers.noApiKey')
    },
    {
      key: 'status',
      title: $t('page.agent.providers.status'),
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
      key: 'remark',
      title: $t('page.agent.providers.remark'),
      align: 'center',
      minWidth: 120,
      render: row => row.remark || '-'
    },
    {
      key: 'created_at',
      title: $t('page.agent.providers.createdAt'),
      align: 'center',
      minWidth: 160,
      render: row => row.created_at || '-'
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 260,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('agent:provider:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('agent:provider:test') && (
            <NButton type="info" text size="small" onClick={() => handleTest(row.id)}>
              {$t('page.agent.providers.test')}
            </NButton>
          )}
          {hasAuth('agent:provider:remote-models') && (
            <NButton type="info" text size="small" onClick={() => handleRemoteModels(row.id, row.name)}>
              {$t('page.agent.providers.remoteModels')}
            </NButton>
          )}
          {hasAuth('agent:provider:delete') && (
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
    const { error } = await fetchDeleteProvider(Number(id));
    if (error) {
      console.error('Batch delete providers failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteProvider(id);
  if (!error) {
    onDeleted();
  }
}

async function handleTest(id: number) {
  message.loading($t('page.agent.providers.testing'));
  const { error, data: result } = await fetchTestProvider(id);
  if (!error && result) {
    if (result.ok) {
      message.success(
        `${$t('page.agent.providers.testSuccess')} · ${result.model || ''} · ${result.content || ''} (${result.prompt_tokens + result.completion_tokens} tokens)`
      );
    } else {
      message.error(`${$t('page.agent.providers.testFailed')}: ${result.error || 'unknown'}`);
    }
  }
}

async function handleRemoteModels(id: number, name: string) {
  message.loading($t('page.agent.providers.loadingModels'));
  const { error, data } = await fetchGetProviderRemoteModels(id);
  if (!error && data) {
    const models = data.models || [];
    if (models.length === 0) {
      message.warning($t('page.agent.providers.noModels'));
    } else {
      message.info(
        `${name}: ${models.slice(0, 8).join(', ')}${models.length > 8 ? ` ... (+${models.length - 8})` : ''}`
      );
    }
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <ProviderSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.agent.providers.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="agent:provider:add"
          delete-auth="agent:provider:delete"
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
      <ProviderOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData" @submitted="getDataByPage" />
    </NCard>
  </div>
</template>

<style scoped></style>
