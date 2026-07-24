<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'RecentLogin'
});

const props = defineProps<{
  /** 最近登录记录列表 */
  logins: Api.Dashboard.RecentLogin[];
}>();

/** 登录时间线条目（NTimeline 所需结构） */
interface TimelineItem {
  type: 'success' | 'error';
  username: string;
  ip: string;
  time: string;
}

/** 将时间字符串格式化为本地可读形式 */
function formatTime(timeStr: string): string {
  if (!timeStr) return '';
  try {
    const dt = new Date(timeStr);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())} ${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  } catch {
    return timeStr;
  }
}

/** 转换为时间线条目 */
const timelineItems = computed<TimelineItem[]>(() =>
  props.logins.map(item => ({
    type: item.status ? 'success' : 'error',
    username: item.username,
    ip: item.ip || '-',
    time: formatTime(item.login_time)
  }))
);

/** 是否为空数据 */
const isEmpty = computed(() => timelineItems.value.length === 0);
</script>

<template>
  <div>
    <h3 class="mb-12px text-16px font-500">{{ $t('page.home.recentLogin') }}</h3>
    <NEmpty v-if="isEmpty" :description="$t('page.home.noData')" />
    <NTimeline v-else size="large">
      <NTimelineItem v-for="(item, idx) in timelineItems" :key="idx" :type="item.type">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-8px">
            <span class="font-500">{{ item.username }}</span>
            <NTag :type="item.type" size="small" round>
              {{ item.type === 'success' ? $t('page.home.loginSuccess') : $t('page.home.loginFailed') }}
            </NTag>
          </div>
          <span class="text-12px op-60">{{ item.time }}</span>
        </div>
        <div class="mt-2px text-12px op-60">IP: {{ item.ip }}</div>
      </NTimelineItem>
    </NTimeline>
  </div>
</template>

<style scoped></style>
