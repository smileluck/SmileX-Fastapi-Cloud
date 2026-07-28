<script setup lang="ts">
import { computed, ref } from 'vue';
import { useThemeStore } from '@/store/modules/theme';
import { $t } from '@/locales';
import { themeCatalog } from '../theme-catalog.generated';
import { PROP_GROUP_ORDER, type PropGroup, inferPropGroup, inferPropKind, needsUnitHint } from '../prop-meta';

defineOptions({
  name: 'PropFields'
});

const props = defineProps<{
  /** Component name (GlobalThemeOverrides top-level key) */
  name: string;
}>();

const themeStore = useThemeStore();
const search = ref('');

const allProps = computed(() => themeCatalog.find(c => c.name === props.name)?.props ?? []);

const entry = computed(() => themeStore.componentConfig[props.name]);

const grouped = computed(() => {
  const q = search.value.trim().toLowerCase();
  const map: Record<PropGroup, typeof allProps.value> = { color: [], size: [], font: [], other: [] };
  for (const p of allProps.value) {
    if (!q || p.key.toLowerCase().includes(q)) {
      map[inferPropGroup(p.key)].push(p);
    }
  }
  return map;
});

function groupTitle(g: PropGroup): string {
  switch (g) {
    case 'color':
      return $t('theme.componentConfig.groupColor');
    case 'size':
      return $t('theme.componentConfig.groupSize');
    case 'font':
      return $t('theme.componentConfig.groupFont');
    default:
      return $t('theme.componentConfig.groupOther');
  }
}

function getValue(key: string): string | number {
  const v = entry.value?.common[key];
  return v ?? '';
}

function getNumberValue(key: string): number | null {
  const v = entry.value?.common[key];
  return typeof v === 'number' ? v : null;
}

function setValue(key: string, value: string | number) {
  themeStore.setComponentCommonField(props.name, key, value);
}
</script>

<template>
  <div class="flex-col-stretch gap-12px">
    <NInput
      v-model:value="search"
      :placeholder="$t('theme.componentConfig.searchPropPlaceholder')"
      clearable
      size="small"
    />

    <div v-if="allProps.length === 0" class="py-24px text-center text-13px opacity-50">
      {{ $t('theme.componentConfig.noProps') }}
    </div>

    <template v-else>
      <div v-for="g in PROP_GROUP_ORDER" :key="g">
        <template v-if="grouped[g].length">
          <NDivider title-placement="left">
            {{ groupTitle(g) }}
            <span class="opacity-50">({{ grouped[g].length }})</span>
          </NDivider>
          <div class="flex-col-stretch gap-6px">
            <div v-for="p in grouped[g]" :key="p.key" class="w-full flex-y-center gap-12px">
              <span class="w-1/2 shrink-0 ellipsis-text text-right text-13px text-base-text" :title="p.key">
                {{ p.key }}
              </span>
              <div class="w-1/2">
                <NColorPicker
                  v-if="inferPropKind(p.key, p.typeText) === 'color'"
                  :value="(getValue(p.key) as string) || null"
                  size="small"
                  clearable
                  class="w-full"
                  :actions="['clear']"
                  @update:value="v => setValue(p.key, v ?? '')"
                />
                <NInputNumber
                  v-else-if="inferPropKind(p.key, p.typeText) === 'number'"
                  :value="getNumberValue(p.key)"
                  size="small"
                  clearable
                  class="w-full"
                  @update:value="v => setValue(p.key, v ?? '')"
                />
                <NInput
                  v-else
                  :value="String(getValue(p.key))"
                  size="small"
                  clearable
                  @update:value="v => setValue(p.key, v)"
                >
                  <template v-if="needsUnitHint(p.key)" #suffix>
                    <span class="text-12px opacity-40">px / rem</span>
                  </template>
                </NInput>
              </div>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>

<style scoped></style>
