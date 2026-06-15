<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';

defineOptions({ name: 'TaskHistorySearch' });

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Task.TaskExecutionSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const statusOptions = [
  { label: '已完成', value: 'completed' },
  { label: '已失败', value: 'failed' },
  { label: '已取消', value: 'cancelled' }
];

function resetModel() {
  Object.assign(model.value, defaultModel);
  emit('reset');
}

function search() {
  emit('search');
}
</script>

<template>
  <NCollapse :default-expanded-names="['task-history-search']">
    <NCollapseItem :title="$t('common.search')" name="task-history-search">
      <NForm :model="model" label-placement="left" :label-width="80">
        <NGrid responsive="screen" item-responsive>
          <NFormItemGi span="24 s:12 m:6" label="任务名称" path="task_name" class="pr-24px">
            <NInput v-model:value="model.task_name" placeholder="请输入任务名称" clearable />
          </NFormItemGi>
          <NFormItemGi span="24 s:12 m:6" label="执行状态" path="status" class="pr-24px">
            <NSelect v-model:value="model.status" :options="statusOptions" placeholder="请选择状态" clearable />
          </NFormItemGi>
          <NFormItemGi span="24 m:6" class="pr-24px">
            <NSpace class="w-full" justify="end">
              <NButton @click="resetModel">
                <template #icon>
                  <icon-ic-round-refresh class="text-icon" />
                </template>
                {{ $t('common.reset') }}
              </NButton>
              <NButton type="primary" ghost @click="search">
                <template #icon>
                  <icon-ic-round-search class="text-icon" />
                </template>
                {{ $t('common.search') }}
              </NButton>
            </NSpace>
          </NFormItemGi>
        </NGrid>
      </NForm>
    </NCollapseItem>
  </NCollapse>
</template>

<style scoped></style>
