<script setup lang="ts">
import { NSelect } from 'naive-ui';
import { useDict } from '@/hooks/business/dict';
import { $t } from '@/locales';

defineOptions({ name: 'DictSelect', inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    dictCode: string;
    value?: string | number | null;
    clearable?: boolean;
    disabled?: boolean;
    multiple?: boolean;
    placeholder?: string;
  }>(),
  {
    value: null,
    clearable: true,
    disabled: false,
    multiple: false,
    placeholder: () => $t('captcha.selectPlaceholder')
  }
);

const emit = defineEmits<{
  'update:value': [value: string | number | Array<string | number> | null];
}>();

const { options, loading } = useDict(() => props.dictCode);

function handleUpdateValue(val: string | number | Array<string | number> | null) {
  emit('update:value', val);
}
</script>

<template>
  <NSelect
    :value="value"
    :options="options"
    :loading="loading"
    :clearable="clearable"
    :disabled="disabled"
    :multiple="multiple"
    :placeholder="placeholder"
    v-bind="$attrs"
    @update:value="handleUpdateValue"
  />
</template>
