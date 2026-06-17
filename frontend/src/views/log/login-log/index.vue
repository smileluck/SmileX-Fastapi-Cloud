<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchBatchDeleteLoginLog, fetchClearLoginLog, fetchDeleteLoginLog, fetchGetLoginLogList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import LoginLogSearch from './modules/login-log-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.SystemManage.LoginLogSearchParams = reactive({
  page: 1,
  page_size: 10,
  username: null,
  ip: null,
  status: null,
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
  api: () => fetchGetLoginLogList(searchParams),
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
      title: $t('page.log.loginLog.username'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'ip',
      title: $t('page.log.loginLog.ip'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'status',
      title: $t('page.log.loginLog.status'),
      align: 'center',
      width: 80,
      render: row => {
        return (
          <NTag type={row.status ? 'success' : 'error'}>
            {row.status ? $t('page.log.loginLog.success') : $t('page.log.loginLog.failed')}
          </NTag>
        );
      }
    },
    {
      key: 'detail',
      title: $t('page.log.loginLog.detail'),
      align: 'center',
      minWidth: 140
    },
    {
      key: 'user_agent',
      title: $t('page.log.loginLog.userAgent'),
      align: 'center',
      minWidth: 200,
      ellipsis: { tooltip: true }
    },
    {
      key: 'login_time',
      title: $t('page.log.loginLog.loginTime'),
      align: 'center',
      minWidth: 160
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 80,
      render: row => {
        if (!hasAuth('sys:log:delete')) return null;
        return (
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
        );
      }
    }
  ]
});

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

async function handleDelete(id: number) {
  try {
    await fetchDeleteLoginLog(id);
    onDeleted();
  } catch (error) {
    console.error('删除登录日志失败:', error);
  }
}

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  try {
    await fetchBatchDeleteLoginLog(checkedRowKeys.value.map(Number));
    onBatchDeleted();
  } catch (error) {
    message.error($t('common.deleteFailed'));
  }
}

async function handleClear() {
  try {
    await fetchClearLoginLog(30);
    message.success($t('common.deleteSuccess'));
    getData();
  } catch (error) {
    message.error($t('common.deleteFailed'));
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <LoginLogSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.log.loginLog.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          :show-add="false"
          delete-auth="sys:log:delete"
          @delete="handleBatchDelete"
          @refresh="getData"
        >
          <template #prefix>
            <NPopconfirm v-if="hasAuth('sys:log:delete')" @positive-click="handleClear">
              {{ $t('page.log.loginLog.clearConfirm') }}
              <template #trigger>
                <NButton type="warning" ghost size="small" :disabled="loading">
                  {{ $t('page.log.loginLog.clear') }}
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
        :scroll-x="1100"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
    </NCard>
  </div>
</template>
