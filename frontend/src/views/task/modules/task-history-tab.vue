<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NDataTable, NTag } from 'naive-ui';
import { fetchGetExecutionHistory } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';
import TaskHistorySearch from './task-history-search.vue';
import TaskDetailDrawer from './task-detail-drawer.vue';

defineOptions({ name: 'TaskHistoryTab' });

const appStore = useAppStore();

const searchParams: Api.Task.TaskExecutionSearchParams = reactive({
  page: 1,
  page_size: 10,
  task_name: null,
  status: null
});

const statusColorMap: Record<string, NaiveUI.ThemeColor> = {
  completed: 'success',
  failed: 'error',
  cancelled: 'default'
};

const statusLabelMap: Record<string, string> = {
  completed: '已完成',
  failed: '已失败',
  cancelled: '已取消'
};

const taskTypeLabel: Record<string, string> = {
  patrol: '巡逻',
  broadcast: '播报'
};

/** 详情抽屉 */
const detailDrawerVisible = ref(false);
const detailExecId = ref<number | null>(null);

function handleViewDetail(row: Api.Task.TaskExecution) {
  detailExecId.value = row.id;
  detailDrawerVisible.value = true;
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
  api: () => fetchGetExecutionHistory(searchParams),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.page = params.page;
    searchParams.page_size = params.pageSize;
  },
  columns: () => [
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'task_name',
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
      key: 'status',
      title: '执行状态',
      align: 'center',
      width: 100,
      render: row => <NTag size="small" type={statusColorMap[row.status] || 'default'}>{statusLabelMap[row.status] || row.status}</NTag>
    },
    {
      key: 'robot_name',
      title: '执行机器人',
      align: 'center',
      width: 120,
      render: row => <span>{row.robot_name || '-'}</span>
    },
    {
      key: 'started_at',
      title: '开始时间',
      align: 'center',
      width: 170,
      render: row => <span>{row.started_at || '-'}</span>
    },
    {
      key: 'ended_at',
      title: '结束时间',
      align: 'center',
      width: 170,
      render: row => <span>{row.ended_at || '-'}</span>
    },
    {
      key: 'triggered_by',
      title: '触发方式',
      align: 'center',
      width: 100,
      render: row => <span>{row.triggered_by === 'manual' ? '手动' : '定时'}</span>
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 100,
      fixed: 'right',
      render: row => (
        <NButton type="primary" ghost size="small" onClick={() => handleViewDetail(row)}>
          查看详情
        </NButton>
      )
    }
  ]
});
</script>

<template>
  <div class="h-full flex-col-stretch gap-12px">
    <TaskHistorySearch v-model:model="searchParams" @search="getDataByPage" @reset="getDataByPage" />
    <div>
      <TableHeaderOperation
        v-model:columns="columnChecks"
        :loading="loading"
        :show-add="false"
        :show-delete="false"
        @refresh="getData"
      />
    </div>
    <NDataTable
      :columns="columns"
      :data="data"
      size="small"
      :flex-height="!appStore.isMobile"
      :scroll-x="1100"
      :loading="loading"
      remote
      :row-key="(row: Api.Task.TaskExecution) => row.id"
      :pagination="mobilePagination"
      class="sm:h-full"
    />
    <TaskDetailDrawer
      v-model:visible="detailDrawerVisible"
      :exec-id="detailExecId"
    />
  </div>
</template>

<style scoped></style>
