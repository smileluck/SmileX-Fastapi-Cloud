<script setup lang="ts">
import { ref, watch } from 'vue';
import { $t } from '@/locales';
import { fetchGetTaskLogDetail } from '@/service/api';

defineOptions({ name: 'TaskLogDrawer' });

interface Props {
  logId: number | null;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', { required: true });

const loading = ref(false);
const detail = ref<Api.Scheduler.TaskLogDetail | null>(null);

watch(visible, async val => {
  if (val && props.logId) {
    await loadDetail(props.logId);
  }
  if (!val) {
    detail.value = null;
  }
});

async function loadDetail(id: number) {
  loading.value = true;
  try {
    const { data, error } = await fetchGetTaskLogDetail(id);
    if (!error) {
      detail.value = data;
    }
  } finally {
    loading.value = false;
  }
}

function formatJson(str: string | null): string {
  if (!str) return '-';
  try {
    return JSON.stringify(JSON.parse(str), null, 2);
  } catch {
    return str;
  }
}

const statusMap: Record<string, { type: NaiveUI.ThemeColor; label: string }> = {
  running: { type: 'info', label: $t('page.manage.scheduler.lastStatuses.running') },
  success: { type: 'success', label: $t('page.manage.scheduler.lastStatuses.success') },
  failed: { type: 'error', label: $t('page.manage.scheduler.lastStatuses.failed') },
  timeout: { type: 'warning', label: $t('page.manage.scheduler.lastStatuses.timeout') }
};
</script>

<template>
  <NDrawer v-model:show="visible" :width="520" display-directive="show">
    <NDrawerContent :title="$t('page.manage.schedulerLog.detailTitle')" :native-scrollbar="false" closable>
      <NSpin :show="loading">
        <template v-if="detail">
          <NDescriptions label-placement="left" bordered :column="1" size="small">
            <NDescriptionsItem :label="$t('page.manage.scheduler.taskName')">
              {{ detail.task_name }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.scheduler.taskKey')">
              {{ detail.task_key }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.schedulerLog.status')">
              <NTag :type="statusMap[detail.status]?.type || 'default'" size="small">
                {{ statusMap[detail.status]?.label || detail.status }}
              </NTag>
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.schedulerLog.startTime')">
              {{ detail.start_time || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.schedulerLog.endTime')">
              {{ detail.end_time || '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.schedulerLog.duration')">
              {{ detail.duration_ms != null ? `${detail.duration_ms.toFixed(0)} ms` : '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.manage.schedulerLog.triggeredBy')">
              {{ detail.triggered_by === 'manual' ? $t('page.manage.schedulerLog.triggeredByValues.manual') : $t('page.manage.schedulerLog.triggeredByValues.scheduler') }}
            </NDescriptionsItem>
          </NDescriptions>

          <NDivider v-if="detail.result">{{ $t('page.manage.schedulerLog.result') }}</NDivider>
          <NScrollbar v-if="detail.result" x-scrollable style="max-height: 200px">
            <pre class="whitespace-pre-wrap break-all rounded bg-gray-100 p-12px text-13px dark:bg-dark-800">{{ formatJson(detail.result) }}</pre>
          </NScrollbar>

          <NDivider v-if="detail.error_message">{{ $t('page.manage.schedulerLog.errorMessage') }}</NDivider>
          <NScrollbar v-if="detail.error_message" x-scrollable style="max-height: 200px">
            <pre class="whitespace-pre-wrap break-all rounded bg-red-50 p-12px text-13px text-red-600 dark:bg-dark-800">{{ detail.error_message }}</pre>
          </NScrollbar>
        </template>
      </NSpin>
      <template #footer>
        <NButton @click="visible = false">{{ $t('common.close') }}</NButton>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>
