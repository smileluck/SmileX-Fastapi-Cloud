<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useMessage } from 'naive-ui';
import { fetchGetRobot, fetchGetRobotList, fetchUpdateRobot } from '@/service/api';

defineOptions({ name: 'BatteryThresholdTab' });

const message = useMessage();

const robotList = ref<Api.Robot.Robot[]>([]);
const selectedRobotId = ref<number | null>(null);
const batteryThreshold = ref(5);
const robotLoading = ref(false);
const configLoading = ref(false);
const saving = ref(false);

const robotOptions = computed(() =>
  robotList.value.map(robot => ({
    label: `${robot.name}（${robot.serial_number}）`,
    value: robot.id
  }))
);

const selectedRobot = computed(() => robotList.value.find(robot => robot.id === selectedRobotId.value) || null);

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
  configLoading.value = true;
  try {
    const { data, error } = await fetchGetRobot(robotId);
    if (!error && data) {
      batteryThreshold.value = data.battery_threshold ?? 5;
    }
  } catch (err) {
    console.error('加载电量阈值失败:', err);
  } finally {
    configLoading.value = false;
  }
}

function handleSelectRobot(robotId: number | null) {
  selectedRobotId.value = robotId;
  batteryThreshold.value = 5;
  if (robotId) {
    loadConfig(robotId);
  }
}

async function handleSave() {
  if (!selectedRobotId.value) {
    message.warning('请先选择机器人');
    return;
  }

  saving.value = true;
  try {
    const { error } = await fetchUpdateRobot(selectedRobotId.value, {
      battery_threshold: batteryThreshold.value
    });
    if (!error) {
      message.success('保存成功');
      const robot = robotList.value.find(item => item.id === selectedRobotId.value);
      if (robot) {
        robot.battery_threshold = batteryThreshold.value;
      }
    }
  } catch (err) {
    console.error('保存电量阈值失败:', err);
  } finally {
    saving.value = false;
  }
}

onMounted(() => {
  loadRobots();
});
</script>

<template>
  <div class="flex-col gap-16px">
    <NCard title="选择机器人" size="small">
      <NSelect
        :value="selectedRobotId"
        :options="robotOptions"
        :loading="robotLoading"
        placeholder="请选择机器人"
        filterable
        clearable
        @update:value="handleSelectRobot"
      />
    </NCard>

    <NCard title="电量报警阈值设置" size="small">
      <div v-if="!selectedRobotId" class="empty-tip">请先选择机器人</div>
      <NSpin v-else :show="configLoading">
        <div class="flex-col gap-16px">
          <div class="text-14px font-medium">
            当前机器人：{{ selectedRobot?.name }}（{{ selectedRobot?.serial_number }}）
          </div>
          <NForm label-placement="left" :label-width="120">
            <NFormItem label="电量报警阈值">
              <div class="slider-row">
                <NSlider v-model:value="batteryThreshold" :min="5" :max="50" :step="5" />
                <span class="threshold-value">{{ batteryThreshold }}%</span>
              </div>
            </NFormItem>
            <NFormItem>
              <NButton type="primary" :loading="saving" @click="handleSave">保存设置</NButton>
            </NFormItem>
          </NForm>
        </div>
      </NSpin>
    </NCard>
  </div>
</template>

<style scoped>
.flex-col {
  display: flex;
  flex-direction: column;
}
.gap-16px {
  gap: 16px;
}
.text-14px {
  font-size: 14px;
}
.font-medium {
  font-weight: 500;
}
.empty-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  color: #9ca3af;
}
.slider-row {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 12px;
}
.threshold-value {
  min-width: 48px;
  text-align: right;
}
</style>
