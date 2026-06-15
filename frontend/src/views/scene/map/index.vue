<script setup lang="tsx">
import { reactive, ref, shallowRef } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag } from 'naive-ui';
import { fetchGetSceneMapList, fetchDeleteSceneMap } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import SceneMapOperateDrawer from './modules/scene-map-operate-drawer.vue';
import SceneMapSearch from './modules/scene-map-search.vue';
import SceneMapDetailDrawer from './modules/scene-map-detail-drawer.vue';

const appStore = useAppStore();
const { hasAuth } = useAuth();

/** 场景地图搜索参数 */
const searchParams: Api.Scene.SceneMapSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  group_id: undefined,
  status: null
});

/** 场景地图表格 */
const {
  columns: mapColumns,
  columnChecks: mapColumnChecks,
  data: mapData,
  getData: getMapData,
  getDataByPage: getMapDataByPage,
  loading: mapLoading,
  mobilePagination: mapMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetSceneMapList(searchParams),
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
      title: '地图名称',
      align: 'center',
      minWidth: 150,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'group_name',
      title: '所属分组',
      align: 'center',
      width: 120,
      render: row => <span>{row.group_name || '-'}</span>
    },
    {
      key: 'image_id',
      title: '地图图片',
      align: 'center',
      width: 100,
      render: row => {
        if (row.image_id) {
          return <NButton text type="primary" size="small">查看图片</NButton>;
        }
        return <span>-</span>;
      }
    },
    {
      key: 'width',
      title: '宽度',
      align: 'center',
      width: 80,
      render: row => <span>{row.width ?? '-'}</span>
    },
    {
      key: 'height',
      title: '高度',
      align: 'center',
      width: 80,
      render: row => <span>{row.height ?? '-'}</span>
    },
    {
      key: 'start_point',
      title: '起始点位',
      align: 'center',
      width: 140,
      render: row => {
        if (row.start_point_x || row.start_point_y) {
          return <span>({row.start_point_x}, {row.start_point_y})</span>;
        }
        return <span>-</span>;
      }
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
      width: 240,
      fixed: 'right',
      render: row => {
        return (
          <div class="flex-center gap-8px">
            <NButton type="info" ghost size="small" onClick={() => handleViewDetail(row)}>
              详情
            </NButton>
            {hasAuth('scene:map:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => handleEditMap(row.id)}>
                编辑
              </NButton>
            )}
            {hasAuth('scene:map:delete') && (
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
  drawerVisible: mapDrawerVisible,
  operateType: mapOperateType,
  editingData: editingMapData,
  handleAdd: handleAddMap,
  handleEdit: handleEditMapRaw,
  checkedRowKeys: checkedMapRowKeys,
  onDeleted: onMapDeleted
} = useTableOperate(mapData, 'id', getMapData);

function handleEditMap(id: number) {
  handleEditMapRaw(id);
}

async function handleDelete(id: number) {
  try {
    await fetchDeleteSceneMap(id);
    window.$message?.success('删除成功');
    onMapDeleted();
  } catch (error) {
    console.error('删除场景地图失败:', error);
  }
}

/** 详情抽屉 */
const detailDrawerVisible = ref(false);
const detailMapData = shallowRef<Api.Scene.SceneMap | null>(null);

function handleViewDetail(row: Api.Scene.SceneMap) {
  detailMapData.value = { ...row };
  detailDrawerVisible.value = true;
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <SceneMapSearch v-model:model="searchParams" @search="getMapDataByPage" @reset="getMapDataByPage" />
    <NCard title="场景地图管理" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="mapColumnChecks"
          :disabled-delete="checkedMapRowKeys.length === 0"
          :loading="mapLoading"
          @refresh="getMapData"
        >
          <template #default>
            <NButton
              v-if="hasAuth('scene:map:add')"
              size="small"
              ghost
              type="primary"
              @click="handleAddMap"
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
        v-model:checked-row-keys="checkedMapRowKeys"
        :columns="mapColumns"
        :data="mapData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1100"
        :loading="mapLoading"
        remote
        :row-key="row => row.id"
        :pagination="mapMobilePagination"
        class="sm:h-full"
      />
      <SceneMapOperateDrawer
        v-model:visible="mapDrawerVisible"
        :operate-type="mapOperateType"
        :row-data="editingMapData"
        @submitted="getMapDataByPage"
      />
      <SceneMapDetailDrawer
        v-model:visible="detailDrawerVisible"
        :map-data="detailMapData"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
