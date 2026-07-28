<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord, userGenderRecord } from '@/constants/business';
import { fetchDeleteUser, fetchGetUserList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import { $t } from '@/locales';
import UserOperateDrawer from './modules/user-operate-drawer.vue';
import UserPasswordDrawer from './modules/user-password-drawer.vue';
import UserSearch from './modules/user-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

// 密码修改相关状态
const passwordDrawerVisible = ref(false);
const currentUserId = ref(0);

const searchParams: Api.SystemManage.UserSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  username: null,
  nickname: null,
  phone: null,
  email: null,
  is_superuser: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetUserList(searchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((user: Api.SystemManage.RawUser) => ({
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
      key: 'username',
      title: $t('page.manage.user.userName'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'nickname',
      title: $t('page.manage.user.nickName'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'phone',
      title: $t('page.manage.user.userPhone'),
      align: 'center',
      width: 120
    },
    {
      key: 'email',
      title: $t('page.manage.user.userEmail'),
      align: 'center',
      minWidth: 200
    },
    {
      key: 'last_login_at',
      title: $t('page.manage.user.lastLoginTime'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'last_login_ip',
      title: $t('page.manage.user.lastLoginIp'),
      align: 'center',
      minWidth: 100
    },
    {
      key: 'status',
      title: $t('page.manage.user.userStatus'),
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
      render: row => {
        if (row.is_superuser === true) {
          return null;
        }
        return (
          <div class="flex flex-wrap justify-center gap-8px">
            {hasAuth('sys:user:edit') && (
              <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('sys:user:edit') && (
              <NButton type="info" text size="small" onClick={() => openPasswordDrawer(row.id)}>
                {$t('common.changePassword')}
              </NButton>
            )}
            {hasAuth('sys:user:delete') && (
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
        );
      }
    }
  ]
});

const {
  drawerVisible,
  operateType,
  editingData,
  handleAdd,
  handleEdit,
  checkedRowKeys,
  onBatchDeleted,
  onDeleted
  // closeDrawer
} = useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }

  // flat request 不抛异常，需显式判断 error；任一失败即停止，避免部分失败仍触发刷新
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteUser(Number(id));
    if (error) {
      console.error('Batch delete users failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteUser(id);
  if (!error) {
    onDeleted();
  } else {
    console.error('Delete user failed:', error);
  }
}

function edit(id: number) {
  handleEdit(id);
}

// 打开修改密码抽屉
function openPasswordDrawer(id: number) {
  currentUserId.value = id;
  passwordDrawerVisible.value = true;
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <UserSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.manage.user.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="sys:user:add"
          delete-auth="sys:user:delete"
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
        :scroll-x="962"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <UserOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
      />
      <UserPasswordDrawer v-model:visible="passwordDrawerVisible" :user-id="currentUserId" @submitted="getDataByPage" />
    </NCard>
  </div>
</template>

<style scoped></style>
