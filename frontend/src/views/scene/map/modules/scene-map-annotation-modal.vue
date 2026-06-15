<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useNaiveForm } from '@/hooks/common/form';
import { useDict } from '@/hooks/business/dict';
import { fetchCreateMapAnnotation, fetchUpdateMapAnnotation } from '@/service/api';

defineOptions({
  name: 'SceneMapAnnotationModal'
});

interface Props {
  mapId: number;
  editData?: Api.Scene.SceneMapAnnotation | null;
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
  return props.editData ? '编辑标注' : '新增标注';
});

interface AnnotationModel {
  name: string;
  x: number;
  y: number;
  angle: number;
  type: string;
}

const model = ref<AnnotationModel>(createDefaultModel());

function createDefaultModel(): AnnotationModel {
  return {
    name: '',
    x: 0,
    y: 0,
    angle: 0,
    type: ''
  };
}

const rules = {
  name: { required: true, message: '请输入标注名称', trigger: 'blur' },
  type: { required: true, message: '请选择标注类型', trigger: 'change' },
  x: { required: true, type: 'number', message: '请输入X坐标', trigger: 'blur' },
  y: { required: true, type: 'number', message: '请输入Y坐标', trigger: 'blur' }
};

/** 字典选项 */
const { options: typeOptions } = useDict('map_annotation_type');

const isEdit = computed(() => !!props.editData);

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.editData) {
    model.value.name = props.editData.name || '';
    model.value.x = props.editData.x ?? 0;
    model.value.y = props.editData.y ?? 0;
    model.value.angle = props.editData.angle ?? 0;
    model.value.type = props.editData.type || '';
  }
}

function closeModal() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const submitData = {
    map_id: props.mapId,
    name: model.value.name,
    x: model.value.x,
    y: model.value.y,
    angle: model.value.angle,
    type: model.value.type
  };

  let error: unknown = null;

  if (isEdit.value && props.editData) {
    const result = await fetchUpdateMapAnnotation(props.mapId, props.editData.id, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateMapAnnotation(submitData);
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
        <NFormItem label="标注名称" path="name">
          <NInput v-model:value="model.name" placeholder="请输入标注名称" />
        </NFormItem>
        <NFormItem label="类型" path="type">
          <NSelect
            v-model:value="model.type"
            :options="typeOptions"
            placeholder="请选择标注类型"
          />
        </NFormItem>
        <NFormItem label="X坐标" path="x">
          <NInputNumber v-model:value="model.x" placeholder="请输入X坐标" class="w-full" />
        </NFormItem>
        <NFormItem label="Y坐标" path="y">
          <NInputNumber v-model:value="model.y" placeholder="请输入Y坐标" class="w-full" />
        </NFormItem>
        <NFormItem label="角度" path="angle">
          <NInputNumber v-model:value="model.angle" placeholder="请输入角度" class="w-full" />
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
