<script setup lang="ts">
import { ref } from 'vue';
import TaskListTab from './modules/task-list-tab.vue';
import TaskExecutionTab from './modules/task-execution-tab.vue';
import TaskHistoryTab from './modules/task-history-tab.vue';

defineOptions({ name: 'TaskPage' });

const activeTab = ref('list');
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NTabs v-model:value="activeTab" type="line" animated class="flex-1-hidden">
      <NTabPane name="list" tab="任务列表" class="flex-1-hidden">
        <TaskListTab />
      </NTabPane>
      <NTabPane name="execution" tab="执行列表" class="flex-1-hidden">
        <TaskExecutionTab />
      </NTabPane>
      <NTabPane name="history" tab="历史任务" class="flex-1-hidden">
        <TaskHistoryTab />
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
:deep(.n-tabs) {
  display: flex;
  flex-direction: column;
}

:deep(.n-tabs > .n-tab-pane) {
  height: 100%;
}

:deep(.n-tabs-pane-wrapper) {
  flex: 1 1 0;
  min-height: 0;
}

:deep(.n-tab-pane) {
  height: 100%;
}
</style>
