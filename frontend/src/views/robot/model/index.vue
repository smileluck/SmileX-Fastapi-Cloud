<script setup lang="tsx">
import { reactive } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchGetRobotModelList, fetchDeleteRobotModel } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import { booleanToEnableStatus } from '@/utils/status';
import RobotModelOperateDrawer from './modules/robot-model-operate-drawer.vue';
import RobotModelSearch from './modules/robot-model-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

/** 机器人型号搜索参数 */
const searchParams: Api.Robot.RobotModelSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  brand: null,
  status: null
});

/** 机器人型号表格 */
const {
  columns: modelColumns,
  columnChecks: modelColumnChecks,
  data: modelData,
  getData: getModelData,
  getDataByPage: getModelDataByPage,
  loading: modelLoading,
  mobilePagination: modelMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetRobotModelList(searchParams),
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
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: '型号名称',
      align: 'center',
      minWidth: 140,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'brand',
      title: '品牌',
      align: 'center',
      width: 120
    },
    {
      key: 'model',
      title: '型号标识',
      align: 'center',
      width: 140
    },
    {
      key: 'status',
      title: $t('common.status'),
      align: 'center',
      width: 80,
      render: row => {
        if (row.status === null) {
          return null;
        }
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = row.status === '1' ? '启用' : '禁用';
        return <NTag type={tagMap[row.status]} size="small">{label}</NTag>;
      }
    },
    {
      key: 'sort',
      title: '排序',
      align: 'center',
      width: 80
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 160,
      fixed: 'right',
      render: row => {
        return (
          <div class="flex-center gap-8px">
            {hasAuth('robot:model:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => handleEditModel(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('robot:model:delete') && (
              <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
                {{
                  default: () => $t('common.confirmDelete'),
                  trigger: () => (
                    <NButton type="error" ghost size="small">
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

/** 机器人型号操作 */
const {
  drawerVisible: modelDrawerVisible,
  operateType: modelOperateType,
  editingData: editingModelData,
  handleAdd: handleAddModel,
  handleEdit: handleEditModel,
  checkedRowKeys: checkedModelRowKeys,
  onBatchDeleted: onModelBatchDeleted,
  onDeleted: onModelDeleted
} = useTableOperate(modelData, 'id', getModelData);

/** 删除机器人型号 */
async function handleDelete(id: number) {
  try {
    await fetchDeleteRobotModel(id);
    message.success($t('common.deleteSuccess'));
    onModelDeleted();
  } catch (error) {
    console.error('删除机器人型号失败:', error);
  }
}

/** 批量删除机器人型号 */
async function handleBatchDelete() {
  if (checkedModelRowKeys.value.length === 0) {
    message.warning($t('common.pleaseSelect'));
    return;
  }
  try {
    for (const key of checkedModelRowKeys.value) {
      await fetchDeleteRobotModel(Number(key));
    }
    message.success($t('common.deleteSuccess'));
    onModelBatchDeleted();
  } catch (error) {
    console.error('批量删除机器人型号失败:', error);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <RobotModelSearch v-model:model="searchParams" @search="getModelDataByPage" @reset="getModelDataByPage" />
    <NCard
      title="机器人型号管理"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="modelColumnChecks"
          :disabled-delete="checkedModelRowKeys.length === 0"
          :loading="modelLoading"
          @refresh="getModelData"
        >
          <template #default>
            <NButton
              v-if="hasAuth('robot:model:add')"
              size="small"
              ghost
              type="primary"
              @click="handleAddModel"
            >
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </NButton>
            <NPopconfirm
              v-if="hasAuth('robot:model:delete')"
              @positive-click="handleBatchDelete"
            >
              <template #trigger>
                <NButton
                  size="small"
                  ghost
                  type="error"
                  :disabled="checkedModelRowKeys.length === 0"
                >
                  <template #icon>
                    <icon-ic-round-delete class="text-icon" />
                  </template>
                  {{ $t('common.batchDelete') }}
                </NButton>
              </template>
              {{ $t('common.confirmDelete') }}
            </NPopconfirm>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedModelRowKeys"
        :columns="modelColumns"
        :data="modelData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="900"
        :loading="modelLoading"
        remote
        :row-key="row => row.id"
        :pagination="modelMobilePagination"
        class="sm:h-full"
      />
      <RobotModelOperateDrawer
        v-model:visible="modelDrawerVisible"
        :operate-type="modelOperateType"
        :row-data="editingModelData"
        @submitted="getModelDataByPage"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
