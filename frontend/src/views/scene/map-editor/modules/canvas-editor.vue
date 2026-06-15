<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import { Canvas, Circle, Rect, Polygon, Line, Group, Text, FabricImage, Triangle, Point } from 'fabric';
import { getFilePreviewUrl } from '@/service/api/file';
import { pixelToWorld, worldToPixel } from '@/utils/coordinate';
import type { SelectedElement, DrawingMode } from '../composables/useMapEditor';
import { fetchGetSceneMapList } from '@/service/api';
interface Props {
  editorData: Api.Scene.EditorMapData | null;
  selectedElement: SelectedElement | null;
  drawingMode: DrawingMode;
  gridSpacing: number;
  resolution: number;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const emit = defineEmits<{
  (e: 'select-element', el: SelectedElement | null): void;
  (e: 'add-annotation', data: { x: number; y: number; type: string }): void;
  (e: 'add-path', data: { startId: number; endId: number }): void;
  (e: 'add-object', data: { type: string; x: number; y: number; width: number; height: number; points?: string }): void;
  (e: 'update-element', data: { type: string; id: number; updates: Record<string, any> }): void;
  (e: 'zoom-change', zoom: number): void;
  (e: 'cursor-position', x: number, y: number): void;
}>();

const canvasContainer = ref<HTMLDivElement>();
const canvasEl = ref<HTMLCanvasElement>();
const minimapEl = ref<HTMLDivElement>();
let fabricCanvas: Canvas | null = null;
let gridGroup: Group | null = null;
let backgroundImgObj: FabricImage | null = null;
let elementMap: Map<string, any> = new Map();
let resizeObserver: ResizeObserver | null = null;
let lastGridSpacingM = 0;
let originMarker: Group | null = null;

const minimapImageUrl = ref('');
const minimapRect = ref({ x: 0, y: 0, w: 0, h: 0 });
const MINIMAP_SIZE = 180;

const minimapScale = computed(() => {
  const mw = canvasWidth.value;
  const mh = canvasHeight.value;
  if (mw === 0 || mh === 0) return { s: 1, w: 0, h: 0, ox: 0, oy: 0 };
  const s = Math.min(MINIMAP_SIZE / mw, MINIMAP_SIZE / mh);
  const w = mw * s;
  const h = mh * s;
  const ox = (MINIMAP_SIZE - w) / 2;
  const oy = (MINIMAP_SIZE - h) / 2;
  return { s, w, h, ox, oy };
});
let start_point_x = 0
let start_point_y = 0
async function loadSceneList() {
  try {
    const { data } = await fetchGetSceneMapList({ page: 1, page_size: 999, status: null, name: null, group_id: undefined });
    if (data?.records) {
      start_point_x = data?.records[0]?.start_point_x
      start_point_y = data?.records[0]?.start_point_y
    }
  } catch {
  }
}
function updateMinimap() {
  if (!fabricCanvas) return;
  const vpt = fabricCanvas.viewportTransform;
  if (!vpt) return;
  const zoom = vpt[0];
  const { s, ox, oy, w: imgW, h: imgH } = minimapScale.value;

  // Visible area in content coordinates
  const viewLeft = -vpt[4] / zoom;
  const viewTop = -vpt[5] / zoom;
  const viewW = containerWidth.value / zoom;
  const viewH = containerHeight.value / zoom;

  const visibleLeft = Math.max(0, viewLeft);
  const visibleTop = Math.max(0, viewTop);
  const visibleRight = Math.min(canvasWidth.value, viewLeft + viewW);
  const visibleBottom = Math.min(canvasHeight.value, viewTop + viewH);

  if (visibleRight <= visibleLeft || visibleBottom <= visibleTop) {
    minimapRect.value = { x: ox, y: oy, w: 0, h: 0 };
    return;
  }

  minimapRect.value = {
    x: ox + visibleLeft * s,
    y: oy + visibleTop * s,
    w: (visibleRight - visibleLeft) * s,
    h: (visibleBottom - visibleTop) * s,
  };
}

// --- Minimap drag-to-navigate ---
let minimapDragging = false;

function minimapClientToContent(clientX: number, clientY: number) {
  if (!minimapEl.value) return null;
  const rect = minimapEl.value.getBoundingClientRect();
  const mx = clientX - rect.left;
  const my = clientY - rect.top;
  const { s, ox, oy } = minimapScale.value;
  // Minimap pixel → content coordinate
  const contentX = (mx - ox) / s;
  const contentY = (my - oy) / s;
  return { x: contentX, y: contentY };
}

function navigateToMinimapPoint(clientX: number, clientY: number) {
  if (!fabricCanvas) return;
  const pt = minimapClientToContent(clientX, clientY);
  if (!pt) return;
  const zoom = fabricCanvas.getZoom();
  // Center the viewport so (pt.x, pt.y) is at the center of the visible area
  const offsetX = containerWidth.value / 2 - pt.x * zoom;
  const offsetY = containerHeight.value / 2 - pt.y * zoom;
  fabricCanvas.setViewportTransform([zoom, 0, 0, zoom, offsetX, offsetY]);
  fabricCanvas.renderAll();
  updateMinimap();
}

function handleMinimapDown(e: MouseEvent) {
  e.preventDefault();
  minimapDragging = true;
  navigateToMinimapPoint(e.clientX, e.clientY);
}

function handleMinimapMove(e: MouseEvent) {
  if (!minimapDragging) return;
  navigateToMinimapPoint(e.clientX, e.clientY);
}

function handleMinimapUp() {
  minimapDragging = false;
}

const MIN_ZOOM = 1;
const MAX_ZOOM = 5;
let currentZoom = 1;
let isPanning = false;
let lastPanPoint = { x: 0, y: 0 };
let spacePressed = false;

let pathStartAnnotationId: number | null = null;

let drawingState: {
  type: 'rect' | 'polygon' | null;
  startX: number;
  startY: number;
  tempObj: any;
  polygonPoints: { x: number; y: number }[];
} | null = null;

const canvasWidth = ref(800);
const canvasHeight = ref(600);
const containerWidth = ref(0);
const containerHeight = ref(0);

const sliderZoomValue = ref(0);

const sliderThemeOverrides = {
  fillColor: '#3b82f6',
  fillColorHover: '#2563eb',
  dotColor: '#3b82f6',
  dotBorder: '2px solid #fff',
  dotBoxShadow: '0 1px 4px rgba(0,0,0,0.2)',
};

function zoomToSliderValue(sliderVal: number): number {
  const minLog = Math.log(MIN_ZOOM);
  const maxLog = Math.log(MAX_ZOOM);
  const scale = (maxLog - minLog) / 100;
  return Math.exp(minLog + scale * sliderVal);
}

function sliderValueToZoom(zoom: number): number {
  const minLog = Math.log(MIN_ZOOM);
  const maxLog = Math.log(MAX_ZOOM);
  return Math.round(((Math.log(zoom) - minLog) / (maxLog - minLog)) * 100);
}

function setElementData(obj: any, data: { type: string; id: number }) {
  (obj as any)._elementData = data;
}

function getElementData(obj: any): { type: string; id: number } | null {
  return (obj as any)._elementData || null;
}

function getElementKey(type: string, id: number) {
  return `${type}-${id}`;
}

function getEffectiveOrigin() {
  if (!props.editorData) return { x: 0, y: 0 };
  const map = props.editorData.map;
  const storedW = map.width || canvasWidth.value;
  const storedH = map.height || canvasHeight.value;
  const sx = canvasWidth.value / storedW;
  const sy = canvasHeight.value / storedH;
  return {
    x: (map.start_point_x ?? 0),
    y: (map.start_point_y ?? 0),
  };
}

function centerContent() {
  if (!fabricCanvas) return;
  const cw = containerWidth.value;
  const ch = containerHeight.value;
  if (cw === 0 || ch === 0) return;

  const zoom = fabricCanvas.getZoom();
  const offsetX = (cw - canvasWidth.value * zoom) / 2;
  const offsetY = (ch - canvasHeight.value * zoom) / 2;

  fabricCanvas.setViewportTransform([
    zoom, 0, 0, zoom,
    Math.max(0, offsetX),
    Math.max(0, offsetY),
  ]);
  updateMinimap();
}

function renderElements() {
  if (!fabricCanvas || !props.editorData) return;

  const map = props.editorData.map;
  const { x: originX, y: originY } = getEffectiveOrigin();
  const res = props.resolution;


  console.log('canvasHeight:', canvasHeight.value, 'backgroundImgObj:', backgroundImgObj ? '已加载' : '未加载'); const existingKeys = new Set<string>();
  for (const ann of props.editorData.annotations) {
    const key = getElementKey('annotation', ann.id);
    existingKeys.add(key);

    const px = worldToPixel(ann.x, ann.y, originX, originY, res);
    px.y = canvasHeight.value - px.y;
    const isSelected = props.selectedElement?.type === 'annotation' && props.selectedElement?.id === ann.id;
    const annColor = isSelected ? '#3b82f6' : '#ef4444';

    if (elementMap.has(key)) {
      const group = elementMap.get(key);
      group.set({ left: px.x, top: px.y });
      const circle = group.getObjects()[0] as Circle;
      circle.set('fill', annColor);
      circle.set('radius', isSelected ? 10 : 8);
      const text = group.getObjects()[2] as Text;
      text.set('text', ann.name);
      text.set('fill', annColor);
    } else {
      const circle = new Circle({
        radius: isSelected ? 10 : 8,
        fill: annColor,
        stroke: '#fff',
        strokeWidth: 2,
        originX: 'center',
        originY: 'center',
      });

      const angleIndicator = new Triangle({
        width: 8,
        height: 12,
        fill: annColor,
        originX: 'center',
        originY: 'center',
        top: -16,
        angle: ann.angle || 0,
        visible: false,
      });

      const text = new Text(ann.name, {
        fontSize: 10,
        fill: annColor,
        originX: 'center',
        originY: 'center',
        top: 18,
        fontFamily: 'sans-serif',
        fontWeight: 'bold',
      });

      const group = new Group([circle, angleIndicator, text], {
        left: px.x,
        top: px.y,
        originX: 'center',
        originY: 'center',
        hasControls: false,
      });
      setElementData(group, { type: 'annotation', id: ann.id });

      fabricCanvas.add(group);
      elementMap.set(key, group);
    }
  }

  for (const path of props.editorData.paths) {
    const key = getElementKey('path', path.id);
    existingKeys.add(key);

    const startAnn = props.editorData.annotations.find(a => a.id === path.start_annotation_id);
    const endAnn = props.editorData.annotations.find(a => a.id === path.end_annotation_id);
    if (!startAnn || !endAnn) continue;

    const startPx = worldToPixel(startAnn.x, startAnn.y, originX, originY, res);
    const endPx = worldToPixel(endAnn.x, endAnn.y, originX, originY, res);

    if (elementMap.has(key)) {
      const line = elementMap.get(key);
      line.set({ x1: startPx.x, y1: startPx.y, x2: endPx.x, y2: endPx.y });
    } else {
      const line = new Line([startPx.x, startPx.y, endPx.x, endPx.y], {
        stroke: '#f97316',
        strokeWidth: 3,
        selectable: false,
        evented: false,
      });
      setElementData(line, { type: 'path', id: path.id });
      fabricCanvas.add(line);
      fabricCanvas.sendObjectToBack(line);
      elementMap.set(key, line);
    }
  }

  for (const obj of props.editorData.objects) {
    const key = getElementKey('object', obj.id);
    existingKeys.add(key);

    const isRestricted = obj.type === 'restricted' || obj.type === '禁区';
    const fillColor = isRestricted ? 'rgba(234, 179, 8, 0.3)' : 'rgba(239, 68, 68, 0.3)';
    const strokeColor = isRestricted ? '#eab308' : '#ef4444';

    if (elementMap.has(key)) {
      const fabricObj = elementMap.get(key);
      fabricObj.set({ left: obj.x, top: obj.y });
      if (fabricObj instanceof Rect) {
        fabricObj.set({ width: obj.width, height: obj.height });
      }
    } else {
      if (obj.points) {
        try {
          const pts = JSON.parse(obj.points);
          const polygon = new Polygon(pts, {
            left: obj.x, top: obj.y,
            fill: fillColor, stroke: strokeColor, strokeWidth: 2,
          });
          setElementData(polygon, { type: 'object', id: obj.id });
          fabricCanvas.add(polygon);
          elementMap.set(key, polygon);
        } catch { /* skip invalid polygon */ }
      } else {
        const rect = new Rect({
          left: obj.x, top: obj.y,
          width: obj.width || 40, height: obj.height || 40,
          fill: fillColor, stroke: strokeColor, strokeWidth: 2,
        });
        setElementData(rect, { type: 'object', id: obj.id });
        fabricCanvas.add(rect);
        elementMap.set(key, rect);
      }
    }
  }

  for (const [key, obj] of elementMap) {
    if (!existingKeys.has(key)) {
      fabricCanvas.remove(obj);
      elementMap.delete(key);
    }
  }

  // Bring annotations to front for higher z-order
  for (const ann of props.editorData.annotations) {
    const key = getElementKey('annotation', ann.id);
    const obj = elementMap.get(key);
    if (obj) fabricCanvas.bringObjectToFront(obj);
  }

  renderOriginMarker();
  updateSelection();
  fabricCanvas.renderAll();
}

function renderOriginMarker() {
  if (!fabricCanvas || !props.editorData) return;
  if (originMarker) {
    fabricCanvas.remove(originMarker);
    originMarker = null;
  }

  // const { x: ox, y: oy } = getEffectiveOrigin();
  const ox = 0
  const oy = 0
  const s = 12;
  const hLine = new Line([ox - s, oy, ox + s, oy], {
    stroke: '#2563eb', strokeWidth: 2, selectable: false, evented: false,
  });
  const vLine = new Line([ox, oy - s, ox, oy + s], {
    stroke: '#2563eb', strokeWidth: 2, selectable: false, evented: false,
  });
  const label = new Text('O', {
    fontSize: 10, fill: '#2563eb', fontFamily: 'sans-serif', fontWeight: 'bold',
    left: ox + 6, top: oy - 14, selectable: false, evented: false,
  });
  originMarker = new Group([hLine, vLine, label], { selectable: false, evented: false });
  fabricCanvas.add(originMarker);
}

function updateSelection() {
  if (!fabricCanvas) return;
  fabricCanvas.discardActiveObject();
  if (props.selectedElement) {
    const key = getElementKey(props.selectedElement.type, props.selectedElement.id);
    const obj = elementMap.get(key);
    if (obj) fabricCanvas.setActiveObject(obj);
  }
  fabricCanvas.renderAll();
}

function formatDist(m: number): string {
  if (m === 0) return '0';
  if (Number.isInteger(m)) return `${m}`;
  if (m >= 1) return m.toFixed(1);
  if (m >= 0.1) return m.toFixed(1);
  return m.toFixed(2);
}

function renderGrid() {
  if (!fabricCanvas) return;

  const w = canvasWidth.value;
  const h = canvasHeight.value;
  const zoom = currentZoom;
  const res = props.resolution;
  const { x: originPx, y: originPy } = getEffectiveOrigin();

  // Adaptive grid: target ~80px visual spacing on screen
  const targetVisualPx = 80;
  const rawSpacingM = (targetVisualPx / zoom) * res;

  // Pick the nearest "nice" real-world distance
  const niceSteps = [0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000];
  const spacingM = niceSteps.find(s => s >= rawSpacingM) || rawSpacingM;

  // Skip re-render if spacing hasn't changed
  if (Math.abs(spacingM - lastGridSpacingM) < 1e-6 && gridGroup) return;
  lastGridSpacingM = spacingM;

  if (gridGroup) fabricCanvas.remove(gridGroup);

  const spacingPx = spacingM / res;
  if (spacingPx <= 0) return;

  const allObjects: any[] = [];

  // Grid extends beyond image to fill visible area
  const margin = Math.max(w, h, 1000);
  const startX = Math.floor(-margin / spacingPx) * spacingPx;
  const startY = Math.floor(-margin / spacingPx) * spacingPx;
  const endX = Math.ceil((w + margin) / spacingPx) * spacingPx;
  const endY = Math.ceil((h + margin) / spacingPx) * spacingPx;

  // Vertical lines
  for (let x = startX; x <= endX; x += spacingPx) {
    const inBounds = x >= 0 && x <= w;
    allObjects.push(new Line([x, startY, x, endY], {
      stroke: inBounds ? 'rgba(0,0,0,0.08)' : 'rgba(0,0,0,0.03)',
      strokeWidth: 1,
      selectable: false,
      evented: false,
    }));
  }
  // Horizontal lines
  for (let y = startY; y <= endY; y += spacingPx) {
    const inBounds = y >= 0 && y <= h;
    allObjects.push(new Line([startX, y, endX, y], {
      stroke: inBounds ? 'rgba(0,0,0,0.08)' : 'rgba(0,0,0,0.03)',
      strokeWidth: 1,
      selectable: false,
      evented: false,
    }));
  }

  // // Zero-axis lines through origin (world X=0, Y=0)
  // allObjects.push(new Line([originPx, startY, originPx, endY], {
  //   stroke: 'rgba(37, 99, 235, 0.25)', strokeWidth: 2,
  //   strokeDashArray: [8, 4], selectable: false, evented: false,
  // }));
  // allObjects.push(new Line([startX, originPy, endX, originPy], {
  //   stroke: 'rgba(37, 99, 235, 0.25)', strokeWidth: 2,
  //   strokeDashArray: [8, 4], selectable: false, evented: false,
  // }));

  // Labels: font size adjusts inversely with zoom so it stays readable on screen
  const fontSize = Math.max(8, Math.min(14, 11 / zoom));
  const labelStyle = {
    fontSize,
    fill: 'rgba(0,0,0,0.4)',
    fontFamily: 'sans-serif',
    selectable: false,
    evented: false,
  };

  // X-axis labels along bottom edge (world X coordinate at each vertical grid line)
  for (let x = 0; x <= endX; x += spacingPx) {
    const world = pixelToWorld(x, 0, originPx, originPy, res);
    const meters = Math.round(world.x * 1000) / 1000;
    allObjects.push(new Text(formatDist(meters), {
      ...labelStyle,
      left: x,
      top: h + 4,
      originX: 'center',
      originY: 'top',
    }));
  }
  // Y-axis labels along left edge (world Y coordinate at each horizontal grid line)
  for (let y = 0; y <= endY; y += spacingPx) {
    const world = pixelToWorld(0, y, originPx, originPy, res);
    const meters = Math.round(world.y * 1000) / 1000;
    allObjects.push(new Text(formatDist(meters), {
      ...labelStyle,
      left: -4,
      top: y,
      originX: 'right',
      originY: 'center',
    }));
  }

  gridGroup = new Group(allObjects, { selectable: false, evented: false, objectCaching: false });
  fabricCanvas.add(gridGroup);
  // Grid at the very bottom; image and other elements render above it
  fabricCanvas.sendObjectToBack(gridGroup);
  fabricCanvas.renderAll();
  updateMinimap();
}

async function loadBackgroundImage(imageId: number) {
  if (!fabricCanvas) return;
  const url = getFilePreviewUrl(imageId);
  try {
    const img = await FabricImage.fromURL(url, { crossOrigin: 'anonymous' });
    canvasWidth.value = img.width || 800;
    canvasHeight.value = img.height || 600;

    // Remove previous background image object
    if (backgroundImgObj) {
      fabricCanvas.remove(backgroundImgObj);
      backgroundImgObj = null;
    }

    // Add image as a regular object at (0,0) so it follows viewport transform
    img.set({ left: 0, top: 0, originX: 'left', originY: 'top', selectable: false, evented: false });
    backgroundImgObj = img;
    fabricCanvas.add(img);
    fabricCanvas.sendObjectToBack(img); // 确保背景图片在最底层

    fabricCanvas.setDimensions({
      width: containerWidth.value || canvasContainer.value!.clientWidth,
      height: containerHeight.value || canvasContainer.value!.clientHeight,
    });
    centerContent();
    fabricCanvas.renderAll();
    renderGrid();
    renderElements(); // 图片加载完成后渲染元素
    currentZoom = 1;
    sliderZoomValue.value = sliderValueToZoom(1);
    minimapImageUrl.value = url;
    updateMinimap();
    emit('zoom-change', 1);
  } catch (e) {
    console.error('Failed to load background image:', e);
  }
}

function handleMouseDown(opt: any) {
  if (!fabricCanvas) return;
  const evt = opt.e as MouseEvent;

  if (spacePressed || evt.button === 1) {
    isPanning = true;
    lastPanPoint = { x: evt.clientX, y: evt.clientY };
    fabricCanvas.selection = false;
    return;
  }

  if (props.drawingMode === 'select') return;

  const pointer = fabricCanvas.getViewportPoint(evt);
  const x = pointer.x;
  const y = pointer.y;

  if (props.drawingMode === 'point-nav') {
    const { x: originX, y: originY } = getEffectiveOrigin();
    const world = pixelToWorld(x, y, originX, originY, props.resolution);
    emit('add-annotation', { x: world.x, y: world.y, type: 'navigation' });
    return;
  }
  if (props.drawingMode === 'point-recv') {
    const { x: originX, y: originY } = getEffectiveOrigin();
    const world = pixelToWorld(x, y, originX, originY, props.resolution);
    emit('add-annotation', { x: world.x, y: world.y, type: 'reception' });
    return;
  }
  if (props.drawingMode === 'path') {
    const clickedAnnotation = findAnnotationAtPoint(x, y);
    if (clickedAnnotation) {
      if (pathStartAnnotationId === null) {
        pathStartAnnotationId = clickedAnnotation.id;
        window.$message?.info('已选择起始点位，请点击终点');
      } else if (clickedAnnotation.id !== pathStartAnnotationId) {
        emit('add-path', { startId: pathStartAnnotationId, endId: clickedAnnotation.id });
        pathStartAnnotationId = null;
      }
    }
    return;
  }
  if (props.drawingMode === 'rect-obstacle') {
    drawingState = { type: 'rect', startX: x, startY: y, tempObj: null, polygonPoints: [] };
    return;
  }
  if (props.drawingMode === 'polygon-restricted') {
    if (!drawingState || drawingState.type !== 'polygon') {
      drawingState = { type: 'polygon', startX: 0, startY: 0, tempObj: null, polygonPoints: [{ x, y }] };
      window.$message?.info('单击添加顶点，双击闭合多边形');
    } else {
      drawingState.polygonPoints.push({ x, y });
    }
    return;
  }
}

function handleMouseMove(opt: any) {
  if (!fabricCanvas) return;
  const evt = opt.e as MouseEvent;
  const pointer = fabricCanvas.getViewportPoint(evt);
  const { x: originX, y: originY } = getEffectiveOrigin();
  const world = pixelToWorld(pointer.x, pointer.y, originX, originY, props.resolution);
  emit('cursor-position', world.x, world.y);

  if (isPanning) {
    const dx = evt.clientX - lastPanPoint.x;
    const dy = evt.clientY - lastPanPoint.y;
    fabricCanvas.relativePan(new Point(dx, dy));
    lastPanPoint = { x: evt.clientX, y: evt.clientY };
    updateMinimap();
    return;
  }

  if (drawingState?.type === 'rect' && drawingState.tempObj) {
    const w = pointer.x - drawingState.startX;
    const h = pointer.y - drawingState.startY;
    drawingState.tempObj.set({
      width: Math.abs(w), height: Math.abs(h),
      left: Math.min(drawingState.startX, pointer.x),
      top: Math.min(drawingState.startY, pointer.y),
    });
    fabricCanvas.renderAll();
  }
}

function handleMouseUp(opt: any) {
  if (isPanning) {
    isPanning = false;
    if (fabricCanvas) {
      fabricCanvas.selection = true;
      updateMinimap();
    }
    return;
  }
  if (drawingState?.type === 'rect' && fabricCanvas) {
    const pointer = fabricCanvas.getViewportPoint(opt.e);
    const x = Math.min(drawingState.startX, pointer.x);
    const y = Math.min(drawingState.startY, pointer.y);
    const w = Math.abs(pointer.x - drawingState.startX);
    const h = Math.abs(pointer.y - drawingState.startY);
    if (drawingState.tempObj) fabricCanvas.remove(drawingState.tempObj);
    if (w > 5 && h > 5) {
      emit('add-object', { type: 'obstacle', x, y, width: w, height: h });
    }
    drawingState = null;
  }
}

function handleDoubleClick() {
  if (drawingState?.type === 'polygon' && fabricCanvas) {
    const pts = drawingState.polygonPoints;
    if (pts.length >= 3) {
      if (drawingState.tempObj) fabricCanvas.remove(drawingState.tempObj);
      const minX = Math.min(...pts.map(p => p.x));
      const minY = Math.min(...pts.map(p => p.y));
      emit('add-object', { type: 'restricted', x: minX, y: minY, width: 0, height: 0, points: JSON.stringify(pts) });
    }
    drawingState = null;
  }
}

function handleObjectMoved(opt: any) {
  const obj = opt.target;
  if (!obj) return;
  const data = getElementData(obj);
  if (!data) return;
  const updates: Record<string, any> = {};
  if (data.type === 'annotation') {
    const { x: originX, y: originY } = getEffectiveOrigin();
    const world = pixelToWorld(obj.left!, obj.top!, originX, originY, props.resolution);
    updates.x = world.x;
    updates.y = world.y;
  } else {
    updates.x = obj.left;
    updates.y = obj.top;
  }
  if (data.type === 'object' && obj instanceof Rect) {
    updates.width = obj.width * obj.scaleX;
    updates.height = obj.height * obj.scaleY;
    obj.set({ scaleX: 1, scaleY: 1 });
  }
  emit('update-element', { type: data.type, id: data.id, updates });
}

function handleObjectSelected(opt: any) {
  if (opt.selected && opt.selected.length > 0) {
    const data = getElementData(opt.selected[0]);
    if (data) emit('select-element', { type: data.type as 'annotation' | 'path' | 'object', id: data.id });
  }
}

function handleSelectionCleared() {
  emit('select-element', null);
}

function handleMouseWheel(opt: any) {
  if (!fabricCanvas) return;
  const evt = opt.e as WheelEvent;
  evt.preventDefault();
  evt.stopPropagation();

  const delta = evt.deltaY;
  let zoom = fabricCanvas.getZoom();
  zoom *= 0.999 ** delta;
  zoom = Math.min(Math.max(zoom, MIN_ZOOM), MAX_ZOOM);
  fabricCanvas.zoomToPoint(new Point(evt.clientX, evt.clientY), zoom);
  currentZoom = zoom;
  sliderZoomValue.value = sliderValueToZoom(zoom);
  renderGrid();
  updateMinimap();
  emit('zoom-change', zoom);
}

function findAnnotationAtPoint(x: number, y: number): Api.Scene.SceneMapAnnotation | null {
  if (!props.editorData) return null;
  const { x: originX, y: originY } = getEffectiveOrigin();
  const threshold = 15;
  for (const ann of props.editorData.annotations) {
    const pos = worldToPixel(ann.x, ann.y, originX, originY, props.resolution);
    if (Math.abs(pos.x - x) < threshold && Math.abs(pos.y - y) < threshold) return ann;
  }
  return null;
}

function handleKeyDown(evt: KeyboardEvent) {
  if (evt.code === 'Space') { spacePressed = true; evt.preventDefault(); }
}

function handleKeyUp(evt: KeyboardEvent) {
  if (evt.code === 'Space') spacePressed = false;
}

function setupCanvas() {
  if (!canvasEl.value || !canvasContainer.value) return;
  const cw = canvasContainer.value.clientWidth;
  const ch = canvasContainer.value.clientHeight;
  containerWidth.value = cw;
  containerHeight.value = ch;

  fabricCanvas = new Canvas(canvasEl.value, {
    selection: true,
    preserveObjectStacking: true,
    width: cw,
    height: ch,
  });
  fabricCanvas.on('mouse:down', handleMouseDown);
  fabricCanvas.on('mouse:move', handleMouseMove);
  fabricCanvas.on('mouse:up', handleMouseUp);
  fabricCanvas.on('mouse:dblclick', handleDoubleClick);
  fabricCanvas.on('mouse:wheel', handleMouseWheel);
  fabricCanvas.on('object:moving', handleObjectMoved);
  fabricCanvas.on('selection:created', handleObjectSelected);
  fabricCanvas.on('selection:updated', handleObjectSelected);
  fabricCanvas.on('selection:cleared', handleSelectionCleared);

  resizeObserver = new ResizeObserver((entries) => {
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
  originMarker = null;
  lastGridSpacingM = 0;
}

watch([containerWidth, containerHeight], () => {
  if (!fabricCanvas) return;
  fabricCanvas.setDimensions({ width: containerWidth.value, height: containerHeight.value });
  centerContent();
});

let loadSeq = 0;

watch(() => props.editorData, async (newData) => {
  if (!newData) return;
  const seq = ++loadSeq;

  for (const [, obj] of elementMap) {
    fabricCanvas?.remove(obj);
  }
  elementMap.clear();
  if (originMarker) {
    fabricCanvas?.remove(originMarker);
    originMarker = null;
  }
  lastGridSpacingM = 0;

  if (newData.map.image_id) {
    await loadBackgroundImage(newData.map.image_id);
    // renderElements 会在 loadBackgroundImage 完成后调用
  } else {
    canvasWidth.value = newData.map.width || 800;
    canvasHeight.value = newData.map.height || 600;
    if (fabricCanvas) {
      fabricCanvas.setDimensions({
        width: containerWidth.value || canvasContainer.value!.clientWidth,
        height: containerHeight.value || canvasContainer.value!.clientHeight,
      });
      centerContent();
    }
    nextTick(() => renderElements());
  }

  // if (seq !== loadSeq) return;
  // renderElements();
}, { deep: false });

watch(() => props.editorData?.annotations, () => renderElements(), { deep: true });
watch(() => props.editorData?.paths, () => renderElements(), { deep: true });
watch(() => props.editorData?.objects, () => renderElements(), { deep: true });
watch(() => props.selectedElement, () => { renderElements(); updateSelection(); });
watch(() => props.gridSpacing, () => renderGrid());
watch(() => props.drawingMode, (mode) => {
  pathStartAnnotationId = null;
  drawingState = null;
  if (fabricCanvas) {
    fabricCanvas.selection = mode === 'select';
    fabricCanvas.defaultCursor = mode === 'select' ? 'default' : 'crosshair';
  }
});

onMounted(async () => {
  await loadSceneList();
  setupCanvas();
  window.addEventListener('keydown', handleKeyDown);
  window.addEventListener('keyup', handleKeyUp);
});

onBeforeUnmount(() => {
  disposeCanvas();
  window.removeEventListener('keydown', handleKeyDown);
  window.removeEventListener('keyup', handleKeyUp);
});

function exportCanvas(format: 'png' | 'jpeg' | 'webp') {
  if (!fabricCanvas) return;
  if (gridGroup) gridGroup.set('visible', false);
  fabricCanvas.renderAll();
  const dataUrl = fabricCanvas.toDataURL({ format, quality: 1, multiplier: 2 });
  if (gridGroup) gridGroup.set('visible', true);
  fabricCanvas.renderAll();
  const link = document.createElement('a');
  link.download = `map-export.${format === 'jpeg' ? 'jpg' : format}`;
  link.href = dataUrl;
  link.click();
}

function zoomIn() {
  if (!fabricCanvas) return;
  const newZoom = Math.min(currentZoom * 1.2, MAX_ZOOM);
  const center = fabricCanvas.getCenterPoint();
  fabricCanvas.zoomToPoint(center, newZoom);
  currentZoom = newZoom;
  sliderZoomValue.value = sliderValueToZoom(newZoom);
  renderGrid();
  emit('zoom-change', newZoom);
}

function zoomOut() {
  if (!fabricCanvas) return;
  const newZoom = Math.max(currentZoom / 1.2, MIN_ZOOM);
  const center = fabricCanvas.getCenterPoint();
  fabricCanvas.zoomToPoint(center, newZoom);
  currentZoom = newZoom;
  sliderZoomValue.value = sliderValueToZoom(newZoom);
  renderGrid();
  emit('zoom-change', newZoom);
}

function zoomReset() {
  if (!fabricCanvas) return;
  currentZoom = 1;
  sliderZoomValue.value = sliderValueToZoom(1);
  centerContent();
  renderGrid();
  emit('zoom-change', 1);
}

function locateMeterPoint(x: number, y: number) {
  if (!fabricCanvas) return;
  const { x: originX, y: originY } = getEffectiveOrigin();
  const pixel = worldToPixel(x, y, originX, originY, props.resolution);
  const zoom = Math.max(currentZoom, MIN_ZOOM);
  const offsetX = containerWidth.value / 2 - pixel.x * zoom;
  const offsetY = containerHeight.value / 2 - pixel.y * zoom;
  fabricCanvas.setViewportTransform([zoom, 0, 0, zoom, offsetX, offsetY]);
  fabricCanvas.renderAll();
  updateMinimap();
}

function handleSliderZoom(val: number) {
  if (!fabricCanvas) return;
  const newZoom = zoomToSliderValue(val);
  const center = fabricCanvas.getCenterPoint();
  fabricCanvas.zoomToPoint(center, newZoom);
  currentZoom = newZoom;
  renderGrid();
  emit('zoom-change', newZoom);
}

defineExpose({ exportCanvas, zoomIn, zoomOut, zoomReset, locateMeterPoint });
</script>

<template>
  <div ref="canvasContainer" class="relative h-full w-full overflow-hidden bg-gray-100">
    <canvas ref="canvasEl" />
    <div v-if="!editorData" class="absolute inset-0 flex items-center justify-center">
      <NEmpty description="请选择一个场景" />
    </div>
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60">
      <NSpin size="large" />
    </div>

    <!-- Zoom slider control -->
    <div v-if="editorData"
      class="absolute right-12px top-12px z-10 flex flex-col items-center gap-4px rounded-lg bg-white/90 px-6px py-8px shadow-md">
      <button
        class="flex h-24px w-24px items-center justify-center rounded-full text-sm font-bold text-blue-500 transition-colors hover:bg-blue-50"
        @click="zoomIn">
        +
      </button>
      <NSlider v-model:value="sliderZoomValue" vertical :min="0" :max="100" :step="1" :tooltip="false"
        :theme-overrides="sliderThemeOverrides" class="!h-160px" @update:value="handleSliderZoom" />
      <button
        class="flex h-24px w-24px items-center justify-center rounded-full text-sm font-bold text-blue-500 transition-colors hover:bg-blue-50"
        @click="zoomOut">
        -
      </button>
      <div class="text-xs text-gray-500">{{ Math.round(currentZoom * 100) }}%</div>
    </div>

    <!-- Minimap navigator -->
    <div v-if="editorData && minimapImageUrl" ref="minimapEl"
      class="absolute bottom-12px left-12px z-10 cursor-pointer overflow-hidden rounded-lg border border-gray-300 bg-white shadow-md"
      :style="{ width: `${MINIMAP_SIZE}px`, height: `${MINIMAP_SIZE}px` }" @mousedown="handleMinimapDown"
      @mousemove="handleMinimapMove" @mouseup="handleMinimapUp" @mouseleave="handleMinimapUp">
      <img :src="minimapImageUrl" :style="{
        position: 'absolute',
        left: `${minimapScale.ox}px`,
        top: `${minimapScale.oy}px`,
        width: `${minimapScale.w}px`,
        height: `${minimapScale.h}px`,
        objectFit: 'fill',
        pointerEvents: 'none',
      }" />
      <!-- Viewport rect: blue border + massive box-shadow as outer mask -->
      <div :style="{
        position: 'absolute',
        left: `${minimapRect.x}px`,
        top: `${minimapRect.y}px`,
        width: `${minimapRect.w}px`,
        height: `${minimapRect.h}px`,
        border: '2px solid #3b82f6',
        backgroundColor: 'transparent',
        boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.45)',
        pointerEvents: 'none',
      }" />
    </div>
  </div>
</template>


