<script setup lang="tsx">
import { computed, ref } from 'vue';
import type { Ref } from 'vue';
import { NButton, NPopconfirm, NTag } from 'naive-ui';
import { useBoolean } from '@sa/hooks';
import { yesOrNoRecord } from '@/constants/common';
import { enableStatusRecord, menuTypeRecord } from '@/constants/business';
import { fetchDeleteMenu, fetchGetAllPages, fetchGetMenuListTree } from '@/service/api';
import { useAppStore } from '@/store/modules/app';
import { useAuth } from '@/hooks/business/auth';
import { tableCellText } from '@/hooks/common/table';
import { formatButtonLabel } from '@/utils/menu-button';
import { $t } from '@/locales';
import SvgIcon from '@/components/custom/svg-icon.vue';
import MenuOperateModal, { type OperateType } from './modules/menu-operate-modal.vue';

const appStore = useAppStore();
const { hasAuth } = useAuth();

const { bool: visible, setTrue: openModal } = useBoolean();

const wrapperRef = ref<HTMLElement | null>(null);

const loading = ref(false);
const data = ref<Api.SystemManage.Menu[]>([]);

async function getData() {
  loading.value = true;
  const { data: list } = await fetchGetMenuListTree();
  data.value = list || [];
  loading.value = false;
}

// 建立 id → 菜单 name 索引，供按钮行查父菜单用
const menuIdToName = computed(() => {
  const map = new Map<number, string>();
  function walk(items: Api.SystemManage.Menu[]) {
    for (const item of items) {
      map.set(item.id, item.routeName);
      if (item.children) walk(item.children);
    }
  }
  walk(data.value);
  return map;
});

const columns = [
  {
    key: 'menuName',
    title: $t('page.manage.menu.menuName'),
    minWidth: 160,
    render: (row: Api.SystemManage.Menu) => {
      // 按钮类型：用 permission 解析动作，拼接父菜单名
      if (row.menuType === '3') {
        const parentName = row.parentId ? menuIdToName.value.get(row.parentId) : null;
        return <span>{formatButtonLabel(row.menuName, row.permission, parentName)}</span>;
      }
      const { i18nKey, menuName } = row;
      const label = i18nKey ? $t(i18nKey) : menuName;
      return <span>{label}</span>;
    }
  },
  {
    key: 'menuType',
    title: $t('page.manage.menu.menuType'),
    align: 'center' as const,
    width: 80,
    render: (row: Api.SystemManage.Menu) => {
      const tagMap: Record<Api.SystemManage.MenuType, NaiveUI.ThemeColor> = {
        '1': 'default',
        '2': 'primary',
        '3': 'warning'
      };

      const label = $t(menuTypeRecord[row.menuType]);

      return <NTag type={tagMap[row.menuType]}>{label}</NTag>;
    }
  },
  {
    key: 'icon',
    title: $t('page.manage.menu.icon'),
    align: 'center' as const,
    width: 60,
    render: (row: Api.SystemManage.Menu) => {
      if (!row.icon) return <div class="flex-center">-</div>;

      const icon = row.iconType === '1' ? row.icon : undefined;

      const localIcon = row.iconType === '2' ? row.icon : undefined;

      return (
        <div class="flex-center">
          <SvgIcon icon={icon} localIcon={localIcon} class="text-icon" />
        </div>
      );
    }
  },
  {
    key: 'routeName',
    title: $t('page.manage.menu.routeName'),
    align: 'center' as const,
    minWidth: 120,
    render: (row: Api.SystemManage.Menu) => tableCellText(row.routeName)
  },
  {
    key: 'routePath',
    title: $t('page.manage.menu.routePath'),
    align: 'center' as const,
    minWidth: 120,
    render: (row: Api.SystemManage.Menu) => tableCellText(row.routePath)
  },
  {
    key: 'status',
    title: $t('page.manage.menu.menuStatus'),
    align: 'center' as const,
    width: 80,
    render: (row: Api.SystemManage.Menu) => {
      if (row.status === null) {
        return null;
      }

      const tagMap: Record<Api.Common.EnableStatus, NaiveUI.ThemeColor> = {
        '1': 'success',
        '2': 'warning'
      };

      return <NTag type={tagMap[row.status]}>{$t(enableStatusRecord[row.status])}</NTag>;
    }
  },
  {
    key: 'is_system',
    title: $t('page.manage.menu.isSystem'),
    align: 'center' as const,
    width: 80,
    render: (row: Api.SystemManage.Menu) => {
      const isSystem = row.is_system === '1';

      return (
        <NTag type={isSystem ? 'info' : 'default'}>
          {isSystem ? $t('common.yesOrNo.yes') : $t('common.yesOrNo.no')}
        </NTag>
      );
    }
  },
  {
    key: 'hideInMenu',
    title: $t('page.manage.menu.hideInMenu'),
    align: 'center' as const,
    width: 80,
    render: (row: Api.SystemManage.Menu) => {
      const hide: CommonType.YesOrNo = row.hideInMenu ? 'Y' : 'N';

      const tagMap: Record<CommonType.YesOrNo, NaiveUI.ThemeColor> = {
        Y: 'error',
        N: 'default'
      };

      const label = $t(yesOrNoRecord[hide]);

      return <NTag type={tagMap[hide]}>{label}</NTag>;
    }
  },
  {
    key: 'order',
    title: $t('page.manage.menu.order'),
    align: 'center' as const,
    width: 60
  },
  {
    key: 'operate',
    title: $t('common.operate'),
    align: 'center' as const,
    minWidth: 150,
    render: (row: Api.SystemManage.Menu) => (
      <div class="flex flex-wrap justify-center gap-8px">
        {row.menuType === '1' && hasAuth('sys:menu:add') && (
          <NButton type="primary" text size="small" onClick={() => handleAddChildMenu(row)}>
            {$t('page.manage.menu.addChildMenu')}
          </NButton>
        )}
        {row.menuType === '2' && hasAuth('sys:menu:add') && (
          <NButton type="primary" text size="small" onClick={() => handleAddChildMenu(row)}>
            {$t('page.manage.menu.addChildButton')}
          </NButton>
        )}
        {hasAuth('sys:menu:edit') && (
          <NButton type="primary" text size="small" onClick={() => handleEdit(row)}>
            {$t('common.edit')}
          </NButton>
        )}
        {hasAuth('sys:menu:delete') && (
          <NPopconfirm onPositiveClick={() => handleDelete(row.id)}>
            {{
              default: () => $t('common.confirmDelete'),
              trigger: () => (
                <NButton type="error" text size="small">
                  {$t('common.delete')}
                </NButton>
              )
            }}
          </NPopconfirm>
        )}
      </div>
    )
  }
];

const operateType = ref<OperateType>('add');

function handleAdd() {
  operateType.value = 'add';
  openModal();
}

async function handleDelete(id: number) {
  const { error } = await fetchDeleteMenu(id);
  if (!error) {
    window.$message?.success($t('common.deleteSuccess'));
    await getData();
  }
}

/** the edit menu data or the parent menu data when adding a child menu */
const editingData: Ref<Api.SystemManage.Menu | null> = ref(null);

function handleEdit(item: Api.SystemManage.Menu) {
  operateType.value = 'edit';
  editingData.value = { ...item };

  openModal();
}

function handleAddChildMenu(item: Api.SystemManage.Menu) {
  operateType.value = 'addChild';

  editingData.value = { ...item };

  openModal();
}

const allPages = ref<string[]>([]);

async function getAllPages() {
  const { data: pages } = await fetchGetAllPages();
  allPages.value = pages || [];
}

function init() {
  getAllPages();
  getData();
}

// init
init();
</script>

<template>
  <div ref="wrapperRef" class="flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <NCard :title="$t('page.manage.menu.title')" :bordered="false" size="small" class="card-wrapper sm:flex-1-hidden">
      <template #header-extra>
        <NSpace>
          <NButton v-permission="'sys:menu:add'" type="primary" size="small" @click="handleAdd">
            <icon-ic-round-plus class="mr-4px text-icon" />
            {{ $t('common.add') }}
          </NButton>
          <NButton size="small" :loading="loading" @click="getData">
            <icon-ic-round-refresh class="mr-4px text-icon" />
            {{ $t('common.refresh') }}
          </NButton>
        </NSpace>
      </template>
      <NDataTable
        :columns="columns"
        :data="data"
        size="small"
        :flex-height="!appStore.isMobile"
        :scroll-x="1088"
        :loading="loading"
        :row-key="(row: Api.SystemManage.Menu) => row.id"
        :default-expand-all="true"
        class="sm:h-full"
      />
      <MenuOperateModal
        v-model:visible="visible"
        :operate-type="operateType"
        :row-data="editingData"
        :all-pages="allPages"
        @submitted="getData"
      />
    </NCard>
  </div>
</template>

<style scoped></style>
