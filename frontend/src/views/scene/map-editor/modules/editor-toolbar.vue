<script setup lang="ts">
import type { DrawingMode } from '../composables/useMapEditor';

interface Props {
  drawingMode: DrawingMode;
  canUndo: boolean;
  canRedo: boolean;
  isDirty: boolean;
  saving: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: 'update:drawingMode', mode: DrawingMode): void;
  (e: 'undo'): void;
  (e: 'redo'): void;
  (e: 'save'): void;
  (e: 'export', format: 'png' | 'jpeg' | 'webp'): void;
}>();

const drawingModes: { key: DrawingMode; label: string; icon: string }[] = [
  { key: 'select', label: '选择', icon: 'ic:round-near-me' },
  { key: 'point-nav', label: '导航点', icon: 'ic:round-location-on' },
  { key: 'point-recv', label: '接待点', icon: 'ic:round-place' },
  { key: 'path', label: '路径', icon: 'ic:round-trending-flat' },
  { key: 'rect-obstacle', label: '障碍物', icon: 'ic:round-crop-square' },
  { key: 'polygon-restricted', label: '禁区', icon: 'ic:round-pentagon' },
];
</script>

<template>
  <div class="flex items-center gap-8px border-b border-gray-200 bg-white px-12px py-8px">
    <NButtonGroup size="small">
      <NButton
        v-for="mode in drawingModes"
        :key="mode.key"
        :type="drawingMode === mode.key ? 'primary' : 'default'"
        @click="emit('update:drawingMode', mode.key)"
      >
        <template #icon>
          <component :is="`icon-${mode.icon}`" />
        </template>
        {{ mode.label }}
      </NButton>
    </NButtonGroup>

    <NDivider vertical />

    <NButtonGroup size="small">
      <NButton :disabled="!canUndo" @click="emit('undo')">
        <template #icon><icon-ic-round-undo /></template>
        撤销
      </NButton>
      <NButton :disabled="!canRedo" @click="emit('redo')">
        <template #icon><icon-ic-round-redo /></template>
        重做
      </NButton>
    </NButtonGroup>

    <NDivider vertical />

    <NButton type="primary" size="small" :loading="saving" @click="emit('save')">
      <template #icon><icon-ic-round-save /></template>
      保存
    </NButton>

    <NDropdown
      :options="[
        { label: 'PNG', key: 'png' },
        { label: 'JPG', key: 'jpeg' },
        { label: 'WebP', key: 'webp' },
      ]"
      @select="(key: string) => emit('export', key as any)"
    >
      <NButton size="small">
        <template #icon><icon-ic-round-download /></template>
        导出
      </NButton>
    </NDropdown>

    <div class="flex-1" />
    <div v-if="isDirty" class="text-xs text-orange-500">有未保存的更改</div>
  </div>
</template>
