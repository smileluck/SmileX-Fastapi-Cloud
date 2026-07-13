<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { NBadge, NButton, NEmpty, NList, NListItem, NPopover, NTag, NTooltip } from 'naive-ui';
import { useRouterPush } from '@/hooks/common/router';
import { fetchDownloadExportFile, fetchGetExportTaskList } from '@/service/api';
import { useAuthStore } from '@/store/modules/auth';
import { $t } from '@/locales';
import SvgIcon from '@/components/custom/svg-icon.vue';

defineOptions({
  name: 'ExportRecordCenter'
});

const authStore = useAuthStore();
const { routerPushByKey } = useRouterPush();

const showPopover = ref(false);
const loading = ref(false);
const recentTasks = ref<Api.ExportTask.ExportTask[]>([]);
const pollingTimer = ref<ReturnType<typeof setInterval> | null>(null);

const statusMap: Record<Api.ExportTask.ExportTaskStatus, { label: string; type: NaiveUI.ThemeColor }> = {
  pending: { label: $t('exportTask.status.pending'), type: 'default' },
  processing: { label: $t('exportTask.status.processing'), type: 'warning' },
  completed: { label: $t('exportTask.status.completed'), type: 'success' },
  failed: { label: $t('exportTask.status.failed'), type: 'error' }
};

const hasRunningTask = computed(() =>
  recentTasks.value.some(task => task.status === 'pending' || task.status === 'processing')
);

/** 获取最近5条导出记录 */
async function getRecentTasks() {
  if (!authStore.isLogin) return;
  loading.value = true;
  const { data } = await fetchGetExportTaskList({ page: 1, page_size: 5 });
  if (data?.records) {
    recentTasks.value = data.records;
  }
  loading.value = false;
}

/** 跳转全部记录页 */
function handleViewAll() {
  showPopover.value = false;
  routerPushByKey('export-record');
}

/** 下载文件 */
async function handleDownload(task: Api.ExportTask.ExportTask, event: MouseEvent) {
  event.stopPropagation();
  const { error, data } = await fetchDownloadExportFile(task.id);
  if (error || !data) {
    window.$message?.error($t('exportTask.downloadFailed'));
    return;
  }

  const blob = new Blob([data], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${task.task_name}_${task.id}.xlsx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/** 处理 WebSocket 导出任务事件 */
function handleWsExportTask() {
  getRecentTasks();
}

/** 启动轮询兜底 */
function startPolling() {
  stopPolling();
  pollingTimer.value = setInterval(() => {
    getRecentTasks();
  }, 30000);
}

/** 停止轮询 */
function stopPolling() {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value);
    pollingTimer.value = null;
  }
}

function onShowChange(show: boolean) {
  showPopover.value = show;
  if (show) {
    getRecentTasks();
  }
}

onMounted(() => {
  getRecentTasks();
  startPolling();
  window.addEventListener('ws:export_task', handleWsExportTask as EventListener);
});

onUnmounted(() => {
  stopPolling();
  window.removeEventListener('ws:export_task', handleWsExportTask as EventListener);
});
</script>

<template>
  <NPopover
    v-model:show="showPopover"
    trigger="click"
    placement="bottom"
    :width="380"
    @update:show="onShowChange"
  >
    <template #trigger>
      <NTooltip>
        <template #trigger>
          <div class="relative cursor-pointer px-8px hover:bg-[#f6f6f6] dark:hover:bg-[#333] rounded-full transition-colors">
            <NBadge dot :show="hasRunningTask">
              <SvgIcon icon="material-symbols:download-2" class="text-20px" />
            </NBadge>
          </div>
        </template>
        {{ $t('exportTask.tooltip') }}
      </NTooltip>
    </template>
    <template #header>
      <div class="flex items-center justify-between px-12px py-8px">
        <span class="font-bold">{{ $t('exportTask.title') }}</span>
        <NButton text size="small" @click="handleViewAll">
          {{ $t('exportTask.viewAll') }}
        </NButton>
      </div>
    </template>
    <div class="max-h-400px overflow-y-auto">
      <NList v-if="recentTasks.length > 0" hoverable :show-divider="false">
        <NListItem v-for="task in recentTasks" :key="task.id">
          <div class="flex flex-col gap-6px w-full">
            <div class="flex items-center gap-8px">
              <NTag :type="statusMap[task.status].type" size="small">{{ statusMap[task.status].label }}</NTag>
              <span class="font-medium truncate flex-1" :title="task.task_name">{{ task.task_name }}</span>
              <NButton v-if="task.status === 'completed'" text size="small" type="primary" @click="handleDownload(task, $event)">
                {{ $t('common.actions.download') }}
              </NButton>
            </div>
            <div class="text-12px text-gray flex items-center gap-8px">
              <span v-if="task.created_at">{{ task.created_at }}</span>
              <NTag v-if="task.status === 'failed' && task.error_message" type="error" size="small" bordered="false">
                {{ task.error_message }}
              </NTag>
            </div>
          </div>
        </NListItem>
      </NList>
      <NEmpty v-else :description="$t('exportTask.noRecords')" />
    </div>
  </NPopover>
</template>

<style scoped></style>
