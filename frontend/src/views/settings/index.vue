<script setup lang="ts">
import { ref } from 'vue';
import VoiceSynthesisTab from './modules/voice-synthesis-tab.vue';
import FaceRecognitionTab from './modules/face-recognition-tab.vue';
import WalkingSpeedTab from './modules/walking-speed-tab.vue';
import BatteryThresholdTab from './modules/battery-threshold-tab.vue';

defineOptions({ name: 'SettingsPage' });

const activeTab = ref('voice');
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :bordered="false" size="small" class="card-wrapper flex-1-hidden">
      <NTabs v-model:value="activeTab" type="line" animated>
        <NTabPane name="voice" tab="语音合成">
          <VoiceSynthesisTab />
        </NTabPane>
        <NTabPane name="face" tab="人脸识别TTS">
          <FaceRecognitionTab />
        </NTabPane>
        <NTabPane name="speed" tab="行走速度设置">
          <WalkingSpeedTab />
        </NTabPane>
        <NTabPane name="battery" tab="电量报警阈值">
          <BatteryThresholdTab />
        </NTabPane>
      </NTabs>
    </NCard>
  </div>
</template>

<style scoped></style>
