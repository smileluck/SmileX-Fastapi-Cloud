<script setup lang="ts">
import { ref } from 'vue';
import { useRobotMonitor } from './composables/useRobotMonitor';
import RobotStatusCard from './modules/robot-status-card.vue';
import PositionMapPanel from './modules/position-map-panel.vue';
import AlertPanel from './modules/alert-panel.vue';
import VideoPlayer from './modules/video-player.vue';

defineOptions({ name: 'OperationMonitorPage' });

const activeTab = ref('realtime');

const {
  robotList,
  selectedRobotId,
  selectedRobot,
  latestStatus,
  parsedLocation,
  loading,
  selectRobot
} = useRobotMonitor();
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NSpin :show="loading">
      <NSpace vertical :size="16">
        <!-- 机器人选择 + 状态卡片 -->
        <RobotStatusCard
          :robot-list="robotList"
          :selected-robot="selectedRobot"
          :status-record="latestStatus"
          @select="selectRobot"
        />

        <!-- Tab 切换 -->
        <NCard :bordered="false" size="small" class="card-wrapper flex-1-hidden">
          <NTabs v-model:value="activeTab" type="line" animated>
            <NTabPane name="realtime" tab="实时">
              <NGrid :x-gap="16" :y-gap="16" responsive="screen" item-responsive>
                <NGi span="24 m:16">
                  <NCard :bordered="true" size="small">
                    <template #header>
                      <NSpace align="center" :size="8">
                        <span>实时位置</span>
                        <NTag v-if="selectedRobot?.status === 'online'" type="success" size="small" round>
                          直播中
                        </NTag>
                      </NSpace>
                    </template>
                    <PositionMapPanel
                      :map-id="selectedRobot?.map_id ?? null"
                      :location="parsedLocation"
                      :robot-name="selectedRobot?.name ?? ''"
                    />
                  </NCard>
                </NGi>
                <NGi span="24 m:8">
                  <AlertPanel :robot-id="selectedRobotId" />
                </NGi>
              </NGrid>
            </NTabPane>
            <NTabPane name="video" tab="视频监控">
              <VideoPlayer :stream-url="null" />
            </NTabPane>
          </NTabs>
        </NCard>
      </NSpace>
    </NSpin>
  </div>
</template>

<style scoped></style>
