<script setup lang="ts">
import { computed, toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'OpenapiLogSearch'
});

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useNaiveForm();

const model = defineModel<Api.SystemManage.OpenapiLogSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

function resetModel() {
  Object.assign(model.value, defaultModel);
}

async function reset() {
  await restoreValidation();
  resetModel();
}

async function search() {
  await validate();
  emit('search');
}
</script>

<template>
  <NCard :bordered="false" size="small" class="card-wrapper">
    <NCollapse :default-expanded-names="['openapi-log-search']">
      <NCollapseItem :title="$t('common.search')" name="openapi-log-search">
        <NForm ref="formRef" :model="model" label-placement="left" :label-width="90">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.appId')" path="app_id" class="pr-24px">
              <NInput v-model:value="model.app_id" :placeholder="$t('page.manage.openapiLog.form.appId')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.path')" path="path" class="pr-24px">
              <NInput v-model:value="model.path" :placeholder="$t('page.manage.openapiLog.form.path')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.method')" path="method" class="pr-24px">
              <NInput v-model:value="model.method" :placeholder="$t('page.manage.openapiLog.form.method')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.errCode')" path="err_code" class="pr-24px">
              <NInputNumber v-model:value="model.err_code" class="w-full" :placeholder="$t('page.manage.openapiLog.form.errCode')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.clientIp')" path="client_ip" class="pr-24px">
              <NInput v-model:value="model.client_ip" :placeholder="$t('page.manage.openapiLog.form.clientIp')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.manage.openapiLog.status')" path="status_code" class="pr-24px">
              <NInputNumber v-model:value="model.status_code" class="w-full" :placeholder="$t('page.manage.openapiLog.form.status')" />
            </NFormItemGi>
            <NFormItemGi span="24 m:12" class="pr-24px">
              <NSpace class="w-full" justify="end">
                <NButton @click="reset">
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
