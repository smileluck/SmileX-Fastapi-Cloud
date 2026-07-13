<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions, userGenderOptions } from '@/constants/business';
import { REG_EMAIL, REG_PHONE } from '@/constants/reg';
import { fetchCreateUser, fetchGetAllRoles, fetchGetDeptTreeSelect, fetchUpdateUser } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';

defineOptions({
  name: 'UserOperateDrawer'
});

interface Props {
  /** the type of operation */
  operateType: NaiveUI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.User | null;
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

const deptOptions = ref<Api.SystemManage.DeptTree[]>([]);

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.manage.user.addUser'),
    edit: $t('page.manage.user.editUser')
  };
  return titles[props.operateType];
});

type Model = Pick<Api.SystemManage.User, 'username' | 'nickname' | 'phone' | 'email' | 'status'> & {
  password: string;
  confirmPassword: string;
  dept_id: number | null;
  roleIds: number[];
};

const model = ref(createDefaultModel());

function createDefaultModel(): Model {
  return {
    username: '',
    nickname: '',
    phone: '',
    email: '',
    password: '',
    confirmPassword: '',
    roleIds: [],
    status: '1',
    dept_id: null
  };
}

/** flatten dept tree to NaiveUI NTree-compatible options */
const deptTreeOptions = computed(() => deptOptions.value);

type RuleKey = Extract<keyof Model, 'username' | 'status' | 'password' | 'confirmPassword' | 'email' | 'phone'>;

const rules: Record<RuleKey, App.Global.FormRule | App.Global.FormRule[]> = {
  username: [
    defaultRequiredRule,
    {
      min: 4,
      max: 20,
      trigger: ['input', 'blur'],
      message: $t('page.manage.user.form.usernameLength')
    }
  ],
  status: defaultRequiredRule,
  password: [
    {
      required: props.operateType === 'add',
      message: $t('form.required'),
      trigger: ['input', 'blur']
    },
    {
      min: 6,
      max: 20,
      trigger: ['input', 'blur'],
      message: $t('page.manage.user.form.passwordLength')
    }
  ],
  confirmPassword: [
    {
      required: props.operateType === 'add',
      message: $t('form.required'),
      trigger: ['input', 'blur']
    },
    {
      min: 6,
      max: 20,
      trigger: ['input', 'blur'],
      message: $t('page.manage.user.form.passwordLength')
    },
    {
      validator: (rule, value) => {
        if (model.value.password !== value) {
          return new Error($t('page.manage.user.form.passwordNotMatch'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ],
  email: [
    {
      validator: (rule, value) => {
        if (value && !REG_EMAIL.test(value)) {
          return new Error($t('page.manage.user.form.emailFormat'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ],
  phone: [
    {
      validator: (rule, value) => {
        if (value && !REG_PHONE.test(value)) {
          return new Error($t('page.manage.user.form.phoneFormat'));
        }
        return true;
      },
      trigger: ['input', 'blur']
    }
  ]
};

/** the enabled role options（value 为角色ID，唯一，避免重名角色互相串选） */
const roleOptions = ref<CommonType.Option<number>[]>([]);

async function getRoleOptions() {
  const { error, data } = await fetchGetAllRoles();

  if (!error) {
    // value 使用角色ID（数据库主键，唯一），避免重名角色在下拉中互相串选
    roleOptions.value = data.map(item => ({
      label: item.name,
      value: item.id
    }));
  }
}

async function getDeptOptions() {
  const { error, data } = await fetchGetDeptTreeSelect(true);
  if (!error) {
    deptOptions.value = data;
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    Object.assign(model.value, jsonClone(props.rowData));
    // 用角色ID回填（rowData.roles 由列表转换时从 RawUser 透传而来）
    const rawRow = props.rowData as Api.SystemManage.RawUser;
    model.value.roleIds = rawRow.roles ? rawRow.roles.map(r => r.id) : [];
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (props.operateType === 'add') {
    // 创建用户
    const result = await fetchCreateUser({
      username: model.value.username,
      nickname: model.value.nickname,
      phone: model.value.phone,
      email: model.value.email,
      password: model.value.password,
      status: model.value.status,
      role_ids: model.value.roleIds,
      dept_id: model.value.dept_id
    });
    error = result.error;
  } else if (props.operateType === 'edit' && props.rowData) {
    // 更新用户
    const result = await fetchUpdateUser(props.rowData.id, {
      username: model.value.username,
      nickname: model.value.nickname,
      phone: model.value.phone,
      email: model.value.email,
      status: model.value.status,
      role_ids: model.value.roleIds,
      dept_id: model.value.dept_id
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
    getRoleOptions();
    getDeptOptions();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.user.userName')" path="username">
          <NInput v-model:value="model.username" :placeholder="$t('page.manage.user.form.userName')" />
        </NFormItem>
        <NFormItem v-if="props.operateType === 'add'" :label="$t('page.manage.user.password')" path="password">
          <NInput
            v-model:value="model.password"
            type="password"
            :placeholder="$t('page.manage.user.form.newPassword')"
          />
        </NFormItem>
        <NFormItem
          v-if="props.operateType === 'add'"
          :label="$t('page.manage.user.confirmPassword')"
          path="confirmPassword"
        >
          <NInput
            v-model:value="model.confirmPassword"
            type="password"
            :placeholder="$t('page.manage.user.form.confirmPassword')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.nickName')" path="nickname">
          <NInput v-model:value="model.nickname" :placeholder="$t('page.manage.user.form.nickName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.userPhone')" path="phone">
          <NInput v-model:value="model.phone" :placeholder="$t('page.manage.user.form.userPhone')" maxlength="11" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.userEmail')" path="email">
          <NInput v-model:value="model.email" :placeholder="$t('page.manage.user.form.userEmail')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.userStatus')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.userRole')" path="roleIds">
          <NSelect
            v-model:value="model.roleIds"
            multiple
            :options="roleOptions"
            :placeholder="$t('page.manage.user.form.userRole')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.user.dept')" path="dept_id">
          <NTreeSelect
            v-model:value="model.dept_id"
            :options="deptTreeOptions"
            key-field="id"
            label-field="label"
            children-field="children"
            clearable
            check-strategy="child"
            :placeholder="$t('captcha.selectPlaceholder')"
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
