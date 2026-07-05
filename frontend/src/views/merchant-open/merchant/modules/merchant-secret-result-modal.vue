<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'MerchantSecretResultModal'
});

interface Props {
  /** 弹窗显隐 */
  visible: boolean;
  /** 凭据数据（app_id + 一次性明文 app_secret） */
  data: {
    app_id: string;
    app_secret: string;
    secret_updated_at?: string | null;
  } | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'update:visible', visible: boolean): void;
}

const emit = defineEmits<Emits>();

const showDialog = computed({
  get: () => props.visible,
  set: (val: boolean) => emit('update:visible', val)
});

async function copy(text: string) {
  if (!text) return;
  try {
    await navigator.clipboard.writeText(text);
    window.$message?.success($t('page.manage.merchant.copied'));
  } catch {
    window.$message?.error($t('page.manage.merchant.copyFailed'));
  }
}

function handleClose() {
  showDialog.value = false;
}
</script>

<template>
  <NModal
    v-model:show="showDialog"
    preset="card"
    :title="$t('page.manage.merchant.secretResultTitle')"
    class="w-480px"
    :mask-closable="false"
    :close-on-esc="false"
  >
    <NSpace vertical :size="16">
      <NAlert type="warning" :show-icon="true" :bordered="false">
        {{ $t('page.manage.merchant.secretOnceWarning') }}
      </NAlert>

      <NDescriptions label-placement="top" bordered :column="1" size="small">
        <NDescriptionsItem :label="$t('page.manage.merchant.appId')">
          <div class="flex items-center gap-8px">
            <NText code class="break-all">{{ props.data?.app_id }}</NText>
            <NButton size="tiny" type="primary" ghost @click="copy(props.data?.app_id || '')">
              {{ $t('page.manage.merchant.copy') }}
            </NButton>
          </div>
        </NDescriptionsItem>
        <NDescriptionsItem :label="$t('page.manage.merchant.appSecret')">
          <div class="flex items-center gap-8px">
            <NText code class="break-all">{{ props.data?.app_secret }}</NText>
            <NButton size="tiny" type="primary" ghost @click="copy(props.data?.app_secret || '')">
              {{ $t('page.manage.merchant.copy') }}
            </NButton>
          </div>
        </NDescriptionsItem>
      </NDescriptions>
    </NSpace>

    <template #footer>
      <div class="flex justify-end">
        <NButton type="primary" @click="handleClose">{{ $t('common.confirm') }}</NButton>
      </div>
    </template>
  </NModal>
</template>

<style scoped></style>
