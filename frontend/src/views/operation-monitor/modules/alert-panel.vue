<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { fetchGetRobotEventLogList } from '@/service/api/log';

interface Props {
  robotId: number | null;
}

const props = defineProps<Props>();

interface AlertItem {
  id: number;
  title: string;
  description: string;
  time: string;
  severity: 'error' | 'warning' | 'info';
  icon: string;
}

const alerts = ref<AlertItem[]>([]);
const loading = ref(false);
let refreshTimer: ReturnType<typeof setInterval> | null = null;

function mapAlertSeverity(eventStatus: string): 'error' | 'warning' | 'info' {
  if (eventStatus === 'abnormal') return 'error';
  return 'warning';
}

function getAlertIcon(severity: string): string {
  if (severity === 'error') return 'ic:round-error';
  if (severity === 'warning') return 'ic:round-warning';
  return 'ic:round-info';
}

function getAlertColor(severity: string): string {
  if (severity === 'error') return '#d03050';
  if (severity === 'warning') return '#f0a020';
  return '#2080f0';
}

async function loadAlerts() {
  if (!props.robotId) {
    alerts.value = [];
    return;
  }
  loading.value = true;
  try {
    const { data } = await fetchGetRobotEventLogList({
      robot_id: props.robotId,
      event_type: 'alarm',
      page: 1,
      page_size: 20,
      event_status: null,
      start_time: null,
      end_time: null
    });
    if (data) {
      const records = (data as any).records || data || [];
      alerts.value = records.map((log: Api.SystemManage.RobotEventLog) => {
        const severity = mapAlertSeverity(log.event_status);
        return {
          id: log.id,
          title: log.event_content ? log.event_content.split('\n')[0] || '告警' : '告警',
          description: log.event_content ? log.event_content.split('\n').slice(1).join('\n') || '' : '',
          time: log.created_at || '',
          severity,
          icon: getAlertIcon(severity)
        };
      });
    }
  } catch {
    alerts.value = [];
  } finally {
    loading.value = false;
  }
}

function startRefresh() {
  stopRefresh();
  refreshTimer = setInterval(loadAlerts, 5000);
}

function stopRefresh() {
  if (refreshTimer !== null) {
    clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

function formatTime(timeStr: string): string {
  if (!timeStr) return '';
  try {
    const date = new Date(timeStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return '刚刚';
    if (diffMin < 60) return `${diffMin}分钟前`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}小时前`;
    return timeStr;
  } catch {
    return timeStr;
  }
}

watch(() => props.robotId, () => {
  loadAlerts();
  startRefresh();
});

onMounted(() => {
  if (props.robotId) {
    loadAlerts();
    startRefresh();
  }
});

onBeforeUnmount(() => {
  stopRefresh();
});
</script>

<template>
  <NCard :bordered="true" size="small">
    <template #header>
      <NSpace align="center" :size="8">
        <span>实时告警</span>
        <NTag v-if="alerts.length > 0" type="error" size="small" round>
          {{ alerts.length }}
        </NTag>
      </NSpace>
    </template>

    <NSpin :show="loading">
      <div v-if="!robotId" class="py-32px">
        <NEmpty description="请先选择机器人" />
      </div>
      <div v-else-if="alerts.length === 0" class="py-32px">
        <NEmpty description="暂无告警" />
      </div>
      <NSpace v-else vertical :size="8" class="max-h-400px overflow-y-auto">
        <div
          v-for="alert in alerts"
          :key="alert.id"
          class="rounded-lg border p-12px"
          :style="{ borderColor: getAlertColor(alert.severity) + '40', backgroundColor: getAlertColor(alert.severity) + '08' }"
        >
          <div class="flex items-start gap-8px">
            <icon-ic-round-error-outline
              class="mt-2px flex-shrink-0 text-18px"
              :style="{ color: getAlertColor(alert.severity) }"
            />
            <div class="min-w-0 flex-1">
              <div class="text-13px font-medium" :style="{ color: getAlertColor(alert.severity) }">
                {{ alert.title }}
              </div>
              <div v-if="alert.description" class="mt-4px text-12px text-gray-500">
                {{ alert.description }}
              </div>
              <div class="mt-4px text-11px text-gray-400">
                {{ formatTime(alert.time) }}
              </div>
            </div>
          </div>
        </div>
      </NSpace>
    </NSpin>
  </NCard>
</template>

<style scoped></style>
