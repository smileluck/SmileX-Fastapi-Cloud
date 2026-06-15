<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { fetchCreateRobot, fetchUpdateRobot, fetchGetAllRobotModels } from '@/service/api';

defineOptions({
  name: 'RobotOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Robot.Robot | null;
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
    add: '新增机器人',
    edit: '编辑机器人'
  };
  return titles[props.operateType];
});

/** 型号下拉选项 */
const modelOptions = ref<{ label: string; value: number }[]>([]);

async function loadModelOptions() {
  const { data, error } = await fetchGetAllRobotModels();
  if (!error && data) {
    modelOptions.value = (data as unknown as Api.Robot.AllRobotModel[]).map(item => ({
      label: `${item.name} (${item.brand} - ${item.model})`,
      value: item.id
    }));
  }
}

/** 机器人状态选项 */
const statusOptions = [
  { label: '在线', value: 'online' },
  { label: '离线', value: 'offline' },
  { label: '未激活', value: 'inactive' }
];

const model = ref(createDefaultModel());

function createDefaultModel(): Api.Robot.RobotCreate {
  return {
    name: '',
    model_id: undefined as unknown as number,
    serial_number: '',
    status: 'inactive'
  };
}

const rules = {
  name: { required: true, message: '请输入机器人名称', trigger: 'blur' },
  model_id: { required: true, message: '请选择机器人型号', trigger: 'change', type: 'number' },
  serial_number: { required: true, message: '请输入序列号', trigger: 'blur' }
};

const robotId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.model_id = clonedData.model_id;
    model.value.serial_number = clonedData.serial_number || '';
    model.value.status = clonedData.status || 'inactive';
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateRobot(robotId.value, model.value);
    error = result.error;
  } else {
    const result = await fetchCreateRobot(model.value);
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

onMounted(() => {
  loadModelOptions();
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="460">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem label="机器人名称" path="name">
          <NInput v-model:value="model.name" placeholder="请输入机器人名称" />
        </NFormItem>
        <NFormItem label="机器人型号" path="model_id">
          <NSelect
            v-model:value="model.model_id"
            :options="modelOptions"
            placeholder="请选择机器人型号"
            filterable
            clearable
          />
        </NFormItem>
        <NFormItem label="序列号" path="serial_number">
          <NInput v-model:value="model.serial_number" placeholder="请输入序列号" />
        </NFormItem>
        <NFormItem :label="$t('common.status')" path="status">
          <NSelect
            v-model:value="model.status"
            :options="statusOptions"
            placeholder="请选择状态"
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
