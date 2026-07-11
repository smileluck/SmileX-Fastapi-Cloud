<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { NBadge, NButton, NPopover, NList, NListItem, NEmpty, NDivider, NModal, NSpace, NTooltip } from 'naive-ui';
import { useAuthStore } from '@/store/modules/auth';
import { fetchGetMyNoticeList, fetchGetUnreadCount, fetchMarkAllAsRead, fetchMarkAsRead } from '@/service/api';
import { $t } from '@/locales';
import SvgIcon from '@/components/custom/svg-icon.vue';

const authStore = useAuthStore();

const unreadCount = ref(0);
const recentNotices = ref<Api.Notification.MyNotice[]>([]);
const showPopover = ref(false);
const loading = ref(false);
const showDetailModal = ref(false);
const selectedNotice = ref<Api.Notification.MyNotice | null>(null);

/** 获取未读数量 */
async function getUnreadCount() {
  if (!authStore.isLogin) return;
  const { data } = await fetchGetUnreadCount();
  if (data != null) {
    unreadCount.value = data;
  }
}

/** 获取最近通知 */
async function getRecentNotices() {
  if (!authStore.isLogin) return;
  loading.value = true;
  const { data } = await fetchGetMyNoticeList({ page: 1, page_size: 10 });
  if (data?.records) {
    recentNotices.value = data.records;
  }
  loading.value = false;
}

/** 标记全部已读 */
async function handleMarkAllAsRead() {
  const { error } = await fetchMarkAllAsRead();
  if (!error) {
    unreadCount.value = 0;
    recentNotices.value = recentNotices.value.map(n => ({ ...n, is_read: true }));
    window.$message?.success($t('notification.markAllReadSuccess'));
  }
}

/** 点击通知项：查看详情并标记已读 */
async function handleNoticeClick(notice: Api.Notification.MyNotice) {
  selectedNotice.value = notice;
  showDetailModal.value = true;
  showPopover.value = false;

  if (!notice.is_read) {
    const { error } = await fetchMarkAsRead(notice.id);
    if (!error) {
      notice.is_read = true;
      unreadCount.value = Math.max(0, unreadCount.value - 1);
    }
  }
}

/** 处理 WebSocket 通知事件 */
function handleWsNotification(event: CustomEvent) {
  unreadCount.value += 1;
  if (showPopover.value) {
    getRecentNotices();
  }
}

/** 优先级标签映射 */
const priorityMap: Record<Api.Notification.NoticePriority, { label: string; type: 'default' | 'success' | 'warning' | 'error' }> = {
  low: { label: $t('notification.priority.low'), type: 'default' },
  normal: { label: $t('notification.priority.normal'), type: 'success' },
  high: { label: $t('notification.priority.high'), type: 'warning' },
  urgent: { label: $t('notification.priority.urgent'), type: 'error' }
};

onMounted(() => {
  getUnreadCount();
  window.addEventListener('ws:notification', handleWsNotification as EventListener);
});

onUnmounted(() => {
  window.removeEventListener('ws:notification', handleWsNotification as EventListener);
});

/** 打开弹窗时刷新 */
function onShowChange(show: boolean) {
  showPopover.value = show;
  if (show) {
    getRecentNotices();
  }
}
</script>

<template>
  <NPopover
    v-model:show="showPopover"
    trigger="click"
    placement="bottom"
    :width="360"
    @update:show="onShowChange"
  >
    <template #trigger>
      <NTooltip>
        <template #trigger>
          <div class="relative cursor-pointer px-8px hover:bg-[#f6f6f6] dark:hover:bg-[#333] rounded-full transition-colors">
            <NBadge :value="unreadCount" :max="99" :show="unreadCount > 0">
              <SvgIcon icon="material-symbols:notifications-outline" class="text-20px" />
            </NBadge>
          </div>
        </template>
        {{ $t('notification.tooltip') }}
      </NTooltip>
    </template>
    <template #header>
      <div class="flex items-center justify-between px-12px py-8px">
        <span class="font-bold">{{ $t('notification.title') }}</span>
        <NButton v-if="unreadCount > 0" text size="small" @click="handleMarkAllAsRead">
          {{ $t('notification.markAllAsRead') }}
        </NButton>
      </div>
    </template>
    <div class="max-h-400px overflow-y-auto">
      <NList v-if="recentNotices.length > 0" hoverable clickable :show-divider="false">
        <NListItem v-for="notice in recentNotices" :key="notice.id" @click="handleNoticeClick(notice)">
          <div class="flex flex-col gap-4px">
            <div class="flex items-center justify-between">
              <span class="font-medium truncate flex-1" :class="{ 'text-gray': notice.is_read }">
                {{ notice.title }}
              </span>
              <span v-if="!notice.is_read" class="w-8px h-8px rounded-full bg-primary" />
            </div>
            <div class="text-12px text-gray flex items-center gap-8px">
              <span>{{ notice.sender_name }}</span>
              <span v-if="priorityMap[notice.priority]">
                <NBadge
                  :value="priorityMap[notice.priority].label"
                  :type="priorityMap[notice.priority].type"
                  size="small"
                />
              </span>
            </div>
          </div>
        </NListItem>
      </NList>
      <NEmpty v-else :description="$t('notification.noNotifications')" />
    </div>
    <template #footer>
      <NDivider class="!my-0" />
      <div class="px-12px py-8px text-center">
        <NButton text size="small" @click="showPopover = false">
          {{ $t('common.close') }}
        </NButton>
      </div>
    </template>
  </NPopover>

  <!-- 通知详情弹窗 -->
  <NModal
    v-model:show="showDetailModal"
    :title="selectedNotice?.title"
    preset="card"
    :style="{ width: '520px', maxWidth: '90vw' }"
    :bordered="false"
    size="small"
  >
    <div v-if="selectedNotice" class="flex flex-col gap-12px">
      <div class="flex items-center gap-12px text-14px text-gray">
        <span>{{ selectedNotice.sender_name }}</span>
        <NBadge
          v-if="priorityMap[selectedNotice.priority]"
          :value="priorityMap[selectedNotice.priority].label"
          :type="priorityMap[selectedNotice.priority].type"
          size="small"
        />
        <span v-if="selectedNotice.published_at">{{ selectedNotice.published_at }}</span>
      </div>
      <NDivider class="!my-0" />
      <div class="text-14px leading-relaxed whitespace-pre-wrap">
        {{ selectedNotice.content }}
      </div>
    </div>
  </NModal>
</template>
