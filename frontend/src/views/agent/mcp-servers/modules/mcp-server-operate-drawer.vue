<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { fetchCreateMcpServer, fetchUpdateMcpServer } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'McpServerOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Agent.McpServer | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.agent.mcpServers.add'),
    edit: $t('page.agent.mcpServers.edit')
  };
  return titles[props.operateType];
});

interface HeaderRow {
  key: string;
  value: string;
}

interface Model {
  name: string;
  code: string;
  transport: string;
  base_url: string;
  token: string;
  headers: HeaderRow[];
  status: Api.Common.EnableStatus;
  remark: string;
}

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    transport: 'streamable_http',
    base_url: '',
    token: '',
    headers: [],
    status: '1',
    remark: ''
  };
}

const model = ref<Model>(createDefaultModel());

const transportOptions = [
  { label: 'streamable_http (2025-03-26)', value: 'streamable_http' },
  { label: 'sse (2024-11-05)', value: 'sse' }
];

const rules = computed<Record<'name' | 'code' | 'base_url' | 'transport' | 'status', App.Global.FormRule | App.Global.FormRule[]>>(() => ({
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  base_url: defaultRequiredRule,
  transport: defaultRequiredRule,
  status: defaultRequiredRule
}));

function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData);
    model.value = {
      name: cloned.name,
      code: cloned.code,
      transport: cloned.transport,
      base_url: cloned.base_url,
      token: '',
      headers: (cloned.headers || []).map(h => ({ key: h.key, value: h.value })),
      status: cloned.status || '1',
      remark: cloned.remark || ''
    };
  }
}

function addHeaderRow() {
  if (model.value.headers.length >= 10) return;
  model.value.headers.push({ key: '', value: '' });
}

function removeHeaderRow(index: number) {
  model.value.headers.splice(index, 1);
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const headers = model.value.headers
    .filter(h => h.key.trim())
    .map(h => ({ key: h.key.trim(), value: h.value }));

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateMcpServer({
      name: model.value.name,
      code: model.value.code,
      transport: model.value.transport,
      base_url: model.value.base_url,
      token: model.value.token || undefined,
      headers,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateMcpServer(props.rowData.id, {
      name: model.value.name,
      transport: model.value.transport,
      base_url: model.value.base_url,
      token: model.value.token || undefined,
      headers,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  }

  if (!error) {
    window.$message?.success(props.operateType === 'add' ? $t('common.addSuccess') : $t('common.updateSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="460">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="90">
        <NFormItem :label="$t('page.agent.mcpServers.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.agent.mcpServers.form.name')" maxlength="20" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.code')" path="code">
          <NInput
            v-model:value="model.code"
            :placeholder="$t('page.agent.mcpServers.form.code')"
            :disabled="operateType === 'edit'"
            maxlength="64"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.transport')" path="transport">
          <NSelect v-model:value="model.transport" :options="transportOptions" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.baseUrl')" path="base_url">
          <NInput v-model:value="model.base_url" :placeholder="$t('page.agent.mcpServers.form.baseUrl')" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.token')" path="token">
          <NInput
            v-model:value="model.token"
            type="password"
            show-password-on="click"
            :placeholder="operateType === 'edit' ? $t('page.agent.mcpServers.form.tokenKeep') : $t('page.agent.mcpServers.form.token')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.headers')" path="headers">
          <div class="w-full flex-col gap-8px">
            <div v-for="(header, index) in model.headers" :key="index" class="flex w-full gap-8px">
              <NInput v-model:value="header.key" placeholder="Header" class="flex-1" maxlength="64" />
              <NInput v-model:value="header.value" placeholder="Value" class="flex-1" maxlength="512" />
              <NButton type="error" text @click="removeHeaderRow(index)">
                <template #icon>
                  <icon-ant-design:delete-outlined />
                </template>
              </NButton>
            </div>
            <NButton dashed size="small" class="w-full" @click="addHeaderRow">
              {{ $t('page.agent.mcpServers.addHeader') }}
            </NButton>
          </div>
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.agent.mcpServers.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.mcpServers.form.remark')"
            maxlength="200"
          />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
