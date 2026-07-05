<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NPopconfirm, NTag, NText, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteMerchant, fetchGetMerchantList, fetchResetMerchantSecret } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import MerchantOperateDrawer from './modules/merchant-operate-drawer.vue';
import MerchantSearch from './modules/merchant-search.vue';
import MerchantSecretResultModal from './modules/merchant-secret-result-modal.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

// 一次性密钥结果弹窗
const secretModalVisible = ref(false);
const secretModalData = ref<{ app_id: string; app_secret: string; secret_updated_at?: string | null } | null>(null);

function showSecretModal(payload: { app_id: string; app_secret: string; secret_updated_at?: string | null }) {
  secretModalData.value = payload;
  secretModalVisible.value = true;
}

const searchParams: Api.SystemManage.MerchantSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null,
  app_id: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetMerchantList(searchParams),
  transform: response => defaultTransform(response),
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
      title: $t('page.manage.merchant.merchantName'),
      align: 'center',
      minWidth: 140
    },
    {
      key: 'code',
      title: $t('page.manage.merchant.merchantCode'),
      align: 'center',
      minWidth: 120,
      render: row => row.code || '-'
    },
    {
      key: 'app_id',
      title: $t('page.manage.merchant.appId'),
      align: 'center',
      minWidth: 180,
      render: row => <NText code>{row.app_id}</NText>
    },
    {
      key: 'contact_name',
      title: $t('page.manage.merchant.contactName'),
      align: 'center',
      minWidth: 100,
      render: row => row.contact_name || '-'
    },
    {
      key: 'contact_phone',
      title: $t('page.manage.merchant.contactPhone'),
      align: 'center',
      minWidth: 120,
      render: row => row.contact_phone || '-'
    },
    {
      key: 'secret_updated_at',
      title: $t('page.manage.merchant.secretUpdatedAt'),
      align: 'center',
      minWidth: 160,
      render: row => row.secret_updated_at || '-'
    },
    {
      key: 'status',
      title: $t('page.manage.merchant.status'),
      align: 'center',
      width: 100,
      render: row => {
        if (row.status === null || row.status === undefined) return null;
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
      minWidth: 200,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('sys:merchant:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('sys:merchant:reset-secret') && (
            <NPopconfirm onPositiveClick={() => handleResetSecret(row.id)}>
              {{
                default: () => $t('page.manage.merchant.resetSecretConfirm'),
                trigger: () => (
                  <NButton type="warning" text size="small">
                    {$t('page.manage.merchant.resetSecret')}
                  </NButton>
                )
              }}
            </NPopconfirm>
          )}
          {hasAuth('sys:merchant:delete') && (
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

const { drawerVisible, operateType, editingData, handleAdd, handleEdit, checkedRowKeys, onDeleted, onBatchDeleted } =
  useTableOperate(data, 'id', getData);

async function handleBatchDelete() {
  if (checkedRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  for (const id of checkedRowKeys.value) {
    const { error } = await fetchDeleteMerchant(Number(id));
    if (error) {
      console.error('Batch delete merchants failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteMerchant(id);
  if (!error) {
    onDeleted();
  }
}

async function handleResetSecret(id: number) {
  const { error, data: result } = await fetchResetMerchantSecret(id);
  if (!error && result) {
    showSecretModal({
      app_id: result.app_id,
      app_secret: result.app_secret,
      secret_updated_at: result.secret_updated_at
    });
    getData();
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <MerchantSearch v-model:model="searchParams" @search="getDataByPage" />
    <NCard :title="$t('page.manage.merchant.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="sys:merchant:add"
          delete-auth="sys:merchant:delete"
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
        :scroll-x="1200"
        :loading="loading"
        remote
        :row-key="row => row.id"
        :pagination="mobilePagination"
        class="sm:h-full"
      />
      <MerchantOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingData"
        @submitted="getDataByPage"
        @created="showSecretModal"
      />
      <MerchantSecretResultModal v-model:visible="secretModalVisible" :data="secretModalData" />
    </NCard>
  </div>
</template>

<style scoped></style>
