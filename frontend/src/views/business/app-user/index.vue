<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteAppUser, fetchGetAppUserList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import { $t } from '@/locales';
import AppUserOperateDrawer from './modules/app-user-operate-drawer.vue';
import AppUserPasswordDrawer from './modules/app-user-password-drawer.vue';
import AppUserSearch from './modules/app-user-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

// 改密抽屉相关状态
const passwordDrawerVisible = ref(false);
const currentUserId = ref(0);

const searchParams: Api.SystemManage.AppUserSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  phone: null,
  phone_code: null,
  email: null,
  wx_openid: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetAppUserList(searchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((user: Api.SystemManage.AppUser) => ({
      ...user,
      status: booleanToEnableStatus(user.status)
    }));
    return result;
  },
  onPaginationParamsChange: params => {
    searchParams.page = params.page;
    searchParams.page_size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      align: 'center',
      width: 48
    },
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: $t('page.manage.appUser.userName'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'phone',
      title: $t('page.manage.appUser.userPhone'),
      align: 'center',
      width: 160,
      render: row => `+${row.phone_code} ${row.phone}`
    },
    {
      key: 'email',
      title: $t('page.manage.appUser.userEmail'),
      align: 'center',
      minWidth: 200
    },
    {
      key: 'wx_openid',
      title: $t('page.manage.appUser.bindWechat'),
      align: 'center',
      width: 110,
      render: row =>
        row.wx_openid ? (
          <NTag type="success">{$t('page.manage.appUser.bound')}</NTag>
        ) : (
          <NTag type="default">{$t('page.manage.appUser.unbound')}</NTag>
        )
    },
    {
      key: 'last_login_at',
      title: $t('page.manage.appUser.lastLoginTime'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'last_login_ip',
      title: $t('page.manage.appUser.lastLoginIp'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'status',
      title: $t('page.manage.appUser.userStatus'),
      align: 'center',
      width: 100,
      render: row => {
        if (row.status === null) {
          return null;
        }

        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };

        const label = $t(enableStatusRecord[row.status]);

        return <NTag type={tagMap[row.status]}>{label}</NTag>;
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 150,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('sys:app_user:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('sys:app_user:edit') && (
            <NButton type="info" text size="small" onClick={() => openPasswordDrawer(row.id)}>
              {$t('common.changePassword')}
            </NButton>
          )}
          {hasAuth('sys:app_user:delete') && (
            <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
              {{
                default: () => $t('common.confirmDelete'),
                trigger: () => (
                  <NButton type="error" text size="small">
                    {$t('common.delete')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          )}
        </div>
      )
    }
  ]
});

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, checkedRowKeys, onBatchDeleted, onDeleted } =
  useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }

  // flat request 不抛异常，需显式判断 error；任一失败即停止，避免部分失败仍触发刷新
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteAppUser(Number(id));
    if (error) {
      console.error('Batch delete app users failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteAppUser(id);
  if (!error) {
    onDeleted();
  } else {
    console.error('Delete app user failed:', error);
  }
}

function edit(id: number) {
  handleEdit(id);
}

// 打开改密抽屉
function openPasswordDrawer(id: number) {
  currentUserId.value = id;
  passwordDrawerVisible.value = true;
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <AppUserSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.manage.appUser.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="sys:app_user:add"
          delete-auth="sys:app_user:delete"
          @add="handleAdd"
          @delete="handleBatchDelete"
          @refresh="getData"
        />
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedRowKeys"
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1062"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <AppUserOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
      <AppUserPasswordDrawer
        v-model:visible="passwordDrawerVisible"
        :user-id="currentUserId"
        @submitted="getDataByPage"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
