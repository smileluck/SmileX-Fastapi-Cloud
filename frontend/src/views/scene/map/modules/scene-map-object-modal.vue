<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useNaiveForm } from '@/hooks/common/form';
import { useDict } from '@/hooks/business/dict';
import { fetchCreateMapObject, fetchUpdateMapObject } from '@/service/api';

defineOptions({
  name: 'SceneMapObjectModal'
});

interface Props {
  mapId: number;
  editData?: Api.Scene.SceneMapObject | null;
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
  return props.editData ? '编辑物体' : '新增物体';
});

interface ObjectModel {
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  points: string;
}

const model = ref<ObjectModel>(createDefaultModel());

function createDefaultModel(): ObjectModel {
  return {
    type: '',
    x: 0,
    y: 0,
    width: 0,
    height: 0,
    points: ''
  };
}

const rules = {
  type: { required: true, message: '请选择物体类型', trigger: 'change' },
  x: { required: true, type: 'number', message: '请输入X坐标', trigger: 'blur' },
  y: { required: true, type: 'number', message: '请输入Y坐标', trigger: 'blur' }
};

/** 字典选项 */
const { options: typeOptions } = useDict('map_object_type');

const isEdit = computed(() => !!props.editData);

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.editData) {
    model.value.type = props.editData.type || '';
    model.value.x = props.editData.x ?? 0;
    model.value.y = props.editData.y ?? 0;
    model.value.width = props.editData.width ?? 0;
    model.value.height = props.editData.height ?? 0;
    model.value.points = props.editData.points || '';
  }
}

function closeModal() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const submitData = {
    map_id: props.mapId,
    type: model.value.type,
    x: model.value.x,
    y: model.value.y,
    width: model.value.width,
    height: model.value.height,
    points: model.value.points || null
  };

  let error: unknown = null;

  if (isEdit.value && props.editData) {
    const result = await fetchUpdateMapObject(props.mapId, props.editData.id, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateMapObject(submitData);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? '修改成功' : '新增成功');
    closeModal();
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
  <NModal v-model:show="visible" :title="title" preset="card" class="w-500px">
    <NScrollbar class="max-h-500px pr-20px">
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="80">
        <NFormItem label="物体类型" path="type">
          <NSelect
            v-model:value="model.type"
            :options="typeOptions"
            placeholder="请选择物体类型"
          />
        </NFormItem>
        <NFormItem label="X坐标" path="x">
          <NInputNumber v-model:value="model.x" placeholder="请输入X坐标" class="w-full" />
        </NFormItem>
        <NFormItem label="Y坐标" path="y">
          <NInputNumber v-model:value="model.y" placeholder="请输入Y坐标" class="w-full" />
        </NFormItem>
        <NFormItem label="宽度" path="width">
          <NInputNumber v-model:value="model.width" placeholder="请输入宽度" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem label="高度" path="height">
          <NInputNumber v-model:value="model.height" placeholder="请输入高度" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem label="多边形顶点" path="points">
          <NInput
            v-model:value="model.points"
            type="textarea"
            placeholder="请输入JSON格式的多边形顶点，如 [[0,0],[100,0],[100,100],[0,100]]"
            :rows="3"
          />
        </NFormItem>
      </NForm>
    </NScrollbar>
    <template #footer>
      <NSpace justify="end" :size="16">
        <NButton @click="closeModal">取消</NButton>
        <NButton type="primary" @click="handleSubmit">确认</NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped></style>
