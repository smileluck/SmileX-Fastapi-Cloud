<script setup lang="ts">
interface Props {
  streamUrl: string | null;
}

defineProps<Props>();
</script>

<template>
  <NCard :bordered="true" size="small">
    <template #header>视频监控</template>
    <div class="flex h-400px items-center justify-center rounded bg-gray-100">
      <NEmpty description="暂无视频源，请配置视频流地址">
        <template #icon>
          <icon-ic-round-videocam-off class="text-48px text-gray-300" />
        </template>
      </NEmpty>
    </div>
  </NCard>
</template>

<style scoped></style>
