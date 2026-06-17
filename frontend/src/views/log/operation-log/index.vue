<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import {
  fetchBatchDeleteOperationLog,
  fetchClearOperationLog,
  fetchDeleteOperationLog,
  fetchGetOperationLogList
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import OperationLogSearch from './modules/operation-log-search.vue';
import OperationLogDetailDrawer from './modules/operation-log-detail-drawer.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.SystemManage.OperationLogSearchParams = reactive({
  page: 1,
  page_size: 10,
  username: null,
  module: null,
  action: null,
  start_time: null,
  end_time: null
});

const {
  columns,
  columnChecks,
  data,
  getData,
  getDataByPage,
  loading,
  mobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetOperationLogList(searchParams),
  transform: response => {
    return defaultTransform(response);
  },
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
      key: 'username',
      title: $t('page.log.operationLog.username'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'module',
      title: $t('page.log.operationLog.module'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'action',
      title: $t('page.log.operationLog.action'),
      align: 'center',
      minWidth: 80
    },
    {
      key: 'method',
      title: $t('page.log.operationLog.method'),
      align: 'center',
      width: 80,
      render: row => {
        const methodColorMap: Record<string, NaiveUI.ThemeColor> = {
          GET: 'success',
          POST: 'info',
          PUT: 'warning',
          DELETE: 'error',
          PATCH: 'default'
        };
        return (
          <NTag type={methodColorMap[row.method ?? ''] || 'default'} size="small">
            {row.method}
          </NTag>
        );
      }
    },
    {
      key: 'path',
      title: $t('page.log.operationLog.path'),
      align: 'center',
      minWidth: 180,
      ellipsis: { tooltip: true }
    },
    {
      key: 'ip',
      title: $t('page.log.operationLog.ip'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'response_code',
      title: $t('page.log.operationLog.responseCode'),
      align: 'center',
      width: 90,
      render: row => {
        if (!row.response_code) return '-';
        const type: NaiveUI.ThemeColor = row.response_code < 400 ? 'success' : 'error';
        return <NTag type={type} size="small">{row.response_code}</NTag>;
      }
    },
    {
      key: 'elapsed_ms',
      title: $t('page.log.operationLog.elapsedMs'),
      align: 'center',
      width: 90,
      render: row => {
        if (row.elapsed_ms == null) return '-';
        const ms = Math.round(row.elapsed_ms);
        return <span>{ms}ms</span>;
      }
    },
    {
      key: 'created_at',
      title: $t('page.log.operationLog.operateTime'),
      align: 'center',
      minWidth: 160
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 140,
      render: row => {
        return (
          <div class="flex flex-wrap justify-center gap-8px">
            <NButton type="primary" text size="small" onClick={() => handleViewDetail(row.id)}>
              {$t('page.log.operationLog.viewDetail')}
            </NButton>
            {hasAuth('sys:oplog:delete') && (
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
        );
      }
    }
  ]
});

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

const detailDrawerVisible = ref(false);
const detailLogId = ref<number | null>(null);

function handleViewDetail(id: number) {
  detailLogId.value = id;
  detailDrawerVisible.value = true;
}

async function handleDelete(id: number) {
  try {
    await fetchDeleteOperationLog(id);
    onDeleted();
  } catch (error) {
    console.error('删除操作日志失败:', error);
  }
}

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  try {
    await fetchBatchDeleteOperationLog(checkedRowKeys.value.map(Number));
    onBatchDeleted();
  } catch (error) {
    message.error($t('common.deleteFailed'));
  }
}

async function handleClear() {
  try {
    await fetchClearOperationLog(30);
    message.success($t('common.deleteSuccess'));
    getData();
  } catch (error) {
    message.error($t('common.deleteFailed'));
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <OperationLogSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.log.operationLog.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          :show-add="false"
          delete-auth="sys:oplog:delete"
          @delete="handleBatchDelete"
          @refresh="getData"
        >
          <template #prefix>
            <NPopconfirm v-if="hasAuth('sys:oplog:delete')" @positive-click="handleClear">
              {{ $t('page.log.operationLog.clearConfirm') }}
              <template #trigger>
                <NButton type="warning" ghost size="small" :disabled="loading">
                  {{ $t('page.log.operationLog.clear') }}
                </NButton>
              </template>
            </NPopconfirm>
          </template>
        </TableHeaderOperation>
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
      <OperationLogDetailDrawer
        v-model:visible="detailDrawerVisible"
        :log-id="detailLogId"
      />
    </NCard>
  </div>
</template>
