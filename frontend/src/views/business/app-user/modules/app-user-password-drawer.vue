<script setup lang="ts">
import { ref } from 'vue';
import { REG_PWD } from '@/constants/reg';
import { fetchUpdateAppUserPassword } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

interface Props {
  /** 用户ID */
  userId: number;
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = $t('page.manage.appUser.changePassword');

type Model = {
  newPassword: string;
  confirmPassword: string;
};

const model = ref<Model>({
  newPassword: '',
  confirmPassword: ''
});

const rules: Record<keyof Model, App.Global.FormRule[]> = {
  newPassword: [
    defaultRequiredRule,
    {
      pattern: REG_PWD,
      message: $t('form.pwd.invalid'),
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    defaultRequiredRule,
    {
      validator: (_rule, value) => {
        if (value !== model.value.newPassword) {
          return new Error($t('page.manage.appUser.form.passwordNotMatch'));
        }
        return true;
      },
      trigger: 'blur'
    }
  ]
};

function closeDrawer() {
  visible.value = false;
  model.value = {
    newPassword: '',
    confirmPassword: ''
  };
}

async function handleSubmit() {
  await validate();

  // 改密后该用户所有设备需重新登录
  const { error } = await fetchUpdateAppUserPassword(props.userId, model.value.newPassword);

  if (!error) {
    window.$message?.success($t('common.updateSuccess'));
    closeDrawer();
    emit('submitted');
  }
}
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.appUser.form.newPassword')" path="newPassword">
          <NInput
            v-model:value="model.newPassword"
            type="password"
            :placeholder="$t('page.manage.appUser.form.newPassword')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.appUser.form.confirmPassword')" path="confirmPassword">
          <NInput
            v-model:value="model.confirmPassword"
            type="password"
            :placeholder="$t('page.manage.appUser.form.confirmPassword')"
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
