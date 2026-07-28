<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import {
  fetchCreateScheduledTask,
  fetchCronPreview,
  fetchGetRegistryTasks,
  fetchGetTaskParamsSchema,
  fetchUpdateScheduledTask
} from '@/service/api';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import JsonSchemaForm from './json-schema-form.vue';

defineOptions({ name: 'TaskOperateDrawer' });

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Scheduler.ScheduledTask | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', { default: false });

const { formRef, validate, restoreValidation } = useNaiveForm();

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.manage.scheduler.addTask'),
    edit: $t('page.manage.scheduler.editTask')
  };
  return titles[props.operateType];
});

const model = ref(createDefaultModel());

const allRegistryTasks = ref<Api.Scheduler.RegistryTask[]>([]);
const genericTemplateOptions = ref<{ label: string; value: string }[]>([]);
const paramsSchema = ref<Api.Scheduler.TaskParamsSchema | null>(null);
const paramsModel = ref<Record<string, any>>({});
const schemaLoading = ref(false);
const selectedTemplateKey = ref<string>('');

const triggerTypeOptions = [
  { label: $t('page.manage.scheduler.triggerTypes.cron'), value: 'cron' },
  { label: $t('page.manage.scheduler.triggerTypes.interval'), value: 'interval' },
  { label: $t('page.manage.scheduler.triggerTypes.date'), value: 'date' }
];

const concurrentPolicyOptions = [
  { label: $t('page.manage.scheduler.concurrentPolicies.skip'), value: 'skip' },
  { label: $t('page.manage.scheduler.concurrentPolicies.replace'), value: 'replace' },
  { label: $t('page.manage.scheduler.concurrentPolicies.run'), value: 'run' }
];

const cronPreviewTimes = ref<string[]>([]);
const cronPreviewLoading = ref(false);

function createDefaultModel(): Api.Scheduler.ScheduledTaskCreate {
  return {
    name: '',
    task_key: '',
    description: '',
    cron_expression: '',
    trigger_type: 'cron',
    trigger_params: '',
    timeout: 300,
    max_retries: 0,
    concurrent_policy: 'skip',
    params: null,
    function_path: undefined as any
  };
}

const rules = {
  name: { required: true, message: $t('page.manage.scheduler.form.taskName'), trigger: 'blur' },
  task_key: { required: true, message: $t('page.manage.scheduler.taskKeyRequired'), trigger: 'blur' },
  cron_expression: { required: true, message: $t('page.manage.scheduler.form.cronExpression'), trigger: 'blur' },
  trigger_type: { required: true, message: $t('page.manage.scheduler.form.triggerType'), trigger: 'change' },
  concurrent_policy: { required: true, message: $t('page.manage.scheduler.form.concurrentPolicy'), trigger: 'change' }
};

const taskId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');
const currentTemplate = computed(() => allRegistryTasks.value.find(t => t.task_key === selectedTemplateKey.value));
const hasParams = computed(() => Boolean(currentTemplate.value?.has_params || paramsSchema.value));

async function loadRegistryTasks() {
  if (genericTemplateOptions.value.length > 0) return;
  const { data, error } = await fetchGetRegistryTasks();
  if (!error && data) {
    allRegistryTasks.value = data;
    genericTemplateOptions.value = data
      .filter(t => t.task_category === 'generic')
      .map(t => ({ label: `${t.name} (${t.task_key})`, value: t.task_key }));
  }
}

async function loadSchema(templateKey: string) {
  if (!templateKey) {
    paramsSchema.value = null;
    paramsModel.value = {};
    return;
  }
  schemaLoading.value = true;
  const { data, error } = await fetchGetTaskParamsSchema(templateKey);
  if (!error) {
    paramsSchema.value = data;
    paramsModel.value = {};
  }
  schemaLoading.value = false;
}

async function onTemplateChange(templateKey: string) {
  selectedTemplateKey.value = templateKey;
  const def = allRegistryTasks.value.find(t => t.task_key === templateKey);
  if (def) {
    model.value.function_path = def.function_path || undefined;
    if (!model.value.name) model.value.name = def.name;
    if (!model.value.description) model.value.description = def.description;
    if (!model.value.cron_expression) model.value.cron_expression = def.cron_expression;
    model.value.timeout = def.timeout;
    model.value.max_retries = def.max_retries;
    model.value.concurrent_policy = def.concurrent_policy;
  }
  await loadSchema(templateKey);
}

function handleInitModel() {
  model.value = createDefaultModel();
  paramsSchema.value = null;
  paramsModel.value = {};
  selectedTemplateKey.value = '';

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.task_key = clonedData.task_key || '';
    model.value.description = clonedData.description || '';
    model.value.cron_expression = clonedData.cron_expression || '';
    model.value.trigger_type = clonedData.trigger_type || 'cron';
    model.value.trigger_params = clonedData.trigger_params || '';
    model.value.timeout = clonedData.timeout ?? 300;
    model.value.max_retries = clonedData.max_retries ?? 0;
    model.value.concurrent_policy = clonedData.concurrent_policy || 'skip';
    model.value.params = clonedData.params || null;
    model.value.function_path = clonedData.function_path || undefined;
    if (clonedData.params && typeof clonedData.params === 'object') {
      paramsModel.value = { ...clonedData.params };
    }
    // 反查模板：按 function_path 找回 registry 中的 generic task
    loadRegistryTasks().then(() => {
      const matched = allRegistryTasks.value.find(t => t.function_path === clonedData.function_path);
      if (matched) {
        selectedTemplateKey.value = matched.task_key;
        loadSchema(matched.task_key);
      }
    });
  }
  cronPreviewTimes.value = [];
}

function closeDrawer() {
  visible.value = false;
}

async function handleCronPreview() {
  if (!model.value.cron_expression) return;
  cronPreviewLoading.value = true;
  const { data, error } = await fetchCronPreview(model.value.cron_expression);
  if (!error && data) {
    cronPreviewTimes.value = data.next_run_times || [];
  }
  cronPreviewLoading.value = false;
}

async function handleSubmit() {
  await validate();

  const payload = { ...model.value };
  if (hasParams.value) {
    payload.params = { ...paramsModel.value };
  } else {
    payload.params = null;
  }

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateScheduledTask(taskId.value, payload);
    error = result.error;
  } else {
    const result = await fetchCreateScheduledTask(payload);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? $t('common.updateSuccess') : $t('common.addSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, async visibleState => {
  if (visibleState) {
    handleInitModel();
    await loadRegistryTasks();
    restoreValidation();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="640">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem v-if="!isEdit" :label="$t('page.manage.scheduler.template')" path="template">
          <NSelect
            v-model:value="selectedTemplateKey"
            :options="genericTemplateOptions"
            :placeholder="$t('page.manage.scheduler.templatePlaceholder')"
            filterable
            @update:value="onTemplateChange"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.taskCategory')" path="task_category">
          <NTag
            v-if="currentTemplate"
            :type="currentTemplate.task_category === 'generic' ? 'success' : 'info'"
            size="small"
          >
            {{
              currentTemplate.task_category === 'generic'
                ? $t('page.manage.scheduler.taskCategories.generic')
                : $t('page.manage.scheduler.taskCategories.specialist')
            }}
          </NTag>
          <span v-else class="text-13px text-gray-400">—</span>
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.taskName')" path="name">
          <NInput
            v-model:value="model.name"
            :placeholder="$t('page.manage.scheduler.form.taskName')"
            maxlength="100"
            show-count
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.taskKey')" path="task_key">
          <NInput
            v-model:value="model.task_key"
            :placeholder="isEdit ? '' : $t('page.manage.scheduler.taskKeyHint')"
            maxlength="200"
            :disabled="isEdit"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.description')" path="description">
          <NInput
            v-model:value="model.description"
            type="textarea"
            :placeholder="$t('page.manage.scheduler.form.description')"
            :rows="3"
            maxlength="500"
          />
        </NFormItem>

        <template v-if="hasParams">
          <NDivider title-placement="left" class="text-13px">{{ $t('page.manage.scheduler.triggerParams') }}</NDivider>
          <div v-if="schemaLoading" class="text-13px text-gray-400">
            {{ $t('page.manage.scheduler.schemaLoading') }}
          </div>
          <JsonSchemaForm v-else v-model="paramsModel" :schema="paramsSchema" :required-mark="true" />
        </template>

        <NDivider title-placement="left" class="text-13px">{{ $t('page.manage.scheduler.advancedConfig') }}</NDivider>
        <NFormItem :label="$t('page.manage.scheduler.triggerType')" path="trigger_type">
          <NSelect v-model:value="model.trigger_type" :options="triggerTypeOptions" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.cronExpression')" path="cron_expression">
          <NSpace vertical class="w-full">
            <NInput
              v-model:value="model.cron_expression"
              :placeholder="$t('page.manage.scheduler.form.cronExpression')"
            />
            <NButton size="small" :loading="cronPreviewLoading" @click="handleCronPreview">
              {{ $t('page.manage.scheduler.cronPreview') }}
            </NButton>
            <div v-if="cronPreviewTimes.length > 0">
              <NText depth="3">{{ $t('page.manage.scheduler.nextRunTimes') }}</NText>
              <ul class="mt-4px pl-16px text-13px">
                <li v-for="(time, idx) in cronPreviewTimes" :key="idx">{{ time }}</li>
              </ul>
            </div>
          </NSpace>
        </NFormItem>
        <NFormItem
          v-if="model.trigger_type !== 'cron'"
          :label="$t('page.manage.scheduler.triggerParams')"
          path="trigger_params"
        >
          <NInput
            v-model:value="model.trigger_params"
            type="textarea"
            :placeholder="
              model.trigger_type === 'interval'
                ? '{&quot;seconds&quot;: 60}'
                : '{&quot;run_date&quot;: &quot;2026-01-01 00:00:00&quot;}'
            "
            :rows="2"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.timeout')" path="timeout">
          <NInputNumber v-model:value="model.timeout" :min="0" :step="60" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.maxRetries')" path="max_retries">
          <NInputNumber v-model:value="model.max_retries" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.scheduler.concurrentPolicy')" path="concurrent_policy">
          <NSelect v-model:value="model.concurrent_policy" :options="concurrentPolicyOptions" />
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
