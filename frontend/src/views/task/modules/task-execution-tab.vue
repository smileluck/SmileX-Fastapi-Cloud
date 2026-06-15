<script setup lang="tsx">
import { onMounted, onUnmounted, ref } from 'vue';
import { NButton, NDataTable, NProgress, NTag, useMessage } from 'naive-ui';
import { fetchGetActiveExecutions, fetchPauseExecution, fetchResumeExecution, fetchStopExecution } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { $t } from '@/locales';

defineOptions({ name: 'TaskExecutionTab' });

const appStore = useAppStore();
const message = useMessage();

const loading = ref(false);
const data = ref<Api.Task.TaskExecution[]>([]);
const page = ref(1);
const pageSize = ref(10);
const total = ref(0);

const statusColorMap: Record<string, NaiveUI.ThemeColor> = {
  running: 'success',
  paused: 'warning',
  pending: 'info'
};

const statusLabelMap: Record<string, string> = {
  running: '执行中',
  paused: '已暂停',
  pending: '等待中'
};

const columns = [
  {
    key: 'task_name',
    title: '任务名称',
    align: 'center' as const,
    minWidth: 140,
    ellipsis: { tooltip: true }
  },
  {
    key: 'task_type',
    title: '任务类型',
    align: 'center' as const,
    width: 100,
    render: (row: Api.Task.TaskExecution) => <NTag size="small" type={row.task_type === 'patrol' ? 'info' : 'success'}>{row.task_type === 'patrol' ? '巡逻' : '播报'}</NTag>
  },
  {
    key: 'robot_name',
    title: '执行机器人',
    align: 'center' as const,
    width: 120,
    render: (row: Api.Task.TaskExecution) => <span>{row.robot_name || '-'}</span>
  },
  {
    key: 'progress',
    title: '进度',
    align: 'center' as const,
    width: 160,
    render: (row: Api.Task.TaskExecution) => <NProgress type="line" percentage={row.progress} indicator-placement="inside" />
  },
  {
    key: 'status',
    title: '状态',
    align: 'center' as const,
    width: 100,
    render: (row: Api.Task.TaskExecution) => <NTag size="small" type={statusColorMap[row.status] || 'default'}>{statusLabelMap[row.status] || row.status}</NTag>
  },
  {
    key: 'started_at',
    title: '开始时间',
    align: 'center' as const,
    width: 170,
    render: (row: Api.Task.TaskExecution) => <span>{row.started_at || '-'}</span>
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center' as const,
    width: 180,
    fixed: 'right' as const,
    render: (row: Api.Task.TaskExecution) => (
      <div class="flex-center gap-8px">
        {row.status === 'running' && (
          <NButton type="warning" ghost size="small" onClick={() => handlePause(row.id)}>暂停</NButton>
        )}
        {row.status === 'paused' && (
          <NButton type="success" ghost size="small" onClick={() => handleResume(row.id)}>恢复</NButton>
        )}
        {(row.status === 'running' || row.status === 'paused') && (
          <NButton type="error" ghost size="small" onClick={() => handleStop(row.id)}>停止</NButton>
        )}
      </div>
    )
  }
];

let pollTimer: ReturnType<typeof setInterval> | null = null;

async function getData() {
  loading.value = true;
  try {
    const { data: result, error } = await fetchGetActiveExecutions({ page: page.value, page_size: pageSize.value });
    if (!error && result) {
      data.value = result.records || [];
      total.value = result.total || 0;
    }
  } finally {
    loading.value = false;
  }
}

async function handlePause(execId: number) {
  const { error } = await fetchPauseExecution(execId);
  if (!error) {
    message.success('任务已暂停');
    getData();
  }
}

async function handleResume(execId: number) {
  const { error } = await fetchResumeExecution(execId);
  if (!error) {
    message.success('任务已恢复');
    getData();
  }
}

async function handleStop(execId: number) {
  const { error } = await fetchStopExecution(execId);
  if (!error) {
    message.success('任务已停止');
    getData();
  }
}

function handlePageChange(p: number) {
  page.value = p;
  getData();
}

function handlePageSizeChange(ps: number) {
  pageSize.value = ps;
  page.value = 1;
  getData();
}

onMounted(() => {
  getData();
  pollTimer = setInterval(getData, 5000);
});

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
});
</script>

<template>
  <div class="h-full flex-col-stretch gap-12px">
    <NDataTable
      :columns="columns"
      :data="data"
      size="small"
      :flex-height="!appStore.isMobile"
      :scroll-x="970"
      :loading="loading"
      remote
      :row-key="(row: Api.Task.TaskExecution) => row.id"
      :pagination="{
        page: page,
        pageSize: pageSize,
        itemCount: total,
        showSizePicker: true,
        pageSizes: [10, 20, 50],
        onChange: handlePageChange,
        onUpdatePageSize: handlePageSizeChange
      }"
      class="sm:h-full"
    />
  </div>
</template>

<style scoped></style>
