<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({
  name: 'LatestNotice'
});

const props = defineProps<{
  /** 最新公告列表 */
  notices: Api.Dashboard.LatestNotice[];
}>();

/** 公告类型与 NTag 颜色的映射 */
const typeColorMap: Record<string, 'info' | 'default' | 'success' | 'warning'> = {
  announcement: 'info',
  system: 'default',
  operation: 'success',
  approval: 'warning'
};

/** 公告列表展示条目 */
interface NoticeItem {
  id: string;
  title: string;
  type: string;
  tagType: 'info' | 'default' | 'success' | 'warning';
  time: string;
}

/** 将时间字符串格式化为本地可读形式 */
function formatTime(timeStr: string): string {
  if (!timeStr) return '';
  try {
    const dt = new Date(timeStr);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}`;
  } catch {
    return timeStr;
  }
}

/** 转换为展示条目 */
const noticeItems = computed<NoticeItem[]>(() =>
  props.notices.map(item => ({
    id: item.id,
    title: item.title,
    type: item.type,
    tagType: typeColorMap[item.type] ?? 'default',
    time: formatTime(item.created_at)
  }))
);

/** 是否为空数据 */
const isEmpty = computed(() => noticeItems.value.length === 0);
</script>

<template>
  <div>
    <h3 class="mb-12px text-16px font-500">{{ $t('page.home.latestNotice') }}</h3>
    <NEmpty v-if="isEmpty" :description="$t('page.home.noData')" />
    <NList v-else hoverable clickable>
      <NListItem v-for="item in noticeItems" :key="item.id">
        <div class="w-full flex items-center justify-between">
          <div class="flex items-center gap-8px overflow-hidden">
            <NTag :type="item.tagType" size="small">{{ item.type }}</NTag>
            <NEllipsis class="font-500" :line-clamp="1">{{ item.title }}</NEllipsis>
          </div>
          <span class="ml-8px shrink-0 text-12px op-60">{{ item.time }}</span>
        </div>
      </NListItem>
    </NList>
  </div>
</template>

<style scoped></style>
