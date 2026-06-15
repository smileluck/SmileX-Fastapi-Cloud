<script setup lang="tsx">
import { reactive, ref, onMounted } from 'vue';
import { NButton, NCard, NDataTable, NForm, NFormItem, NInput, NPopconfirm, NSpace, NUpload, useMessage, type UploadFileInfo } from 'naive-ui';
import {
  fetchGetFaceRecognitionList,
  fetchCreateFaceRecognition,
  fetchUpdateFaceRecognition,
  fetchDeleteFaceRecognition,
  fetchUploadFacePhoto,
  getPersistentFilePreviewPath,
  resolveFilePreviewUrl
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { useNaiveForm } from '@/hooks/common/form';

defineOptions({ name: 'FaceRecognitionTab' });

const message = useMessage();
const appStore = useAppStore();
const { formRef, validate } = useNaiveForm();

const loading = ref(false);
const tableLoading = ref(false);
const editingId = ref<number | null>(null);

const model = reactive<Api.RobotConfig.FaceRecognitionCreate>({
  person_name: '',
  photo_url: '',
  broadcast_text: ''
});

const fileList = ref<UploadFileInfo[]>([]);

const faceList = ref<Api.RobotConfig.FaceRecognition[]>([]);

const rules = {
  person_name: [{ required: true, message: '请输入人员名称', trigger: 'blur' }],
  photo_url: [{ required: true, message: '请上传人像', trigger: 'change' }],
  broadcast_text: [{ required: true, message: '请输入语音播报内容', trigger: 'blur' }]
};

async function loadData() {
  tableLoading.value = true;
  try {
    const { data, error } = await fetchGetFaceRecognitionList({ page: 1, page_size: 100 });
    if (!error && data) {
      faceList.value = data.records || [];
    }
  } catch (err) {
    console.error('加载人脸识别TTS列表失败:', err);
  } finally {
    tableLoading.value = false;
  }
}

async function handleUpload({ file }: { file: UploadFileInfo }) {
  if (!file.file) return;
  try {
    const { data, error } = await fetchUploadFacePhoto(file.file);
    if (!error && data) {
      model.photo_url = getPersistentFilePreviewPath(data.id);
      message.success('上传成功');
    }
  } catch (err) {
    message.error('上传失败');
    console.error('上传人像失败:', err);
  }
}

function handleRemovePhoto() {
  model.photo_url = '';
  return true;
}

async function handleSave() {
  try {
    await validate();
    loading.value = true;
    if (editingId.value) {
      const { error } = await fetchUpdateFaceRecognition(editingId.value, { ...model });
      if (!error) {
        message.success('更新成功');
        resetForm();
        await loadData();
      }
    } else {
      const { error } = await fetchCreateFaceRecognition({ ...model });
      if (!error) {
        message.success('保存成功');
        resetForm();
        await loadData();
      }
    }
  } catch (err) {
    console.error('保存人脸识别配置失败:', err);
  } finally {
    loading.value = false;
  }
}

function handleEdit(row: Api.RobotConfig.FaceRecognition) {
  editingId.value = row.id;
  model.person_name = row.person_name;
  model.photo_url = row.photo_url;
  model.broadcast_text = row.broadcast_text;
  fileList.value = [];
}

async function handleDelete(id: number) {
  try {
    const { error } = await fetchDeleteFaceRecognition(id);
    if (!error) {
      message.success('删除成功');
      await loadData();
    }
  } catch (err) {
    console.error('删除人脸识别配置失败:', err);
  }
}

function resetForm() {
  editingId.value = null;
  model.person_name = '';
  model.photo_url = '';
  model.broadcast_text = '';
  fileList.value = [];
  formRef.value?.restoreValidation();
}

const columns = [
  { key: 'index', title: '序号', align: 'center' as const, width: 64, render: (_: any, index: number) => index + 1 },
  { key: 'person_name', title: '人员名称', align: 'center' as const, minWidth: 120 },
  {
    key: 'photo_url',
    title: '人像',
    align: 'center' as const,
    width: 100,
    render: (row: Api.RobotConfig.FaceRecognition) => (
      <img src={resolveFilePreviewUrl(row.photo_url)} class="h-48px w-48px rounded object-cover" alt="人像" />
    )
  },
  { key: 'broadcast_text', title: '播报内容', align: 'center' as const, minWidth: 200, ellipsis: { tooltip: true } },
  {
    key: 'operate',
    title: '操作',
    align: 'center' as const,
    width: 160,
    render: (row: Api.RobotConfig.FaceRecognition) => (
      <div class="flex-center gap-8px">
        <NButton type="primary" ghost size="small" onClick={() => handleEdit(row)}>编辑</NButton>
        <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
          {{
            default: () => '确认删除吗？',
            trigger: () => (
              <NButton type="error" ghost size="small">删除</NButton>
            )
          }}
        </NPopconfirm>
      </div>
    )
  }
];

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="flex-col gap-16px">
    <!-- 配置表单 -->
    <NCard title="配置人脸识别TTS" size="small">
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
        <NGrid responsive="screen" :cols="1">
          <NFormItemGi label="人员名称" path="person_name">
            <NInput v-model:value="model.person_name" placeholder="请输入人员名称" clearable />
          </NFormItemGi>
          <NFormItemGi label="人像" path="photo_url">
            <NUpload
              v-model:file-list="fileList"
              :max="1"
              accept="image/*"
              :custom-request="handleUpload"
              :on-remove="handleRemovePhoto"
              list-type="image-card"
            />
            <span v-if="model.photo_url && !fileList.length" class="text-12px text-gray">已上传: {{ model.photo_url }}</span>
          </NFormItemGi>
          <NFormItemGi label="播报内容" path="broadcast_text">
            <NInput
              v-model:value="model.broadcast_text"
              type="textarea"
              placeholder="请输入语音播报内容"
              :rows="3"
              clearable
            />
          </NFormItemGi>
          <NFormItemGi>
            <NSpace>
              <NButton type="primary" :loading="loading" @click="handleSave">
                {{ editingId ? '更新配置' : '保存配置' }}
              </NButton>
              <NButton v-if="editingId" @click="resetForm">取消</NButton>
            </NSpace>
          </NFormItemGi>
        </NGrid>
      </NForm>
    </NCard>

    <!-- 已配置列表 -->
    <NCard title="已配置人员列表" size="small">
      <NDataTable
        :columns="columns"
        :data="faceList"
        size="small"
        :loading="tableLoading"
        :row-key="row => row.id"
        :scroll-x="600"
        class="sm:h-full"
      />
    </NCard>
  </div>
</template>

<style scoped>
.h-48px {
  height: 48px;
}
.w-48px {
  width: 48px;
}
.rounded {
  border-radius: 4px;
}
.object-cover {
  object-fit: cover;
}
.text-12px {
  font-size: 12px;
}
.text-gray {
  color: #999;
}
</style>
