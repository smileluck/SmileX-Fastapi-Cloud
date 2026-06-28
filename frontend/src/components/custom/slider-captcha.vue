<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { fetchVerifyCaptcha } from '@/service/api/auth';
import { $t } from '@/locales';

defineOptions({ name: 'SliderCaptcha' });

interface Props {
  captchaId: string;
  backgroundImage: string;
  puzzleImage: string;
  puzzleY: number;
  sliderWidth: number;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  (e: 'success', token: string): void;
  (e: 'fail'): void;
  (e: 'refresh'): void;
}>();

const IMAGE_HEIGHT = 200;
const PUZZLE_SIZE = 55;

const sliderX = ref(0);
const isDragging = ref(false);
const dragStartX = ref(0);
const dragStartSliderX = ref(0);
const status = ref<'idle' | 'success' | 'fail'>('idle');
const verifyLoading = ref(false);

function getMaxX() {
  return props.sliderWidth - 42;
}

function resetSlider() {
  sliderX.value = 0;
  status.value = 'idle';
  isDragging.value = false;
}

watch(() => props.captchaId, () => {
  resetSlider();
});

function startDrag(e: MouseEvent | TouchEvent) {
  if (status.value === 'success' || verifyLoading.value) return;
  e.preventDefault();
  isDragging.value = true;
  status.value = 'idle';
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
  dragStartX.value = clientX;
  dragStartSliderX.value = sliderX.value;
}

function onDrag(e: MouseEvent | TouchEvent) {
  if (!isDragging.value) return;
  const clientX = 'touches' in e ? e.touches[0].clientX : e.clientX;
  const delta = clientX - dragStartX.value;
  sliderX.value = Math.max(0, Math.min(dragStartSliderX.value + delta, getMaxX()));
}

async function endDrag() {
  if (!isDragging.value) return;
  isDragging.value = false;
  if (sliderX.value < 5) return;

  verifyLoading.value = true;
  const { data, error } = await fetchVerifyCaptcha(props.captchaId, Math.round(sliderX.value));
  verifyLoading.value = false;

  if (!error && data) {
    status.value = 'success';
    emit('success', data.captcha_token);
  } else {
    status.value = 'fail';
    emit('fail');
    setTimeout(() => {
      resetSlider();
      emit('refresh');
    }, 600);
  }
}

function handleRefresh() {
  if (verifyLoading.value) return;
  resetSlider();
  emit('refresh');
}

onMounted(() => {
  document.addEventListener('mouseup', endDrag);
  document.addEventListener('touchend', endDrag);
  document.addEventListener('mousemove', onDrag);
  document.addEventListener('touchmove', onDrag);
});

defineExpose({ verifyLoading });

onBeforeUnmount(() => {
  document.removeEventListener('mouseup', endDrag);
  document.removeEventListener('touchend', endDrag);
  document.removeEventListener('mousemove', onDrag);
  document.removeEventListener('touchmove', onDrag);
});
</script>

<template>
  <div class="sc" :style="{ width: `${sliderWidth}px` }">
    <!-- 图片区域 -->
    <div class="sc-image" :style="{ height: `${IMAGE_HEIGHT}px` }">
      <img :src="backgroundImage" class="sc-image__bg" alt="" />
      <img
        :src="puzzleImage"
        class="sc-image__piece"
        :style="{ top: `${puzzleY}px`, left: `${sliderX}px` }"
        alt=""
      />
      <!-- 遮罩 -->
      <transition name="sc-fade">
        <div v-if="status === 'success'" class="sc-image__mask sc-image__mask--success">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
          <span>{{ $t('captcha.success') }}</span>
        </div>
        <div v-else-if="status === 'fail'" class="sc-image__mask sc-image__mask--fail">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
          <span>{{ $t('captcha.fail') }}</span>
        </div>
      </transition>
      <!-- 刷新按钮 -->
      <button v-if="status !== 'success'" class="sc-image__refresh" :disabled="verifyLoading" @click="handleRefresh" :title="$t('captcha.refresh')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10" /><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" /></svg>
      </button>
    </div>

    <!-- 滑动条 -->
    <div class="sc-track">
      <div class="sc-track__fill" :style="{ width: `${sliderX + 40}px` }" />
      <div
        class="sc-track__thumb"
        :class="{
          'sc-track__thumb--dragging': isDragging,
          'sc-track__thumb--success': status === 'success',
          'sc-track__thumb--fail': status === 'fail'
        }"
        :style="{ transform: `translateX(${sliderX}px)` }"
        @mousedown="startDrag"
        @touchstart="startDrag"
      >
        <svg v-if="verifyLoading" class="sc-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" /></svg>
        <svg v-else-if="status === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
        <svg v-else-if="status === 'fail'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="8 6 4 12 8 18" /><polyline points="16 6 20 12 16 18" /></svg>
      </div>
      <span v-if="sliderX === 0 && status === 'idle'" class="sc-track__hint">{{ $t('captcha.slideToVerify') }}</span>
    </div>
  </div>
</template>

<style scoped>
.sc {
  display: flex;
  flex-direction: column;
  gap: 12px;
  user-select: none;
  -webkit-user-select: none;
}

/* ---- 图片区 ---- */
.sc-image {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.08);
}

.sc-image__bg {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.sc-image__piece {
  position: absolute;
  width: 55px;
  height: 55px;
  pointer-events: none;
  filter: drop-shadow(0 2px 6px rgb(0 0 0 / 0.45));
}

.sc-image__mask {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.sc-image__mask--success {
  background: rgb(82 196 26 / 0.42);
}

.sc-image__mask--fail {
  background: rgb(245 34 45 / 0.42);
}

.sc-fade-enter-active { transition: opacity 0.2s; }
.sc-fade-leave-active { transition: opacity 0.15s; }
.sc-fade-enter-from, .sc-fade-leave-to { opacity: 0; }

.sc-image__refresh {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgb(0 0 0 / 0.35);
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  backdrop-filter: blur(4px);
}

.sc-image__refresh:hover {
  background: rgb(0 0 0 / 0.55);
}

.sc-image__refresh:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* ---- 滑动条 ---- */
.sc-track {
  position: relative;
  height: 42px;
  background: #e8ecef;
  border-radius: 21px;
  overflow: hidden;
}

.sc-track__fill {
  position: absolute;
  left: 2px;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, #d4e8ff, #a8cdff);
  border-radius: 21px;
  transition: none;
}

.sc-track__thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
  box-shadow: 0 2px 8px rgb(0 0 0 / 0.18);
  z-index: 1;
  transition: box-shadow 0.15s, background 0.2s;
  color: #999;
}

.sc-track__thumb :deep(svg) {
  display: block;
}

.sc-track__thumb--dragging {
  cursor: grabbing;
  box-shadow: 0 3px 14px rgb(0 0 0 / 0.25);
  color: #1890ff;
}

.sc-track__thumb--success {
  background: #52c41a;
  color: #fff;
  box-shadow: 0 2px 10px rgb(82 196 26 / 0.4);
}

.sc-track__thumb--fail {
  background: #ff4d4f;
  color: #fff;
  box-shadow: 0 2px 10px rgb(255 77 79 / 0.4);
}

.sc-track__hint {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 13px;
  letter-spacing: 2px;
  pointer-events: none;
}

@keyframes sc-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.sc-spin {
  animation: sc-rotate 1s linear infinite;
}
</style>
