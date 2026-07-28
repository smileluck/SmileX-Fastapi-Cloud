<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { NImage, NModal } from 'naive-ui';
import { fetchGetPreviewToken, getFilePreviewUrl } from '@/service/api/file';
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

const previewUrl = ref('');
const previewLoading = ref(false);

// 打开预览时先换取短期、绑定单文件的预览令牌，再构造 URL
// 不再直接使用 access token，避免令牌进入 URL 日志/Referer 造成泄露
async function loadPreview() {
  if (!props.file) {
    previewUrl.value = '';
    return;
  }
  previewLoading.value = true;
  previewUrl.value = '';
  try {
    const { data, error } = await fetchGetPreviewToken(props.file.id);
    if (!error && data) {
      previewUrl.value = getFilePreviewUrl(props.file.id, data.preview_token);
    }
  } finally {
    previewLoading.value = false;
  }
}

watch(
  () => [props.visible, props.file?.id] as const,
  ([visible]) => {
    if (visible) loadPreview();
    else previewUrl.value = '';
  },
  { immediate: true }
);
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
      <video v-else-if="isVideo" :src="previewUrl" controls style="max-width: 100%; max-height: 75vh">
        {{ $t('page.manage.file.videoNotSupported') }}
      </video>
      <span v-else style="color: #999">{{ $t('page.manage.file.previewNotSupported') }}</span>
    </div>
  </NModal>
</template>
