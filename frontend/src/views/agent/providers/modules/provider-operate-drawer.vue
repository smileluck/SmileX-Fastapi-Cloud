<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { fetchCreateProvider, fetchUpdateProvider } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'ProviderOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Agent.Provider | null;
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
    add: $t('page.agent.providers.add'),
    edit: $t('page.agent.providers.edit')
  };
  return titles[props.operateType];
});

interface Model {
  name: string;
  code: string;
  base_url: string;
  api_key: string;
  protocol: string;
  status: Api.Common.EnableStatus;
  remark: string;
}

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    base_url: '',
    api_key: '',
    protocol: 'openai',
    status: '1',
    remark: ''
  };
}

const model = ref<Model>(createDefaultModel());

const rules = computed<Record<'name' | 'code' | 'base_url' | 'status', App.Global.FormRule | App.Global.FormRule[]>>(() => ({
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  base_url: defaultRequiredRule,
  status: defaultRequiredRule
}));

function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData);
    model.value = {
      name: cloned.name,
      code: cloned.code,
      base_url: cloned.base_url,
      api_key: '',
      protocol: cloned.protocol || 'openai',
      status: cloned.status || '1',
      remark: cloned.remark || ''
    };
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateProvider({
      name: model.value.name,
      code: model.value.code,
      base_url: model.value.base_url,
      api_key: model.value.api_key || undefined,
      protocol: model.value.protocol,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateProvider(props.rowData.id, {
      name: model.value.name,
      base_url: model.value.base_url,
      api_key: model.value.api_key || undefined,
      protocol: model.value.protocol,
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
  <NDrawer v-model:show="visible" display-directive="show" :width="420">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="90">
        <NFormItem :label="$t('page.agent.providers.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.agent.providers.form.name')" maxlength="20" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.providers.code')" path="code">
          <NInput
            v-model:value="model.code"
            :placeholder="$t('page.agent.providers.form.code')"
            :disabled="operateType === 'edit'"
            maxlength="64"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.providers.baseUrl')" path="base_url">
          <NInput v-model:value="model.base_url" :placeholder="$t('page.agent.providers.form.baseUrl')" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.providers.apiKey')" path="api_key">
          <NInput
            v-model:value="model.api_key"
            type="password"
            show-password-on="click"
            :placeholder="operateType === 'edit' ? $t('page.agent.providers.form.apiKeyKeep') : $t('page.agent.providers.form.apiKey')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.providers.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.agent.providers.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.providers.form.remark')"
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
