<script setup lang="tsx">
import { ref, watch } from 'vue';
import { NButton, NDataTable, NPopconfirm, NSpace, NTab, NTabs } from 'naive-ui';
import { useNaivePaginatedTable } from '@/hooks/common/table';
import {
  fetchGetMapAnnotations,
  fetchDeleteMapAnnotation,
  fetchGetMapObjects,
  fetchDeleteMapObject
} from '@/service/api';
import { fetchSaveEditorData } from '@/service/api/scene';
import { getFilePreviewUrl } from '@/service/api/file';
import SceneMapAnnotationModal from './scene-map-annotation-modal.vue';
import SceneMapObjectModal from './scene-map-object-modal.vue';

defineOptions({
  name: 'SceneMapDetailDrawer'
});

interface Props {
  mapData?: Api.Scene.SceneMap | null;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', {
  default: false
});

/** 当前激活的Tab */
const activeTab = ref('annotation');

/** ========== 标注管理 ========== */
const annotationSearchParams = ref<{ page: number; page_size: number }>({ page: 1, page_size: 10 });

const annotationModalVisible = ref(false);
const editingAnnotation = ref<Api.Scene.SceneMapAnnotation | null>(null);

const {
  columns: annotationColumns,
  data: annotationData,
  getData: getAnnotationData,
  getDataByPage: getAnnotationDataByPage,
  loading: annotationLoading,
  mobilePagination: annotationPagination
} = useNaivePaginatedTable({
  api: () => fetchGetMapAnnotations(props.mapData?.id ?? 0, annotationSearchParams.value),
  transform: response => {
    const { data, error } = response;
    if (error) {
      return { data: [], pageNum: 1, pageSize: 10, total: 0, totalPages: 1 };
    }
    const list = Array.isArray(data) ? data : data?.records ?? [];
    return { data: list, pageNum: 1, pageSize: list.length || 10, total: list.length, totalPages: 1 };
  },
  onPaginationParamsChange: params => {
    annotationSearchParams.value.page = params.page;
    annotationSearchParams.value.page_size = params.pageSize;
  },
  columns: () => [
    {
      key: 'index',
      title: '序号',
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'name',
      title: '标注名称',
      align: 'center',
      minWidth: 120,
      ellipsis: { tooltip: true }
    },
    {
      key: 'type',
      title: '类型',
      align: 'center',
      width: 100
    },
    {
      key: 'x',
      title: 'X坐标',
      align: 'center',
      width: 80
    },
    {
      key: 'y',
      title: 'Y坐标',
      align: 'center',
      width: 80
    },
    {
      key: 'angle',
      title: '角度',
      align: 'center',
      width: 80
    },
    {
      key: 'operate',
      title: '操作',
      align: 'center',
      width: 150,
      render: (row: any) => {
        return (
          <NSpace size="small" justify="center">
            <NButton type="primary" ghost size="small" onClick={() => handleEditAnnotation(row)}>
              编辑
            </NButton>
            <NPopconfirm onPositiveClick={() => handleDeleteAnnotation(row.id)}>
              {{
                default: () => '确认删除？',
                trigger: () => (
                  <NButton type="error" ghost size="small">
                    删除
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

function handleAddAnnotation() {
  editingAnnotation.value = null;
  annotationModalVisible.value = true;
}

function handleEditAnnotation(row: Api.Scene.SceneMapAnnotation) {
  editingAnnotation.value = { ...row };
  annotationModalVisible.value = true;
}

async function handleDeleteAnnotation(id: number) {
  try {
    await fetchDeleteMapAnnotation(props.mapData?.id ?? 0, id);
    window.$message?.success('删除成功');
    getAnnotationDataByPage();
  } catch (error) {
    console.error('删除标注失败:', error);
  }
}

/** ========== 物体管理 ========== */
const objectSearchParams = ref<{ page: number; page_size: number }>({ page: 1, page_size: 10 });

const objectModalVisible = ref(false);
const editingObject = ref<Api.Scene.SceneMapObject | null>(null);

const {
  columns: objectColumns,
  data: objectData,
  getData: getObjectData,
  getDataByPage: getObjectDataByPage,
  loading: objectLoading,
  mobilePagination: objectPagination
} = useNaivePaginatedTable({
  api: () => fetchGetMapObjects(props.mapData?.id ?? 0, objectSearchParams.value),
  transform: response => {
    const { data, error } = response;
    if (error) {
      return { data: [], pageNum: 1, pageSize: 10, total: 0, totalPages: 1 };
    }
    const list = Array.isArray(data) ? data : data?.records ?? [];
    return { data: list, pageNum: 1, pageSize: list.length || 10, total: list.length, totalPages: 1 };
  },
  onPaginationParamsChange: params => {
    objectSearchParams.value.page = params.page;
    objectSearchParams.value.page_size = params.pageSize;
  },
  columns: () => [
    {
      key: 'index',
      title: '序号',
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'type',
      title: '类型',
      align: 'center',
      width: 100
    },
    {
      key: 'x',
      title: 'X坐标',
      align: 'center',
      width: 80
    },
    {
      key: 'y',
      title: 'Y坐标',
      align: 'center',
      width: 80
    },
    {
      key: 'width',
      title: '宽度',
      align: 'center',
      width: 80
    },
    {
      key: 'height',
      title: '高度',
      align: 'center',
      width: 80
    },
    {
      key: 'operate',
      title: '操作',
      align: 'center',
      width: 150,
      render: (row: any) => {
        return (
          <NSpace size="small" justify="center">
            <NButton type="primary" ghost size="small" onClick={() => handleEditObject(row)}>
              编辑
            </NButton>
            <NPopconfirm onPositiveClick={() => handleDeleteObject(row.id)}>
              {{
                default: () => '确认删除？',
                trigger: () => (
                  <NButton type="error" ghost size="small">
                    删除
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

function handleAddObject() {
  editingObject.value = null;
  objectModalVisible.value = true;
}

function handleEditObject(row: Api.Scene.SceneMapObject) {
  editingObject.value = { ...row };
  objectModalVisible.value = true;
}

async function handleDeleteObject(id: number) {
  try {
    await fetchDeleteMapObject(props.mapData?.id ?? 0, id);
    window.$message?.success('删除成功');
    getObjectDataByPage();
  } catch (error) {
    console.error('删除物体失败:', error);
  }
}

/** ========== 导入JSON点位 ========== */
const importDialogVisible = ref(false);
const importJsonText = ref('');

interface ImportMapPoint {
  label: string;
  position: [number, number, number];
  description?: string;
}

function handleImportJson() {
  importJsonText.value = '';
  importDialogVisible.value = true;
}

async function confirmImportJson() {
  if (!props.mapData?.id) {
    window.$message?.warning('请先选择场景地图');
    return false;
  }

  let points: ImportMapPoint[];
  try {
    const parsed = JSON.parse(importJsonText.value);
    if (!Array.isArray(parsed)) {
      window.$message?.error('JSON 必须是数组');
      return false;
    }
    points = parsed;
  } catch {
    window.$message?.error('JSON 格式错误');
    return false;
  }

  try {
    const annotations = points.map((point, index) => {
      const [rwX, rwY, angle] = point.position || [];
      if (!point.label || !Number.isFinite(rwX) || !Number.isFinite(rwY) || !Number.isFinite(angle)) {
        throw new Error(`第 ${index + 1} 条数据缺少 label 或有效 position`);
      }
      return {
        id: null,
        x: rwX,
        y: rwY,
        angle,
        name: point.label.trim(),
        type: index === 0 ? 'navigation' : 'reception',
      };
    });

    const { error } = await fetchSaveEditorData(props.mapData.id, {
      annotations,
      paths: [],
      objects: [],
      deleted_annotation_ids: [],
      deleted_path_ids: [],
      deleted_object_ids: [],
    });

    if (error) {
      const msg = (error.response?.data as any)?.msg || error.message || '导入失败';
      window.$message?.error(msg);
      return false;
    }

    window.$message?.success(`已导入 ${annotations.length} 个点位`);
    importDialogVisible.value = false;
    getAnnotationDataByPage();
    return true;
  } catch (e: any) {
    window.$message?.error(e?.message || '导入失败');
    return false;
  }
}

/** 抽屉打开时加载数据 */
watch(visible, () => {
  if (visible.value && props.mapData?.id) {
    activeTab.value = 'annotation';
    annotationSearchParams.value = { page: 1, page_size: 10 };
    objectSearchParams.value = { page: 1, page_size: 10 };
    getAnnotationData();
    getObjectData();
  }
});

function closeDrawer() {
  visible.value = false;
}
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="'80%'">
    <NDrawerContent title="场景地图详情" :native-scrollbar="false" closable>
      <!-- 地图图片预览 -->
      <div v-if="mapData?.image_id" class="mb-16px">
        <NImage
          :src="getFilePreviewUrl(mapData.image_id)"
          :alt="mapData.name"
          object-fit="contain"
          class="max-h-400px"
          width="100%"
        />
      </div>
      <div v-else class="mb-16px">
        <NEmpty description="暂无地图图片" />
      </div>

      <!-- 地图基本信息 -->
      <NDescriptions bordered :column="3" label-placement="left" size="small" class="mb-16px">
        <NDescriptionsItem label="地图名称">{{ mapData?.name || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="所属分组">{{ mapData?.group_name || '-' }}</NDescriptionsItem>
        <NDescriptionsItem label="尺寸">{{ mapData?.width && mapData?.height ? `${mapData.width} x ${mapData.height}` : '-' }}</NDescriptionsItem>
      </NDescriptions>

      <!-- 标签页 -->
      <NTabs v-model:value="activeTab" type="line">
        <NTab name="annotation">标注信息</NTab>
        <NTab name="object">物体信息</NTab>
      </NTabs>

      <!-- 标注列表 -->
      <div v-show="activeTab === 'annotation'" class="mt-12px">
        <div class="mb-12px flex gap-8px">
          <NButton type="primary" size="small" @click="handleAddAnnotation">
            <template #icon>
              <icon-ic-round-plus class="text-icon" />
            </template>
            新增标注
          </NButton>
          <NButton size="small" @click="handleImportJson">
            <template #icon>
              <icon-ic-round-upload-file class="text-icon" />
            </template>
            导入JSON
          </NButton>
        </div>
        <NDataTable
          :columns="annotationColumns"
          :data="annotationData"
          size="small"
          :loading="annotationLoading"
          remote
          :row-key="(row: any) => row.id"
          :pagination="annotationPagination"
        />
      </div>

      <!-- 物体列表 -->
      <div v-show="activeTab === 'object'" class="mt-12px">
        <div class="mb-12px">
          <NButton type="primary" size="small" @click="handleAddObject">
            <template #icon>
              <icon-ic-round-plus class="text-icon" />
            </template>
            新增物体
          </NButton>
        </div>
        <NDataTable
          :columns="objectColumns"
          :data="objectData"
          size="small"
          :loading="objectLoading"
          remote
          :row-key="(row: any) => row.id"
          :pagination="objectPagination"
        />
      </div>

      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">关闭</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>

  <!-- 标注弹窗 -->
  <SceneMapAnnotationModal
    v-model:visible="annotationModalVisible"
    :map-id="mapData?.id ?? 0"
    :edit-data="editingAnnotation"
    @submitted="getAnnotationDataByPage"
  />

  <!-- 物体弹窗 -->
  <SceneMapObjectModal
    v-model:visible="objectModalVisible"
    :map-id="mapData?.id ?? 0"
    :edit-data="editingObject"
    @submitted="getObjectDataByPage"
  />

  <!-- 导入JSON点位弹窗 -->
  <NModal v-model:show="importDialogVisible" preset="dialog" title="导入JSON点位" positive-text="导入" negative-text="取消" @positive-click="confirmImportJson">
    <NInput
      v-model:value="importJsonText"
      type="textarea"
      :autosize="{ minRows: 12, maxRows: 18 }"
      placeholder="请粘贴包含 label、position 的 JSON 数组，例: [{&quot;label&quot;: &quot;点1&quot;, &quot;position&quot;: [1.0, 2.0, 90]}]"
    />
    <div class="mt-8px text-xs text-gray-500">position 按 [x, y, angle] 导入，坐标使用 ROS 世界坐标系，将按地图分辨率和起始点位自动转换。</div>
  </NModal>
</template>

<style scoped></style>
