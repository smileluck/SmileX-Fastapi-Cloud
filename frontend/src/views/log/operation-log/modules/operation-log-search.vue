<script setup lang="ts">
import { computed, toRaw } from 'vue';
import {
  NButton,
  NCard,
  NCollapse,
  NCollapseItem,
  NDatePicker,
  NForm,
  NFormItemGi,
  NGrid,
  NInput,
  NSpace
} from 'naive-ui';
import dayjs from 'dayjs';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';
import { getGridActionSpan } from '@/utils/common';

defineOptions({
  name: 'OperationLogSearch'
});

interface Emits {
  (e: 'search'): void;
}

const model = defineModel<Api.SystemManage.OperationLogSearchParams>('model', { required: true });

const emit = defineEmits<Emits>();

const defaultModel = jsonClone(toRaw(model.value));

/** 搜索/重置按钮所在网格项的响应式 span：填满末行剩余宽度，使按钮固定在右下角 */
const actionSpan = getGridActionSpan(4);

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
    <NCollapse :default-expanded-names="['operation-log-search']">
      <NCollapseItem :title="$t('common.search')" name="operation-log-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.log.operationLog.username')"
              path="username"
              class="pr-24px"
            >
              <NInput
                v-model:value="model.username"
                :placeholder="$t('page.log.operationLog.form.username')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.operationLog.module')" path="module" class="pr-24px">
              <NInput v-model:value="model.module" :placeholder="$t('page.log.operationLog.form.module')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.operationLog.action')" path="action" class="pr-24px">
              <NInput v-model:value="model.action" :placeholder="$t('page.log.operationLog.form.action')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.operationLog.form.timeRange')" class="pr-24px">
              <NDatePicker v-model:value="timeRange" type="datetimerange" clearable class="w-full" />
            </NFormItemGi>
            <NFormItemGi :span="actionSpan" class="pr-24px">
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
