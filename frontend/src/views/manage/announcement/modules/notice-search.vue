<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { $t } from '@/locales';
import { getGridActionSpan } from '@/utils/common';

defineOptions({
  name: 'NoticeSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Notification.NoticeSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

/** 搜索/重置按钮所在网格项的响应式 span：填满末行剩余宽度，使按钮固定在右下角 */
const actionSpan = getGridActionSpan(5);

/** 通知类型选项 */
const noticeTypeOptions = [
  { label: $t('page.manage.announcement.type.announcement'), value: 'announcement' },
  { label: $t('page.manage.announcement.type.system'), value: 'system' },
  { label: $t('page.manage.announcement.type.operation'), value: 'operation' },
  { label: $t('page.manage.announcement.type.approval'), value: 'approval' }
];

/** 推送范围选项 */
const targetTypeOptions = [
  { label: $t('page.manage.announcement.targetType.all'), value: 'all' },
  { label: $t('page.manage.announcement.targetType.role'), value: 'role' },
  { label: $t('page.manage.announcement.targetType.user'), value: 'user' }
];

/** 优先级选项 */
const priorityOptions = [
  { label: $t('notification.priority.low'), value: 'low' },
  { label: $t('notification.priority.normal'), value: 'normal' },
  { label: $t('notification.priority.high'), value: 'high' },
  { label: $t('notification.priority.urgent'), value: 'urgent' }
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
    <NCollapse :default-expanded-names="['notice-search']">
      <NCollapseItem :title="$t('common.search')" name="notice-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.title')" path="title" class="pr-24px">
              <NInput v-model:value="model.title" :placeholder="$t('page.manage.announcement.form.title')" clearable />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.announcement.noticeType')"
              path="type"
              class="pr-24px"
            >
              <NSelect
                v-model:value="model.type"
                :options="noticeTypeOptions"
                :placeholder="$t('page.manage.announcement.form.type')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.announcement.targetTypeLabel')"
              path="target_type"
              class="pr-24px"
            >
              <NSelect
                v-model:value="model.target_type"
                :options="targetTypeOptions"
                :placeholder="$t('page.manage.announcement.form.targetType')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.status')" path="status" class="pr-24px">
              <NSelect
                v-model:value="model.status"
                :options="enableStatusOptions"
                :placeholder="$t('page.manage.announcement.form.status')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.announcement.priority')"
              path="priority"
              class="pr-24px"
            >
              <NSelect
                v-model:value="model.priority"
                :options="priorityOptions"
                :placeholder="$t('page.manage.announcement.form.priority')"
                clearable
              />
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

<style scoped></style>
