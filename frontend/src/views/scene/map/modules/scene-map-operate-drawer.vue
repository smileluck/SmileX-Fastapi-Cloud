<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useNaiveForm } from '@/hooks/common/form';
import {
  fetchCreateSceneMap,
  fetchUpdateSceneMap,
  fetchGetSceneGroupList,
  fetchUploadFile,
  getFilePreviewUrl
} from '@/service/api';

defineOptions({
  name: 'SceneMapOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Scene.SceneMap | null;
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
    add: '新增场景地图',
    edit: '编辑场景地图'
  };
  return titles[props.operateType];
});

interface MapModel {
  name: string;
  group_id: number | null;
  group_name: string | null;
  image_id: number | null;
  width: number | null;
  height: number | null;
  start_point_x: number;
  start_point_y: number;
  status: Api.Common.EnableStatus;
}

const model = ref<MapModel>(createDefaultModel());

function createDefaultModel(): MapModel {
  return {
    name: '',
    group_id: null,
    group_name: null,
    image_id: null,
    width: null,
    height: null,
    start_point_x: 0,
    start_point_y: 0,
    status: '1'
  };
}

const rules = {
  name: { required: true, message: '请输入地图名称', trigger: 'blur' },
  group_id: { required: true, type: 'number', message: '请选择所属分组', trigger: 'change' },
  image_id: { required: true, type: 'number', message: '请上传地图图片', trigger: 'change' },
  status: { required: true, message: '请选择状态', trigger: 'change' }
};

/** 分组选项 */
const groupOptions = ref<{ label: string; value: number }[]>([]);
const groupValue = ref<number | string | null>(null);

async function loadGroupOptions() {
  const { data } = await fetchGetSceneGroupList({ page: 1, page_size: 1000 });
  if (data?.records) {
    groupOptions.value = data.records.map((item: any) => ({
      label: item.name,
      value: item.id
    }));
  }
}

function handleGroupChange(val: number | string | null) {
  groupValue.value = val;
  if (val === null) {
    model.value.group_id = null;
    model.value.group_name = null;
  } else if (typeof val === 'number') {
    model.value.group_id = val;
    model.value.group_name = null;
  } else {
    model.value.group_id = null;
    model.value.group_name = val;
  }
}

/** 图片上传 */
const uploading = ref(false);
const imageUrl = ref('');

async function handleUpload({ file }: { file: { file: File } }) {
  uploading.value = true;
  try {
    const { data, error } = await fetchUploadFile(file.file, { includeImageInfo: true });
    if (!error && data) {
      model.value.image_id = data.id;
      imageUrl.value = getFilePreviewUrl(data.id);
      if (data.image_width != null && data.image_height != null) {
        model.value.width = data.image_width;
        model.value.height = data.image_height;
      }
      window.$message?.success('图片上传成功');
    }
  } finally {
    uploading.value = false;
  }
}

function handleRemoveImage() {
  model.value.image_id = null;
  imageUrl.value = '';
}

const mapId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

function handleInitModel() {
  model.value = createDefaultModel();
  groupValue.value = null;
  imageUrl.value = '';

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.group_id = clonedData.group_id ?? null;
    model.value.image_id = clonedData.image_id ?? null;
    model.value.width = clonedData.width ?? null;
    model.value.height = clonedData.height ?? null;
    model.value.start_point_x = clonedData.start_point_x ?? 0;
    model.value.start_point_y = clonedData.start_point_y ?? 0;
    model.value.status = clonedData.status ?? '1';
    groupValue.value = clonedData.group_id ?? null;
    if (clonedData.image_id) {
      imageUrl.value = getFilePreviewUrl(clonedData.image_id);
    }
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const submitData: Record<string, any> = {
    name: model.value.name,
    group_id: model.value.group_id,
    group_name: model.value.group_name,
    image_id: model.value.image_id,
    width: model.value.width,
    height: model.value.height,
    start_point_x: model.value.start_point_x,
    start_point_y: model.value.start_point_y,
    status: model.value.status
  };

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateSceneMap(mapId.value, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateSceneMap(submitData);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? '修改成功' : '新增成功');
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    loadGroupOptions();
  }
});

onMounted(() => {
  loadGroupOptions();
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="560">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem label="地图名称" path="name">
          <NInput v-model:value="model.name" placeholder="请输入地图名称" maxlength="200" show-count />
        </NFormItem>
        <NFormItem label="所属分组" path="group_id">
          <NSelect
            :value="groupValue"
            :options="groupOptions"
            placeholder="选择或输入分组名称"
            filterable
            tag
            clearable
            @update:value="handleGroupChange"
          />
        </NFormItem>
        <NFormItem label="地图图片" path="image_id">
          <div class="w-full">
            <NUpload
              :max="1"
              accept="image/*"
              :custom-request="handleUpload"
              :show-file-list="false"
            >
              <NButton :loading="uploading" ghost>
                <template #icon>
                  <icon-ic-round-upload class="text-icon" />
                </template>
                {{ uploading ? '上传中...' : '选择图片' }}
              </NButton>
            </NUpload>
            <div v-if="imageUrl" class="mt-8px flex items-center gap-8px">
              <NImage :src="imageUrl" width="120" object-fit="contain" />
              <NButton text type="error" @click="handleRemoveImage">
                移除
              </NButton>
            </div>
          </div>
        </NFormItem>
        <NFormItem v-show="false" label="宽度" path="width">
          <NInputNumber
            v-model:value="model.width"
            placeholder="请输入地图宽度"
            :min="0"
            class="w-full"
          />
        </NFormItem>
        <NFormItem v-show="false" label="高度" path="height">
          <NInputNumber
            v-model:value="model.height"
            placeholder="请输入地图高度"
            :min="0"
            class="w-full"
          />
        </NFormItem>
        <NFormItem label="起始点位X" path="start_point_x">
          <NInputNumber
            v-model:value="model.start_point_x"
            placeholder="请输入起始点位X坐标"
            clearable
            class="w-full"
          />
        </NFormItem>
        <NFormItem label="起始点位Y" path="start_point_y">
          <NInputNumber
            v-model:value="model.start_point_y"
            placeholder="请输入起始点位Y坐标"
            clearable
            class="w-full"
          />
        </NFormItem>
        <NFormItem label="状态" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">取消</NButton>
          <NButton type="primary" @click="handleSubmit">确认</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
