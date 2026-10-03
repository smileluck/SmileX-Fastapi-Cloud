<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { fetchCreateKnowledge, fetchGetAgentModelList, fetchUpdateKnowledge } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'KnowledgeOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Agent.Knowledge | null;
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
    add: $t('page.agent.knowledge.add'),
    edit: $t('page.agent.knowledge.edit')
  };
  return titles[props.operateType];
});

interface Model {
  name: string;
  code: string;
  description: string;
  embedding_model_id: number | null;
  status: Api.Common.EnableStatus;
  remark: string;
}

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    description: '',
    embedding_model_id: null,
    status: '1',
    remark: ''
  };
}

const model = ref<Model>(createDefaultModel());

// 向量化模型下拉（仅 embedding 类型）
const embeddingModelOptions = ref<{ label: string; value: number }[]>([]);

async function loadEmbeddingModels() {
  const { data, error } = await fetchGetAgentModelList({ page: 1, page_size: 200 });
  if (!error && data) {
    embeddingModelOptions.value = (data.records || [])
      .filter(item => item.model_type === 'embedding')
      .map(item => ({
        label: `${item.provider_name ? `${item.provider_name} / ` : ''}${item.display_name || item.name}`,
        value: item.id
      }));
  }
}

const rules = computed<
  Record<'name' | 'code' | 'embedding_model_id' | 'status', App.Global.FormRule | App.Global.FormRule[]>
>(() => ({
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  embedding_model_id: defaultRequiredRule,
  status: defaultRequiredRule
}));

async function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData);
    model.value = {
      name: cloned.name,
      code: cloned.code,
      description: cloned.description || '',
      embedding_model_id: cloned.embedding_model_id,
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
  if (!model.value.embedding_model_id) return;

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateKnowledge({
      name: model.value.name,
      code: model.value.code,
      description: model.value.description || undefined,
      embedding_model_id: model.value.embedding_model_id,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateKnowledge(props.rowData.id, {
      name: model.value.name,
      description: model.value.description || undefined,
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

watch(
  visible,
  () => {
    if (visible.value) {
      handleInitModel();
      restoreValidation();
      loadEmbeddingModels();
    }
  },
  { immediate: true }
);
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="480">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="110">
        <NFormItem :label="$t('page.agent.knowledge.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.agent.knowledge.form.name')" maxlength="20" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.knowledge.code')" path="code">
          <NInput
            v-model:value="model.code"
            :placeholder="$t('page.agent.knowledge.form.code')"
            :disabled="operateType === 'edit'"
            maxlength="64"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.knowledge.embeddingModel')" path="embedding_model_id">
          <NSelect
            v-model:value="model.embedding_model_id"
            :options="embeddingModelOptions"
            :placeholder="$t('page.agent.knowledge.form.embeddingModel')"
            :disabled="operateType === 'edit'"
            filterable
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.knowledge.description')" path="description">
          <NInput
            v-model:value="model.description"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.knowledge.form.description')"
            maxlength="200"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.knowledge.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.agent.knowledge.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.knowledge.form.remark')"
            maxlength="200"
          />
        </NFormItem>
        <NAlert v-if="operateType === 'add'" type="info" :show-icon="true" class="mb-12px">
          {{ $t('page.agent.knowledge.form.embeddingLockTip') }}
        </NAlert>
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
