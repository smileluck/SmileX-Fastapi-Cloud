<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NDrawer, NDrawerContent, NIcon, NSpace, NText, NUpload, NUploadDragger, useMessage } from 'naive-ui';
import type { UploadFileInfo } from 'naive-ui';
import { fetchUploadFile, fetchUploadFiles } from '@/service/api/file';
import { $t } from '@/locales';

defineOptions({
  name: 'FileUploadDrawer'
});

interface Props {
  multiple?: boolean;
}

withDefaults(defineProps<Props>(), {
  multiple: true
});

const visible = defineModel<boolean>('visible', { required: true });
const emit = defineEmits<{ (e: 'submitted'): void }>();

const message = useMessage();
const uploading = ref(false);

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

async function handleUpload({
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

  try {
    const { data, error } = await fetchUploadFile(file.file);
    if (!error && data) {
      message.success(`${data.original_name} ${$t('page.demo.upload.uploadSuccess')}`);
      emit('submitted');
      onFinish();
    } else {
      message.error((error?.response?.data as any)?.msg || $t('page.demo.upload.uploadFailed'));
      onError();
    }
  } catch {
    onError();
  }
}
</script>

<template>
  <NDrawer v-model:show="visible" :width="400">
    <NDrawerContent :title="$t('page.manage.file.upload')" closable>
      <NSpace vertical :size="16">
        <NUpload :multiple="multiple" :custom-request="handleUpload" directory-dnd>
          <NUploadDragger>
            <div style="padding: 20px 0">
              <NText style="font-size: 16px">{{ $t('page.demo.upload.dragOrClick') }}</NText>
            </div>
          </NUploadDragger>
        </NUpload>
      </NSpace>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
