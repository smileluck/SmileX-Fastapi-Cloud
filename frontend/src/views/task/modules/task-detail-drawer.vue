<script setup lang="ts">
import { ref, watch } from 'vue';
import { fetchGetExecutionDetail } from '@/service/api';

defineOptions({ name: 'TaskDetailDrawer' });

interface Props {
  execId: number | null;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', { default: false });

const loading = ref(false);
const detail = ref<Api.Task.TaskExecutionDetail | null>(null);

const taskTypeLabel: Record<string, string> = {
  patrol: '巡逻',
  broadcast: '播报'
};

const statusLabelMap: Record<string, string> = {
  pending: '等待中',
  running: '执行中',
  paused: '已暂停',
  completed: '已完成',
  failed: '已失败',
  cancelled: '已取消'
};

const actionLabel: Record<string, string> = {
  wave: '挥手',
  bow: '鞠躬',
  turn: '转身',
  wait: '停留等待',
  nod: '点头'
};

async function loadDetail() {
  if (!props.execId) return;
  loading.value = true;
  try {
    const { data, error } = await fetchGetExecutionDetail(props.execId);
    if (!error && data) {
      detail.value = data;
    }
  } finally {
    loading.value = false;
  }
}

watch(visible, () => {
  if (visible.value && props.execId) {
    loadDetail();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="560">
    <NDrawerContent title="执行详情" :native-scrollbar="false" closable>
      <NSpin v-if="loading" class="w-full" />
      <template v-else-if="detail">
        <NDescriptions bordered :column="2" label-placement="left" size="small">
          <NDescriptionsItem label="任务 ID">{{ detail.task_id }}</NDescriptionsItem>
          <NDescriptionsItem label="任务名称">{{ detail.task_name }}</NDescriptionsItem>
          <NDescriptionsItem label="任务类型">{{ taskTypeLabel[detail.task_type] || detail.task_type }}</NDescriptionsItem>
          <NDescriptionsItem label="执行状态">
            <NTag size="small" :type="detail.status === 'completed' ? 'success' : detail.status === 'failed' ? 'error' : 'default'">
              {{ statusLabelMap[detail.status] || detail.status }}
            </NTag>
          </NDescriptionsItem>
          <NDescriptionsItem label="执行机器人">{{ detail.robot_name || '-' }}</NDescriptionsItem>
          <NDescriptionsItem label="触发方式">{{ detail.triggered_by === 'manual' ? '手动' : '定时' }}</NDescriptionsItem>
          <NDescriptionsItem label="开始时间">{{ detail.started_at || '-' }}</NDescriptionsItem>
          <NDescriptionsItem label="结束时间">{{ detail.ended_at || '-' }}</NDescriptionsItem>
          <NDescriptionsItem label="进度" :span="2">
            <NProgress type="line" :percentage="detail.progress" />
          </NDescriptionsItem>
          <NDescriptionsItem v-if="detail.error_message" label="错误信息" :span="2">
            <NText type="error">{{ detail.error_message }}</NText>
          </NDescriptionsItem>
        </NDescriptions>

        <!-- 巡逻点位时间线 -->
        <template v-if="detail.task_type === 'patrol' && detail.points && detail.points.length > 0">
          <NDivider title-placement="left">巡逻点位</NDivider>
          <NTimeline>
            <NTimelineItem
              v-for="(point, index) in detail.points"
              :key="point.id"
              :type="index < (detail.progress / 100) * detail.points.length ? 'success' : 'default'"
              :title="`点位 ${index + 1}: ${point.point_name || '-'}`"
            >
              <NText depth="3">
                动作: {{ actionLabel[point.action] || point.action }}
              </NText>
              <br v-if="point.voice_text" />
              <NText v-if="point.voice_text" depth="3">
                语音: {{ point.voice_text }}
              </NText>
            </NTimelineItem>
          </NTimeline>
        </template>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
