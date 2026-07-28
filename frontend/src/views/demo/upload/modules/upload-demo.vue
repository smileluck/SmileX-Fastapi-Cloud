<script setup lang="ts">
import { computed, h, ref } from 'vue';
import { NTag } from 'naive-ui';
import type { UploadFileInfo } from 'naive-ui';
import { fetchUploadFile } from '@/service/api/file';
import { $t } from '@/locales';

interface Props {
  multiple?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  multiple: false
});

interface UploadResult {
  name: string;
  size: number;
  extension: string;
  status: 'success' | 'error' | 'uploading';
  message?: string;
}

const fileList = ref<UploadFileInfo[]>([]);
const results = ref<UploadResult[]>([]);
const uploading = ref(false);
const uploadedCount = ref(0);
const totalCount = ref(0);

const uploadProgress = computed(() => {
  if (totalCount.value === 0) return 0;
  return Math.round((uploadedCount.value / totalCount.value) * 100);
});

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function handleFileChange({ fileList: newFileList }: { file: UploadFileInfo; fileList: UploadFileInfo[] }) {
  fileList.value = newFileList;
}

function renderStatus(row: UploadResult) {
  const typeMap = { success: 'success', error: 'error', uploading: 'warning' } as const;
  const labelMap = {
    success: $t('page.demo.upload.uploadSuccess'),
    error: $t('page.demo.upload.uploadFailed'),
    uploading: $t('page.demo.upload.uploading')
  };
  return h(NTag, { type: typeMap[row.status], size: 'small', round: true }, { default: () => labelMap[row.status] });
}

const tableColumns = computed(() => [
  { title: $t('page.demo.upload.fileName'), key: 'name', ellipsis: { tooltip: true } },
  {
    title: $t('page.demo.upload.fileType'),
    key: 'extension',
    width: 100,
    render: (row: UploadResult) => row.extension || '-'
  },
  {
    title: $t('page.demo.upload.fileSize'),
    key: 'size',
    width: 120,
    render: (row: UploadResult) => formatFileSize(row.size)
  },
  { title: $t('page.demo.upload.uploadResult'), key: 'status', width: 120, render: renderStatus }
]);

/** 将新结果插入数组头部，返回响应式代理的索引 */
function pushResult(result: UploadResult): number {
  results.value.unshift(result);
  return 0;
}

function updateResult(index: number, patch: Partial<UploadResult>) {
  Object.assign(results.value[index], patch);
}

/** 单文件 custom-request 回调 */
function handleSingleCustomRequest({
  file,
  onFinish,
  onError
}: {
  file: UploadFileInfo;
  onFinish: () => void;
  onError: () => void;
}) {
  if (!file.file) {
    onError();
    return;
  }

  const ext = file.name.includes('.') ? `.${file.name.split('.').pop()!}` : '';
  const idx = pushResult({ name: file.name, size: file.file.size, extension: ext, status: 'uploading' });

  fetchUploadFile(file.file)
    .then(({ data, error }) => {
      if (!error && data) {
        updateResult(idx, {
          name: data.original_name,
          size: data.file_size,
          extension: data.extension,
          status: 'success'
        });
        onFinish();
      } else {
        updateResult(idx, { status: 'error', message: (error?.response?.data as any)?.msg || 'Upload failed' });
        onError();
      }
    })
    .catch(() => {
      updateResult(idx, { status: 'error', message: 'Network error' });
      onError();
    });
}

/** 多文件：点击按钮触发逐个上传 */
async function doBatchUpload() {
  const files = fileList.value.map(f => f.file).filter((f): f is File => f !== null);
  if (files.length === 0) return;

  uploading.value = true;
  totalCount.value = files.length;
  uploadedCount.value = 0;

  for (const file of files) {
    const ext = file.name.includes('.') ? `.${file.name.split('.').pop()!}` : '';
    const idx = pushResult({ name: file.name, size: file.size, extension: ext, status: 'uploading' });

    try {
      const { data, error } = await fetchUploadFile(file);
      if (!error && data) {
        updateResult(idx, {
          name: data.original_name,
          size: data.file_size,
          extension: data.extension,
          status: 'success'
        });
      } else {
        updateResult(idx, { status: 'error', message: (error?.response?.data as any)?.msg || 'Upload failed' });
      }
    } catch {
      updateResult(idx, { status: 'error', message: 'Network error' });
    }

    uploadedCount.value++;
  }

  uploading.value = false;
  fileList.value = [];
  totalCount.value = 0;
  uploadedCount.value = 0;
}

const canUpload = computed(() => {
  if (!props.multiple) return false;
  return fileList.value.some(f => f.status === 'pending');
});

const pendingCount = computed(() => fileList.value.filter(f => f.status === 'pending').length);
</script>

<template>
  <NSpace vertical :size="12">
    <NUpload
      :multiple="props.multiple"
      :custom-request="props.multiple ? () => {} : handleSingleCustomRequest"
      :directory-dnd="true"
      @change="handleFileChange"
    >
      <NUploadDragger>
        <div style="padding: 20px 0">
          <NIcon size="48" :depth="3" style="margin-bottom: 8px">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path
                d="M11 20H6.5a3.5 3.5 0 0 1 0-7h.05A5 5 0 0 1 16 8.05A4.5 4.5 0 0 1 20 12.5a4.5 4.5 0 0 1-4.5 4.5H13v3a1 1 0 0 1-2 0v-3zm1-8a1 1 0 0 1 1 1v3h2.5a2.5 2.5 0 0 0 0-5h-.5l-.05-.5a3 3 0 0 0-5.67-1.21l-.21.71H7.5a1.5 1.5 0 0 0 0 3H11v-1a1 1 0 0 1 1-1z"
              />
            </svg>
          </NIcon>
          <NText style="font-size: 16px">{{ $t('page.demo.upload.dragOrClick') }}</NText>
          <NP v-if="props.multiple" style="margin-top: 4px" depth="3">
            {{ $t('page.demo.upload.selectFiles') }}
          </NP>
        </div>
      </NUploadDragger>
    </NUpload>

    <!-- Multi-file: upload button + progress -->
    <template v-if="props.multiple">
      <NProgress v-if="uploading" type="line" :percentage="uploadProgress" indicator-placement="inside" processing />

      <NSpace>
        <NButton type="primary" :disabled="!canUpload" :loading="uploading" @click="doBatchUpload">
          {{ $t('page.demo.upload.startUpload') }}
          <template v-if="pendingCount > 0">({{ pendingCount }})</template>
        </NButton>
      </NSpace>
    </template>

    <NDataTable
      v-if="results.length > 0"
      :columns="tableColumns"
      :data="results"
      :bordered="false"
      size="small"
      :max-height="300"
    />
  </NSpace>
</template>
