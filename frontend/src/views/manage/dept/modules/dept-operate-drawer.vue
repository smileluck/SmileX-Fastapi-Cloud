<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import {
  fetchCreateDept,
  fetchGetDeptTreeSelect,
  fetchUpdateDept
} from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { booleanToEnableStatus } from '@/utils/status';

defineOptions({
  name: 'DeptOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.SystemManage.Dept | null;
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

const title = computed(() => (props.operateType === 'add' ? $t('page.manage.dept.addDept') : $t('page.manage.dept.editDept')));

type Model = {
  parent_id: number | null;
  name: string;
  code: string;
  status: Api.Common.EnableStatus;
  sort: number;
};

const model = ref<Model>(createDefaultModel());

function createDefaultModel(): Model {
  return {
    parent_id: null,
    name: '',
    code: '',
    status: '1',
    sort: 0
  };
}

const rules: Record<keyof Model, App.Global.FormRule | App.Global.FormRule[]> = {
  parent_id: [],
  name: defaultRequiredRule,
  code: [],
  status: defaultRequiredRule,
  sort: []
};

const deptOptions = ref<Api.SystemManage.DeptTree[]>([]);

async function loadDeptOptions() {
  const { data } = await fetchGetDeptTreeSelect(false);
  deptOptions.value = data || [];
}

function handleInitModel() {
  model.value = createDefaultModel();
  if (props.operateType === 'edit' && props.rowData) {
    const cloned = jsonClone(props.rowData);
    model.value.parent_id = cloned.parent_id ?? null;
    model.value.name = cloned.name || '';
    model.value.code = cloned.code || '';
    model.value.status = booleanToEnableStatus(cloned.status);
    model.value.sort = cloned.sort ?? 0;
  } else if (props.operateType === 'add' && props.rowData?.parent_id) {
    // 添加子部门：预设 parent_id
    model.value.parent_id = props.rowData.parent_id;
  } else {
    model.value.parent_id = props.rowData?.id ?? null;
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;
  if (props.operateType === 'edit' && props.rowData?.id) {
    const result = await fetchUpdateDept(props.rowData.id, { ...model.value });
    error = result.error;
  } else {
    const result = await fetchCreateDept({ ...model.value });
    error = result.error;
  }

  if (!error) {
    window.$message?.success(props.operateType === 'edit' ? $t('common.updateSuccess') : $t('common.addSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, async () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    await loadDeptOptions();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="420">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.dept.parentDept')" path="parent_id">
          <NTreeSelect
            v-model:value="model.parent_id"
            :options="deptOptions"
            key-field="id"
            label-field="label"
            clearable
            check-strategy="child"
            :placeholder="$t('page.manage.dept.form.parentDept')"
          />
        </NFormItem>
        <NFormItem :label="$t('page.manage.dept.deptName')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.manage.dept.form.deptName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.dept.deptCode')" path="code">
          <NInput v-model:value="model.code" :placeholder="$t('page.manage.dept.form.deptCode')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.dept.sort')" path="sort">
          <NInputNumber v-model:value="model.sort" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.dept.status')" path="status">
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
