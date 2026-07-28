<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { REG_EMAIL, REG_PHONE } from '@/constants/reg';
import { fetchCreateMerchant, fetchUpdateMerchant } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'MerchantOperateDrawer'
});

interface Props {
  /** the type of operation */
  operateType: NaiveUI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.Merchant | null;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
  /** 创建成功时回调，携带一次性明文 app_secret */
  (e: 'created', payload: Api.SystemManage.MerchantCreateResult): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.manage.merchant.addMerchant'),
    edit: $t('page.manage.merchant.editMerchant')
  };
  return titles[props.operateType];
});

type Model = Pick<
  Api.SystemManage.Merchant,
  'name' | 'code' | 'contact_name' | 'contact_phone' | 'contact_email' | 'status' | 'remark' | 'sort'
>;

function createDefaultModel(): Model {
  return {
    name: '',
    code: '',
    contact_name: '',
    contact_phone: '',
    contact_email: '',
    status: '1',
    remark: '',
    sort: 0
  };
}

const model = ref<Model>(createDefaultModel());

type RuleKey = Extract<keyof Model, 'name' | 'status' | 'contact_email' | 'contact_phone'>;

const rules = computed<Record<RuleKey, App.Global.FormRule | App.Global.FormRule[]>>(() => ({
  name: [
    defaultRequiredRule,
    { min: 1, max: 100, trigger: ['input', 'blur'], message: $t('page.manage.merchant.form.merchantName') }
  ],
  status: defaultRequiredRule,
  contact_email: [
    {
      validator: (_rule, value) => {
        if (value && !REG_EMAIL.test(value)) {
          return new Error($t('page.manage.merchant.form.emailFormat'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ],
  contact_phone: [
    {
      validator: (_rule, value) => {
        if (value && !REG_PHONE.test(value)) {
          return new Error($t('page.manage.merchant.form.phoneFormat'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ]
}));

function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, jsonClone(props.rowData));
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateMerchant({
      name: model.value.name,
      code: model.value.code || undefined,
      contact_name: model.value.contact_name || undefined,
      contact_phone: model.value.contact_phone || undefined,
      contact_email: model.value.contact_email || undefined,
      status: model.value.status,
      remark: model.value.remark || undefined,
      sort: model.value.sort
    });
    error = result.error;
    if (!error && result.data) {
      emit('created', result.data);
    }
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateMerchant(props.rowData.id, {
      name: model.value.name,
      code: model.value.code || undefined,
      contact_name: model.value.contact_name || undefined,
      contact_phone: model.value.contact_phone || undefined,
      contact_email: model.value.contact_email || undefined,
      status: model.value.status,
      remark: model.value.remark || undefined,
      sort: model.value.sort
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
  <NDrawer v-model:show="visible" display-directive="show" :width="380">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="90">
        <NFormItem :label="$t('page.manage.merchant.merchantName')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.manage.merchant.form.merchantName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.merchantCode')" path="code">
          <NInput v-model:value="model.code" :placeholder="$t('page.manage.merchant.form.merchantCode')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.contactName')" path="contact_name">
          <NInput v-model:value="model.contact_name" :placeholder="$t('page.manage.merchant.form.contactName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.contactPhone')" path="contact_phone">
          <NInput
            v-model:value="model.contact_phone"
            :placeholder="$t('page.manage.merchant.form.contactPhone')"
            maxlength="11"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.contactEmail')" path="contact_email">
          <NInput v-model:value="model.contact_email" :placeholder="$t('page.manage.merchant.form.contactEmail')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.sort')" path="sort">
          <NInputNumber v-model:value="model.sort" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.merchant.remark')" path="remark">
          <NInput
            v-model:value="model.remark"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 4 }"
            :placeholder="$t('page.manage.merchant.form.remark')"
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
