<script setup lang="ts">
import { computed, ref } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';
import { themeComponentNames } from './theme-catalog.generated';
import { componentLabel } from './component-label';
import ComponentEditor from './modules/component-editor.vue';

defineOptions({
  name: 'ComponentSettings'
});

const appStore = useAppStore();
const themeStore = useThemeStore();
const selected = ref<string>('common');
const search = ref('');

const options = computed(() => themeComponentNames.map(name => ({ label: componentLabel(name), value: name })));

const enabledCount = computed(() => Object.values(themeStore.componentConfig).filter(e => e?.enabled).length);

const filteredNames = computed(() => {
  const q = search.value.trim().toLowerCase();
  if (!q) return themeComponentNames;
  return themeComponentNames.filter(
    name => name.toLowerCase().includes(q) || componentLabel(name).toLowerCase().includes(q)
  );
});

function isEnabled(name: string) {
  return themeStore.componentConfig[name]?.enabled ?? false;
}
</script>

<template>
  <div class="flex-col-stretch gap-12px">
    <div class="flex-y-center justify-between">
      <span class="text-13px opacity-70">{{ $t('theme.componentConfig.title') }}</span>
      <NTag size="small" :bordered="false" type="primary">
        {{ $t('theme.componentConfig.enabled') }}: {{ enabledCount }}
      </NTag>
    </div>

    <!-- Mobile: compact select above the editor -->
    <template v-if="appStore.isMobile">
      <NSelect v-model:value="selected" filterable :options="options" size="small" />
      <ComponentEditor :name="selected" />
    </template>

    <!-- Desktop: component list on the left, editor on the right -->
    <div v-else class="flex items-stretch gap-16px">
      <div class="w-210px flex-col-stretch shrink-0 gap-8px">
        <NInput
          v-model:value="search"
          :placeholder="$t('theme.componentConfig.searchPlaceholder')"
          clearable
          size="small"
        />
        <NScrollbar class="component-list">
          <div
            v-for="name in filteredNames"
            :key="name"
            class="component-item flex-y-center cursor-pointer justify-between rounded-4px px-10px py-6px text-13px transition-colors"
            :class="{ 'component-item--active': name === selected }"
            @click="selected = name"
          >
            <span class="ellipsis-text">{{ componentLabel(name) }}</span>
            <span v-if="isEnabled(name)" class="ml-8px h-6px w-6px shrink-0 rounded-full bg-primary"></span>
          </div>
          <div v-if="filteredNames.length === 0" class="py-24px text-center text-13px opacity-50">
            {{ $t('theme.componentConfig.noMatch') }}
          </div>
        </NScrollbar>
      </div>

      <NDivider vertical class="m-0! h-auto!" />

      <ComponentEditor :name="selected" class="min-w-0 flex-1" />
    </div>
  </div>
</template>

<style scoped>
.component-list {
  max-height: calc(100vh - 280px);
}

.component-item:hover {
  background-color: rgba(var(--primary-color), 0.08);
}

.component-item--active,
.component-item--active:hover {
  background-color: rgba(var(--primary-color), 0.12);
  color: rgb(var(--primary-color));
}
</style>
