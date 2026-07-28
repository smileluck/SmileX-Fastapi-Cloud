<script setup lang="ts">
import { computed, h, shallowRef, watch } from 'vue';
import { NTag } from 'naive-ui';
import { menuTypeRecord } from '@/constants/business';
import { fetchAssignMenuToRole, fetchGetAllPages, fetchGetAssignMenuTree, fetchGetRole } from '@/service/api';
import { formatButtonLabel } from '@/utils/menu-button';
import { $t } from '@/locales';

defineOptions({
  name: 'MenuAuthModal'
});

interface Props {
  /** the roleId */
  roleId: number;
}

const props = defineProps<Props>();

const visible = defineModel<boolean>('visible', {
  default: false
});

function closeModal() {
  visible.value = false;
}

const title = computed(() => $t('common.edit') + $t('page.manage.role.menuAuth'));

const tagTypeMap: Record<string, NaiveUI.ThemeColor> = {
  '1': 'default',
  '2': 'primary',
  '3': 'warning'
};

const home = shallowRef('');

async function getHome() {
  home.value = 'home';
}

async function updateHome(val: string) {
  home.value = val;
}

const pages = shallowRef<string[]>([]);

async function getPages() {
  const { error, data } = await fetchGetAllPages();

  if (!error) {
    pages.value = data;
  }
}

const pageSelectOptions = computed(() => {
  const opts: CommonType.Option[] = pages.value.map(page => ({
    label: page,
    value: page
  }));

  return opts;
});

const tree = shallowRef<Api.SystemManage.MenuTree[]>([]);

async function getTree() {
  const { error, data } = await fetchGetAssignMenuTree();

  if (!error) {
    tree.value = data;
  }
}

const checks = shallowRef<number[]>([]);

async function getChecks() {
  const { error, data } = await fetchGetRole(props.roleId);

  if (!error && data) {
    checks.value = data.menu_ids || [];
  }
}

const expandedKeys = shallowRef<number[]>([]);

function getAncestorKeys(treeData: Api.SystemManage.MenuTree[], targetIds: number[]): number[] {
  const ancestorSet = new Set<number>();

  function findAncestors(nodes: Api.SystemManage.MenuTree[], targetId: number, currentPath: number[]): boolean {
    for (const node of nodes) {
      if (node.id === targetId) {
        for (const ancestorId of currentPath) {
          ancestorSet.add(ancestorId);
        }
        return true;
      }
      if (node.children && node.children.length > 0) {
        if (findAncestors(node.children, targetId, [...currentPath, node.id])) {
          return true;
        }
      }
    }
    return false;
  }

  for (const targetId of targetIds) {
    findAncestors(treeData, targetId, []);
  }

  return Array.from(ancestorSet);
}

async function handleSubmit() {
  const { error } = await fetchAssignMenuToRole(props.roleId, checks.value);

  if (!error) {
    window.$message?.success?.($t('common.modifySuccess'));
    closeModal();
  }
}

// 建立 id → 父节点 name 索引（按钮要拼父级菜单名）
const parentIdToName = computed(() => {
  const map = new Map<number, string>();
  function walk(nodes: Api.SystemManage.MenuTree[], parentId: number | null) {
    for (const node of nodes) {
      if (parentId !== null) {
        // 只记录非按钮节点作为父级候选
        if (node.menuType !== '3') map.set(node.id, node.label);
      }
      if (node.children && node.children.length > 0) {
        walk(node.children, node.id);
      }
    }
  }
  walk(tree.value, null);
  return map;
});

function getTranslatedLabel(node: Api.SystemManage.MenuTree): string {
  const i18nKey = `route.${node.label}` as App.I18n.I18nKey;
  return $t(i18nKey);
}

function renderLabel({ option }: { option: Record<string, unknown> }) {
  const node = option as unknown as Api.SystemManage.MenuTree;
  const tagType = tagTypeMap[node.menuType];

  // 按钮节点：显示 "{父菜单 i18n} - {动作}"，并把 type tag 移到末尾以强化主语
  if (node.menuType === '3') {
    const parentName = node.pId ? parentIdToName.value.get(node.pId) : null;
    const buttonLabel = formatButtonLabel(node.label, null, parentName);
    return h(
      'span',
      { class: 'flex items-center gap-8px' },
      {
        default: () => [
          buttonLabel,
          h(
            NTag,
            { type: tagType, size: 'small', bordered: false },
            { default: () => $t(menuTypeRecord[node.menuType]) }
          )
        ]
      }
    );
  }

  // 目录/菜单节点：原 i18n 名 + 类型 tag
  const displayLabel = getTranslatedLabel(node);
  return h(
    'span',
    { class: 'flex items-center gap-8px' },
    {
      default: () => [
        displayLabel,
        h(NTag, { type: tagType, size: 'small', bordered: false }, { default: () => $t(menuTypeRecord[node.menuType]) })
      ]
    }
  );
}

async function init() {
  getHome();
  getPages();
  await Promise.all([getTree(), getChecks()]);
  expandedKeys.value = getAncestorKeys(tree.value, checks.value);
}

watch(visible, val => {
  if (val) {
    init();
  }
});
</script>

<template>
  <NModal v-model:show="visible" :title="title" preset="card" class="w-480px">
    <div class="flex-y-center gap-16px pb-12px">
      <div>{{ $t('page.manage.menu.home') }}</div>
      <NSelect :value="home" :options="pageSelectOptions" size="small" class="w-160px" @update:value="updateHome" />
    </div>
    <NTree
      v-model:checked-keys="checks"
      v-model:expanded-keys="expandedKeys"
      :data="tree"
      key-field="id"
      checkable
      cascade
      expand-on-click
      virtual-scroll
      block-line
      :render-label="renderLabel"
      class="h-280px"
    />
    <template #footer>
      <NSpace justify="end">
        <NButton size="small" class="mt-16px" @click="closeModal">
          {{ $t('common.cancel') }}
        </NButton>
        <NButton type="primary" size="small" class="mt-16px" @click="handleSubmit">
          {{ $t('common.confirm') }}
        </NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped></style>
