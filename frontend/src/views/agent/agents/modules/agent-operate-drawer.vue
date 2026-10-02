<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import {
  fetchCreateAgent,
  fetchGetAgentModelList,
  fetchGetAllEnabledSkills,
  fetchGetToolGroups,
  fetchUpdateAgent
} from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'AgentOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Agent.Agent | null;
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
    add: $t('page.agent.agents.add'),
    edit: $t('page.agent.agents.edit')
  };
  return titles[props.operateType];
});

interface Model {
  name: string;
  code: string;
  model_id: number | null;
  system_prompt: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
  tools: string[];
  skills: string[];
  status: Api.Common.EnableStatus;
  remark: string;
}

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    model_id: null,
    system_prompt: '',
    temperature: 0,
    top_p: 0,
    max_tokens: 0,
    tools: [],
    skills: [],
    status: '1',
    remark: ''
  };
}

const model = ref<Model>(createDefaultModel());

// 模型下拉（含供应商前缀展示）
const modelOptions = ref<{ label: string; value: number }[]>([]);
// 技能下拉
const skillOptions = ref<{ label: string; value: string }[]>([]);
// 工具分组多选（NSelect group）
const toolGroupOptions = ref<{ label: string; key: string; children: { label: string; value: string }[] }[]>([]);

async function loadOptions() {
  const [modelRes, skillRes, toolRes] = await Promise.all([
    fetchGetAgentModelList({ page: 1, page_size: 200 }),
    fetchGetAllEnabledSkills(),
    fetchGetToolGroups()
  ]);
  if (!modelRes.error && modelRes.data) {
    modelOptions.value = (modelRes.data.records || []).map(item => ({
      label: `${item.provider_name ? `${item.provider_name} / ` : ''}${item.display_name || item.name}`,
      value: item.id
    }));
  }
  if (!skillRes.error && skillRes.data) {
    skillOptions.value = skillRes.data.map(item => ({
      label: `${item.name} (${item.code})`,
      value: item.code
    }));
  }
  if (!toolRes.error && toolRes.data) {
    toolGroupOptions.value = toolRes.data.map(group => ({
      label: group.label,
      key: group.group,
      children: group.tools.map(tool => ({
        label: tool.description ? `${tool.name} — ${tool.description}` : tool.name,
        value: tool.name
      }))
    }));
  }
}

onMounted(() => {
  loadOptions();
});

const rules = computed<Record<'name' | 'code' | 'model_id' | 'status', App.Global.FormRule | App.Global.FormRule[]>>(() => ({
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  model_id: defaultRequiredRule,
  status: defaultRequiredRule
}));

function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData);
    model.value = {
      name: cloned.name,
      code: cloned.code,
      model_id: cloned.model_id,
      system_prompt: cloned.system_prompt || '',
      temperature: cloned.temperature || 0,
      top_p: cloned.top_p || 0,
      max_tokens: cloned.max_tokens || 0,
      tools: cloned.tools || [],
      skills: cloned.skills || [],
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
  if (!model.value.model_id) return;

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateAgent({
      name: model.value.name,
      code: model.value.code,
      model_id: model.value.model_id,
      system_prompt: model.value.system_prompt || undefined,
      temperature: model.value.temperature,
      top_p: model.value.top_p,
      max_tokens: model.value.max_tokens,
      tools: model.value.tools,
      skills: model.value.skills,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateAgent(props.rowData.id, {
      name: model.value.name,
      model_id: model.value.model_id,
      system_prompt: model.value.system_prompt || undefined,
      temperature: model.value.temperature,
      top_p: model.value.top_p,
      max_tokens: model.value.max_tokens,
      tools: model.value.tools,
      skills: model.value.skills,
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
    loadOptions();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="480">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
        <NFormItem :label="$t('page.agent.agents.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.agent.agents.form.name')" maxlength="20" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.code')" path="code">
          <NInput
            v-model:value="model.code"
            :placeholder="$t('page.agent.agents.form.code')"
            :disabled="operateType === 'edit'"
            maxlength="64"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.model')" path="model_id">
          <NSelect
            v-model:value="model.model_id"
            :options="modelOptions"
            :placeholder="$t('page.agent.agents.form.model')"
            filterable
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.systemPrompt')" path="system_prompt">
          <NInput
            v-model:value="model.system_prompt"
            type="textarea"
            :autosize="{ minRows: 4, maxRows: 10 }"
            :placeholder="$t('page.agent.agents.form.systemPrompt')"
            maxlength="4000"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.tools')" path="tools">
          <NSelect
            v-model:value="model.tools"
            multiple
            filterable
            :options="toolGroupOptions"
            :placeholder="$t('page.agent.agents.form.tools')"
            :max-tag-count="3"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.skills')" path="skills">
          <NSelect
            v-model:value="model.skills"
            multiple
            filterable
            :options="skillOptions"
            :placeholder="$t('page.agent.agents.form.skills')"
            :max-tag-count="3"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.temperature')" path="temperature">
          <NInputNumber v-model:value="model.temperature" :min="0" :max="2" :step="0.1" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.topP')" path="top_p">
          <NInputNumber v-model:value="model.top_p" :min="0" :max="1" :step="0.1" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.maxTokens')" path="max_tokens">
          <NInputNumber v-model:value="model.max_tokens" :min="0" :max="131072" :step="256" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.agent.agents.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.agents.form.remark')"
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
