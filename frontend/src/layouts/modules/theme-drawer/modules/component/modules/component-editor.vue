<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import Clipboard from 'clipboard';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';
import { componentLabel } from '../component-label';
import PropFields from './prop-fields.vue';
import AdvancedJson from './advanced-json.vue';

defineOptions({
  name: 'ComponentEditor'
});

const props = defineProps<{
  /** Component name (GlobalThemeOverrides top-level key) */
  name: string;
}>();

const themeStore = useThemeStore();

const label = computed(() => componentLabel(props.name));
const enabled = computed(() => themeStore.componentConfig[props.name]?.enabled ?? false);

const copyDomRef = ref<HTMLElement | null>(null);
const copyText = computed(() => themeStore.componentConfigJson);

function onEnable(val: boolean) {
  themeStore.setComponentEnabled(props.name, val);
}

function initClipboard() {
  if (!copyDomRef.value) return;
  const clipboard = new Clipboard(copyDomRef.value);
  clipboard.on('success', () => {
    window.$message?.success($t('theme.componentConfig.copySuccess'));
  });
}

onMounted(initClipboard);
</script>

<template>
  <div class="h-full flex-col-stretch gap-16px">
    <div class="flex-y-center justify-between">
      <span class="text-15px font-600">{{ label }}</span>
      <div class="flex-y-center gap-8px">
        <textarea id="themeComponentConfigCopyTarget" :value="copyText" class="absolute opacity-0 -z-1" />
        <div ref="copyDomRef" data-clipboard-target="#themeComponentConfigCopyTarget">
          <NButton size="small" ghost>{{ $t('theme.componentConfig.copy') }}</NButton>
        </div>
        <NSwitch :value="enabled" size="small" @update:value="onEnable" />
      </div>
    </div>

    <NAlert v-if="!enabled" type="info" :show-icon="true">
      {{ $t('theme.componentConfig.notEnabledHint') }}
    </NAlert>

    <NScrollbar class="flex-1">
      <div class="flex-col-stretch gap-16px pb-16px">
        <PropFields :name="name" />

        <AdvancedJson :name="name" />
      </div>
    </NScrollbar>
  </div>
</template>

<style scoped></style>
