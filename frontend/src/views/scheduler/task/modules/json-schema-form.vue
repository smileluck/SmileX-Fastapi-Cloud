<script setup lang="ts">
import { computed, watch } from 'vue';
import { NDynamicInput, NForm, NFormItem, NInput, NInputNumber, NSelect, NSwitch } from 'naive-ui';
import { $t } from '@/locales';

defineOptions({ name: 'JsonSchemaForm' });

interface Props {
  schema: Api.Scheduler.TaskParamsSchema | null;
  modelValue: Record<string, any>;
  requiredMark?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  requiredMark: false
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, any>): void;
}>();

const entries = computed<Array<{ key: string; prop: Api.Scheduler.JsonSchemaProperty; required: boolean }>>(() => {
  if (!props.schema?.properties) return [];
  const requiredList = props.schema.required || [];
  return Object.entries(props.schema.properties).map(([key, prop]) => ({
    key,
    prop,
    required: requiredList.includes(key)
  }));
});

function updateField(key: string, value: any) {
  emit('update:modelValue', { ...props.modelValue, [key]: value });
}

function initDefaults() {
  if (!props.schema?.properties) return;
  const next: Record<string, any> = { ...props.modelValue };
  for (const [key, prop] of Object.entries(props.schema.properties)) {
    if (!(key in next)) {
      if (prop.default !== undefined) {
        next[key] = prop.default;
      } else if (prop.type === 'boolean') {
        next[key] = false;
      } else if (prop.type === 'integer' || prop.type === 'number') {
        next[key] = null;
      } else if (prop.type === 'array') {
        next[key] = [];
      } else if (prop.type === 'object') {
        next[key] = {};
      } else {
        next[key] = '';
      }
    }
  }
  emit('update:modelValue', next);
}

watch(
  () => props.schema,
  () => initDefaults(),
  { immediate: true }
);

function resolveOptions(prop: Api.Scheduler.JsonSchemaProperty) {
  if (!prop.enum) return [];
  return prop.enum.map(v => ({ label: String(v), value: v }));
}

function labelOf(entry: { key: string; prop: Api.Scheduler.JsonSchemaProperty }): string {
  return entry.prop.title || entry.key;
}

function isNumberType(prop: Api.Scheduler.JsonSchemaProperty): boolean {
  if (prop.type === 'integer' || prop.type === 'number') return true;
  const anyOf = prop.anyOf || [];
  return anyOf.some(t => t.type === 'integer' || t.type === 'number');
}

function isStringType(prop: Api.Scheduler.JsonSchemaProperty): boolean {
  if (prop.type === 'string') return true;
  const anyOf = prop.anyOf || [];
  return anyOf.some(t => t.type === 'string');
}
</script>

<template>
  <div v-if="entries.length === 0" class="text-13px text-gray-400">
    {{ $t('page.manage.scheduler.noParams') }}
  </div>
  <NForm v-else label-placement="left" :show-require-mark="requiredMark" :show-feedback="false" size="small">
    <NFormItem
      v-for="entry in entries"
      :key="entry.key"
      :label="labelOf(entry)"
      :path="`params.${entry.key}`"
      class="mb-12px"
    >
      <NSwitch
        v-if="entry.prop.type === 'boolean'"
        :value="Boolean(modelValue[entry.key])"
        @update:value="v => updateField(entry.key, v)"
      />
      <NInputNumber
        v-else-if="isNumberType(entry.prop)"
        :value="modelValue[entry.key] ?? null"
        :min="entry.prop.minimum"
        :max="entry.prop.maximum"
        class="w-full"
        @update:value="v => updateField(entry.key, v)"
      />
      <NSelect
        v-else-if="entry.prop.enum && entry.prop.enum.length > 0"
        :value="modelValue[entry.key]"
        :options="resolveOptions(entry.prop)"
        class="w-full"
        @update:value="v => updateField(entry.key, v)"
      />
      <NInput
        v-else-if="isStringType(entry.prop)"
        :value="modelValue[entry.key] ?? ''"
        :placeholder="entry.prop.description || entry.prop.title || ''"
        :maxlength="entry.prop.maxLength"
        @update:value="v => updateField(entry.key, v)"
      />
      <NDynamicInput
        v-else-if="entry.prop.type === 'array'"
        :value="Array.isArray(modelValue[entry.key]) ? modelValue[entry.key] : []"
        @update:value="v => updateField(entry.key, v)"
      />
      <NInput
        v-else
        :value="typeof modelValue[entry.key] === 'string' ? modelValue[entry.key] : JSON.stringify(modelValue[entry.key] ?? '')"
        type="textarea"
        :rows="2"
        :placeholder="entry.prop.description || $t('page.manage.scheduler.paramPlaceholder', { label: labelOf(entry) })"
        @update:value="v => updateField(entry.key, v)"
      />
      <span v-if="entry.prop.description" class="ml-8px text-12px text-gray-400">{{ entry.prop.description }}</span>
    </NFormItem>
  </NForm>
</template>
