<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NSpace, useMessage } from 'naive-ui';
import { fetchGetOnlineUserList, fetchKickAllOnlineUsers, fetchKickUser } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import OnlineUserSearch from './modules/online-user-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.SystemManage.OnlineUserSearchParams = reactive({
  page: 1,
  page_size: 10,
  username: null,
  ip: null
});

const { columns, columnChecks, data, getData, getDataByPage, loading, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetOnlineUserList(searchParams),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    searchParams.page = params.page;
    searchParams.page_size = params.pageSize;
  },
  columns: () => [
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'username',
      title: $t('page.log.onlineUser.username'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'nickname',
      title: $t('page.log.onlineUser.nickname'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'ip',
      title: $t('page.log.onlineUser.ip'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'user_agent',
      title: $t('page.log.onlineUser.userAgent'),
      align: 'center',
      minWidth: 200,
      ellipsis: { tooltip: true }
    },
    {
      key: 'login_time',
      title: $t('page.log.onlineUser.loginTime'),
      align: 'center',
      minWidth: 160
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 100,
      render: row => {
        if (!hasAuth('sys:online:kick')) return null;
        return (
          <NSpace justify="center">
            <NPopconfirm onPositiveClick={() => handleKick(row)}>
              {{
                default: () => $t('page.log.onlineUser.kickConfirm'),
                trigger: () => (
                  <NButton type="warning" text size="small">
                    {$t('page.log.onlineUser.kick')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          </NSpace>
        );
      }
    }
  ]
});

async function handleKick(row: Api.SystemManage.OnlineUser) {
  try {
    await fetchKickUser({ user_id: row.user_id, session_id: row.session_id });
    message.success($t('page.log.onlineUser.kickSuccess'));
    getData();
  } catch (error) {
    message.error($t('common.updateFailed'));
  }
}

async function handleKickAllOnline() {
  try {
    await fetchKickAllOnlineUsers();
    message.success($t('page.log.onlineUser.kickAllSuccess'));
    getData();
  } catch (error) {
    message.error($t('common.updateFailed'));
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <OnlineUserSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.log.onlineUser.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :loading="loading"
          :show-add="false"
          :show-delete="false"
          @refresh="getData"
        >
          <template #suffix>
            <NPopconfirm v-if="hasAuth('sys:online:kick')" @positive-click="handleKickAllOnline">
              <template #trigger>
                <NButton size="small" ghost type="error">
                  <template #icon>
                    <icon-ic-round-delete-forever class="text-icon" />
                  </template>
                  {{ $t('page.log.onlineUser.kickAll') }}
                </NButton>
              </template>
              {{ $t('page.log.onlineUser.kickAllConfirm') }}
            </NPopconfirm>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="900"
        :loading="loading"
        remote
        :row-key="row => row.session_id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
    </NCard>
  </div>
</template>
