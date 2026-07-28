<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NPopconfirm, NTag, NText, useMessage } from 'naive-ui';
import { fetchBatchDeleteOpenapiLog, fetchDeleteOpenapiLog, fetchGetOpenapiLogList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import OpenapiLogSearch from './modules/openapi-log-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.SystemManage.OpenapiLogSearchParams = reactive({
  page: 1,
  page_size: 10,
  app_id: null,
  path: null,
  method: null,
  status_code: null,
  err_code: null,
  client_ip: null,
  request_id: null,
  start_time: null,
  end_time: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetOpenapiLogList(searchParams),
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
      key: 'app_id',
      title: $t('page.manage.openapiLog.appId'),
      align: 'center',
      minWidth: 160,
      render: row => <NText code>{row.app_id}</NText>
    },
    {
      key: 'merchant_name',
      title: $t('page.manage.openapiLog.merchantName'),
      align: 'center',
      minWidth: 120,
      render: row => row.merchant_name || '-'
    },
    {
      key: 'method',
      title: $t('page.manage.openapiLog.method'),
      align: 'center',
      width: 80
    },
    {
      key: 'path',
      title: $t('page.manage.openapiLog.path'),
      align: 'center',
      minWidth: 180
    },
    {
      key: 'status_code',
      title: $t('page.manage.openapiLog.status'),
      align: 'center',
      width: 90,
      render: row => {
        if (row.status_code === null || row.status_code === undefined) return '-';
        const ok = row.status_code >= 200 && row.status_code < 300;
        return (
          <NTag type={ok ? 'success' : 'error'} size="small">
            {row.status_code}
          </NTag>
        );
      }
    },
    {
      key: 'err_code',
      title: $t('page.manage.openapiLog.errCode'),
      align: 'center',
      width: 100,
      render: row =>
        row.err_code === null || row.err_code === undefined ? '-' : <NTag size="small">{row.err_code}</NTag>
    },
    {
      key: 'client_ip',
      title: $t('page.manage.openapiLog.clientIp'),
      align: 'center',
      minWidth: 120,
      render: row => row.client_ip || '-'
    },
    {
      key: 'latency_ms',
      title: $t('page.manage.openapiLog.latency'),
      align: 'center',
      width: 100,
      render: row => (row.latency_ms === null || row.latency_ms === undefined ? '-' : `${row.latency_ms} ms`)
    },
    {
      key: 'created_at',
      title: $t('page.manage.openapiLog.createdAt'),
      align: 'center',
      minWidth: 160,
      render: row => row.created_at || '-'
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 100,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('sys:openapi-log:delete') && (
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

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteOpenapiLog(Number(id));
    if (error) {
      console.error('Batch delete openapi logs failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteOpenapiLog(id);
  if (!error) {
    onDeleted();
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <OpenapiLogSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.manage.openapiLog.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          :show-add="false"
          delete-auth="sys:openapi-log:delete"
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
        :scroll-x="1400"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
