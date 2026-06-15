<script setup lang="ts">
import { toRaw, computed, onMounted, ref } from 'vue';
import dayjs from 'dayjs';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';
import {
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NDatePicker,
  NForm,
  NFormItemGi,
  NGrid,
  NSelect,
  NSpace
} from 'naive-ui';
import { fetchGetRobotList } from '@/service/api/robot';

defineOptions({
  name: 'RobotEventLogSearch'
});

interface Emits {
  (e: 'search'): void;
}

const model = defineModel<Api.SystemManage.RobotEventLogSearchParams>('model', { required: true });

const emit = defineEmits<Emits>();

const defaultModel = jsonClone(toRaw(model.value));

const robotOptions = ref<{ label: string; value: number }[]>([]);

const eventTypeOptions = [
  { label: $t('page.log.robotEventLog.typeTask'), value: 'task' },
  { label: $t('page.log.robotEventLog.typeAlarm'), value: 'alarm' }
];

const eventStatusOptions = [
  { label: $t('page.log.robotEventLog.statusNormal'), value: 'normal' },
  { label: $t('page.log.robotEventLog.statusAbnormal'), value: 'abnormal' }
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

async function loadRobotOptions() {
  try {
    const { data } = await fetchGetRobotList({ page: 1, page_size: 999 });
    if (data?.records) {
      robotOptions.value = data.records.map((r: any) => ({ label: r.name, value: r.id }));
    }
  } catch {
    robotOptions.value = [];
  }
}

function resetModel() {
  Object.assign(model.value, defaultModel);
  emit('search');
}

function search() {
  emit('search');
}

onMounted(() => {
  loadRobotOptions();
});
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['robot-event-log-search']">
      <NCollapseItem :title="$t('common.search')" name="robot-event-log-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.robotEventLog.robotName')" path="robot_id" class="pr-24px">
              <NSelect
                v-model:value="model.robot_id as any"
                :options="robotOptions"
                :placeholder="$t('page.log.robotEventLog.form.robotName')"
                clearable
                filterable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.robotEventLog.eventType')" path="event_type" class="pr-24px">
              <NSelect
                v-model:value="model.event_type as any"
                :options="eventTypeOptions"
                :placeholder="$t('page.log.robotEventLog.form.eventType')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.robotEventLog.eventStatus')" path="event_status" class="pr-24px">
              <NSelect
                v-model:value="model.event_status as any"
                :options="eventStatusOptions"
                :placeholder="$t('page.log.robotEventLog.form.eventStatus')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.robotEventLog.form.timeRange')" class="pr-24px">
              <NDatePicker v-model:value="timeRange" type="datetimerange" clearable class="w-full" />
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
