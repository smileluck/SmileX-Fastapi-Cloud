<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';

defineOptions({
  name: 'RobotSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Robot.RobotSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

/** 机器人状态选项 */
const statusOptions = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
  { label: '未激活', value: 'inactive' }
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
    <NCollapse :default-expanded-names="['robot-search']">
      <NCollapseItem :title="$t('common.search')" name="robot-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" label="机器人名称" path="name" class="pr-24px">
              <NInput v-model:value="model.name" placeholder="请输入机器人名称" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" label="序列号" path="serial_number" class="pr-24px">
              <NInput v-model:value="model.serial_number" placeholder="请输入序列号" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.status')" path="status" class="pr-24px">
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
  </NCard>
</template>

<style scoped></style>
