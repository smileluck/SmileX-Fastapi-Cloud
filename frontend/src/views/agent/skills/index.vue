<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteSkill, fetchGetSkillList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import SkillOperateDrawer from './modules/skill-operate-drawer.vue';
import SkillSearch from './modules/skill-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

const searchParams: Api.Agent.SkillSearchParams = reactive({
  page: 1,
  page_size: 10,
  status: null,
  name: null,
  code: null
});

const { columns, columnChecks, data, loading, getData, getDataByPage, mobilePagination } = useNaivePaginatedTable({
  api: () => fetchGetSkillList(searchParams),
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
      title: $t('page.agent.skills.name'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'code',
      title: $t('page.agent.skills.code'),
      align: 'center',
      minWidth: 110
    },
    {
      key: 'description',
      title: $t('page.agent.skills.description'),
      align: 'center',
      minWidth: 200,
      ellipsis: { tooltip: true },
      render: row => row.description || '-'
    },
    {
      key: 'file_count',
      title: $t('page.agent.skills.fileCount'),
      align: 'center',
      width: 100,
      render: row =>
        row.file_count > 0 ? (
          <NTag size="small" type="info">
            {row.file_count}
          </NTag>
        ) : (
          '-'
        )
    },
    {
      key: 'status',
      title: $t('page.agent.skills.status'),
      align: 'center',
      width: 90,
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
      key: 'updated_at',
      title: $t('page.agent.skills.updatedAt'),
      align: 'center',
      minWidth: 160,
      render: row => row.updated_at || '-'
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 140,
      render: row => (
        <div class="flex flex-wrap justify-center gap-8px">
          {hasAuth('skill:edit') && (
            <NButton type="primary" text size="small" onClick={() => edit(row.id)}>
              {$t('common.edit')}
            </NButton>
          )}
          {hasAuth('skill:delete') && (
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
    const { error } = await fetchDeleteSkill(Number(id));
    if (error) {
      console.error('Batch delete skills failed:', error);
      return;
    }
  }
  onBatchDeleted();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteSkill(id);
  if (!error) {
    onDeleted();
  }
}

function edit(id: number) {
  handleEdit(id);
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <SkillSearch :model="searchParams" @search="getDataByPage" />
    <NCard
      :title="$t('page.agent.skills.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="columnChecks"
          :disabled-delete="checkedRowKeys.length === 0"
          :loading="loading"
          add-auth="skill:add"
          delete-auth="skill:delete"
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
      <SkillOperateDrawer v-model:visible="drawerVisible" :operate-type="operateType" :row-data="editingData" @submitted="getDataByPage" />
    </NCard>
  </div>
</template>

<style scoped></style>
