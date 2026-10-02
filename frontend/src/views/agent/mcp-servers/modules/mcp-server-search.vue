<script setup lang="ts">
import { toRaw } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { getGridActionSpan } from '@/utils/common';

defineOptions({
  name: 'McpServerSearch'
});

interface Emits {
  (e: 'search'): void;
}

const emit = defineEmits<Emits>();

const { formRef, validate, restoreValidation } = useNaiveForm();

const model = defineModel<Api.Agent.McpServerSearchParams>('model', { required: true });

const defaultModel = jsonClone(toRaw(model.value));

const actionSpan = getGridActionSpan(4);

const transportOptions = [
  { label: 'streamable_http', value: 'streamable_http' },
  { label: 'sse', value: 'sse' }
];

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
    <NCollapse :default-expanded-names="['mcp-server-search']">
      <NCollapseItem :title="$t('common.search')" name="mcp-server-search">
        <NForm ref="formRef" :model="model" label-placement="left" :label-width="80">
          <NGrid responsive="screen" item-responsive>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.agent.mcpServers.name')" path="name" class="pr-24px">
              <NInput v-model:value="model.name" :placeholder="$t('page.agent.mcpServers.form.name')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.agent.mcpServers.code')" path="code" class="pr-24px">
              <NInput v-model:value="model.code" :placeholder="$t('page.agent.mcpServers.form.code')" />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.agent.mcpServers.transport')" path="transport" class="pr-24px">
              <NSelect v-model:value="model.transport" :options="transportOptions" clearable />
            </NFormItemGi>
            <NFormItemGi span="24 s:12 m:6" :label="$t('page.agent.mcpServers.status')" path="status" class="pr-24px">
              <NSelect
                v-model:value="model.status"
                :placeholder="$t('page.agent.mcpServers.form.status')"
                :options="enableStatusOptions"
                clearable
              />
            </NFormItemGi>
            <NFormItemGi :span="actionSpan" class="pr-24px">
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
