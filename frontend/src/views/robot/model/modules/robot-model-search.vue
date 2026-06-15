<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { $t } from '@/locales';

defineOptions({
  name: 'RobotModelSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.Robot.RobotModelSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

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
    <NCollapse :default-expanded-names="['robot-model-search']">
      <NCollapseItem :title="$t('common.search')" name="robot-model-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" label="型号名称" path="name" class="pr-24px">
              <NInput v-model:value="model.name" placeholder="请输入型号名称" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" label="品牌" path="brand" class="pr-24px">
              <NInput v-model:value="model.brand" placeholder="请输入品牌" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('common.status')" path="status" class="pr-24px">
              <NSelect v-model:value="model.status" :options="enableStatusOptions" placeholder="请选择状态" clearable />
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
