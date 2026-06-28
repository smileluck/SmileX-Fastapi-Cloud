<script setup lang="tsx">
import { computed, reactive, ref, watch } from 'vue';
import { useVModel } from '@vueuse/core';
import {
  NButton,
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NFormItemGi,
  NGrid,
  NInput,
  NModal,
  NSelect,
  NSwitch,
  useMessage
} from 'naive-ui';
import { yesOrNoOptions } from '@/constants/business';
import { fetchCreateConfig, fetchUpdateConfig } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

export type OperateType = NaiveUI.TableOperateType | 'addChild';

interface Props {
  visible: boolean;
  operateType: OperateType;
  rowData?: Api.SystemManage.Config | null;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:visible': [visible: boolean];
  submitted: [];
}>();

const message = useMessage();
const visible = useVModel(props, 'visible');

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

// JSON 编辑弹窗状态
const jsonModalVisible = ref(false);
const jsonModalField = ref<'value' | 'default_value'>('value');
const jsonModalContent = ref('');

// 打开 JSON 编辑弹窗
function openJsonModal(field: 'value' | 'default_value') {
  jsonModalField.value = field;
  jsonModalContent.value = form[field] || '';
  jsonModalVisible.value = true;
}

// 保存 JSON 编辑内容
function saveJsonModalContent() {
  try {
    // 验证 JSON 格式
    JSON.parse(jsonModalContent.value);
    form[jsonModalField.value] = jsonModalContent.value;
    message.success($t('common.saveSuccess'));
    jsonModalVisible.value = false;
  } catch (error) {
    message.error($t('page.manage.config.form.jsonFormatError'));
  }
}

// 美化 JSON 格式
function beautifyJsonInModal() {
  try {
    const parsed = JSON.parse(jsonModalContent.value);
    jsonModalContent.value = JSON.stringify(parsed, null, 2);
    message.success($t('page.manage.config.form.jsonBeautifySuccess'));
  } catch (error) {
    message.error($t('page.manage.config.form.jsonFormatError'));
  }
}

// 验证配置值
function validateConfigValue(value: string, type: string): boolean | string {
  if (!value) {
    return false;
  }

  switch (type) {
    case 'number':
      if (isNaN(Number(value))) {
        return $t('page.manage.config.form.invalidNumber');
      }
      break;
    case 'boolean':
      const booleanValues = ['true', 'false', '1', '0', 'yes', 'no'];
      if (!booleanValues.includes(value.toLowerCase())) {
        return $t('page.manage.config.form.invalidBoolean');
      }
      break;
    case 'json':
      try {
        JSON.parse(value);
      } catch {
        return $t('page.manage.config.form.invalidJson');
      }
      break;
    case 'array':
      try {
        const parsed = JSON.parse(value);
        if (!Array.isArray(parsed)) {
          return $t('page.manage.config.form.invalidArray');
        }
      } catch {
        return $t('page.manage.config.form.invalidArray');
      }
      break;
    default: // string
      break;
  }
  return true;
}

// 动态表单验证规则
const formRules = computed(() => {
  return {
    key: [defaultRequiredRule],
    value: [
      defaultRequiredRule,
      {
        validator: (_rule: App.Global.FormRule, value: string) => {
          const result = validateConfigValue(value, form.type);
          if (result !== true) {
            return new Error(result as string);
          }
          return true;
        },
        trigger: ['input', 'blur']
      }
    ],
    default_value: [
      {
        validator: (_rule: App.Global.FormRule, value: string) => {
          if (value) {
            const result = validateConfigValue(value, form.type);
            if (result !== true) {
              return new Error(result as string);
            }
          }
          return true;
        },
        trigger: ['input', 'blur']
      }
    ]
  };
});

// 美化JSON格式
function beautifyJson(field: 'value' | 'default_value') {
  const jsonString = form[field];
  if (!jsonString) {
    message.warning($t('page.manage.config.form.jsonEmpty'));
    return;
  }

  try {
    const parsed = JSON.parse(jsonString);
    form[field] = JSON.stringify(parsed, null, 2);
    message.success($t('page.manage.config.form.jsonBeautifySuccess'));
  } catch (error) {
    message.error($t('page.manage.config.form.jsonFormatError'));
  }
}

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

const defaultFormValue: Api.SystemManage.ConfigCreate = {
  key: '',
  value: '',
  default_value: '',
  validation_rule: '',
  description: '',
  type: 'string',
  group: 'system',
  is_system: '2'
};

const form = reactive<Api.SystemManage.ConfigCreate>({ ...defaultFormValue });

const drawerTitle = computed(() => {
  return props.operateType === 'add' ? $t('page.manage.config.addConfig') : $t('page.manage.config.editConfig');
});

watch(
  () => props.visible,
  val => {
    if (val) {
      restoreValidation();
      if (props.operateType === 'edit' && props.rowData) {
        Object.assign(form, props.rowData);
      } else {
        Object.assign(form, defaultFormValue);
      }
    }
  }
);

async function handleSubmit() {
  try {
    await validate();
    if (props.operateType === 'add') {
      await fetchCreateConfig(form);
      message.success($t('common.addSuccess'));
    } else if (props.operateType === 'edit' && props.rowData) {
      await fetchUpdateConfig(props.rowData.id, form);
      message.success($t('common.updateSuccess'));
    }
    emit('submitted');
    visible.value = false;
  } catch (error) {
    console.error('提交失败:', error);
  }
}
</script>

<template>
  <NDrawer v-model:show="visible" :width="560" preset="card">
    <NDrawerContent :title="drawerTitle" :native-scrollbar="false">
      <NForm ref="formRef" :model="form" :rules="formRules" label-placement="left" label-width="auto" size="small">
        <NGrid :x-gap="16" :cols="24">
          <NFormItemGi :span="24" :label="$t('page.manage.config.configKey')" path="key">
            <NInput v-model:value="form.key" :placeholder="$t('page.manage.config.form.configKey')" />
          </NFormItemGi>
          <NFormItemGi :span="24" :label="$t('page.manage.config.configValue')" path="value">
            <div class="w-full flex gap-8px">
              <NInput
                v-model:value="form.value"
                :placeholder="$t('page.manage.config.form.configValue')"
                :type="form.type === 'json' ? 'textarea' : 'text'"
                :autosize="form.type === 'json' ? { minRows: 3, maxRows: 6 } : undefined"
                class="w-full flex-1"
                style="width: 100%"
              />
              <div v-if="form.type === 'json'" class="flex gap-8px">
                <NButton size="small" type="info" ghost @click="beautifyJson('value')">
                  {{ $t('page.manage.config.beautifyJson') }}
                </NButton>
                <NButton size="small" type="primary" ghost @click="openJsonModal('value')">
                  {{ $t('page.manage.config.editInModal') }}
                </NButton>
              </div>
            </div>
          </NFormItemGi>
          <NFormItemGi :span="24" :label="$t('page.manage.config.defaultValue')" path="default_value">
            <div class="w-full flex gap-8px">
              <NInput
                v-model:value="form.default_value"
                :placeholder="$t('page.manage.config.form.defaultValue')"
                :type="form.type === 'json' ? 'textarea' : 'text'"
                :autosize="form.type === 'json' ? { minRows: 2, maxRows: 4 } : undefined"
                class="w-full flex-1"
                style="width: 100%"
              />
              <div v-if="form.type === 'json'" class="flex gap-8px">
                <NButton size="small" type="info" ghost @click="beautifyJson('default_value')">
                  {{ $t('page.manage.config.beautifyJson') }}
                </NButton>
                <NButton size="small" type="primary" ghost @click="openJsonModal('default_value')">
                  {{ $t('page.manage.config.editInModal') }}
                </NButton>
              </div>
            </div>
          </NFormItemGi>
          <NFormItemGi :span="24" :label="$t('page.manage.config.configDesc')">
            <NInput
              v-model:value="form.description"
              :placeholder="$t('page.manage.config.form.configDesc')"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 3 }"
              class="w-full"
              style="width: 100%"
            />
          </NFormItemGi>
          <NFormItemGi :span="12" :label="$t('page.manage.config.configType')">
            <NSelect
              v-model:value="form.type"
              :options="configTypeOptions"
              :placeholder="$t('page.manage.config.form.configType')"
            />
          </NFormItemGi>
          <NFormItemGi :span="12" :label="$t('page.manage.config.configGroup')">
            <NSelect
              v-model:value="form.group"
              :options="configGroupOptions"
              :placeholder="$t('page.manage.config.form.configGroup')"
            />
          </NFormItemGi>
          <NFormItemGi :span="12" :label="$t('page.manage.config.validationRule')">
            <NInput v-model:value="form.validation_rule" :placeholder="$t('page.manage.config.form.validationRule')" />
          </NFormItemGi>
          <NFormItemGi :span="12" :label="$t('page.manage.config.isSystem')">
            <NSelect
              v-model:value="form.is_system"
              :options="yesOrNoOptions"
              :placeholder="$t('page.manage.config.form.isSystem')"
            />
          </NFormItemGi>
        </NGrid>
      </NForm>
      <template #footer>
        <div class="gap-12px flex-justify-end">
          <NButton size="small" @click="visible = false">
            {{ $t('common.cancel') }}
          </NButton>
          <NButton type="primary" size="small" @click="handleSubmit">
            {{ $t('common.confirm') }}
          </NButton>
        </div>
      </template>
    </NDrawerContent>
  </NDrawer>

  <!-- JSON 编辑弹窗 -->
  <NModal v-model:show="jsonModalVisible" :width="800" preset="card" :title="$t('page.manage.config.editJson')">
    <div class="mb-12px">
      <NInput
        v-model:value="jsonModalContent"
        type="textarea"
        :autosize="{ minRows: 12, maxRows: 20 }"
        class="w-full"
        style="width: 100%"
      />
    </div>
    <div class="mb-12px flex justify-end gap-8px">
      <NButton size="small" type="info" ghost @click="beautifyJsonInModal">
        {{ $t('page.manage.config.beautifyJson') }}
      </NButton>
    </div>
    <template #footer>
      <div class="flex justify-end gap-12px">
        <NButton size="small" @click="jsonModalVisible = false">
          {{ $t('common.cancel') }}
        </NButton>
        <NButton type="primary" size="small" @click="saveJsonModalContent">
          {{ $t('common.confirm') }}
        </NButton>
      </div>
    </template>
  </NModal>
</template>

<style scoped></style>
