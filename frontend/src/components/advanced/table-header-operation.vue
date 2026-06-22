<script setup lang="ts">
import { computed } from 'vue';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';

defineOptions({
  name: 'TableHeaderOperation'
});

interface Props {
  itemAlign?: NaiveUI.Align;
  disabledDelete?: boolean;
  disabledAdd?: boolean;
  loading?: boolean;
  /** permission code required to show the add button; required for the button to render */
  addAuth?: string;
  /** permission code required to show the batch delete button; required for the button to render */
  deleteAuth?: string;
  /** explicitly hide add button (overrides addAuth) */
  showAdd?: boolean;
  /** explicitly hide delete button (overrides deleteAuth) */
  showDelete?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  showAdd: true,
  showDelete: true,
  disabledAdd: false,
  disabledDelete: false
});

interface Emits {
  (e: 'add'): void;
  (e: 'delete'): void;
  (e: 'refresh'): void;
}

const emit = defineEmits<Emits>();

const columns = defineModel<NaiveUI.TableColumnCheck[]>('columns', {
  default: () => []
});

const { hasAuth } = useAuth();

const canShowAdd = computed(() => {
  if (!props.showAdd || !props.addAuth) return false;
  return hasAuth(props.addAuth);
});
const canShowDelete = computed(() => {
  if (!props.showDelete || !props.deleteAuth) return false;
  return hasAuth(props.deleteAuth);
});

function add() {
  emit('add');
}

function batchDelete() {
  emit('delete');
}

function refresh() {
  emit('refresh');
}
</script>

<template>
  <NSpace :align="itemAlign" wrap justify="end" class="lt-sm:w-200px">
    <slot name="prefix"></slot>
    <slot name="add">
      <NButton v-if="canShowAdd" :disabled="disabledAdd" size="small" ghost type="primary" @click="add">
        <template #icon>
          <icon-ic-round-plus class="text-icon" />
        </template>
        {{ $t('common.add') }}
      </NButton>
    </slot>
    <slot name="delete">
      <NPopconfirm v-if="canShowDelete" @positive-click="batchDelete">
        <template #trigger>
          <NButton size="small" ghost type="error" :disabled="disabledDelete">
            <template #icon>
              <icon-ic-round-delete class="text-icon" />
            </template>
            {{ $t('common.batchDelete') }}
          </NButton>
        </template>
        {{ $t('common.confirmDelete') }}
      </NPopconfirm>
    </slot>
    <slot name="extra"></slot>
    <NButton size="small" @click="refresh">
      <template #icon>
        <icon-mdi-refresh class="text-icon" :class="{ 'animate-spin': loading }" />
      </template>
      {{ $t('common.refresh') }}
    </NButton>
    <TableColumnSetting v-model:columns="columns" />
    <slot name="suffix"></slot>
  </NSpace>
</template>

<style scoped></style>
