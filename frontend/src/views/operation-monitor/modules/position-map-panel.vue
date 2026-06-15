<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { Canvas, Circle, Rect, Polygon, Line, Group, Text, FabricImage, Triangle, Point } from 'fabric';
import { fetchGetEditorMapData } from '@/service/api/scene';
import { getFilePreviewUrl } from '@/service/api/file';
import { worldToPixel } from '@/utils/coordinate';
import type { ParsedLocation } from '../composables/useRobotMonitor';

interface Props {
  mapId: number | null;
  location: ParsedLocation | null;
  robotName: string;
}

const props = defineProps<Props>();

const canvasContainer = ref<HTMLDivElement>();
const canvasEl = ref<HTMLCanvasElement>();
let fabricCanvas: Canvas | null = null;
let backgroundImgObj: FabricImage | null = null;
let robotMarker: Group | null = null;
let elementMap: Map<string, any> = new Map();
let resizeObserver: ResizeObserver | null = null;

const canvasWidth = ref(800);
const canvasHeight = ref(600);
const containerWidth = ref(0);
const containerHeight = ref(0);
const mapLoading = ref(false);
const mapData = ref<Api.Scene.EditorMapData | null>(null);

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 5;
let currentZoom = 1;

function centerContent() {
  if (!fabricCanvas) return;
  const cw = containerWidth.value;
  const ch = containerHeight.value;
  if (cw === 0 || ch === 0) return;
  const zoom = fabricCanvas.getZoom();
  const offsetX = (cw - canvasWidth.value * zoom) / 2;
  const offsetY = (ch - canvasHeight.value * zoom) / 2;
  fabricCanvas.setViewportTransform([zoom, 0, 0, zoom, Math.max(0, offsetX), Math.max(0, offsetY)]);
}

function getEffectiveOrigin() {
  if (!mapData.value) return { x: 0, y: 0 };
  const mMap = mapData.value.map;
  const storedW = mMap.width || canvasWidth.value;
  const storedH = mMap.height || canvasHeight.value;
  const sx = canvasWidth.value / storedW;
  const sy = canvasHeight.value / storedH;
  return {
    x: (mMap.start_point_x ?? 0) * sx,
    y: (mMap.start_point_y ?? 0) * sy,
  };
}

function renderElements() {
  if (!fabricCanvas || !mapData.value) return;
  const existingKeys = new Set<string>();
  const mMap = mapData.value.map;
  const { x: originX, y: originY } = getEffectiveOrigin();
  const res = mMap.resolution || 0.2;

  // Render annotations (stored in world coordinates)
  for (const ann of mapData.value.annotations) {
    const key = `ann-${ann.id}`;
    existingKeys.add(key);
    const px = worldToPixel(ann.x, ann.y, originX, originY, res);
    if (elementMap.has(key)) {
      const group = elementMap.get(key);
      group.set({ left: px.x, top: px.y });
      const text = group.getObjects()[1] as Text;
      text.set('text', ann.name);
    } else {
      const circle = new Circle({
        radius: 6,
        fill: '#ef4444',
        stroke: '#fff',
        strokeWidth: 2,
        originX: 'center',
        originY: 'center'
      });
      const text = new Text(ann.name, {
        fontSize: 9,
        fill: '#ef4444',
        originX: 'center',
        originY: 'center',
        top: 14,
        fontFamily: 'sans-serif'
      });
      const group = new Group([circle, text], {
        left: px.x,
        top: px.y,
        originX: 'center',
        originY: 'center',
        hasControls: false,
        selectable: false,
        evented: false
      });
      fabricCanvas.add(group);
      elementMap.set(key, group);
    }
  }

  // Render paths
  for (const path of mapData.value.paths) {
    const key = `path-${path.id}`;
    existingKeys.add(key);
    const startAnn = mapData.value.annotations.find(a => a.id === path.start_annotation_id);
    const endAnn = mapData.value.annotations.find(a => a.id === path.end_annotation_id);
    if (!startAnn || !endAnn) continue;
    const startPx = worldToPixel(startAnn.x, startAnn.y, originX, originY, res);
    const endPx = worldToPixel(endAnn.x, endAnn.y, originX, originY, res);
    if (elementMap.has(key)) {
      const line = elementMap.get(key);
      line.set({ x1: startPx.x, y1: startPx.y, x2: endPx.x, y2: endPx.y });
    } else {
      const line = new Line([startPx.x, startPx.y, endPx.x, endPx.y], {
        stroke: '#f97316',
        strokeWidth: 2,
        selectable: false,
        evented: false
      });
      fabricCanvas.add(line);
      fabricCanvas.sendObjectToBack(line);
      elementMap.set(key, line);
    }
  }

  // Render objects
  for (const obj of mapData.value.objects) {
    const key = `obj-${obj.id}`;
    existingKeys.add(key);
    const isRestricted = obj.type === 'restricted';
    const fillColor = isRestricted ? 'rgba(234,179,8,0.25)' : 'rgba(239,68,68,0.25)';
    const strokeColor = isRestricted ? '#eab308' : '#ef4444';
    if (elementMap.has(key)) {
      const fabricObj = elementMap.get(key);
      fabricObj.set({ left: obj.x, top: obj.y });
    } else {
      if (obj.points) {
        try {
          const pts = JSON.parse(obj.points);
          const polygon = new Polygon(pts, {
            left: obj.x,
            top: obj.y,
            fill: fillColor,
            stroke: strokeColor,
            strokeWidth: 2
          });
          fabricCanvas.add(polygon);
          elementMap.set(key, polygon);
        } catch { /* skip */ }
      } else {
        const rect = new Rect({
          left: obj.x,
          top: obj.y,
          width: obj.width || 40,
          height: obj.height || 40,
          fill: fillColor,
          stroke: strokeColor,
          strokeWidth: 2
        });
        fabricCanvas.add(rect);
        elementMap.set(key, rect);
      }
    }
  }

  // Remove stale elements
  for (const [key, obj] of elementMap) {
    if (!existingKeys.has(key)) {
      fabricCanvas.remove(obj);
      elementMap.delete(key);
    }
  }

  fabricCanvas.renderAll();
}

function renderRobotMarker() {
  if (!fabricCanvas) return;

  if (robotMarker) {
    fabricCanvas.remove(robotMarker);
    robotMarker = null;
  }

  if (!props.location) return;

  const { x: originX, y: originY } = getEffectiveOrigin();
  const res = mapData.value?.map.resolution || 0.2;
  const robotPx = worldToPixel(props.location.x, props.location.y, originX, originY, res);

  const body = new Circle({
    radius: 12,
    fill: '#2080f0',
    stroke: '#fff',
    strokeWidth: 3,
    originX: 'center',
    originY: 'center'
  });

  const arrow = new Triangle({
    width: 10,
    height: 14,
    fill: '#fff',
    originX: 'center',
    originY: 'center',
    top: -20,
    angle: 0
  });

  const label = new Text(props.robotName || '机器人', {
    fontSize: 10,
    fill: '#2080f0',
    originX: 'center',
    originY: 'center',
    top: 22,
    fontFamily: 'sans-serif',
    fontWeight: 'bold'
  });

  robotMarker = new Group([body, arrow, label], {
    left: robotPx.x,
    top: robotPx.y,
    originX: 'center',
    originY: 'center',
    angle: props.location.angle || 0,
    hasControls: false,
    selectable: false,
    evented: false
  });

  fabricCanvas.add(robotMarker);
  fabricCanvas.renderAll();
}

async function loadBackgroundImage(imageId: number) {
  if (!fabricCanvas) return;
  const url = getFilePreviewUrl(imageId);
  try {
    const img = await FabricImage.fromURL(url, { crossOrigin: 'anonymous' });
    canvasWidth.value = img.width || 800;
    canvasHeight.value = img.height || 600;

    if (backgroundImgObj) {
      fabricCanvas.remove(backgroundImgObj);
    }

    img.set({ left: 0, top: 0, originX: 'left', originY: 'top', selectable: false, evented: false });
    backgroundImgObj = img;
    fabricCanvas.add(img);
    fabricCanvas.sendObjectToBack(img);

    fabricCanvas.setDimensions({
      width: containerWidth.value || canvasContainer.value!.clientWidth,
      height: containerHeight.value || canvasContainer.value!.clientHeight
    });
    centerContent();
    fabricCanvas.renderAll();
    currentZoom = 1;
  } catch (e) {
    console.error('Failed to load background image:', e);
  }
}

async function loadMapData(mapId: number) {
  mapLoading.value = true;
  try {
    const { data } = await fetchGetEditorMapData(mapId);
    if (!data) return;
    mapData.value = data;

    // Clear existing elements
    for (const [, obj] of elementMap) {
      fabricCanvas?.remove(obj);
    }
    elementMap.clear();
    if (robotMarker) {
      fabricCanvas?.remove(robotMarker);
      robotMarker = null;
    }

    if (data.map.image_id) {
      await loadBackgroundImage(data.map.image_id);
    } else {
      canvasWidth.value = data.map.width || 800;
      canvasHeight.value = data.map.height || 600;
    }

    await nextTick();
    renderElements();
    renderRobotMarker();
  } catch (e) {
    console.error('Failed to load map data:', e);
  } finally {
    mapLoading.value = false;
  }
}

function handleMouseWheel(opt: any) {
  if (!fabricCanvas) return;
  const evt = opt.e as WheelEvent;
  evt.preventDefault();
  evt.stopPropagation();
  let zoom = fabricCanvas.getZoom();
  zoom *= 0.999 ** evt.deltaY;
  zoom = Math.min(Math.max(zoom, MIN_ZOOM), MAX_ZOOM);
  fabricCanvas.zoomToPoint(new Point(evt.clientX, evt.clientY), zoom);
  currentZoom = zoom;
}

let isPanning = false;
let lastPanPoint = { x: 0, y: 0 };

function handleMouseDown(opt: any) {
  const evt = opt.e as MouseEvent;
  isPanning = true;
  lastPanPoint = { x: evt.clientX, y: evt.clientY };
  if (fabricCanvas) fabricCanvas.selection = false;
}

function handleMouseMove(opt: any) {
  if (!isPanning || !fabricCanvas) return;
  const evt = opt.e as MouseEvent;
  const dx = evt.clientX - lastPanPoint.x;
  const dy = evt.clientY - lastPanPoint.y;
  fabricCanvas.relativePan(new Point(dx, dy));
  lastPanPoint = { x: evt.clientX, y: evt.clientY };
}

function handleMouseUp() {
  isPanning = false;
  if (fabricCanvas) fabricCanvas.selection = true;
}

function setupCanvas() {
  if (!canvasEl.value || !canvasContainer.value) return;
  const cw = canvasContainer.value.clientWidth;
  const ch = canvasContainer.value.clientHeight;
  containerWidth.value = cw;
  containerHeight.value = ch;

  fabricCanvas = new Canvas(canvasEl.value, {
    selection: false,
    preserveObjectStacking: true,
    width: cw,
    height: ch
  });
  fabricCanvas.on('mouse:down', handleMouseDown);
  fabricCanvas.on('mouse:move', handleMouseMove);
  fabricCanvas.on('mouse:up', handleMouseUp);
  fabricCanvas.on('mouse:wheel', handleMouseWheel);

  resizeObserver = new ResizeObserver(entries => {
    for (const entry of entries) {
      containerWidth.value = entry.contentRect.width;
      containerHeight.value = entry.contentRect.height;
    }
  });
  resizeObserver.observe(canvasContainer.value);
}

function disposeCanvas() {
  if (resizeObserver) { resizeObserver.disconnect(); resizeObserver = null; }
  if (fabricCanvas) { fabricCanvas.dispose(); fabricCanvas = null; }
  elementMap.clear();
  robotMarker = null;
  backgroundImgObj = null;
}

function zoomIn() {
  if (!fabricCanvas) return;
  const newZoom = Math.min(currentZoom * 1.2, MAX_ZOOM);
  const center = fabricCanvas.getCenterPoint();
  fabricCanvas.zoomToPoint(center, newZoom);
  currentZoom = newZoom;
}

function zoomOut() {
  if (!fabricCanvas) return;
  const newZoom = Math.max(currentZoom / 1.2, MIN_ZOOM);
  const center = fabricCanvas.getCenterPoint();
  fabricCanvas.zoomToPoint(center, newZoom);
  currentZoom = newZoom;
}

function zoomReset() {
  if (!fabricCanvas) return;
  currentZoom = 1;
  centerContent();
}

watch([containerWidth, containerHeight], () => {
  if (!fabricCanvas) return;
  fabricCanvas.setDimensions({ width: containerWidth.value, height: containerHeight.value });
  centerContent();
});

watch(() => props.mapId, (newMapId) => {
  if (newMapId) {
    loadMapData(newMapId);
  } else {
    mapData.value = null;
    for (const [, obj] of elementMap) {
      fabricCanvas?.remove(obj);
    }
    elementMap.clear();
    if (robotMarker) {
      fabricCanvas?.remove(robotMarker);
      robotMarker = null;
    }
    fabricCanvas?.renderAll();
  }
});

watch(() => props.location, () => {
  renderRobotMarker();
}, { deep: true });

onMounted(() => {
  setupCanvas();
  if (props.mapId) {
    loadMapData(props.mapId);
  }
});

onBeforeUnmount(() => {
  disposeCanvas();
});
</script>

<template>
  <div class="relative" style="min-height: 400px">
    <NSpin :show="mapLoading">
      <div ref="canvasContainer" class="h-400px w-full overflow-hidden rounded bg-gray-100">
        <canvas ref="canvasEl" />
        <div v-if="!mapId" class="absolute inset-0 flex items-center justify-center">
          <NEmpty description="该机器人未绑定场景地图" />
        </div>
      </div>
    </NSpin>

    <!-- 缩放控制 -->
    <div v-if="mapData" class="absolute bottom-16px right-16px flex flex-col gap-4px">
      <NButton size="tiny" quaternary @click="zoomIn">
        <template #icon><icon-ic-round-add /></template>
      </NButton>
      <NButton size="tiny" quaternary @click="zoomReset">
        <template #icon><icon-ic-round-gps-fixed /></template>
      </NButton>
      <NButton size="tiny" quaternary @click="zoomOut">
        <template #icon><icon-ic-round-remove /></template>
      </NButton>
    </div>
  </div>
</template>

<style scoped></style>
