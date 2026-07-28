<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { fetchDashboardSummary } from '@/service/api/dashboard';
import { useAppStore } from '@/store/modules/app';
import { useAuthStore } from '@/store/modules/auth';
import CardData from './modules/card-data.vue';
import RecentLogin from './modules/recent-login.vue';
import LatestNotice from './modules/latest-notice.vue';

defineOptions({
  name: 'Home'
});

const appStore = useAppStore();
const authStore = useAuthStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

const loading = ref(true);
const stats = ref<Api.Dashboard.Stats>({
  user_count: 0,
  role_count: 0,
  online_count: 0,
  today_login_count: 0
});
const recentLogins = ref<Api.Dashboard.RecentLogin[]>([]);
const latestNotices = ref<Api.Dashboard.LatestNotice[]>([]);

/** 加载仪表盘汇总数据 */
async function loadData() {
  loading.value = true;
  try {
    const { data } = await fetchDashboardSummary();
    if (data) {
      stats.value = data.stats;
      recentLogins.value = data.recent_logins;
      latestNotices.value = data.latest_notices;
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <NSpin :show="loading">
    <NSpace vertical :size="16">
      <!-- 欢迎横幅 -->
      <NCard :bordered="false" class="card-wrapper">
        <div class="text-18px font-500">
          {{ $t('page.home.welcome', { name: authStore.userInfo.nickname || authStore.userInfo.username }) }}
        </div>
      </NCard>

      <!-- 统计卡片 -->
      <CardData
        :user-count="stats.user_count"
        :role-count="stats.role_count"
        :online-count="stats.online_count"
        :today-login-count="stats.today_login_count"
      />

      <!-- 活动流：最近登录 + 最新公告 -->
      <NGrid :x-gap="gap" :y-gap="16" responsive="screen" item-responsive>
        <NGi span="24 s:24 m:14">
          <NCard :bordered="false" class="card-wrapper">
            <RecentLogin :logins="recentLogins" />
          </NCard>
        </NGi>
        <NGi span="24 s:24 m:10">
          <NCard :bordered="false" class="card-wrapper">
            <LatestNotice :notices="latestNotices" />
          </NCard>
        </NGi>
      </NGrid>
    </NSpace>
  </NSpin>
</template>

<style scoped></style>
