<script setup lang="tsx">
import { ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import {
  fetchDeleteDept,
  fetchGetDeptTree
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import DeptOperateDrawer from './modules/dept-operate-drawer.vue';

const appStore = useAppStore();
const { hasAuth } = useAuth();

const loading = ref(false);
const data = ref<Api.SystemManage.Dept[]>([]);
const drawerVisible = ref(false);
const operateType = ref<NaiveUI.TableOperateType>('add');
const editingRow = ref<Api.SystemManage.Dept | null>(null);

async function getData() {
  loading.value = true;
  const { data: tree } = await fetchGetDeptTree(false);
  data.value = tree || [];
  loading.value = false;
}

function handleAdd(parentId?: number) {
  operateType.value = 'add';
  editingRow.value = parentId ? ({ id: -1, parent_id: parentId } as Api.SystemManage.Dept) : null;
  drawerVisible.value = true;
}

function handleEdit(row: Api.SystemManage.Dept) {
  operateType.value = 'edit';
  editingRow.value = row;
  drawerVisible.value = true;
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteDept(id);
  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    getData();
  }
}

const columns = [
  {
    key: 'name',
    title: $t('page.manage.dept.deptName'),
    minWidth: 200
  },
  {
    key: 'code',
    title: $t('page.manage.dept.deptCode'),
    align: 'center' as const,
    minWidth: 140,
    render: (row: Api.SystemManage.Dept) => row.code || '-'
  },
  {
    key: 'sort',
    title: $t('page.manage.dept.sort'),
    align: 'center' as const,
    width: 80
  },
  {
    key: 'status',
    title: $t('page.manage.dept.status'),
    align: 'center' as const,
    width: 100,
    render: (row: Api.SystemManage.Dept) => {
      if (row.status === null || row.status === undefined) return null;
      const tagMap: Record<string, NaiveUI.ThemeColor> = {
        '1': 'success',
        '2': 'warning'
      };
      const label = $t(enableStatusRecord[row.status as '1' | '2']);
      return <NTag type={tagMap[row.status as string]}>{label}</NTag>;
    }
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center' as const,
    width: 200,
    render: (row: Api.SystemManage.Dept) => (
      <div class="flex flex-wrap justify-center gap-8px">
        {hasAuth('sys:dept:add') && (
          <NButton type="primary" text size="small" onClick={() => handleAdd(row.id)}>
            {$t('page.manage.dept.addChild')}
          </NButton>
        )}
        {hasAuth('sys:dept:edit') && (
          <NButton type="primary" text size="small" onClick={() => handleEdit(row)}>
            {$t('common.edit')}
          </NButton>
        )}
        {hasAuth('sys:dept:delete') && (
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
];

getData();
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :title="$t('page.manage.dept.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <NSpace :size="12">
          <NButton @click="getData">{{ $t('common.refresh') }}</NButton>
          <NButton v-if="hasAuth('sys:dept:add')" type="primary" @click="handleAdd()">
            {{ $t('common.add') }}
          </NButton>
        </NSpace>
      </template>
      <NDataTable
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :loading="loading"
        :row-key="(row: Api.SystemManage.Dept) => row.id"
        default-expand-all
      />
      <DeptOperateDrawer
        v-model:visible="drawerVisible"
        :operate-type="operateType"
        :row-data="editingRow"
        @submitted="getData"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
