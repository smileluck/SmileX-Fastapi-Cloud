import { reactive, ref, computed } from 'vue';
import { fetchGetEditorMapData, fetchSaveEditorData, fetchGetSceneMapList, fetchDeleteSceneMap } from '@/service/api/scene';
import { pixelToWorld, worldToPixel, pixelsDeltaToMeters, metersDeltaToPixels } from '@/utils/coordinate';

export type DrawingMode = 'select' | 'point-nav' | 'point-recv' | 'path' | 'rect-obstacle' | 'polygon-restricted';

export interface SelectedElement {
  type: 'annotation' | 'path' | 'object';
  id: number;
}

const MAX_UNDO_LEVELS = 50;

export function useMapEditor() {
  const editorData = ref<Api.Scene.EditorMapData | null>(null);
  const selectedMapId = ref<number | null>(null);
  const selectedElement = ref<SelectedElement | null>(null);
  const drawingMode = ref<DrawingMode>('select');
  const gridSpacing = ref(5);
  const isDirty = ref(false);
  const loading = ref(false);
  const saving = ref(false);
  const sceneList = ref<Api.Scene.SceneMap[]>([]);

  const undoStack: string[] = [];
  const redoStack: string[] = [];

  const deletedAnnotationIds: Set<number> = new Set();
  const deletedPathIds: Set<number> = new Set();
  const deletedObjectIds: Set<number> = new Set();

  const resolution = computed(() => editorData.value?.map.resolution ?? 0.2);

  function pixelToMeterDelta(px: number): number {
    return pixelsDeltaToMeters(px, resolution.value);
  }

  function meterToPixelDelta(m: number): number {
    return metersDeltaToPixels(m, resolution.value);
  }

  function pixelToWorldCoords(px: number, py: number) {
    const map = editorData.value?.map;
    return pixelToWorld(px, py, map?.start_point_x ?? 0, map?.start_point_y ?? 0, resolution.value);
  }

  function worldToPixelCoords(wx: number, wy: number) {
    const map = editorData.value?.map;
    return worldToPixel(wx, wy, map?.start_point_x ?? 0, map?.start_point_y ?? 0, resolution.value);
  }

  async function loadSceneList() {
    try {
      const { data } = await fetchGetSceneMapList({ page: 1, page_size: 999, status: null, name: null, group_id: undefined });
      if (data) {
        sceneList.value = (data as any).records || data || [];
      }
    } catch {
      sceneList.value = [];
    }
  }

  async function loadMap(mapId: number) {
    loading.value = true;
    try {
      const { data } = await fetchGetEditorMapData(mapId);
      if (data) {
        editorData.value = data;
        selectedMapId.value = mapId;
        selectedElement.value = null;
        isDirty.value = false;
        undoStack.length = 0;
        redoStack.length = 0;
        deletedAnnotationIds.clear();
        deletedPathIds.clear();
        deletedObjectIds.clear();
      }
    } finally {
      loading.value = false;
    }
  }

  function pushUndoSnapshot() {
    if (!editorData.value) return;
    const snapshot = JSON.stringify({
      annotations: editorData.value.annotations,
      paths: editorData.value.paths,
      objects: editorData.value.objects,
    });
    undoStack.push(snapshot);
    if (undoStack.length > MAX_UNDO_LEVELS) {
      undoStack.shift();
    }
    redoStack.length = 0;
    isDirty.value = true;
  }

  function undo() {
    if (!editorData.value || undoStack.length === 0) return;
    const current = JSON.stringify({
      annotations: editorData.value.annotations,
      paths: editorData.value.paths,
      objects: editorData.value.objects,
    });
    redoStack.push(current);

    const snapshot = undoStack.pop()!;
    const parsed = JSON.parse(snapshot);
    editorData.value.annotations = parsed.annotations;
    editorData.value.paths = parsed.paths;
    editorData.value.objects = parsed.objects;
    selectedElement.value = null;
    isDirty.value = true;
  }

  function redo() {
    if (!editorData.value || redoStack.length === 0) return;
    const current = JSON.stringify({
      annotations: editorData.value.annotations,
      paths: editorData.value.paths,
      objects: editorData.value.objects,
    });
    undoStack.push(current);

    const snapshot = redoStack.pop()!;
    const parsed = JSON.parse(snapshot);
    editorData.value.annotations = parsed.annotations;
    editorData.value.paths = parsed.paths;
    editorData.value.objects = parsed.objects;
    selectedElement.value = null;
    isDirty.value = true;
  }

  const canUndo = computed(() => undoStack.length > 0);
  const canRedo = computed(() => redoStack.length > 0);

  function validateBeforeSave(): string[] {
    const errors: string[] = [];
    if (!editorData.value) {
      errors.push('未加载地图数据');
      return errors;
    }
    const annotations = editorData.value.annotations;
    if (annotations.length === 0) {
      return errors;
    }
    const hasNav = annotations.some(a => a.type === 'navigation' || a.type === '导航点');
    if (!hasNav) {
      errors.push('地图至少需要包含1个导航点');
    }
    const minDist = 0.5;
    for (let i = 0; i < annotations.length; i++) {
      for (let j = i + 1; j < annotations.length; j++) {
        const dx = Math.abs(annotations[i].x - annotations[j].x);
        const dy = Math.abs(annotations[i].y - annotations[j].y);
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < minDist) {
          errors.push(`标注 "${annotations[i].name}" 和 "${annotations[j].name}" 间距小于 ${minDist}m`);
          break;
        }
      }
      if (errors.length > 5) break;
    }
    return errors;
  }

  async function saveMap(options?: { silent?: boolean }): Promise<boolean> {
    if (!editorData.value || !selectedMapId.value) return false;
    const errors = validateBeforeSave();
    if (errors.length > 0) {
      window.$message?.error(errors[0]);
      return false;
    }
    saving.value = true;
    try {
      const existingIds = new Set([
        ...editorData.value.annotations.map(a => a.id),
        ...editorData.value.paths.map(p => p.id),
        ...editorData.value.objects.map(o => o.id),
      ]);

      await fetchSaveEditorData(selectedMapId.value, {
        annotations: editorData.value.annotations.map(a => ({
          id: a.id > 0 ? a.id : null,
          x: a.x,
          y: a.y,
          name: a.name,
          angle: a.angle,
          type: a.type,
        })),
        paths: editorData.value.paths.map(p => ({
          id: p.id > 0 ? p.id : null,
          start_annotation_id: p.start_annotation_id,
          end_annotation_id: p.end_annotation_id,
          name: p.name,
          points: p.points,
        })),
        objects: editorData.value.objects.map(o => ({
          id: o.id > 0 ? o.id : null,
          type: o.type,
          x: o.x,
          y: o.y,
          width: o.width,
          height: o.height,
          points: o.points,
        })),
        deleted_annotation_ids: [...deletedAnnotationIds],
        deleted_path_ids: [...deletedPathIds],
        deleted_object_ids: [...deletedObjectIds],
      });

      deletedAnnotationIds.clear();
      deletedPathIds.clear();
      deletedObjectIds.clear();

      isDirty.value = false;
      if (!options?.silent) {
        window.$message?.success('保存成功');
      }
      return true;
    } catch (e: any) {
      window.$message?.error(e?.message || '保存失败');
      return false;
    } finally {
      saving.value = false;
    }
  }

  async function deleteScene(id: number) {
    await fetchDeleteSceneMap(id);
    if (selectedMapId.value === id) {
      editorData.value = null;
      selectedMapId.value = null;
      selectedElement.value = null;
    }
    await loadSceneList();
    window.$message?.success('删除成功');
  }

  function createAnnotation(annotation: { x: number; y: number; name: string; angle: number; type: string }, id: number) {
    return {
      id,
      map_id: selectedMapId.value!,
      x: annotation.x,
      y: annotation.y,
      name: annotation.name,
      angle: annotation.angle,
      type: annotation.type,
      created_by: '',
      updated_by: '',
      status: null,
      created_at: null,
      updated_at: null,
    } as unknown as Api.Scene.SceneMapAnnotation;
  }

  function addAnnotation(annotation: { x: number; y: number; name: string; angle: number; type: string }) {
    if (!editorData.value) return;
    pushUndoSnapshot();
    const newId = -(Date.now());
    editorData.value.annotations.push(createAnnotation(annotation, newId));
    return newId;
  }

  function addAnnotations(annotations: { x: number; y: number; name: string; angle: number; type: string }[]) {
    if (!editorData.value || annotations.length === 0) return;
    pushUndoSnapshot();
    const baseId = Date.now();
    editorData.value.annotations.push(...annotations.map((annotation, index) => createAnnotation(annotation, -(baseId + index))));
  }

  function addPath(path: { start_annotation_id: number; end_annotation_id: number; name?: string; points?: string | null }) {
    if (!editorData.value) return;
    pushUndoSnapshot();
    const newId = -(Date.now());
    const newItem = {
      id: newId,
      map_id: selectedMapId.value!,
      start_annotation_id: path.start_annotation_id,
      end_annotation_id: path.end_annotation_id,
      name: path.name ?? null,
      points: path.points ?? null,
      created_by: '',
      updated_by: '',
      status: null,
      created_at: null,
      updated_at: null,
    } as unknown as Api.Scene.SceneMapPath;
    editorData.value.paths.push(newItem);
    return newId;
  }

  function addObject(obj: { type: string; x: number; y: number; width: number; height: number; points: string | null }) {
    if (!editorData.value) return;
    pushUndoSnapshot();
    const newId = -(Date.now());
    const newItem = {
      id: newId,
      map_id: selectedMapId.value!,
      type: obj.type,
      x: obj.x,
      y: obj.y,
      width: obj.width,
      height: obj.height,
      points: obj.points,
      created_by: '',
      updated_by: '',
      status: null,
      created_at: null,
      updated_at: null,
    } as unknown as Api.Scene.SceneMapObject;
    editorData.value.objects.push(newItem);
    return newId;
  }

  function removeElement(type: 'annotation' | 'path' | 'object', id: number) {
    if (!editorData.value) return;
    pushUndoSnapshot();
    if (type === 'annotation') {
      if (id > 0) deletedAnnotationIds.add(id);
      const removedPaths = editorData.value.paths.filter(
        p => p.start_annotation_id === id || p.end_annotation_id === id
      );
      removedPaths.forEach(p => { if (p.id > 0) deletedPathIds.add(p.id); });
      editorData.value.annotations = editorData.value.annotations.filter(a => a.id !== id);
      editorData.value.paths = editorData.value.paths.filter(
        p => p.start_annotation_id !== id && p.end_annotation_id !== id
      );
    } else if (type === 'path') {
      if (id > 0) deletedPathIds.add(id);
      editorData.value.paths = editorData.value.paths.filter(p => p.id !== id);
    } else if (type === 'object') {
      if (id > 0) deletedObjectIds.add(id);
      editorData.value.objects = editorData.value.objects.filter(o => o.id !== id);
    }
    if (selectedElement.value?.id === id) {
      selectedElement.value = null;
    }
  }

  function updateElement(type: 'annotation' | 'path' | 'object', id: number, data: Record<string, any>) {
    if (!editorData.value) return;
    pushUndoSnapshot();
    let list: any[];
    if (type === 'annotation') {
      list = editorData.value.annotations;
    } else if (type === 'path') {
      list = editorData.value.paths;
    } else {
      list = editorData.value.objects;
    }
    const item = list.find((i: any) => i.id === id);
    if (item) {
      Object.assign(item, data);
    }
  }

  return {
    editorData,
    selectedMapId,
    selectedElement,
    drawingMode,
    gridSpacing,
    isDirty,
    loading,
    saving,
    sceneList,
    resolution,
    canUndo,
    canRedo,
    pixelToMeterDelta,
    meterToPixelDelta,
    pixelToWorldCoords,
    worldToPixelCoords,
    loadSceneList,
    loadMap,
    undo,
    redo,
    saveMap,
    deleteScene,
    addAnnotation,
    addAnnotations,
    addPath,
    addObject,
    removeElement,
    updateElement,
    pushUndoSnapshot,
    validateBeforeSave,
  };
}
