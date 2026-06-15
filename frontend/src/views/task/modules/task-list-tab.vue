<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchGetTaskList, fetchDeleteTask, fetchToggleTaskEnabled, fetchStartTaskExecution } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import TaskSearch from './task-search.vue';
import TaskOperateDrawer from './task-operate-drawer.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Task.TaskSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  task_type: null,
  enabled: null
});

const taskTypeLabel: Record<string, string> = {
  patrol: '巡逻',
  broadcast: '播报'
};

const scheduleCycleLabel: Record<string, string> = {
  none: '不重复',
  mon: '周一',
  tue: '周二',
  wed: '周三',
  thu: '周四',
  fri: '周五',
  sat: '周六',
  sun: '周日'
};

function formatSchedule(row: Api.Task.Task): string {
  if (!row.schedule_enabled) return '未配置';
  const parts: string[] = [];
  if (row.schedule_date) parts.push(row.schedule_date);
  if (row.schedule_start_time) parts.push(row.schedule_start_time);
  if (row.schedule_repeat_cycle) {
    const labels = row.schedule_repeat_cycle
      .split(',')
      .filter(v => v && v !== 'none')
      .map(v => scheduleCycleLabel[v] || v);
    if (labels.length > 0) parts.push(labels.join('、'));
  }
  return parts.length > 0 ? parts.join(' ') : '已启用';
}

const {
  columns,
  columnChecks,
  data,
  getData,
  getDataByPage,
  loading,
  mobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetTaskList(searchParams),
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
      title: '任务名称',
      align: 'center',
      minWidth: 140,
      ellipsis: { tooltip: true }
    },
    {
      key: 'task_type',
      title: '任务类型',
      align: 'center',
      width: 100,
      render: row => <NTag size="small" type={row.task_type === 'patrol' ? 'info' : 'success'}>{taskTypeLabel[row.task_type] || row.task_type}</NTag>
    },
    {
      key: 'point_count',
      title: '点位数量',
      align: 'center',
      width: 90,
      render: row => row.task_type === 'patrol' ? <span>{row.point_count}</span> : <span>-</span>
    },
    {
      key: 'schedule',
      title: '定时配置',
      align: 'center',
      minWidth: 160,
      render: row => <span>{formatSchedule(row)}</span>
    },
    {
      key: 'enabled',
      title: '启用状态',
      align: 'center',
      width: 100,
      render: row => <NTag size="small" type={row.enabled ? 'success' : 'default'}>{row.enabled ? '启用' : '禁用'}</NTag>
    },
    {
      key: 'robots',
      title: '绑定机器人',
      align: 'center',
      width: 120,
      render: row => {
        if (!row.robots || row.robots.length === 0) return <span>-</span>;
        return <span>{row.robots.map((r: Api.Task.TaskRobot) => r.name).join(', ')}</span>;
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 260,
      fixed: 'right',
      render: row => (
        <div class="flex-center gap-8px">
          {row.enabled && hasAuth('task:execution:start') && (
            <NButton type="success" ghost size="small" onClick={() => handleStart(row)}>
              启动
            </NButton>
          )}
          {hasAuth('task:edit') && (
            <NButton type="primary" ghost size="small" onClick={() => handleEdit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('task:edit') && (
            <NButton size="small" ghost onClick={() => handleToggleEnabled(row)}>
              {row.enabled ? '禁用' : '启用'}
            </NButton>
          )}
          {hasAuth('task:delete') && (
            <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
              {{
                default: () => $t('common.confirmDelete'),
                trigger: () => <NButton type="error" ghost size="small">{$t('common.delete')}</NButton>
              }}
            </NPopconfirm>
          )}
        </div>
      )
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
  onDeleted
} = useTableOperate(data, 'id', getData);

async function handleDelete(id: number) {
  try {
    await fetchDeleteTask(id);
    message.success($t('common.deleteSuccess'));
    onDeleted();
  } catch (error) {
    console.error('删除任务失败:', error);
  }
}

async function handleToggleEnabled(row: Api.Task.Task) {
  try {
    await fetchToggleTaskEnabled(row.id, !row.enabled);
    message.success(row.enabled ? '已禁用' : '已启用');
    getData();
  } catch (error) {
    console.error('切换启用状态失败:', error);
  }
}

async function handleStart(row: Api.Task.Task) {
  try {
    const robotIds = row.robots?.map((r: Api.Task.TaskRobot) => r.id) || [];
    await fetchStartTaskExecution(row.id, robotIds);
    message.success('任务已启动');
  } catch (error) {
    console.error('启动任务失败:', error);
  }
}
</script>

<template>
  <div class="h-full flex-col-stretch gap-12px">
    <TaskSearch v-model:model="searchParams" @search="getDataByPage" @reset="getDataByPage" />
    <div>
      <TableHeaderOperation
        v-model:columns="columnChecks"
        :disabled-delete="checkedRowKeys.length === 0"
        :loading="loading"
        add-auth="task:add"
        :show-delete="false"
        @add="handleAdd"
        @refresh="getData"
      />
    </div>
    <NDataTable
      v-model:checked-row-keys="checkedRowKeys"
      :columns="columns"
      :data="data"
      size="small"
      :flex-height="!appStore.isMobile"
      :scroll-x="1100"
      :loading="loading"
      remote
      :row-key="(row: Api.Task.Task) => row.id"
      :pagination="mobilePagination"
      class="sm:h-full"
    />
    <TaskOperateDrawer
      v-model:visible="drawerVisible"
      :operate-type="operateType"
      :row-data="editingData"
      @submitted="getDataByPage"
    />
  </div>
</template>

<style scoped></style>
