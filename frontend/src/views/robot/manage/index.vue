<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import { fetchGetRobotList, fetchDeleteRobot } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import RobotOperateDrawer from './modules/robot-operate-drawer.vue';
import RobotSearch from './modules/robot-search.vue';
import RobotStatusDrawer from './modules/robot-status-drawer.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

/** 机器人搜索参数 */
const searchParams: Api.Robot.RobotSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  serial_number: null,
  status: null,
  model_id: undefined
});

/** 机器人状态颜色映射 */
const statusColorMap: Record<string, NaiveUI.ThemeColor> = {
  online: 'success',
  offline: 'warning',
  inactive: 'default'
};

/** 机器人状态标签映射 */
const statusLabelMap: Record<string, string> = {
  online: '在线',
  offline: '离线',
  inactive: '未激活'
};

/** 状态抽屉 */
const statusDrawerVisible = ref(false);
const statusDrawerRobotId = ref<number | null>(null);

function handleViewStatus(row: Api.Robot.Robot) {
  statusDrawerRobotId.value = row.id;
  statusDrawerVisible.value = true;
}

/** 机器人表格 */
const {
  columns: robotColumns,
  columnChecks: robotColumnChecks,
  data: robotData,
  getData: getRobotData,
  getDataByPage: getRobotDataByPage,
  loading: robotLoading,
  mobilePagination: robotMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetRobotList(searchParams),
  transform: response => {
    return defaultTransform(response);
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
      title: '机器人名称',
      align: 'center',
      minWidth: 140,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'model_name',
      title: '型号',
      align: 'center',
      width: 140,
      render: row => <span>{row.model_name || '-'}</span>
    },
    {
      key: 'serial_number',
      title: '序列号',
      align: 'center',
      width: 160,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'status',
      title: $t('common.status'),
      align: 'center',
      width: 100,
      render: row => {
        const tagType = statusColorMap[row.status] || 'default';
        const label = statusLabelMap[row.status] || row.status;
        return <NTag type={tagType} size="small">{label}</NTag>;
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 240,
      fixed: 'right',
      render: row => {
        return (
          <div class="flex-center gap-8px">
            {hasAuth('robot:manage:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => handleEditRobot(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('robot:manage:list') && (
              <NButton type="info" ghost size="small" onClick={() => handleViewStatus(row)}>
                状态
              </NButton>
            )}
            {hasAuth('robot:manage:delete') && (
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

/** 机器人操作 */
const {
  drawerVisible: robotDrawerVisible,
  operateType: robotOperateType,
  editingData: editingRobotData,
  handleAdd: handleAddRobot,
  handleEdit: handleEditRobot,
  checkedRowKeys: checkedRobotRowKeys,
  onBatchDeleted: onRobotBatchDeleted,
  onDeleted: onRobotDeleted
} = useTableOperate(robotData, 'id', getRobotData);

/** 删除机器人 */
async function handleDelete(id: number) {
  try {
    await fetchDeleteRobot(id);
    message.success($t('common.deleteSuccess'));
    onRobotDeleted();
  } catch (error) {
    console.error('删除机器人失败:', error);
  }
}

/** 批量删除机器人 */
async function handleBatchDelete() {
  if (checkedRobotRowKeys.value.length === 0) {
    message.warning($t('common.pleaseSelect'));
    return;
  }
  try {
    for (const key of checkedRobotRowKeys.value) {
      await fetchDeleteRobot(Number(key));
    }
    message.success($t('common.deleteSuccess'));
    onRobotBatchDeleted();
  } catch (error) {
    console.error('批量删除机器人失败:', error);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <RobotSearch v-model:model="searchParams" @search="getRobotDataByPage" @reset="getRobotDataByPage" />
    <NCard
      title="机器人管理"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="robotColumnChecks"
          :disabled-delete="checkedRobotRowKeys.length === 0"
          :loading="robotLoading"
          @refresh="getRobotData"
        >
          <template #default>
            <NButton
              v-if="hasAuth('robot:manage:add')"
              size="small"
              ghost
              type="primary"
              @click="handleAddRobot"
            >
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </NButton>
            <NPopconfirm
              v-if="hasAuth('robot:manage:delete')"
              @positive-click="handleBatchDelete"
            >
              <template #trigger>
                <NButton
                  size="small"
                  ghost
                  type="error"
                  :disabled="checkedRobotRowKeys.length === 0"
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
        v-model:checked-row-keys="checkedRobotRowKeys"
        :columns="robotColumns"
        :data="robotData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1000"
        :loading="robotLoading"
        remote
        :row-key="row => row.id"
        :pagination="robotMobilePagination"
        class="sm:h-full"
      />
      <RobotOperateDrawer
        v-model:visible="robotDrawerVisible"
        :operate-type="robotOperateType"
        :row-data="editingRobotData"
        @submitted="getRobotDataByPage"
      />
      <RobotStatusDrawer
        v-model:visible="statusDrawerVisible"
        :robot-id="statusDrawerRobotId"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
