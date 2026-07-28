<script setup lang="ts">
import { ref, watch } from 'vue';
import JSON5 from 'json5';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';

defineOptions({
  name: 'AdvancedJson'
});

const props = defineProps<{
  /** Component name (GlobalThemeOverrides top-level key) */
  name: string;
}>();

const themeStore = useThemeStore();

const text = ref('');
const valid = ref(true);
const error = ref('');

let timer: ReturnType<typeof setTimeout> | null = null;

/** Serialize the entry's current advanced object into the textarea (no commit). */
function syncFromStore() {
  const advanced = themeStore.componentConfig[props.name]?.advanced;
  text.value = advanced && Object.keys(advanced).length > 0 ? JSON.stringify(advanced, null, 2) : '';
  valid.value = true;
  error.value = '';
}

// re-sync when the selected component changes (programmatic — does NOT commit)
watch(() => props.name, syncFromStore, { immediate: true });

function scheduleParse() {
  if (timer) clearTimeout(timer);
  timer = setTimeout(commit, 300);
}

/** Parse the textarea and commit on user edits only. */
function commit() {
  const trimmed = text.value.trim();
  if (!trimmed) {
    valid.value = true;
    error.value = '';
    // clear existing advanced, but never create an entry just from an empty editor
    const existing = themeStore.componentConfig[props.name];
    if (existing && Object.keys(existing.advanced).length > 0) {
      themeStore.setComponentAdvanced(props.name, {});
    }
    return;
  }
  try {
    const obj = JSON5.parse(trimmed) as Record<string, unknown>;
    valid.value = true;
    error.value = '';
    themeStore.setComponentAdvanced(props.name, obj);
  } catch (e) {
    valid.value = false;
    error.value = e instanceof Error ? e.message : String(e);
  }
}

function onInput(v: string) {
  text.value = v;
  scheduleParse();
}
</script>

<template>
  <div class="flex-col-stretch gap-6px">
    <div class="flex-y-center justify-between">
      <span class="text-13px font-500">{{ $t('theme.componentConfig.advanced') }}</span>
      <NTag size="small" :type="valid ? 'success' : 'error'">
        {{ $t(valid ? 'theme.componentConfig.jsonValid' : 'theme.componentConfig.jsonInvalid') }}
      </NTag>
    </div>
    <div class="text-12px opacity-50">{{ $t('theme.componentConfig.advancedHint') }}</div>
    <NInput
      :value="text"
      type="textarea"
      :rows="5"
      size="small"
      placeholder='{ "borderRadius": "10px" }'
      @update:value="onInput"
    />
    <NText v-if="!valid" type="error" class="text-12px">{{ error }}</NText>
  </div>
</template>

<style scoped></style>
