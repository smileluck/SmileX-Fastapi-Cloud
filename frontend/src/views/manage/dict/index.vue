<script setup lang="tsx">
import { reactive, ref, watch } from 'vue';
import { NButton, NCard, NDataTable, NEmpty, NPopconfirm, NSpin, NTabPane, NTabs, NTag, useMessage } from 'naive-ui';
import { enableStatusRecord } from '@/constants/business';
import { fetchDeleteDict, fetchDeleteDictItem, fetchGetDictItemList, fetchGetDictList } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { booleanToEnableStatus } from '@/utils/status';
import { $t } from '@/locales';
import DictOperateDrawer from './modules/dict-operate-drawer.vue';
import DictItemOperateDrawer from './modules/dict-item-operate-drawer.vue';
import DictSearch from './modules/dict-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

/** 字典搜索参数 */
const dictSearchParams: Api.SystemManage.DictSearchParams = reactive({
  page: 1,
  page_size: 10,
  name: null,
  code: null,
  status: null,
  is_system: null
});

/** 当前选中的字典 */
const selectedDict = ref<Api.SystemManage.Dict | null>(null);
const activeTab = ref<'dict' | 'dictItem'>('dict');

/** 字典项搜索参数 */
const dictItemSearchParams: Api.SystemManage.DictItemSearchParams = reactive({
  page: 1,
  page_size: 10,
  dict_id: null,
  label: null,
  value: null,
  status: null
});

/** 字典项数据是否已加载（用于控制首次加载） */
const dictItemDataLoaded = ref(false);

/** 加载字典项数据（仅当已选择字典时执行） */
async function loadDictItemData() {
  if (!selectedDict.value) {
    return;
  }

  try {
    await getDictItemDataByPage();
    dictItemDataLoaded.value = true;
  } catch (error) {
    console.error('加载字典项数据失败:', error);
    message.error($t('common.loadDataFailed'));
  }
}

/** 监听选中字典变化，重新加载字典项数据 */
watch(
  () => selectedDict.value,
  async newDict => {
    if (newDict) {
      dictItemSearchParams.dict_id = newDict.id;
      dictItemSearchParams.page = 1;
      dictItemDataLoaded.value = false;
      await loadDictItemData();
    } else {
      dictItemSearchParams.dict_id = null;
      dictItemDataLoaded.value = false;
    }
  }
);

/** 字典表格 */
const {
  columns: dictColumns,
  columnChecks: dictColumnChecks,
  data: dictData,
  getData: getDictData,
  getDataByPage: getDictDataByPage,
  loading: dictLoading,
  mobilePagination: dictMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetDictList(dictSearchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((dict: Api.SystemManage.Dict) => ({
      ...dict,
      status: booleanToEnableStatus(dict.status)
    }));
    return result;
  },
  onPaginationParamsChange: params => {
    dictSearchParams.page = params.page;
    dictSearchParams.page_size = params.pageSize;
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
      key: 'name',
      title: $t('page.manage.dict.dictName'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'code',
      title: $t('page.manage.dict.dictCode'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'description',
      title: $t('page.manage.dict.dictDesc'),
      align: 'center',
      minWidth: 200
    },
    {
      key: 'status',
      title: $t('page.manage.dict.dictStatus'),
      align: 'center',
      width: 100,
      render: (row: any) => {
        const status = row.status as Api.Common.EnableStatus;
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = $t(enableStatusRecord[status]);
        return <NTag type={tagMap[status]}>{label}</NTag>;
      }
    },
    {
      key: 'is_system',
      title: $t('page.manage.dict.isSystem'),
      align: 'center',
      width: 100,
      render: row => {
        const isSystem = row.is_system === '1';
        return (
          <NTag type={isSystem ? 'info' : 'default'}>
            {isSystem ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no')}
          </NTag>
        );
      }
    },
    {
      key: 'sort',
      title: $t('page.manage.dict.sort'),
      align: 'center',
      width: 80
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 240,
      render: row => {
        return (
          <div class="flex flex-wrap justify-center gap-8px">
            <NButton type="primary" ghost size="small" onClick={() => handleSelectDict(row)}>
              {$t('page.manage.dict.itemManage')}
            </NButton>
            {hasAuth('sys:dict:edit') && (
              <NButton type="info" ghost size="small" onClick={() => editDict(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {row.is_system !== '1' && hasAuth('sys:dict:delete') && (
              <NPopconfirm onPositiveClick={() => handleDeleteDict(row.id)}>
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

/** 字典操作 */
const {
  drawerVisible: dictDrawerVisible,
  operateType: dictOperateType,
  editingData: editingDictData,
  handleAdd: handleAddDict,
  handleEdit: handleEditDict,
  checkedRowKeys: checkedDictRowKeys,
  onBatchDeleted: onDictBatchDeleted,
  onDeleted: onDictDeleted
} = useTableOperate(dictData, 'id', getDictData);

/** 字典项表格 */
const {
  columns: dictItemColumns,
  columnChecks: dictItemColumnChecks,
  data: dictItemData,
  getData: getDictItemData,
  getDataByPage: getDictItemDataByPage,
  loading: dictItemLoading,
  mobilePagination: dictItemMobilePagination
} = useNaivePaginatedTable({
  api: () => {
    // 只有在选中字典后才调用 API，避免初始化时请求空数据
    if (!dictItemSearchParams.dict_id) {
      // 直接返回一个空的响应，让 defaultTransform 处理
      return Promise.resolve({
        data: { records: [], page: 1, page_size: 10, total: 0, total_pages: 0 }
      } as any);
    }
    return fetchGetDictItemList(dictItemSearchParams);
  },
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((item: any) => ({
      ...item,
      status: booleanToEnableStatus(item.status)
    }));
    return result;
  },
  onPaginationParamsChange: params => {
    dictItemSearchParams.page = params.page;
    dictItemSearchParams.page_size = params.pageSize;
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
      key: 'value',
      title: $t('page.manage.dict.itemValue'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'label',
      title: $t('page.manage.dict.itemLabel'),
      align: 'center',
      minWidth: 120
    },
    {
      key: 'description',
      title: $t('page.manage.dict.itemDesc'),
      align: 'center',
      minWidth: 200
    },
    {
      key: 'status',
      title: $t('page.manage.dict.itemStatus'),
      align: 'center',
      width: 100,
      render: (row: any) => {
        const status = row.status as Api.Common.EnableStatus;
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = $t(enableStatusRecord[status]);
        return <NTag type={tagMap[status]}>{label}</NTag>;
      }
    },
    {
      key: 'sort',
      title: $t('page.manage.dict.sort'),
      align: 'center',
      width: 80
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      minWidth: 180,
      render: (row: any) => {
        return (
          <div class="flex flex-wrap justify-center gap-8px">
            {hasAuth('sys:dict:edit') && (
              <NButton type="info" ghost size="small" onClick={() => editDictItem(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('sys:dict:delete') && (
              <NPopconfirm onPositiveClick={() => handleDeleteDictItem(row.id)}>
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

/** 字典项操作 */
const {
  drawerVisible: dictItemDrawerVisible,
  operateType: dictItemOperateType,
  editingData: editingDictItemData,
  handleAdd: handleAddDictItem,
  handleEdit: handleEditDictItem,
  checkedRowKeys: checkedDictItemRowKeys,
  onBatchDeleted: onDictItemBatchDeleted,
  onDeleted: onDictItemDeleted
} = useTableOperate(dictItemData as any, 'id', getDictItemData);

/** 选中字典 */
function handleSelectDict(row: Api.SystemManage.Dict) {
  selectedDict.value = row;
  activeTab.value = 'dictItem';
}

/** 编辑字典 */
function editDict(id: number) {
  handleEditDict(id);
}

/** 删除字典 */
async function handleDeleteDict(id: number) {
  try {
    await fetchDeleteDict(id);
    onDictDeleted();
  } catch (error) {
    console.error('删除字典失败:', error);
  }
}

/** 编辑字典项 */
function editDictItem(id: number) {
  handleEditDictItem(id as number);
}

/** 删除字典项 */
async function handleDeleteDictItem(id: number) {
  try {
    await fetchDeleteDictItem(id);
    onDictItemDeleted();
  } catch (error) {
    console.error('删除字典项失败:', error);
  }
}

/** 批量删除字典 */
async function handleBatchDeleteDict() {
  if (checkedDictRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  try {
    for (const id of checkedDictRowKeys.value) {
      await fetchDeleteDict(Number(id));
    }
    onDictBatchDeleted();
  } catch (error) {
    message.error($t('common.deleteFailed'));
    console.error('Batch delete dicts failed:', error);
  }
}

/** 批量删除字典项 */
async function handleBatchDeleteDictItem() {
  if (checkedDictItemRowKeys.value.length === 0) {
    message.warning($t('common.selectAtLeastOne'));
    return;
  }
  try {
    for (const id of checkedDictItemRowKeys.value) {
      await fetchDeleteDictItem(Number(id));
    }
    onDictItemBatchDeleted();
  } catch (error) {
    message.error($t('common.deleteFailed'));
    console.error('Batch delete dict items failed:', error);
  }
}

watch(selectedDict, value => {
  if (!value && activeTab.value === 'dictItem') {
    activeTab.value = 'dict';
  }
});

watch(activeTab, tab => {
  if (tab === 'dictItem') {
    checkedDictItemRowKeys.value = [];
  }
});
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NTabs v-model:value="activeTab" type="line" class="flex-1-hidden">
      <NTabPane name="dict" :tab="$t('page.manage.dict.dictManage')" class="flex-1-hidden">
        <DictSearch v-model:model="dictSearchParams" @search="getDictDataByPage" />
        <NCard :title="$t('page.manage.dict.title')" :bordered="false" size="small" class="flex-1-hidden card-wrapper">
          <template #header-extra>
            <TableHeaderOperation
              v-model:columns="dictColumnChecks"
              :disabled-delete="checkedDictRowKeys.length === 0"
              :loading="dictLoading"
              add-auth="sys:dict:add"
              delete-auth="sys:dict:delete"
              @add="handleAddDict"
              @delete="handleBatchDeleteDict"
              @refresh="getDictData"
            />
          </template>
          <NDataTable
            v-model:checked-row-keys="checkedDictRowKeys"
            :columns="dictColumns as any"
            :data="dictData"
            size="small"
            :flex-height="!appStore.isMobile"
            :scroll-x="962"
            :loading="dictLoading"
            remote
            :row-key="row => row.id"
            :pagination="dictMobilePagination"
            class="sm:h-full"
          />
          <DictOperateDrawer
            v-model:visible="dictDrawerVisible"
            :operate-type="dictOperateType"
            :row-data="editingDictData"
            @submitted="getDictDataByPage"
          />
        </NCard>
      </NTabPane>
      <NTabPane
        name="dictItem"
        :tab="$t('page.manage.dict.itemManage')"
        :disabled="activeTab === 'dict' || !selectedDict"
        class="flex-1-hidden"
      >
        <div class="mb-16px">
          <NButton
            type="info"
            ghost
            size="small"
            @click="
              activeTab = 'dict';
              selectedDict = null;
              dictItemSearchParams.dict_id = null;
            "
          >
            {{ $t('common.back') }}
          </NButton>
          <span class="ml-8px">
            {{ selectedDict ? `${$t('page.manage.dict.dictName')}: ${selectedDict.name}` : '' }}
          </span>
        </div>
        <NCard
          :title="$t('page.manage.dict.itemTitle')"
          :bordered="false"
          size="small"
          class="flex-1-hidden card-wrapper"
        >
          <template #header-extra>
            <TableHeaderOperation
              v-model:columns="dictItemColumnChecks"
              :disabled-delete="checkedDictItemRowKeys.length === 0"
              :loading="dictItemLoading"
              :disabled-add="!selectedDict"
              add-auth="sys:dict:add"
              delete-auth="sys:dict:delete"
              @add="handleAddDictItem"
              @delete="handleBatchDeleteDictItem"
              @refresh="loadDictItemData"
            />
          </template>
          <NSpin :show="dictItemLoading && !dictItemDataLoaded">
            <NEmpty
              v-if="!selectedDict || (!dictItemLoading && dictItemDataLoaded && dictItemData.length === 0)"
              :description="$t(selectedDict ? 'common.noData' : 'page.manage.dict.pleaseSelectDict')"
              class="h-200px"
            />
            <NDataTable
              v-else
              v-model:checked-row-keys="checkedDictItemRowKeys"
              :columns="dictItemColumns as any"
              :data="dictItemData as any"
              size="small"
              :flex-height="!appStore.isMobile"
              :scroll-x="962"
              remote
              :row-key="row => row.id"
              :pagination="dictItemMobilePagination"
              class="sm:h-full"
            />
          </NSpin>
          <DictItemOperateDrawer
            v-model:visible="dictItemDrawerVisible"
            :operate-type="dictItemOperateType"
            :row-data="(editingDictItemData as any)"
            :dict-id="selectedDict?.id"
            @submitted="loadDictItemData"
          />
        </NCard>
      </NTabPane>
    </NTabs>
  </div>
</template>

<style scoped>
:deep(.n-tabs) {
  display: flex;
  min-height: 0;
  flex-direction: column;
}

:deep(.n-tabs-pane-wrapper) {
  min-height: 0;
  flex: 1;
}

:deep(.n-tab-pane) {
  display: flex;
  min-height: 0;
  flex-direction: column;
  gap: 16px;
}
</style>
