<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { REG_EMAIL, REG_PHONE, REG_PWD } from '@/constants/reg';
import { fetchCreateAppUser, fetchUpdateAppUser } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'AppUserOperateDrawer'
});

interface Props {
  /** the type of operation */
  operateType: NaiveUI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.AppUser | null;
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
    add: $t('page.manage.appUser.addUser'),
    edit: $t('page.manage.appUser.editUser')
  };
  return titles[props.operateType];
});

type Model = {
  name: string;
  phone_code: string;
  phone: string;
  password: string;
  confirmPassword: string;
  email: string;
  status: Api.Common.EnableStatus;
};

function createDefaultModel(): Model {
  return {
    name: '',
    phone_code: '86',
    phone: '',
    password: '',
    confirmPassword: '',
    email: '',
    status: '1'
  };
}

const model = ref(createDefaultModel());

type RuleKey = Extract<
  keyof Model,
  'name' | 'phone_code' | 'phone' | 'status' | 'password' | 'confirmPassword' | 'email'
>;

const rules: Record<RuleKey, App.Global.FormRule | App.Global.FormRule[]> = {
  name: defaultRequiredRule,
  phone_code: defaultRequiredRule,
  phone: [
    defaultRequiredRule,
    {
      pattern: REG_PHONE,
      message: $t('page.manage.appUser.form.phoneFormat'),
      trigger: ['input', 'blur']
    }
  ],
  status: defaultRequiredRule,
  // 密码选填：留空表示该用户只能通过短信验证码登录
  password: [
    {
      validator: (_rule, value) => {
        if (!value) return true;
        if (!REG_PWD.test(value)) return new Error($t('form.pwd.invalid'));
        return true;
      },
      trigger: ['input', 'blur']
    }
  ],
  confirmPassword: [
    {
      validator: (_rule, value) => {
        // 未设置密码时跳过确认校验
        if (!model.value.password) return true;
        if (model.value.password !== value) {
          return new Error($t('page.manage.appUser.form.passwordNotMatch'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ],
  email: [
    {
      validator: (_rule, value) => {
        if (value && !REG_EMAIL.test(value)) {
          return new Error($t('page.manage.appUser.form.emailFormat'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ]
};

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, jsonClone(props.rowData));
    // 编辑时不改密：清空密码字段（改密走专用入口）
    model.value.password = '';
    model.value.confirmPassword = '';
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (props.operateType === 'add') {
    const result = await fetchCreateAppUser({
      name: model.value.name,
      phone_code: model.value.phone_code,
      phone: model.value.phone,
      password: model.value.password || undefined,
      email: model.value.email || undefined,
      status: model.value.status
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    const result = await fetchUpdateAppUser(props.rowData.id, {
      name: model.value.name,
      phone_code: model.value.phone_code,
      phone: model.value.phone,
      email: model.value.email || undefined,
      status: model.value.status
    });
    error = result.error;
  }

  // flat request 不抛异常，需显式判断 error；后端错误 msg 已由全局拦截器弹出
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
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.appUser.userName')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.manage.appUser.form.userName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.appUser.phoneCode')" path="phone_code">
          <NInput v-model:value="model.phone_code" :placeholder="$t('page.manage.appUser.form.phoneCode')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.appUser.userPhone')" path="phone">
          <NInput v-model:value="model.phone" :placeholder="$t('page.manage.appUser.form.userPhone')" maxlength="11" />
        </NFormItem>
        <NFormItem v-if="props.operateType === 'add'" :label="$t('page.manage.appUser.password')" path="password">
          <NInput
            v-model:value="model.password"
            type="password"
            :placeholder="$t('page.manage.appUser.form.passwordPlaceholder')"
          />
        </NFormItem>
        <NFormItem
          v-if="props.operateType === 'add'"
          :label="$t('page.manage.appUser.confirmPassword')"
          path="confirmPassword"
        >
          <NInput
            v-model:value="model.confirmPassword"
            type="password"
            :placeholder="$t('page.manage.appUser.form.confirmPassword')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.appUser.userEmail')" path="email">
          <NInput v-model:value="model.email" :placeholder="$t('page.manage.appUser.form.userEmail')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.appUser.userStatus')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
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
