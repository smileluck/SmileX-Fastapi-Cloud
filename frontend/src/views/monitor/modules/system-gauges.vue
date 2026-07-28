<script setup lang="ts">
import { computed, watch } from 'vue';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

interface Props {
  metrics?: Api.Monitor.SystemMetrics | null;
}

const props = defineProps<Props>();

function getCompactGaugeOption(title: string, value: number, color: string) {
  return {
    series: [
      {
        type: 'gauge' as const,
        startAngle: 200,
        endAngle: -20,
        min: 0,
        max: 100,
        splitNumber: 5,
        itemStyle: { color },
        progress: { show: true, width: 8 },
        pointer: { show: true, width: 3 },
        axisLine: { lineStyle: { width: 8 } },
        axisTick: {
          distance: -14,
          splitNumber: 3,
          lineStyle: { width: 1, color: '#999' }
        },
        splitLine: {
          distance: -16,
          length: 6,
          lineStyle: { width: 1, color: '#999' }
        },
        axisLabel: { distance: -10, color: '#999', fontSize: 9 },
        anchor: {
          show: true,
          size: 12,
          itemStyle: { borderWidth: 2 }
        },
        title: { show: true, offsetCenter: [0, '70%'], fontSize: 12 },
        detail: {
          valueAnimation: true,
          fontSize: 16,
          offsetCenter: [0, '50%'],
          formatter: '{value}%'
        },
        data: [{ value: Math.round(value), name: title }]
      }
    ]
  };
}

const { domRef: cpuDomRef, updateOptions: updateCpu } = useEcharts(() =>
  getCompactGaugeOption($t('page.monitor.cpuUsage'), 0, '#5470c6')
);
const { domRef: memoryDomRef, updateOptions: updateMemory } = useEcharts(() =>
  getCompactGaugeOption($t('page.monitor.memoryUsage'), 0, '#91cc75')
);
const { domRef: diskDomRef, updateOptions: updateDisk } = useEcharts(() =>
  getCompactGaugeOption($t('page.monitor.diskUsage'), 0, '#fac858')
);

watch(
  () => props.metrics?.cpu_percent,
  val => {
    if (val != null)
      updateCpu(opts => {
        opts.series[0].data[0].value = Math.round(val);
        return opts;
      });
  }
);

watch(
  () => props.metrics?.memory?.percent,
  val => {
    if (val != null)
      updateMemory(opts => {
        opts.series[0].data[0].value = Math.round(val);
        return opts;
      });
  }
);

watch(
  () => props.metrics?.disk?.percent,
  val => {
    if (val != null)
      updateDisk(opts => {
        opts.series[0].data[0].value = Math.round(val);
        return opts;
      });
  }
);

const cpuCores = computed(() => props.metrics?.cpu_percent_per_core ?? []);

const uptime = computed(() => {
  const bootTime = props.metrics?.boot_time;
  if (!bootTime) return '-';
  const boot = new Date(bootTime);
  const now = new Date();
  const diff = Math.floor((now.getTime() - boot.getTime()) / 1000);
  const days = Math.floor(diff / 86400);
  const hours = Math.floor((diff % 86400) / 3600);
  const minutes = Math.floor((diff % 3600) / 60);
  return `${days}${$t('page.monitor.day')} ${hours}${$t('page.monitor.hour')} ${minutes}${$t('page.monitor.minute')}`;
});

function getCoreColor(val: number): string {
  if (val >= 80) return '#e88080';
  if (val >= 60) return '#f0c060';
  return '#91cc75';
}
</script>

<template>
  <NGrid cols="1 s:2" responsive="screen" :x-gap="16" :y-gap="16">
    <!-- CPU -->
    <NGi>
      <NCard size="small" :title="$t('page.monitor.cpuUsage')">
        <div class="card-body">
          <div class="h-full flex items-center gap-16px">
            <div class="grid grid-cols-2 flex-1 gap-x-12px gap-y-6px">
              <div v-for="(val, idx) in cpuCores" :key="idx" class="flex items-center gap-6px">
                <span class="w-42px shrink-0 text-12px text-gray">C{{ idx }}</span>
                <div class="h-8px flex-1 overflow-hidden rounded-full" style="background: var(--n-border-color)">
                  <div
                    class="h-full rounded-full transition-all duration-500"
                    :style="{ width: `${Math.max(val, 2)}%`, backgroundColor: getCoreColor(val) }"
                  ></div>
                </div>
                <span class="w-32px shrink-0 text-right text-12px">{{ Math.round(val) }}%</span>
              </div>
            </div>
            <div ref="cpuDomRef" class="h-200px w-200px shrink-0"></div>
          </div>
        </div>
      </NCard>
    </NGi>

    <!-- Memory -->
    <NGi>
      <NCard size="small" :title="$t('page.monitor.memoryUsage')">
        <div class="card-body">
          <div class="h-full flex items-center gap-16px">
            <div class="flex-1">
              <NDescriptions label-placement="left" :column="1" bordered size="small">
                <NDescriptionsItem label="Total (MB)">
                  {{ (metrics?.memory?.total_mb ?? 0).toLocaleString() }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Used (MB)">
                  {{ (metrics?.memory?.used_mb ?? 0).toLocaleString() }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Free (MB)">
                  {{ (metrics?.memory?.free_mb ?? 0).toLocaleString() }}
                </NDescriptionsItem>
              </NDescriptions>
            </div>
            <div ref="memoryDomRef" class="h-200px w-200px shrink-0"></div>
          </div>
        </div>
      </NCard>
    </NGi>

    <!-- System Info -->
    <NGi>
      <NCard size="small" :title="$t('page.monitor.systemInfo')">
        <div class="card-body flex flex-col justify-center">
          <NDescriptions label-placement="left" :column="1" bordered size="small">
            <NDescriptionsItem :label="$t('page.monitor.osName')">
              {{ metrics?.os_name ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.cpuCount')">
              {{ metrics?.cpu_count ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.pythonVersion')">
              {{ metrics?.python_version ?? '-' }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.uptime')">
              {{ uptime }}
            </NDescriptionsItem>
            <NDescriptionsItem :label="$t('page.monitor.processCount')">
              {{ metrics?.process_count ?? '-' }}
            </NDescriptionsItem>
          </NDescriptions>
        </div>
      </NCard>
    </NGi>

    <!-- Disk -->
    <NGi>
      <NCard size="small" :title="$t('page.monitor.diskUsage')">
        <div class="card-body">
          <div class="h-full flex items-center gap-16px">
            <div class="flex-1">
              <NDescriptions label-placement="left" :column="1" bordered size="small">
                <NDescriptionsItem label="Total (GB)">
                  {{ (metrics?.disk?.total ?? 0).toLocaleString() }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Used (GB)">
                  {{ (metrics?.disk?.used ?? 0).toLocaleString() }}
                </NDescriptionsItem>
                <NDescriptionsItem label="Free (GB)">
                  {{ (metrics?.disk?.free ?? 0).toLocaleString() }}
                </NDescriptionsItem>
              </NDescriptions>
            </div>
            <div ref="diskDomRef" class="h-200px w-200px shrink-0"></div>
          </div>
        </div>
      </NCard>
    </NGi>
  </NGrid>
</template>

<style scoped>
.card-body {
  height: 280px;
  overflow-y: auto;
}
</style>
