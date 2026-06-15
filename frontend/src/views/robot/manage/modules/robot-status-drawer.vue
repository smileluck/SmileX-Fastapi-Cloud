<script setup lang="tsx">
import { computed, reactive, ref, watch } from 'vue';
import { NDataTable, NProgress, NTag } from 'naive-ui';
import { $t } from '@/locales';
import { fetchGetRobotStatusRecords, fetchGetLatestRobotStatus } from '@/service/api';
import { defaultTransform } from '@/hooks/common/table';

defineOptions({
  name: 'RobotStatusDrawer'
});

interface Props {
  robotId?: number | null;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', {
  default: false
});

/** 最新状态 */
const latestStatus = ref<Api.Robot.RobotStatusRecord | null>(null);
const loadingLatest = ref(false);

/** 状态记录分页参数 */
const paginationParams = reactive({
  page: 1,
  page_size: 10
});

/** 状态记录数据 */
const statusData = ref<Api.Robot.RobotStatusRecord[]>([]);
const statusTotal = ref(0);
const statusLoading = ref(false);

/** 电池颜色 */
function getBatteryColor(battery: number): string {
  if (battery >= 60) return '#18a058';
  if (battery >= 30) return '#f0a020';
  return '#d03050';
}

/** 状态记录列 */
const statusColumns = computed(() => [
  {
    key: 'index',
    title: $t('common.index'),
    align: 'center' as const,
    width: 64,
    render: (_: any, index: number) => (paginationParams.page - 1) * paginationParams.page_size + index + 1
  },
  {
    key: 'battery',
    title: '电量',
    align: 'center' as const,
    width: 140,
    render: (row: Api.Robot.RobotStatusRecord) => (
      <NProgress
        type="line"
        percentage={row.battery}
        color={getBatteryColor(row.battery)}
        indicatorPlacement="inside"
      />
    )
  },
  {
    key: 'signal',
    title: '信号强度',
    align: 'center' as const,
    width: 100,
    render: (row: Api.Robot.RobotStatusRecord) => <span>{row.signal}%</span>
  },
  {
    key: 'speed',
    title: '速度',
    align: 'center' as const,
    width: 100,
    render: (row: Api.Robot.RobotStatusRecord) => <span>{row.speed} m/s</span>
  },
  {
    key: 'location',
    title: '位置',
    align: 'center' as const,
    minWidth: 140,
    ellipsis: { tooltip: true },
    render: (row: Api.Robot.RobotStatusRecord) => <span>{row.location || '-'}</span>
  },
  {
    key: 'created_at',
    title: '记录时间',
    align: 'center' as const,
    width: 180,
    render: (row: Api.Robot.RobotStatusRecord) => <span>{row.created_at || '-'}</span>
  }
]);

/** 分页配置 */
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showSizePicker: true,
  pageSizes: [10, 15, 20, 25, 30],
  prefix: (page: { itemCount: number }) => $t('datatable.itemCount', { total: page.itemCount }),
  onUpdatePage: (page: number) => {
    pagination.page = page;
    paginationParams.page = page;
  },
  onUpdatePageSize: (pageSize: number) => {
    pagination.pageSize = pageSize;
    pagination.page = 1;
    paginationParams.page = 1;
    paginationParams.page_size = pageSize;
  }
});

/** 加载最新状态 */
async function loadLatestStatus() {
  if (!props.robotId) return;
  loadingLatest.value = true;
  try {
    const { data, error } = await fetchGetLatestRobotStatus(props.robotId);
    if (!error && data) {
      latestStatus.value = data as unknown as Api.Robot.RobotStatusRecord;
    } else {
      latestStatus.value = null;
    }
  } catch {
    latestStatus.value = null;
  } finally {
    loadingLatest.value = false;
  }
}

/** 加载状态记录列表 */
async function loadStatusRecords() {
  if (!props.robotId) return;
  statusLoading.value = true;
  try {
    const response = await fetchGetRobotStatusRecords(props.robotId, paginationParams);
    const result = defaultTransform(response);
    statusData.value = result.data as Api.Robot.RobotStatusRecord[];
    statusTotal.value = result.total;
    pagination.itemCount = result.total;
  } catch {
    statusData.value = [];
    pagination.itemCount = 0;
  } finally {
    statusLoading.value = false;
  }
}

function closeDrawer() {
  visible.value = false;
}

watch(visible, () => {
  if (visible.value && props.robotId) {
    paginationParams.page = 1;
    pagination.page = 1;
    loadLatestStatus();
    loadStatusRecords();
  }
});

watch(
  () => paginationParams.page,
  () => {
    if (visible.value) {
      loadStatusRecords();
    }
  }
);

watch(
  () => paginationParams.page_size,
  () => {
    if (visible.value) {
      loadStatusRecords();
    }
  }
);
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="720">
    <NDrawerContent title="机器人状态" :native-scrollbar="false" closable>
      <!-- 最新状态卡片 -->
      <NCard
        v-if="latestStatus"
        title="最新状态"
        size="small"
        :bordered="true"
        class="mb-16px"
      >
        <NDescriptions label-placement="left" :column="3" bordered size="small">
          <NDescriptionsItem label="电量">
            <NProgress
              type="line"
              :percentage="latestStatus.battery"
              :color="getBatteryColor(latestStatus.battery)"
              indicator-placement="inside"
            />
          </NDescriptionsItem>
          <NDescriptionsItem label="信号强度">
            {{ latestStatus.signal }}%
          </NDescriptionsItem>
          <NDescriptionsItem label="速度">
            {{ latestStatus.speed }} m/s
          </NDescriptionsItem>
          <NDescriptionsItem label="位置" :span="2">
            {{ latestStatus.location || '-' }}
          </NDescriptionsItem>
          <NDescriptionsItem label="更新时间">
            {{ latestStatus.created_at || '-' }}
          </NDescriptionsItem>
        </NDescriptions>
      </NCard>

      <!-- 状态记录表格 -->
      <NCard title="状态记录" size="small" :bordered="true">
        <NDataTable
          :columns="statusColumns"
          :data="statusData"
          size="small"
          :loading="statusLoading"
          remote
          :row-key="(row: Api.Robot.RobotStatusRecord) => row.id"
          :pagination="pagination"
          :scroll-x="800"
        />
      </NCard>

      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
