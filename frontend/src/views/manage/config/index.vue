<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import {
  fetchBatchDeleteConfig,
  fetchCreateConfig,
  fetchDeleteConfig,
  fetchGetConfigList,
  fetchResetConfigs,
  fetchUpdateConfig
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import ConfigOperateDrawer from './modules/config-operate-drawer.vue';
import ConfigSearch from './modules/config-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

/** 配置搜索参数 */
const configSearchParams: Api.SystemManage.ConfigSearchParams = reactive({
  page: 1,
  page_size: 10,
  key: null,
  description: null,
  type: null,
  group: null,
  is_system: null
});

/** 配置类型选项 */
const configTypeOptions = [
  { label: $t('page.manage.config.type.string'), value: 'string' },
  { label: $t('page.manage.config.type.number'), value: 'number' },
  { label: $t('page.manage.config.type.boolean'), value: 'boolean' },
  { label: $t('page.manage.config.type.json'), value: 'json' },
  { label: $t('page.manage.config.type.array'), value: 'array' }
];

/** 配置分组选项 */
const configGroupOptions = [
  { label: $t('page.manage.config.group.system'), value: 'system' },
  { label: $t('page.manage.config.group.security'), value: 'security' },
  { label: $t('page.manage.config.group.log'), value: 'log' },
  { label: $t('page.manage.config.group.network'), value: 'network' },
  { label: $t('page.manage.config.group.storage'), value: 'storage' },
  { label: $t('page.manage.config.group.custom'), value: 'custom' }
];

/** 配置表格 */
const {
  columns: configColumns,
  columnChecks: configColumnChecks,
  data: configData,
  getData: getConfigData,
  getDataByPage: getConfigDataByPage,
  loading: configLoading,
  mobilePagination: configMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetConfigList(configSearchParams),
  transform: response => defaultTransform(response),
  onPaginationParamsChange: params => {
    configSearchParams.page = params.page;
    configSearchParams.page_size = params.pageSize;
  },
  columns: () => [
    {
      type: 'selection',
      align: 'center',
      width: 48
    },
    {
      key: 'index',
      title: $t('common.index'),
      align: 'center',
      width: 64,
      render: (_, index) => index + 1
    },
    {
      key: 'key',
      title: $t('page.manage.config.configKey'),
      align: 'center',
      minWidth: 150
    },
    {
      key: 'value',
      title: $t('page.manage.config.configValue'),
      align: 'center',
      minWidth: 150,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'description',
      title: $t('page.manage.config.configDesc'),
      align: 'center',
      minWidth: 200,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'type',
      title: $t('page.manage.config.configType'),
      align: 'center',
      width: 100,
      render: row => {
        const typeLabel = configTypeOptions.find(opt => opt.value === row.type)?.label || row.type;
        return <NTag type="info">{typeLabel}</NTag>;
      }
    },
    {
      key: 'group',
      title: $t('page.manage.config.configGroup'),
      align: 'center',
      width: 120,
      render: row => {
        const groupLabel = configGroupOptions.find(opt => opt.value === row.group)?.label || row.group;
        return <NTag type="default">{groupLabel}</NTag>;
      }
    },

    {
      key: 'is_system',
      title: $t('page.manage.config.isSystem'),
      align: 'center',
      width: 100,
      render: row => {
        return (
          <NTag type={row.is_system === '1' ? 'info' : 'default'}>
            {row.is_system === '1' ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no')}
          </NTag>
        );
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 200,
      fixed: 'right',
      render: row => {
        return (
          <div class="flex-center gap-8px">
            {hasAuth('sys:config:edit') && (
              <NButton type="primary" ghost size="small" onClick={() => editConfig(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {row.default_value && hasAuth('sys:config:edit') && (
              <NButton type="info" ghost size="small" onClick={() => handleResetConfig(row.id)}>
                {$t('page.manage.config.resetConfig')}
              </NButton>
            )}
            {row.is_system !== '1' && hasAuth('sys:config:delete') && (
              <NPopconfirm onPositiveClick={() => handleDeleteConfig(row.id)}>
                {{
                  default: () => $t('common.confirmDelete'),
                  trigger: () => (
                    <NButton type="error" ghost size="small">
                      {$t('common.delete')}
                    </NButton>
                  )
                }}
              </NPopconfirm>
            )}
          </div>
        );
      }
    }
  ]
});

/** 配置操作 */
const {
  drawerVisible: configDrawerVisible,
  operateType: configOperateType,
  editingData: editingConfigData,
  handleAdd: handleAddConfig,
  handleEdit: handleEditConfig,
  checkedRowKeys: checkedConfigRowKeys,
  onBatchDeleted: onConfigBatchDeleted,
  onDeleted: onConfigDeleted
} = useTableOperate(configData, 'id', getConfigData);

/** 编辑配置 */
function editConfig(id: number) {
  handleEditConfig(id);
}

/** 删除配置 */
async function handleDeleteConfig(id: number) {
  try {
    await fetchDeleteConfig(id);
    onConfigDeleted();
  } catch (error) {
    console.error('删除配置失败:', error);
  }
}

/** 重置配置 */
async function handleResetConfig(id: number) {
  try {
    await fetchResetConfigs({ ids: [id.toString()] });
    message.success($t('common.updateSuccess'));
    getConfigDataByPage();
  } catch (error) {
    console.error('重置配置失败:', error);
  }
}

/** 批量删除配置 */
async function handleBatchDeleteConfig() {
  if (checkedConfigRowKeys.value.length === 0) {
    return;
  }
  try {
    await fetchBatchDeleteConfig(checkedConfigRowKeys.value.map(Number));
    onConfigBatchDeleted();
  } catch (error) {
    console.error('批量删除配置失败:', error);
  }
}

/** 批量重置配置 */
async function handleBatchResetConfig() {
  if (checkedConfigRowKeys.value.length === 0) {
    message.warning('请选择要重置的配置');
    return;
  }
  try {
    await fetchResetConfigs({ ids: checkedConfigRowKeys.value as string[] });
    message.success($t('common.updateSuccess'));
    getConfigDataByPage();
  } catch (error) {
    console.error('批量重置配置失败:', error);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <ConfigSearch v-model:model="configSearchParams" @search="getConfigDataByPage" />
    <NCard :title="$t('page.manage.config.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="configColumnChecks"
          :disabled-delete="checkedConfigRowKeys.length === 0"
          :loading="configLoading"
          @add="handleAddConfig"
          @delete="handleBatchDeleteConfig"
          @refresh="getConfigData"
        >
          <template #default>
            <NButton v-if="hasAuth('sys:config:add')" size="small" ghost type="primary" @click="handleAddConfig">
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </NButton>
            <NPopconfirm v-if="hasAuth('sys:config:delete')" @positive-click="handleBatchDeleteConfig">
              <template #trigger>
                <NButton size="small" ghost type="error" :disabled="checkedConfigRowKeys.length === 0">
                  <template #icon>
                    <icon-ic-round-delete class="text-icon" />
                  </template>
                  {{ $t('common.batchDelete') }}
                </NButton>
              </template>
              {{ $t('common.confirmDelete') }}
            </NPopconfirm>
            <NButton
              v-if="hasAuth('sys:config:edit')"
              type="info"
              ghost
              size="small"
              :disabled="checkedConfigRowKeys.length === 0"
              @click="handleBatchResetConfig"
            >
              {{ $t('page.manage.config.resetConfig') }}
            </NButton>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedConfigRowKeys"
        :columns="configColumns"
        :data="configData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1600"
        :loading="configLoading"
        remote
        :row-key="row => row.id"
        :pagination="configMobilePagination"
        class="sm:h-full"
      />
      <ConfigOperateDrawer
        v-model:visible="configDrawerVisible"
        :operate-type="configOperateType"
        :row-data="editingConfigData"
        @submitted="getConfigDataByPage"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
