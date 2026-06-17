<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { useRouter } from 'vue-router';
import {
  fetchGetScheduledTaskList,
  fetchDeleteScheduledTask,
  fetchBatchDeleteScheduledTask,
  fetchToggleScheduledTaskStatus,
  fetchManualTriggerTask,
  fetchSyncRegistry
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import { $t } from '@/locales';
import TaskSearch from './modules/task-search.vue';
import TaskOperateDrawer from './modules/task-operate-drawer.vue';

defineOptions({ name: 'SchedulerPage' });

const router = useRouter();
const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Scheduler.ScheduledTaskSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  task_key: null,
  status: null,
  trigger_type: null
});

const triggerTypeOptions = [
  { label: $t('page.manage.scheduler.triggerTypes.cron'), value: 'cron' },
  { label: $t('page.manage.scheduler.triggerTypes.interval'), value: 'interval' },
  { label: $t('page.manage.scheduler.triggerTypes.date'), value: 'date' }
];

const lastStatusMap: Record<string, NaiveUI.ThemeColor> = {
  success: 'success',
  failed: 'error',
  running: 'info'
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
  api: () => fetchGetScheduledTaskList(searchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((task: Api.Scheduler.ScheduledTask) => ({
      ...task,
      status: booleanToEnableStatus(task.status as unknown as boolean),
      is_system: booleanToEnableStatus(task.is_system as unknown as boolean)
    }));
    return result;
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
      key: 'name',
      title: $t('page.manage.scheduler.taskName'),
      align: 'center',
      minWidth: 140,
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
      key: 'cron_expression',
      title: $t('page.manage.scheduler.cronExpression'),
      align: 'center',
      width: 140
    },
    {
      key: 'trigger_type',
      title: $t('page.manage.scheduler.triggerType'),
      align: 'center',
      width: 100,
      render: row => {
        const opt = triggerTypeOptions.find(o => o.value === row.trigger_type);
        return <NTag type="info" size="small">{opt?.label || row.trigger_type}</NTag>;
      }
    },
    {
      key: 'status',
      title: $t('common.status'),
      align: 'center',
      width: 80,
      render: row => {
        if (!row.status) return null;
        const tagMap: Record<string, NaiveUI.ThemeColor> = { '1': 'success', '2': 'warning' };
        const label = row.status === '1'
          ? $t('page.manage.scheduler.statusEnabled')
          : $t('page.manage.scheduler.statusDisabled');
        return <NTag type={tagMap[row.status] || 'default'} size="small">{label}</NTag>;
      }
    },
    {
      key: 'last_status',
      title: $t('page.manage.scheduler.lastStatus'),
      align: 'center',
      width: 90,
      render: row => {
        if (!row.last_status) return '-';
        const labels: Record<string, string> = {
          success: $t('page.manage.scheduler.lastStatuses.success'),
          failed: $t('page.manage.scheduler.lastStatuses.failed'),
          running: $t('page.manage.scheduler.lastStatuses.running'),
          timeout: $t('page.manage.scheduler.lastStatuses.timeout')
        };
        return <NTag type={lastStatusMap[row.last_status] || 'default'} size="small">{labels[row.last_status] || row.last_status}</NTag>;
      }
    },
    {
      key: 'last_run_at',
      title: $t('page.manage.scheduler.lastRunAt'),
      align: 'center',
      width: 160
    },
    {
      key: 'next_run_at',
      title: $t('page.manage.scheduler.nextRunAt'),
      align: 'center',
      width: 160
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 260,
      fixed: 'right',
      render: row => {
        const isEnabled = row.status === '1';
        return (
          <div class="flex-center gap-8px">
            {hasAuth('sys:scheduler:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => handleEdit(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('sys:scheduler:status') && (
              <NButton
                type={isEnabled ? 'warning' : 'success'}
                ghost
                size="small"
                onClick={() => handleToggleStatus(row.id, row.status)}
              >
                {isEnabled ? $t('page.manage.scheduler.disable') : $t('page.manage.scheduler.enable')}
              </NButton>
            )}
            {hasAuth('sys:scheduler:trigger') && (
              <NPopconfirm onPositiveClick={() => handleManualTrigger(row.id)}>
                {{
                  default: () => $t('page.manage.scheduler.manualTriggerConfirm'),
                  trigger: () => (
                    <NButton type="info" ghost size="small">
                      {$t('page.manage.scheduler.manualTrigger')}
                    </NButton>
                  )
                }}
              </NPopconfirm>
            )}
            <NButton type="primary" text size="small" onClick={() => handleViewLogs(row.name)}>
              {$t('page.manage.scheduler.viewLogs')}
            </NButton>
            {hasAuth('sys:scheduler:delete') && row.is_system !== '1' && (
              <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
                {{
                  default: () => $t('common.confirmDelete'),
                  trigger: () => (
                    <NButton type="error" ghost size="small">
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

const {
  drawerVisible,
  operateType,
  editingData,
  handleAdd,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data, 'id', getData);

async function handleToggleStatus(taskId: number, currentStatus: string) {
  const newStatus = currentStatus !== '1';
  const { error } = await fetchToggleScheduledTaskStatus(taskId, newStatus);
  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    getData();
  }
}

async function handleManualTrigger(taskId: number) {
  const { error } = await fetchManualTriggerTask(taskId);
  if (!error) {
    window.$message?.success($t('page.manage.scheduler.manualTriggerSuccess'));
    getData();
  }
}

function handleViewLogs(taskName: string) {
  router.push({ path: '/manage/scheduler-log', query: { task_name: taskName } });
}

async function handleDelete(taskId: number) {
  const { error } = await fetchDeleteScheduledTask(taskId);
  if (!error) {
    onDeleted();
  }
}

async function handleBatchDelete() {
  const { error } = await fetchBatchDeleteScheduledTask(checkedRowKeys.value as number[]);
  if (!error) {
    onBatchDeleted();
  }
}

async function handleSyncRegistry() {
  const { error, data } = await fetchSyncRegistry();
  if (!error) {
    window.$message?.success($t('page.manage.scheduler.syncRegistrySuccess'));
    getData();
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <TaskSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.manage.scheduler.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="sys:scheduler:add"
          delete-auth="sys:scheduler:delete"
          @add="handleAdd"
          @delete="handleBatchDelete"
          @refresh="getData"
        >
          <template #prefix>
            <NButton
              v-if="hasAuth('sys:scheduler:add')"
              type="info"
              ghost
              size="small"
              :disabled="loading"
              @click="handleSyncRegistry"
            >
              <template #icon>
                <icon-ic-round-sync class="text-icon" />
              </template>
              {{ $t('page.manage.scheduler.syncRegistry') }}
            </NButton>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1500"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
    </NCard>
    <TaskOperateDrawer
      v-model:visible="drawerVisible"
      :operate-type="operateType"
      :row-data="editingData"
      @submitted="getData"
    />
  </div>
</template>
