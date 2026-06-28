<script setup lang="ts">
import { computed } from 'vue';
import { NModal, NImage } from 'naive-ui';
import { getFilePreviewUrl } from '@/service/api/file';
import { $t } from '@/locales';

defineOptions({
  name: 'FilePreviewModal'
});

interface Props {
  visible: boolean;
  file: Api.FileManage.FileListItem | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{ (e: 'update:visible', val: boolean): void }>();

const showModal = computed({
  get: () => props.visible,
  set: val => emit('update:visible', val)
});

const isImage = computed(() => {
  if (!props.file) return false;
  const ext = props.file.extension.toLowerCase();
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico'].includes(ext);
});

const isVideo = computed(() => {
  if (!props.file) return false;
  const ext = props.file.extension.toLowerCase();
  return ['mp4', 'webm', 'ogg', 'mov', 'avi'].includes(ext);
});

const previewUrl = computed(() => {
  if (!props.file) return '';
  return getFilePreviewUrl(props.file.id);
});
</script>

<template>
  <NModal
    v-model:show="showModal"
    preset="card"
    :title="file?.original_name ?? $t('page.manage.file.previewTitle')"
    style="max-width: 90vw; max-height: 90vh"
    :segmented="{ content: true }"
  >
    <div style="display: flex; justify-content: center; align-items: center; min-height: 300px">
      <NImage
        v-if="isImage"
        :src="previewUrl"
        :alt="file?.original_name"
        object-fit="contain"
        style="max-height: 75vh"
      />
      <video
        v-else-if="isVideo"
        :src="previewUrl"
        controls
        style="max-width: 100%; max-height: 75vh"
      >
        {{ $t('page.manage.file.videoNotSupported') }}
      </video>
      <span v-else style="color: #999">{{ $t('page.manage.file.previewNotSupported') }}</span>
    </div>
  </NModal>
</template>
