<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchGetFileList, fetchDownloadFile, fetchDeleteFile, fetchBatchDeleteFiles } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import FileSearch from './modules/file-search.vue';
import FileUploadDrawer from './modules/file-upload-drawer.vue';
import FilePreviewModal from './modules/file-preview-modal.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.FileManage.FileSearchParams = reactive({
  page: 1,
  page_size: 10,
  original_name: undefined,
  extension: undefined,
  storage_platform: undefined
});

const previewVisible = ref(false);
const previewFile = ref<Api.FileManage.FileListItem | null>(null);

function isPreviewable(extension: string): boolean {
  const ext = extension?.toLowerCase() || '';
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'mp4', 'webm', 'ogg', 'mov'].includes(ext);
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
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
  api: () => fetchGetFileList(searchParams),
  transform: defaultTransform as any,
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
      key: 'original_name',
      title: $t('page.manage.file.fileName'),
      align: 'left',
      minWidth: 200
    },
    {
      key: 'file_size',
      title: $t('page.manage.file.fileSize'),
      align: 'center',
      width: 120,
      render: (row: any) => formatFileSize(row.file_size)
    },
    {
      key: 'mime_type',
      title: $t('page.manage.file.fileType'),
      align: 'center',
      minWidth: 140
    },
    {
      key: 'extension',
      title: $t('page.manage.file.fileExtension'),
      align: 'center',
      width: 100,
      render: (row: any) => <NTag size="small">.{row.extension}</NTag>
    },
    {
      key: 'storage_platform',
      title: $t('page.manage.file.storagePlatform'),
      align: 'center',
      width: 120,
      render: (row: any) => {
        const platformMap: Record<string, string> = {
          local: $t('page.manage.file.platform.local'),
          oss: $t('page.manage.file.platform.oss')
        };
        return <NTag type="info" size="small">{platformMap[row.storage_platform] || row.storage_platform}</NTag>;
      }
    },
    {
      key: 'created_at',
      title: $t('page.manage.file.uploadTime'),
      align: 'center',
      width: 180
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 240,
      render: (row: any) => {
        return (
          <div class="flex flex-wrap justify-center gap-8px">
            {isPreviewable(row.extension) && hasAuth('sys:file:download') && (
              <NButton type="info" ghost size="small" onClick={() => handlePreview(row)}>
                {$t('page.manage.file.preview')}
              </NButton>
            )}
            {hasAuth('sys:file:download') && (
              <NButton type="primary" ghost size="small" onClick={() => handleDownload(row.id, row.original_name)}>
                {$t('page.manage.file.download')}
              </NButton>
            )}
            {hasAuth('sys:file:delete') && (
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
  drawerVisible: uploadDrawerVisible,
  handleAdd: handleUpload,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
} = useTableOperate(data as any, 'id', getData);

function handlePreview(row: Api.FileManage.FileListItem) {
  previewFile.value = row;
  previewVisible.value = true;
}

async function handleDownload(fileId: number, fileName: string) {
  try {
    const blob = await fetchDownloadFile(fileId);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    URL.revokeObjectURL(url);
  } catch {
    message.error($t('common.loadDataFailed'));
  }
}

async function handleDelete(fileId: number) {
  try {
    await fetchDeleteFile(fileId);
    onDeleted();
  } catch {
    message.error($t('common.deleteFailed'));
  }
}

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  try {
    await fetchBatchDeleteFiles(checkedRowKeys.value.map(Number));
    onBatchDeleted();
  } catch {
    message.error($t('common.deleteFailed'));
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <FileSearch v-model:model="searchParams" @search="getDataByPage" @reset="getDataByPage" />
    <NCard :title="$t('page.manage.file.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="sys:file:upload"
          delete-auth="sys:file:delete"
          @add="handleUpload"
          @delete="handleBatchDelete"
          @refresh="getData"
        />
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns as any"
        :data="data as any"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1200"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <FileUploadDrawer
        v-model:visible="uploadDrawerVisible"
        @submitted="getDataByPage"
      />
    </NCard>
    <FilePreviewModal
      v-model:visible="previewVisible"
      :file="previewFile"
    />
  </div>
</template>

<style scoped></style>
