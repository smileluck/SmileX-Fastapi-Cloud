<script setup lang="tsx">
import { onMounted, reactive, ref } from 'vue';
import { useRoute } from 'vue-router';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchGetTaskLogList, fetchBatchDeleteTaskLog, fetchClearTaskLog } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import TaskLogSearch from './modules/task-log-search.vue';
import TaskLogDrawer from '../scheduler/modules/task-log-drawer.vue';

defineOptions({ name: 'SchedulerLogPage' });

const route = useRoute();
const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Scheduler.TaskLogSearchParams = reactive({
  page: 1,
  page_size: 10,
  task_id: null,
  task_name: null,
  task_key: null,
  status: null,
  start_time: null,
  end_time: null
});

const statusMap: Record<string, { type: NaiveUI.ThemeColor; label: string }> = {
  running: { type: 'info', label: $t('page.manage.scheduler.lastStatuses.running') },
  success: { type: 'success', label: $t('page.manage.scheduler.lastStatuses.success') },
  failed: { type: 'error', label: $t('page.manage.scheduler.lastStatuses.failed') },
  timeout: { type: 'warning', label: $t('page.manage.scheduler.lastStatuses.timeout') }
};

const {
  columns,
  columnChecks,
  data,
  getData,
  getDataByPage,
  loading,
  mobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetTaskLogList(searchParams),
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
      key: 'task_name',
      title: $t('page.manage.schedulerLog.taskName'),
      align: 'center',
      minWidth: 120,
      ellipsis: { tooltip: true }
    },
    {
      key: 'task_key',
      title: $t('page.manage.scheduler.taskKey'),
      align: 'center',
      minWidth: 160,
      ellipsis: { tooltip: true }
    },
    {
      key: 'status',
      title: $t('page.manage.schedulerLog.status'),
      align: 'center',
      width: 80,
      render: row => {
        const s = statusMap[row.status];
        return <NTag type={s?.type || 'default'} size="small">{s?.label || row.status}</NTag>;
      }
    },
    {
      key: 'start_time',
      title: $t('page.manage.schedulerLog.startTime'),
      align: 'center',
      width: 160
    },
    {
      key: 'end_time',
      title: $t('page.manage.schedulerLog.endTime'),
      align: 'center',
      width: 160
    },
    {
      key: 'duration_ms',
      title: $t('page.manage.schedulerLog.duration'),
      align: 'center',
      width: 100,
      render: row => row.duration_ms != null ? `${row.duration_ms.toFixed(0)} ms` : '-'
    },
    {
      key: 'triggered_by',
      title: $t('page.manage.schedulerLog.triggeredBy'),
      align: 'center',
      width: 80,
      render: row => {
        const isManual = row.triggered_by === 'manual';
        return <NTag type={isManual ? 'warning' : 'info'} size="small">
          {isManual ? $t('page.manage.schedulerLog.triggeredByValues.manual') : $t('page.manage.schedulerLog.triggeredByValues.scheduler')}
        </NTag>;
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 80,
      render: row => {
        return (
          <NButton type="primary" text size="small" onClick={() => handleViewDetail(row.id)}>
            {$t('page.manage.schedulerLog.viewDetail')}
          </NButton>
        );
      }
    }
  ]
});

const { checkedRowKeys, onBatchDeleted, onDeleted } = useTableOperate(data, 'id', getData);

const detailVisible = ref(false);
const detailLogId = ref<number | null>(null);

function handleViewDetail(logId: number) {
  detailLogId.value = logId;
  detailVisible.value = true;
}

onMounted(() => {
  if (route.query.task_name) {
    searchParams.task_name = route.query.task_name as string;
    getData();
  }
});

async function handleBatchDelete() {
  const { error } = await fetchBatchDeleteTaskLog(checkedRowKeys.value as number[]);
  if (!error) {
    onBatchDeleted();
  }
}

async function handleClear() {
  const { error } = await fetchClearTaskLog(30);
  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    getData();
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <TaskLogSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.manage.schedulerLog.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          :show-add="false"
          delete-auth="sys:scheduler:log:delete"
          @delete="handleBatchDelete"
          @refresh="getData"
        >
          <template #prefix>
            <NPopconfirm v-if="hasAuth('sys:scheduler:log:delete')" @positive-click="handleClear">
              {{ $t('page.manage.schedulerLog.clearConfirm') }}
              <template #trigger>
                <NButton type="warning" ghost size="small" :disabled="loading">
                  {{ $t('page.manage.schedulerLog.clear') }}
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
      <TaskLogDrawer
        v-model:visible="detailVisible"
        :log-id="detailLogId"
      />
    </NCard>
  </div>
</template>
