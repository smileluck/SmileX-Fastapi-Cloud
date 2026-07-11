<script setup lang="tsx">
import { onMounted, reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NTag, useMessage } from 'naive-ui';
import { fetchDownloadExportFile, fetchGetExportTaskList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable } from '@/hooks/common/table';
import { $t } from '@/locales';

defineOptions({ name: 'ExportRecordPage' });

const appStore = useAppStore();
const message = useMessage();

const searchParams: Api.ExportTask.ExportTaskSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null
});

const statusMap: Record<Api.ExportTask.ExportTaskStatus, { type: NaiveUI.ThemeColor; label: string }> = {
  pending: { type: 'default', label: $t('exportTask.status.pending') },
  processing: { type: 'warning', label: $t('exportTask.status.processing') },
  completed: { type: 'success', label: $t('exportTask.status.completed') },
  failed: { type: 'error', label: $t('exportTask.status.failed') }
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
  api: () => fetchGetExportTaskList(searchParams),
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
      title: $t('exportTask.taskName'),
      align: 'center',
      minWidth: 140,
      ellipsis: { tooltip: true }
    },
    {
      key: 'module_key',
      title: $t('exportTask.moduleKey'),
      align: 'center',
      minWidth: 120,
      ellipsis: { tooltip: true }
    },
    {
      key: 'status',
      title: $t('exportTask.status.title'),
      align: 'center',
      width: 100,
      render: row => {
        const s = statusMap[row.status];
        return <NTag type={s?.type || 'default'} size="small">{s?.label || row.status}</NTag>;
      }
    },
    {
      key: 'total_rows',
      title: $t('exportTask.totalRows'),
      align: 'center',
      width: 100,
      render: row => row.total_rows ?? '-'
    },
    {
      key: 'file_size',
      title: $t('exportTask.fileSize'),
      align: 'center',
      width: 120,
      render: row => {
        if (row.file_size == null) return '-';
        const size = row.file_size;
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(2)} KB`;
        return `${(size / 1024 / 1024).toFixed(2)} MB`;
      }
    },
    {
      key: 'error_message',
      title: $t('exportTask.errorMessage'),
      align: 'center',
      minWidth: 160,
      ellipsis: { tooltip: true },
      render: row => row.error_message || '-'
    },
    {
      key: 'created_at',
      title: $t('exportTask.createdAt'),
      align: 'center',
      width: 160
    },
    {
      key: 'finished_at',
      title: $t('exportTask.finishedAt'),
      align: 'center',
      width: 160,
      render: row => row.finished_at || '-'
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 100,
      render: row => {
        if (row.status !== 'completed') return null;
        return (
          <NButton type="primary" text size="small" onClick={() => handleDownload(row.id, row.task_name)}>
            {$t('common.download')}
          </NButton>
        );
      }
    }
  ]
});

async function handleDownload(taskId: number, taskName: string) {
  const { error, data } = await fetchDownloadExportFile(taskId);
  if (error || !data) {
    message.error($t('exportTask.downloadFailed'));
    return;
  }

  const blob = new Blob([data], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${taskName}_${taskId}.xlsx`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

onMounted(() => {
  getData();
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :title="$t('exportTask.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :loading="loading"
          :show-add="false"
          :show-delete="false"
          @refresh="getData"
        />
      </template>
      <NDataTable
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
