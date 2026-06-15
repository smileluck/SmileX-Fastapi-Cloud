<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue';
import { useMapEditor, type DrawingMode } from './composables/useMapEditor';
import EditorToolbar from './modules/editor-toolbar.vue';
import CanvasEditor from './modules/canvas-editor.vue';
import PropertyPanel from './modules/property-panel.vue';
import { fetchCreateSceneMap } from '@/service/api/scene';
import { fetchUploadFile, getFilePreviewUrl } from '@/service/api/file';

defineOptions({ name: 'SceneMapEditor' });

const editor = useMapEditor();
const canvasRef = ref<InstanceType<typeof CanvasEditor>>();

const zoomLevel = ref(1);
const cursorX = ref(0);
const cursorY = ref(0);

const addDialogVisible = ref(false);
const newMapName = ref('');
const newMapGroupId = ref<number | null>(null);
const newMapImageId = ref<number | null>(null);
const newMapImageUrl = ref('');
const newMapOriginalWidth = ref<number | null>(null);
const newMapOriginalHeight = ref<number | null>(null);
const newMapImageRef = ref<HTMLImageElement>();
const newMapPointX = ref<number | null>(null);
const newMapPointY = ref<number | null>(null);
const newMapPointAngle = ref(0);
const newMapResolution = ref(0.05);
const addSceneUploading = ref(false);

function getScaledStartPoint() {
  const imageRect = newMapImageRef.value?.getBoundingClientRect();
  if (
    !imageRect ||
    !newMapOriginalWidth.value ||
    !newMapOriginalHeight.value ||
    imageRect.width <= 0 ||
    imageRect.height <= 0 ||
    newMapPointX.value === null ||
    newMapPointY.value === null
  ) {
    return null;
  }
  const scaleX = newMapOriginalWidth.value / imageRect.width;
  const scaleY = newMapOriginalHeight.value / imageRect.height;
  return {
    x: newMapPointX.value * scaleX,
    y: newMapPointY.value * scaleY,
    angle: newMapPointAngle.value,
  };
}

onMounted(async () => {
  await editor.loadSceneList();
  if (editor.sceneList.value.length > 0) {
    await editor.loadMap(editor.sceneList.value[0].id);
  }
});

async function handleSelectMap(mapId: number) {
  await editor.loadMap(mapId);
}

async function handleAddScene() {
  newMapName.value = '';
  newMapGroupId.value = null;
  newMapImageId.value = null;
  newMapImageUrl.value = '';
  newMapOriginalWidth.value = null;
  newMapOriginalHeight.value = null;
  newMapPointX.value = null;
  newMapPointY.value = null;
  newMapPointAngle.value = 0;
  newMapResolution.value = 0.05;
  addDialogVisible.value = true;
}

async function handleAddSceneUpload({ file }: { file: { file: File | null } }) {
  if (!file.file) return;
  addSceneUploading.value = true;
  try {
    const { data, error } = await fetchUploadFile(file.file, { includeImageInfo: true });
    if (!error && data) {
      newMapImageId.value = data.id;
      newMapImageUrl.value = getFilePreviewUrl(data.id);
      newMapOriginalWidth.value = data.image_width ?? null;
      newMapOriginalHeight.value = data.image_height ?? null;
      window.$message?.success('图片上传成功');
    }
  } finally {
    addSceneUploading.value = false;
  }
}

function handleRemoveAddSceneImage() {
  newMapImageId.value = null;
  newMapImageUrl.value = '';
  newMapOriginalWidth.value = null;
  newMapOriginalHeight.value = null;
}

async function confirmAddScene() {
  if (!newMapName.value.trim()) {
    window.$message?.warning('请输入场景名称');
    return false;
  }
  if (!newMapImageId.value) {
    window.$message?.warning('请上传场景图片');
    return false;
  }
  if (!newMapOriginalWidth.value || !newMapOriginalHeight.value) {
    window.$message?.warning('请确认图片原图尺寸');
    return false;
  }
  const startPoint = getScaledStartPoint();
  if (!startPoint) {
    window.$message?.warning('请输入起始点位 X、Y 和角度');
    return false;
  }
  try {
    const { data } = await fetchCreateSceneMap({
      name: newMapName.value.trim(),
      group_id: newMapGroupId.value,
      image_id: newMapImageId.value,
      width: newMapOriginalWidth.value,
      height: newMapOriginalHeight.value,
      resolution: newMapResolution.value,
      start_point_x: startPoint.x,
      start_point_y: startPoint.y,
    });
    if (data) {
      addDialogVisible.value = false;
      await editor.loadSceneList();
      await editor.loadMap((data as any).id);

      editor.addAnnotation({
        x: 0,
        y: 0,
        name: '起始点位',
        angle: startPoint.angle,
        type: 'navigation',
      });
      await editor.saveMap({ silent: true });

      window.$message?.success('创建成功');
    }
  } catch (e: any) {
    window.$message?.error(e?.message || '创建失败');
  }
  return false;
}

async function handleDeleteScene(mapId: number) {
  try {
    await editor.deleteScene(mapId);
  } catch (e: any) {
    window.$message?.error(e?.message || '删除失败');
  }
}

function handleAddAnnotation(data: { x: number; y: number; type: string }) {
  const name = data.type === 'navigation' ? `导航点${(editor.editorData.value?.annotations.length || 0) + 1}` : `接待点${(editor.editorData.value?.annotations.length || 0) + 1}`;
  editor.addAnnotation({ x: data.x, y: data.y, name, angle: 0, type: data.type });
}

function handleAddPath(data: { startId: number; endId: number }) {
  editor.addPath({ start_annotation_id: data.startId, end_annotation_id: data.endId });
}

function handleAddObject(data: { type: string; x: number; y: number; width: number; height: number; points?: string }) {
  editor.addObject({
    type: data.type,
    x: data.x,
    y: data.y,
    width: data.width,
    height: data.height,
    points: data.points || null,
  });
}

function handleUpdateElement(data: { type: string; id: number; updates: Record<string, any> }) {
  editor.updateElement(data.type as any, data.id, data.updates);
}

function handleExport(format: 'png' | 'jpeg' | 'webp') {
  canvasRef.value?.exportCanvas(format);
}

function handleZoomChange(zoom: number) {
  zoomLevel.value = zoom;
}

async function handleLocateRobot(data: { mapId: number; x: number; y: number }) {
  if (editor.selectedMapId.value !== data.mapId) {
    await editor.loadMap(data.mapId);
  }
  await nextTick();
  canvasRef.value?.locateMeterPoint(data.x, data.y);
}

function handleCursorPosition(x: number, y: number) {
  cursorX.value = x;
  cursorY.value = y;
}

function handleFocusAnnotation(id: number) {
  if (!editor.editorData.value) return;
  const ann = editor.editorData.value.annotations.find(a => a.id === id);
  if (!ann) return;
  canvasRef.value?.locateMeterPoint(ann.x, ann.y);
}
</script>

<template>
  <div class="flex h-full min-h-0 flex-col">
    <EditorToolbar
      :drawing-mode="editor.drawingMode.value"
      :can-undo="editor.canUndo.value"
      :can-redo="editor.canRedo.value"
      :is-dirty="editor.isDirty.value"
      :saving="editor.saving.value"
      @update:drawing-mode="(m: DrawingMode) => (editor.drawingMode.value = m)"
      @undo="editor.undo()"
      @redo="editor.redo()"
      @save="editor.saveMap()"
      @export="handleExport"
    />

    <div class="flex min-h-0 flex-1 overflow-hidden">
      <div class="relative min-w-0 flex-1">
        <CanvasEditor
          ref="canvasRef"
          :editor-data="editor.editorData.value"
          :selected-element="editor.selectedElement.value"
          :drawing-mode="editor.drawingMode.value"
          :grid-spacing="editor.gridSpacing.value"
          :resolution="editor.resolution.value"
          :loading="editor.loading.value"
          @select-element="el => (editor.selectedElement.value = el)"
          @add-annotation="handleAddAnnotation"
          @add-path="handleAddPath"
          @add-object="handleAddObject"
          @update-element="handleUpdateElement"
          @zoom-change="handleZoomChange"
          @cursor-position="handleCursorPosition"
        />
        <div class="absolute bottom-8px left-8px rounded bg-black/50 px-8px py-4px text-xs text-white">
          坐标: {{ cursorX.toFixed(2) }}m, {{ cursorY.toFixed(2) }}m
        </div>
      </div>

      <PropertyPanel
        class="w-380px flex-shrink-0"
        :editor-data="editor.editorData.value"
        :selected-element="editor.selectedElement.value"
        :resolution="editor.resolution.value"
        :scene-list="editor.sceneList.value"
        :selected-map-id="editor.selectedMapId.value"
        :map-id="editor.selectedMapId.value"
        @update-element="handleUpdateElement"
        @remove-element="editor.removeElement"
        @select-scene="handleSelectMap"
        @add-scene="handleAddScene"
        @delete-scene="handleDeleteScene"
        @locate-robot="handleLocateRobot"
        @focus-annotation="handleFocusAnnotation"
        @select-element="el => (editor.selectedElement.value = el)"
      />
    </div>

    <!-- Add scene dialog -->
    <NModal v-model:show="addDialogVisible" preset="dialog" title="新增场景" positive-text="确定" negative-text="取消" @positive-click="confirmAddScene">
      <NForm label-placement="left" label-width="92">
        <NFormItem label="场景名称">
          <NInput v-model:value="newMapName" placeholder="请输入场景名称" />
        </NFormItem>
        <NFormItem label="场景图片">
          <div class="w-full">
            <NUpload :max="1" accept="image/*" :custom-request="handleAddSceneUpload" :show-file-list="false">
              <NButton :loading="addSceneUploading" ghost>
                <template #icon><icon-ic-round-upload /></template>
                {{ addSceneUploading ? '上传中...' : '选择图片' }}
              </NButton>
            </NUpload>
            <div v-if="newMapImageUrl" class="mt-8px flex items-center gap-8px">
              <img ref="newMapImageRef" :src="newMapImageUrl" class="max-h-160px max-w-260px object-contain" />
              <div class="text-xs text-gray-500">
                原图：{{ newMapOriginalWidth ?? '-' }} × {{ newMapOriginalHeight ?? '-' }} px
              </div>
              <NButton text type="error" @click="handleRemoveAddSceneImage">移除</NButton>
            </div>
          </div>
        </NFormItem>
        <NFormItem label="起始点位">
          <div class="grid w-full grid-cols-4 gap-8px">
            <NInputNumber v-model:value="newMapPointX" placeholder="原始X" class="w-full" />
            <NInputNumber v-model:value="newMapPointY" placeholder="原始Y" class="w-full" />
            <NInputNumber v-model:value="newMapPointAngle" placeholder="角度" class="w-full" />
            <NInputNumber v-model:value="newMapResolution" placeholder="分辨率" :step="0.01" :min="0.01" class="w-full" />
          </div>
        </NFormItem>
        <div class="text-xs text-gray-500">
          起始点位按上方图片当前网页显示尺寸录入，保存时会按 原图尺寸 / 网页显示尺寸 缩放到地图原图坐标。分辨率(m/px)对应 ROS map.yaml 中的 resolution，默认 0.05。
        </div>
      </NForm>
    </NModal>
  </div>
</template>
