<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { yesOrNoOptions } from '@/constants/business';
import { $t } from '@/locales';

defineOptions({
  name: 'ConfigSearch'
});

interface Emits {
  (e: 'search'): void;
  (e: 'reset'): void;
}

const emit = defineEmits<Emits>();

const model = defineModel<Api.SystemManage.ConfigSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

/** 配置类型选项 */
const configTypeOptions = [
  { label: $t('page.manage.config.type.string'), value: 'string' },
  { label: $t('page.manage.config.type.number'), value: 'number' },
  { label: $t('page.manage.config.type.boolean'), value: 'boolean' },
  { label: $t('page.manage.config.type.json'), value: 'json' },
  { label: $t('page.manage.config.type.array'), value: 'array' }
];

/** 配置分组选项 */
const configGroupOptions = [
  { label: $t('page.manage.config.group.system'), value: 'system' },
  { label: $t('page.manage.config.group.security'), value: 'security' },
  { label: $t('page.manage.config.group.log'), value: 'log' },
  { label: $t('page.manage.config.group.network'), value: 'network' },
  { label: $t('page.manage.config.group.storage'), value: 'storage' },
  { label: $t('page.manage.config.group.custom'), value: 'custom' }
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
    <NCollapse :default-expanded-names="['config-search']">
      <NCollapseItem :title="$t('common.search')" name="config-search">
        <NForm :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.config.configKey')" path="key" class="pr-24px">
              <NInput v-model:value="model.key" :placeholder="$t('page.manage.config.form.configKey')" clearable />
            </NFormItemGi>
            <NFormItemGi
              span="24 s:12 m:6"
              :label="$t('page.manage.config.configDesc')"
              path="description"
              class="pr-24px"
            >
              <NInput
                v-model:value="model.description"
                :placeholder="$t('page.manage.config.form.configDesc')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.config.configType')" path="type" class="pr-24px">
              <NSelect
                v-model:value="model.type"
                :options="configTypeOptions"
                :placeholder="$t('page.manage.config.form.configType')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.config.configGroup')" path="group" class="pr-24px">
              <NSelect
                v-model:value="model.group"
                :options="configGroupOptions"
                :placeholder="$t('page.manage.config.form.configGroup')"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.config.isSystem')" path="is_system" class="pr-24px">
              <NSelect
                v-model:value="model.is_system"
                :options="yesOrNoOptions"
                :placeholder="$t('page.manage.config.form.isSystem')"
                clearable
              />
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

<style scoped></style>
