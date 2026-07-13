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

function copy(text: string) {
  if (!text) return;
  // execCommand 必须在用户手势(click)的同步调用栈内执行；任何 await 都会跨微任务，
  // 破坏 user activation，导致 Chrome 返回 true 却不写入剪贴板（这正是之前“提示成功但粘不出来”的根因）
  if (copyViaExecCommand(text)) {
    window.$message?.success($t('page.manage.merchant.copied'));
    return;
  }
  // 兜底：安全上下文下用异步 Clipboard API
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard
      .writeText(text)
      .then(() => window.$message?.success($t('page.manage.merchant.copied')))
      .catch(() => window.$message?.error($t('page.manage.merchant.copyFailed')));
    return;
  }
  window.$message?.error($t('page.manage.merchant.copyFailed'));
}

/** execCommand 同步复制：用移出视口的隐藏 textarea，返回是否成功 */
function copyViaExecCommand(text: string): boolean {
  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.top = '0';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    textarea.setSelectionRange(0, text.length); // iOS Safari 下 select() 不生效，需手动设选区
    const success = document.execCommand('copy');
    document.body.removeChild(textarea);
    return success;
  } catch {
    return false;
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
