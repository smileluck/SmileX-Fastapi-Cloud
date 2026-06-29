<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { $t } from '@/locales';

defineOptions({ name: 'TaskSearch' });

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Scheduler.ScheduledTaskSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const triggerTypeOptions = [
  { label: $t('page.manage.scheduler.triggerTypes.cron'), value: 'cron' },
  { label: $t('page.manage.scheduler.triggerTypes.interval'), value: 'interval' },
  { label: $t('page.manage.scheduler.triggerTypes.date'), value: 'date' }
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
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['task-search']">
      <NCollapseItem :title="$t('common.search')" name="task-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.scheduler.taskName')" path="name" class="pr-24px">
              <NInput v-model:value="model.name" :placeholder="$t('page.manage.scheduler.form.taskName')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.scheduler.taskKey')" path="task_key" class="pr-24px">
              <NInput v-model:value="model.task_key" :placeholder="$t('page.manage.scheduler.form.taskKey')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.status')" path="status" class="pr-24px">
              <NSelect v-model:value="model.status" :options="enableStatusOptions" :placeholder="$t('page.manage.scheduler.form.status')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.scheduler.triggerType')" path="trigger_type" class="pr-24px">
              <NSelect v-model:value="model.trigger_type" :options="triggerTypeOptions" :placeholder="$t('page.manage.scheduler.form.triggerType')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 m:12" class="pr-24px">
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
