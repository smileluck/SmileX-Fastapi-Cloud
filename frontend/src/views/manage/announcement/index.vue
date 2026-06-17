<script setup lang="tsx">
import { reactive, ref } from 'vue';
import { NButton, NCard, NDataTable, NPopconfirm, NTag, useMessage } from 'naive-ui';
import {
  fetchGetNoticeList,
  fetchDeleteNotice,
  fetchBatchDeleteNotice,
  fetchPublishNotice
} from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { defaultTransform, useNaivePaginatedTable, useTableOperate } from '@/hooks/common/table';
import { useAuth } from '@/hooks/business/auth';
import { $t } from '@/locales';
import { booleanToEnableStatus } from '@/utils/status';
import NoticeOperateDrawer from './modules/notice-operate-drawer.vue';
import NoticeSearch from './modules/notice-search.vue';

const appStore = useAppStore();
const message = useMessage();
const { hasAuth } = useAuth();

/** 通知搜索参数 */
const searchParams: Api.Notification.NoticeSearchParams = reactive({
  page: 1,
  page_size: 10,
  title: null,
  type: null,
  target_type: null,
  status: null,
  priority: null
});

/** 优先级选项 */
const priorityOptions = [
  { label: $t('notification.priority.low'), value: 'low' },
  { label: $t('notification.priority.normal'), value: 'normal' },
  { label: $t('notification.priority.high'), value: 'high' },
  { label: $t('notification.priority.urgent'), value: 'urgent' }
];

/** 类型选项 */
const typeOptions = [
  { label: $t('page.manage.announcement.type.announcement'), value: 'announcement' },
  { label: $t('page.manage.announcement.type.system'), value: 'system' },
  { label: $t('page.manage.announcement.type.operation'), value: 'operation' },
  { label: $t('page.manage.announcement.type.approval'), value: 'approval' }
];

/** 推送范围选项 */
const targetTypeOptions = [
  { label: $t('page.manage.announcement.targetType.all'), value: 'all' },
  { label: $t('page.manage.announcement.targetType.role'), value: 'role' },
  { label: $t('page.manage.announcement.targetType.user'), value: 'user' }
];

/** 通知表格 */
const {
  columns: noticeColumns,
  columnChecks: noticeColumnChecks,
  data: noticeData,
  getData: getNoticeData,
  getDataByPage: getNoticeDataByPage,
  loading: noticeLoading,
  mobilePagination: noticeMobilePagination
} = useNaivePaginatedTable({
  api: () => fetchGetNoticeList(searchParams),
  transform: response => {
    const result = defaultTransform(response);
    result.data = result.data.map((notice: any) => ({
      ...notice,
      status: booleanToEnableStatus(notice.status)
    }));
    return result;
  },
  onPaginationParamsChange: params => {
    searchParams.page = params.page;
    searchParams.page_size = params.pageSize;
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
      key: 'title',
      title: $t('common.title'),
      align: 'center',
      minWidth: 180,
      ellipsis: {
        tooltip: true
      }
    },
    {
      key: 'type',
      title: $t('page.manage.announcement.noticeType'),
      align: 'center',
      width: 100,
      render: row => {
        const typeLabel = typeOptions.find(opt => opt.value === row.type)?.label || row.type;
        return <NTag type="info" size="small">{typeLabel}</NTag>;
      }
    },
    {
      key: 'target_type',
      title: $t('page.manage.announcement.targetTypeLabel'),
      align: 'center',
      width: 100,
      render: row => {
        const targetLabel = targetTypeOptions.find(opt => opt.value === row.target_type)?.label || row.target_type;
        return <NTag type="default" size="small">{targetLabel}</NTag>;
      }
    },
    {
      key: 'priority',
      title: $t('page.manage.announcement.priority'),
      align: 'center',
      width: 90,
      render: row => {
        const pm = priorityOptions.find(opt => opt.value === row.priority);
        if (!pm) return null;
        return <NTag type={pm.value === 'low' ? 'default' : pm.value === 'normal' ? 'success' : pm.value === 'high' ? 'warning' : 'error'} size="small">{pm.label}</NTag>;
      }
    },
    {
      key: 'status',
      title: $t('common.status'),
      align: 'center',
      width: 80,
      render: row => {
        if (row.status === null) {
          return null;
        }
        const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
          '1': 'success',
          '2': 'warning'
        };
        const label = row.status === '1' ? $t('page.manage.announcement.status.published') : $t('page.manage.announcement.status.draft');
        return <NTag type={tagMap[row.status]} size="small">{label}</NTag>;
      }
    },
    {
      key: 'sender_name',
      title: $t('page.manage.announcement.senderName'),
      align: 'center',
      width: 100
    },
    {
      key: 'published_at',
      title: $t('page.manage.announcement.publishedAt'),
      align: 'center',
      width: 160,
      render: row => {
        return <span>{row.published_at || '-'}</span>;
      }
    },
    {
      key: 'operate',
      title: $t('common.operate'),
      align: 'center',
      width: 240,
      fixed: 'right',
      render: row => {
        const isDraft = row.status === '2';
        return (
          <div class="flex-center gap-8px">
            {hasAuth('sys:notice:edit') && isDraft && (
              <NButton type="primary" ghost size="small" onClick={() => editNotice(row.id)}>
                {$t('common.edit')}
              </NButton>
            )}
            {hasAuth('sys:notice:publish') && isDraft && (
              <NButton type="warning" ghost size="small" onClick={() => handlePublish(row.id)}>
                {$t('page.manage.announcement.publish')}
              </NButton>
            )}
            {hasAuth('sys:notice:delete') && (
              <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
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

/** 通知操作 */
const {
  drawerVisible: noticeDrawerVisible,
  operateType: noticeOperateType,
  editingData: editingNoticeData,
  handleAdd: handleAddNotice,
  handleEdit: handleEditNotice,
  checkedRowKeys: checkedNoticeRowKeys,
  onBatchDeleted: onNoticeBatchDeleted,
  onDeleted: onNoticeDeleted
} = useTableOperate(noticeData, 'id', getNoticeData);

/** 编辑通知 */
function editNotice(id: number) {
  handleEditNotice(id);
}

/** 删除通知 */
async function handleDelete(id: number) {
  try {
    await fetchDeleteNotice(id);
    onNoticeDeleted();
  } catch (error) {
    console.error('删除通知失败:', error);
  }
}

/** 发布通知 */
async function handlePublish(id: number) {
  try {
    await fetchPublishNotice(id);
    message.success($t('page.manage.announcement.publishSuccess'));
    getNoticeDataByPage();
  } catch (error) {
    console.error('发布通知失败:', error);
  }
}

/** 批量删除通知 */
async function handleBatchDelete() {
  if (checkedNoticeRowKeys.value.length === 0) {
    message.warning($t('common.pleaseSelect'));
    return;
  }
  try {
    await fetchBatchDeleteNotice(checkedNoticeRowKeys.value.map(Number));
    onNoticeBatchDeleted();
  } catch (error) {
    console.error('批量删除通知失败:', error);
  }
}
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NoticeSearch v-model:model="searchParams" @search="getNoticeDataByPage" @reset="getNoticeDataByPage" />
    <NCard
      :title="$t('page.manage.announcement.title')"
      :bordered="false"
      size="small"
      class="card-wrapper sm:flex-1-hidden"
    >
      <template #header-extra>
        <TableHeaderOperation
          v-model:columns="noticeColumnChecks"
          :disabled-delete="checkedNoticeRowKeys.length === 0"
          :loading="noticeLoading"
          @refresh="getNoticeData"
        >
          <template #default>
            <NButton
              v-if="hasAuth('sys:notice:add')"
              size="small"
              ghost
              type="primary"
              @click="handleAddNotice"
            >
              <template #icon>
                <icon-ic-round-plus class="text-icon" />
              </template>
              {{ $t('common.add') }}
            </NButton>
            <NPopconfirm
              v-if="hasAuth('sys:notice:delete')"
              @positive-click="handleBatchDelete"
            >
              <template #trigger>
                <NButton
                  size="small"
                  ghost
                  type="error"
                  :disabled="checkedNoticeRowKeys.length === 0"
                >
                  <template #icon>
                    <icon-ic-round-delete class="text-icon" />
                  </template>
                  {{ $t('common.batchDelete') }}
                </NButton>
              </template>
              {{ $t('common.confirmDelete') }}
            </NPopconfirm>
          </template>
        </TableHeaderOperation>
      </template>
      <NDataTable
        v-model:checked-row-keys="checkedNoticeRowKeys"
        :columns="noticeColumns"
        :data="noticeData"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1200"
        :loading="noticeLoading"
        remote
        :row-key="row => row.id"
        :pagination="noticeMobilePagination"
        class="sm:h-full"
      />
      <NoticeOperateDrawer
        v-model:visible="noticeDrawerVisible"
        :operate-type="noticeOperateType"
        :row-data="editingNoticeData"
        @submitted="getNoticeDataByPage"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
