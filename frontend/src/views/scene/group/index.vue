<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag } from 'naive-ui';
import { fetchGetSceneGroupList, fetchDeleteSceneGroup } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import SceneGroupOperateDrawer from './modules/scene-group-operate-drawer.vue';
import SceneGroupSearch from './modules/scene-group-search.vue';

const appStore = useAppStore();
const { hasAuth } = useAuth();

/** 场景分组搜索参数 */
const searchParams: Api.Scene.SceneGroupSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  status: null
});

/** 场景分组表格 */
const {
  columns: groupColumns,
  columnChecks: groupColumnChecks,
  data: groupData,
  getData: getGroupData,
  getDataByPage: getGroupDataByPage,
  loading: groupLoading,
  mobilePagination: groupMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetSceneGroupList(searchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((item: any) => ({
      ...item,
      status: booleanToEnableStatus(item.status)
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
      title: '序号',
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: '分组名称',
      align: 'center',
      minWidth: 150,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'parent_id',
      title: '上级分组',
      align: 'center',
      width: 150,
      render: row => {
        return <span>{row.parent_name || (row.parent_id ? `ID: ${row.parent_id}` : '-')}</span>;
      }
    },
    {
      key: 'sort',
      title: '排序',
      align: 'center',
      width: 80
    },
    {
      key: 'status',
      title: '状态',
      align: 'center',
      width: 80,
      render: row => {
        if (row.status === null) return null;
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = row.status === '1' ? '启用' : '禁用';
        return <NTag type={tagMap[row.status]} size="small">{label}</NTag>;
      }
    },
    {
      key: 'operate',
      title: '操作',
      align: 'center',
      width: 180,
      fixed: 'right',
      render: row => {
        return (
          <div class="flex-center gap-8px">
            {hasAuth('scene:group:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => handleEditGroup(row.id)}>
                编辑
              </NButton>
            )}
            {hasAuth('scene:group:delete') && (
              <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
                {{
                  default: () => '确认删除？',
                  trigger: () => (
                    <NButton type="error" ghost size="small">
                      删除
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

/** 表格操作 */
const {
  drawerVisible: groupDrawerVisible,
  operateType: groupOperateType,
  editingData: editingGroupData,
  handleAdd: handleAddGroup,
  handleEdit: handleEditGroupRaw,
  checkedRowKeys: checkedGroupRowKeys,
  onDeleted: onGroupDeleted
} = useTableOperate(groupData, 'id', getGroupData);

function handleEditGroup(id: number) {
  handleEditGroupRaw(id);
}

async function handleDelete(id: number) {
  try {
    await fetchDeleteSceneGroup(id);
    window.$message?.success('删除成功');
    onGroupDeleted();
  } catch (error) {
    console.error('删除场景分组失败:', error);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <SceneGroupSearch v-model:model="searchParams" @search="getGroupDataByPage" @reset="getGroupDataByPage" />
    <NCard title="场景分组管理" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="groupColumnChecks"
          :disabled-delete="checkedGroupRowKeys.length === 0"
          :loading="groupLoading"
          @refresh="getGroupData"
        >
          <template #default>
            <NButton
              v-if="hasAuth('scene:group:add')"
              size="small"
              ghost
              type="primary"
              @click="handleAddGroup"
            >
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              新增
            </NButton>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedGroupRowKeys"
        :columns="groupColumns"
        :data="groupData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="800"
        :loading="groupLoading"
        remote
        :row-key="row => row.id"
        :pagination="groupMobilePagination"
        class="sm:h-full"
      />
      <SceneGroupOperateDrawer
        v-model:visible="groupDrawerVisible"
        :operate-type="groupOperateType"
        :row-data="editingGroupData"
        @submitted="getGroupDataByPage"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
