<script setup lang="ts">
import { toRaw } from 'vue';
import { NButton, NCard, NCollapse, NCollapseItem, NForm, NFormItemGi, NGrid, NInput, NSpace } from 'naive-ui';
import { jsonClone } from '@sa/utils';
import { $t } from '@/locales';
import { getGridActionSpan } from '@/utils/common';

defineOptions({
  name: 'OnlineUserSearch'
});

interface Emits {
  (e: 'search'): void;
}

const model = defineModel<Api.SystemManage.OnlineUserSearchParams>('model', { required: true });

const emit = defineEmits<Emits>();

const defaultModel = jsonClone(toRaw(model.value));

/** 搜索/重置按钮所在网格项的响应式 span：填满末行剩余宽度，使按钮固定在右下角 */
const actionSpan = getGridActionSpan(2);

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
    <NCollapse :default-expanded-names="['online-user-search']">
      <NCollapseItem :title="$t('common.search')" name="online-user-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.onlineUser.username')" path="username" class="pr-24px">
              <NInput v-model:value="model.username" :placeholder="$t('page.log.onlineUser.form.username')" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.log.onlineUser.ip')" path="ip" class="pr-24px">
              <NInput v-model:value="model.ip" :placeholder="$t('page.log.onlineUser.form.ip')" clearable />
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
