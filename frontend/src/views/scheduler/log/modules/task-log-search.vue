<script setup lang="ts">
import { computed, toRaw } from 'vue';
import dayjs from 'dayjs';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';

defineOptions({ name: 'TaskLogSearch' });

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Scheduler.TaskLogSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const statusOptions = [
  { label: $t('page.manage.scheduler.lastStatuses.success'), value: 'success' },
  { label: $t('page.manage.scheduler.lastStatuses.failed'), value: 'failed' },
  { label: $t('page.manage.scheduler.lastStatuses.running'), value: 'running' },
  { label: $t('page.manage.scheduler.lastStatuses.timeout'), value: 'timeout' }
];

const timeRange = computed<[number, number] | null>({
  get() {
    const start = model.value.start_time ? dayjs(model.value.start_time).valueOf() : null;
    const end = model.value.end_time ? dayjs(model.value.end_time).valueOf() : null;
    return start && end ? [start, end] : null;
  },
  set(val: [number, number] | null) {
    if (val) {
      model.value.start_time = dayjs(val[0]).format();
      model.value.end_time = dayjs(val[1]).format();
    } else {
      model.value.start_time = undefined;
      model.value.end_time = undefined;
    }
  }
});

function resetModel() {
  Object.assign(model.value, defaultModel);
  emit('search');
}

function search() {
  emit('search');
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['task-log-search']">
      <NCollapseItem :title="$t('common.search')" name="task-log-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.schedulerLog.taskName')" path="task_name" class="pr-24px">
              <NInput v-model:value="model.task_name" :placeholder="$t('page.manage.schedulerLog.form.taskName')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.schedulerLog.status')" path="status" class="pr-24px">
              <NSelect v-model:value="model.status" :options="statusOptions" :placeholder="$t('page.manage.schedulerLog.form.status')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.schedulerLog.form.timeRange')" class="pr-24px">
              <NDatePicker v-model:value="timeRange" type="datetimerange" clearable class="w-full" />
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
  </NCard>
</template>
