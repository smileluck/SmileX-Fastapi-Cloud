<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { fetchGetUsageSummary } from '@/service/api';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

defineOptions({
  name: 'AgentUsage'
});

const days = ref(7);
const onlyMine = ref(false);
const loading = ref(false);
const summary = ref<Api.Agent.UsageSummary | null>(null);

const { domRef, updateOptions } = useEcharts(() => ({
  tooltip: {
    trigger: 'axis' as const,
    axisPointer: {
      type: 'cross' as const
    }
  },
  legend: {
    data: [
      $t('page.agent.usage.totalTokens'),
      $t('page.agent.usage.promptTokens'),
      $t('page.agent.usage.completionTokens')
    ],
    top: '0'
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  xAxis: {
    type: 'category' as const,
    boundaryGap: false,
    data: [] as string[]
  },
  yAxis: {
    type: 'value' as const,
    name: $t('page.agent.usage.tokens')
  },
  series: [
    {
      name: $t('page.agent.usage.totalTokens'),
      type: 'line' as const,
      smooth: true,
      showSymbol: true,
      data: [] as number[]
    },
    {
      name: $t('page.agent.usage.promptTokens'),
      type: 'line' as const,
      smooth: true,
      data: [] as number[]
    },
    {
      name: $t('page.agent.usage.completionTokens'),
      type: 'line' as const,
      smooth: true,
      data: [] as number[]
    }
  ]
}));

const daysOptions = [
  { label: $t('page.agent.usage.days7'), value: 7 },
  { label: $t('page.agent.usage.days30'), value: 30 },
  { label: $t('page.agent.usage.days90'), value: 90 }
];

const statCards = ref<{ label: string; value: string }[]>([]);

async function loadUsage() {
  loading.value = true;
  const { error, data } = await fetchGetUsageSummary(days.value, onlyMine.value);
  loading.value = false;
  if (!error && data) {
    summary.value = data;
    updateOptions(opts => {
      opts.xAxis.data = data.trend.map(p => p.date.slice(5));
      opts.series[0].data = data.trend.map(p => p.total_tokens);
      opts.series[1].data = data.trend.map(p => p.prompt_tokens);
      opts.series[2].data = data.trend.map(p => p.completion_tokens);
      return opts;
    });
    statCards.value = [
      { label: $t('page.agent.usage.totalCalls'), value: String(data.total_calls) },
      { label: $t('page.agent.usage.totalTokens'), value: data.total_tokens.toLocaleString() },
      { label: $t('page.agent.usage.promptTokens'), value: data.total_prompt_tokens.toLocaleString() },
      { label: $t('page.agent.usage.completionTokens'), value: data.total_completion_tokens.toLocaleString() }
    ];
  }
}

watch([days, onlyMine], () => {
  loadUsage();
});

onMounted(() => {
  loadUsage();
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :bordered="false" size="small" class="card-wrapper">
      <div class="flex items-center justify-between gap-12px flex-wrap">
        <span class="text-16px font-500">{{ $t('page.agent.usage.title') }}</span>
        <div class="flex items-center gap-12px">
          <NCheckbox v-model:checked="onlyMine">{{ $t('page.agent.usage.onlyMine') }}</NCheckbox>
          <NRadioGroup v-model:value="days" size="small">
            <NRadioButton v-for="item in daysOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </div>
      </div>
    </NCard>
    <NCard :bordered="false" size="small" class="card-wrapper">
      <div class="grid grid-cols-2 gap-16px md:grid-cols-4">
        <div v-for="card in statCards" :key="card.label" class="rounded-8px bg-primary-50 px-16px py-12px dark:bg-dark">
          <div class="text-13px opacity-60">{{ card.label }}</div>
          <div class="text-24px font-600">{{ card.value }}</div>
        </div>
      </div>
    </NCard>
    <NCard :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <div ref="domRef" class="h-360px"></div>
    </NCard>
  </div>
</template>

<style scoped></style>
