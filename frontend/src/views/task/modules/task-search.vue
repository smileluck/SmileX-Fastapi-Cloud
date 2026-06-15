<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';

defineOptions({ name: 'TaskSearch' });

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Task.TaskSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const taskTypeOptions = [
  { label: '巡逻', value: 'patrol' },
  { label: '播报', value: 'broadcast' }
];

const enabledOptions = [
  { label: '启用', value: '1' },
  { label: '禁用', value: '2' }
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
  <NCollapse :default-expanded-names="['task-search']">
    <NCollapseItem :title="$t('common.search')" name="task-search">
      <NForm :model="model" label-placement="left" :label-width="80">
        <NGrid responsive="screen" item-responsive>
          <NFormItemGi span="24 s:12 m:6" label="任务名称" path="name" class="pr-24px">
            <NInput v-model:value="model.name" placeholder="请输入任务名称" clearable />
          </NFormItemGi>
          <NFormItemGi span="24 s:12 m:6" label="任务类型" path="task_type" class="pr-24px">
            <NSelect v-model:value="model.task_type" :options="taskTypeOptions" placeholder="请选择类型" clearable />
          </NFormItemGi>
          <NFormItemGi span="24 s:12 m:6" label="启用状态" path="enabled" class="pr-24px">
            <NSelect v-model:value="model.enabled" :options="enabledOptions" placeholder="请选择状态" clearable />
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
