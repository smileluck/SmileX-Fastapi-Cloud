<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchCreateRobotModel, fetchUpdateRobotModel } from '@/service/api';

defineOptions({
  name: 'RobotModelOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Robot.RobotModel | null;
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

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: '新增机器人型号',
    edit: '编辑机器人型号'
  };
  return titles[props.operateType];
});

const model = ref(createDefaultModel());

function createDefaultModel(): Api.Robot.RobotModelCreate {
  return {
    name: '',
    brand: '',
    model: '',
    status: '1',
    sort: 0
  };
}

const rules = {
  name: { required: true, message: '请输入型号名称', trigger: 'blur' },
  brand: { required: true, message: '请输入品牌', trigger: 'blur' },
  model: { required: true, message: '请输入型号标识', trigger: 'blur' }
};

const modelId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.brand = clonedData.brand || '';
    model.value.model = clonedData.model || '';
    model.value.status = clonedData.status || '1';
    model.value.sort = clonedData.sort ?? 0;
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateRobotModel(modelId.value, model.value);
    error = result.error;
  } else {
    const result = await fetchCreateRobotModel(model.value);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? $t('common.updateSuccess') : $t('common.addSuccess'));
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
  <NDrawer v-model:show="visible" display-directive="show" :width="460">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem label="型号名称" path="name">
          <NInput v-model:value="model.name" placeholder="请输入型号名称" />
        </NFormItem>
        <NFormItem label="品牌" path="brand">
          <NInput v-model:value="model.brand" placeholder="请输入品牌" />
        </NFormItem>
        <NFormItem label="型号标识" path="model">
          <NInput v-model:value="model.model" placeholder="请输入型号标识" />
        </NFormItem>
        <NFormItem :label="$t('common.status')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio value="1">启用</NRadio>
            <NRadio value="2">禁用</NRadio>
          </NRadioGroup>
        </NFormItem>
        <NFormItem label="排序" path="sort">
          <NInputNumber v-model:value="model.sort" placeholder="请输入排序" :min="0" class="w-full" />
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
