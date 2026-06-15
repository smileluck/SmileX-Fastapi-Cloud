<script setup lang="ts">
import { reactive, ref, computed, onMounted } from 'vue';
import { useMessage } from 'naive-ui';
import {
  fetchGetRobotList,
  fetchGetVoiceConfig,
  fetchSaveVoiceConfig,
  fetchTestWakeWord,
  fetchTestTTS
} from '@/service/api';
import { useNaiveForm } from '@/hooks/common/form';

defineOptions({ name: 'VoiceSynthesisTab' });

const message = useMessage();
const { formRef, validate, restoreValidation } = useNaiveForm();
const loading = ref(false);
const saving = ref(false);
const robotLoading = ref(false);
const showAlert = ref(false);

const robotList = ref<Api.Robot.Robot[]>([]);
const selectedRobotId = ref<number | null>(null);

const model = reactive<Api.RobotConfig.VoiceConfig>({
  robot_id: 0,
  wake_word: '',
  tts_voice: 'female',
  tts_speed: 50,
  tts_volume: 80
});

const rules = computed(() => ({
  wake_word: [
    { required: true, message: '请输入唤醒词', trigger: 'blur' },
    { min: 4, max: 6, message: '唤醒词必须为 4-6 个字', trigger: 'blur' }
  ],
  tts_voice: { required: true, message: '请选择音色', trigger: 'change' }
}));

const voiceOptions = [
  { label: '男声', value: 'male' },
  { label: '女声', value: 'female' }
];

const canSaveWakeWord = computed(() => {
  const len = model.wake_word.trim().length;
  return len >= 4 && len <= 6;
});

const selectedRobot = computed(() =>
  robotList.value.find(r => r.id === selectedRobotId.value) || null
);

async function loadRobots() {
  robotLoading.value = true;
  try {
    const { data, error } = await fetchGetRobotList({ page: 1, page_size: 200 });
    if (!error && data) {
      robotList.value = data.records || [];
    }
  } catch (err) {
    console.error('加载机器人列表失败:', err);
  } finally {
    robotLoading.value = false;
  }
}

async function loadConfig(robotId: number) {
  loading.value = true;
  try {
    const { data, error } = await fetchGetVoiceConfig(robotId);
    if (!error && data) {
      Object.assign(model, data);
    }
  } catch (err) {
    console.error('加载语音配置失败:', err);
  } finally {
    loading.value = false;
  }
}

function handleSelectRobot(robotId: number) {
  selectedRobotId.value = robotId;
  model.robot_id = robotId;
  restoreValidation();
  loadConfig(robotId);
}

async function handleSaveVoice() {
  if (!selectedRobotId.value) {
    message.warning('请先选择机器人');
    return;
  }
  try {
    await validate();
    saving.value = true;
    const { error } = await fetchSaveVoiceConfig(model);
    if (!error) {
      message.success('保存成功');
      showAlert.value = true;
      setTimeout(() => {
        showAlert.value = false;
      }, 5000);
    }
  } catch (err) {
    console.error('保存语音配置失败:', err);
  } finally {
    saving.value = false;
  }
}

async function handleTestWakeWord() {
  if (!canSaveWakeWord.value) {
    message.warning('唤醒词必须为 4-6 个字');
    return;
  }
  try {
    const { error } = await fetchTestWakeWord(model.wake_word);
    if (!error) {
      message.success('测试指令已下发');
    }
  } catch (err) {
    console.error('测试唤醒词失败:', err);
  }
}

async function handleTestTTS() {
  try {
    const { error } = await fetchTestTTS({
      voice: model.tts_voice,
      speed: model.tts_speed,
      volume: model.tts_volume,
      text: '您好，这是语音合成测试。'
    });
    if (!error) {
      message.success('测试指令已下发');
    }
  } catch (err) {
    console.error('测试TTS失败:', err);
  }
}

const robotColumns = [
  { key: 'name', title: '机器人名称', align: 'center' as const, minWidth: 140 },
  { key: 'serial_number', title: '序列号', align: 'center' as const, minWidth: 160 }
];

function rowClassName(row: Api.Robot.Robot, _index: number) {
  return row.id === selectedRobotId.value ? 'selected-row' : '';
}

onMounted(() => {
  loadRobots();
});
</script>

<template>
  <div class="flex gap-16px h-full">
    <!-- 左侧：机器人列表 -->
    <NCard title="选择机器人" size="small" class="flex-1 flex flex-col">
      <NDataTable
        :columns="robotColumns"
        :data="robotList"
        size="small"
        :loading="robotLoading"
        :row-key="row => row.id"
        :row-class-name="rowClassName"
        :scroll-x="300"
        class="flex-1"
        :row-props="(row: Api.Robot.Robot) => ({ onClick: () => handleSelectRobot(row.id), style: 'cursor: pointer' })"
      >
        <template #empty>
          <NEmpty description="暂无机器人数据" />
        </template>
      </NDataTable>
    </NCard>

    <!-- 右侧：配置表单 -->
    <NCard title="语音配置" size="small" class="flex-1 flex flex-col">
      <div v-if="!selectedRobotId" class="flex items-center justify-center h-full text-gray-400">
        请在左侧选择机器人
      </div>
      <div v-else class="flex-col gap-16px">
        <NAlert v-if="showAlert" type="info" closable>
          唤醒词设置成功，预计 1 分钟后生效
        </NAlert>

        <div class="mb-8px text-14px font-medium">
          当前机器人：{{ selectedRobot?.name }}（{{ selectedRobot?.serial_number }}）
        </div>

        <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
          <!-- 唤醒词 -->
          <NCard title="唤醒词设置" size="small">
            <NGrid responsive="screen" :cols="1">
              <NFormItemGi label="唤醒词" path="wake_word">
                <NInput
                  v-model:value="model.wake_word"
                  placeholder="请输入 4-6 字唤醒词"
                  maxlength="6"
                  show-count
                  clearable
                />
              </NFormItemGi>
              <NFormItemGi>
                <NSpace>
                  <NButton type="primary" ghost @click="handleTestWakeWord">测试</NButton>
                </NSpace>
              </NFormItemGi>
            </NGrid>
          </NCard>

          <!-- 语音合成 -->
          <NCard title="语音合成设置" size="small" class="mt-16px">
            <NGrid responsive="screen" :cols="1">
              <NFormItemGi label="音色" path="tts_voice">
                <NSelect v-model:value="model.tts_voice" :options="voiceOptions" placeholder="请选择音色" />
              </NFormItemGi>
              <NFormItemGi label="语速">
                <NSlider v-model:value="model.tts_speed" :min="0" :max="100" :step="1" />
                <span class="ml-8px">{{ model.tts_speed }}</span>
              </NFormItemGi>
              <NFormItemGi label="音量">
                <NSlider v-model:value="model.tts_volume" :min="0" :max="100" :step="1" />
                <span class="ml-8px">{{ model.tts_volume }}</span>
              </NFormItemGi>
              <NFormItemGi>
                <NSpace>
                  <NButton type="primary" ghost @click="handleTestTTS">测试语音</NButton>
                </NSpace>
              </NFormItemGi>
            </NGrid>
          </NCard>

          <div class="mt-16px">
            <NButton type="primary" :loading="saving" :disabled="!canSaveWakeWord" @click="handleSaveVoice">
              保存设置
            </NButton>
          </div>
        </NForm>
      </div>
    </NCard>
  </div>
</template>

<style scoped>
.flex {
  display: flex;
}
.flex-col {
  display: flex;
  flex-direction: column;
}
.flex-1 {
  flex: 1;
}
.gap-16px {
  gap: 16px;
}
.h-full {
  height: 100%;
}
.items-center {
  align-items: center;
}
.justify-center {
  justify-content: center;
}
.mt-16px {
  margin-top: 16px;
}
.ml-8px {
  margin-left: 8px;
}
.mb-8px {
  margin-bottom: 8px;
}
.text-14px {
  font-size: 14px;
}
.font-medium {
  font-weight: 500;
}
.text-gray-400 {
  color: #9ca3af;
}
:deep(.selected-row td) {
  background-color: var(--n-td-color-hover) !important;
}
</style>
