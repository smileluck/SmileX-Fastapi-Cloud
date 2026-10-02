<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { fetchCreateSkill, fetchGetSkill, fetchUpdateSkill } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'SkillOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Agent.Skill | null;
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
    add: $t('page.agent.skills.add'),
    edit: $t('page.agent.skills.edit')
  };
  return titles[props.operateType];
});

interface FileRow {
  path: string;
  content: string;
}

interface Model {
  name: string;
  code: string;
  description: string;
  instruction: string;
  files: FileRow[];
  status: Api.Common.EnableStatus;
  remark: string;
}

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    description: '',
    instruction: '',
    files: [],
    status: '1',
    remark: ''
  };
}

const model = ref<Model>(createDefaultModel());

const rules = computed<Record<'name' | 'code' | 'instruction' | 'status', App.Global.FormRule | App.Global.FormRule[]>>(() => ({
  name: defaultRequiredRule,
  code: defaultRequiredRule,
  instruction: defaultRequiredRule,
  status: defaultRequiredRule
}));

async function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    // 列表行不含 files 内容，拉详情补齐
    const { data: detail } = await fetchGetSkill(props.rowData.id);
    const source = detail || jsonClone(props.rowData);
    model.value = {
      name: source.name,
      code: source.code,
      description: source.description || '',
      instruction: source.instruction || '',
      files: (source.files || []).map(f => ({ path: f.path, content: f.content })),
      status: source.status || '1',
      remark: source.remark || ''
    };
  }
}

function addFileRow() {
  if (model.value.files.length >= 10) return;
  model.value.files.push({ path: '', content: '' });
}

function removeFileRow(index: number) {
  model.value.files.splice(index, 1);
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const files = model.value.files.filter(f => f.path.trim());

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateSkill({
      name: model.value.name,
      code: model.value.code,
      description: model.value.description || undefined,
      instruction: model.value.instruction,
      files,
      status: model.value.status,
      remark: model.value.remark || undefined
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateSkill(props.rowData.id, {
      name: model.value.name,
      description: model.value.description || undefined,
      instruction: model.value.instruction,
      files,
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
  <NDrawer v-model:show="visible" display-directive="show" :width="560">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="90">
        <NFormItem :label="$t('page.agent.skills.name')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.agent.skills.form.name')" maxlength="20" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.code')" path="code">
          <NInput
            v-model:value="model.code"
            :placeholder="$t('page.agent.skills.form.code')"
            :disabled="operateType === 'edit'"
            maxlength="64"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.description')" path="description">
          <NInput v-model:value="model.description" :placeholder="$t('page.agent.skills.form.description')" maxlength="200" />
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.instruction')" path="instruction">
          <NInput
            v-model:value="model.instruction"
            type="textarea"
            :autosize="{ minRows: 8, maxRows: 20 }"
            :placeholder="$t('page.agent.skills.form.instruction')"
            maxlength="8000"
          />
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.files')" path="files">
          <div class="w-full flex-col gap-12px">
            <div v-for="(file, index) in model.files" :key="index" class="w-full flex-col gap-4px">
              <div class="flex w-full gap-8px">
                <NInput v-model:value="file.path" placeholder="reference/guide.md" class="flex-1" maxlength="128" />
                <NButton type="error" text @click="removeFileRow(index)">
                  <template #icon>
                    <icon-ant-design:delete-outlined />
                  </template>
                </NButton>
              </div>
              <NInput
                v-model:value="file.content"
                type="textarea"
                :autosize="{ minRows: 3, maxRows: 8 }"
                :placeholder="$t('page.agent.skills.form.fileContent')"
                maxlength="32768"
              />
            </div>
            <NButton dashed size="small" class="w-full" @click="addFileRow">
              {{ $t('page.agent.skills.addFile') }}
            </NButton>
          </div>
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.agent.skills.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.agent.skills.form.remark')"
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
