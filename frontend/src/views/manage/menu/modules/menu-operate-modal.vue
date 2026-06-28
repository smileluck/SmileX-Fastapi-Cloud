<script setup lang="tsx">
import { computed, ref, watch } from 'vue';
import type { SelectOption } from 'naive-ui';
import { enableStatusOptions, menuIconTypeOptions, menuTypeOptions } from '@/constants/business';
import { fetchCreateMenu, fetchGetMenuTree, fetchUpdateMenu } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { getLocalIcons } from '@/utils/icon';
import { $t } from '@/locales';
import SvgIcon from '@/components/custom/svg-icon.vue';
import {
  getLayoutAndPage,
  getRoutePathByRouteName,
  transformLayoutAndPageToComponent
} from './shared';

defineOptions({
  name: 'MenuOperateModal'
});

export type OperateType = NaiveUI.TableOperateType | 'addChild';

interface Props {
  /** the type of operation */
  operateType: OperateType;
  /** the edit menu data or the parent menu data when adding a child menu */
  rowData?: Api.SystemManage.Menu | null;
  /** all pages */
  allPages: string[];
}

const props = defineProps<Props>();

interface Emits {
  (e: 'submitted'): void;
}

const emit = defineEmits<Emits>();

const visible = defineModel<boolean>('visible', {
  default: false
});

const { formRef, validate, restoreValidation } = useNaiveForm();
const { defaultRequiredRule } = useFormRules();

const title = computed(() => {
  const titles: Record<OperateType, string> = {
    add: $t('page.manage.menu.addMenu'),
    addChild: $t('page.manage.menu.addChildMenu'),
    edit: $t('page.manage.menu.editMenu')
  };
  return titles[props.operateType];
});

type Model = Pick<
  Api.SystemManage.Menu,
  | 'menuType'
  | 'menuName'
  | 'routePath'
  | 'component'
  | 'order'
  | 'icon'
  | 'iconType'
  | 'status'
  | 'parentId'
  | 'keepAlive'
  | 'href'
  | 'hideInMenu'
  | 'is_system'
> & {
  permission: string;
  layout: string;
  page: string;
};

const model = ref(createDefaultModel());

const menuTreeRaw = ref<Api.SystemManage.MenuTree[]>([]);

async function getMenuTree() {
  const { data } = await fetchGetMenuTree();
  menuTreeRaw.value = data || [];
}

function collectDescendantIds(trees: Api.SystemManage.MenuTree[], excludeId: number): Set<number> {
  const ids = new Set<number>();
  function walk(nodes: Api.SystemManage.MenuTree[]) {
    for (const node of nodes) {
      if (node.id === excludeId) {
        ids.add(node.id);
        if (node.children) walk(node.children);
        continue;
      }
      if (node.children) walk(node.children);
    }
  }
  walk(trees);
  return ids;
}

function filterTree(
  trees: Api.SystemManage.MenuTree[],
  excludeIds: Set<number>
): Api.SystemManage.MenuTree[] {
  return trees
    .filter(t => !excludeIds.has(t.id))
    .map(t => ({
      ...t,
      children: t.children ? filterTree(t.children, excludeIds) : undefined
    }));
}

function markDisabledByType(
  trees: Api.SystemManage.MenuTree[],
  allowedParentType: Api.SystemManage.MenuType
): Api.SystemManage.MenuTree[] {
  // 保留所有节点（让用户能看到完整树结构），但只允许选择指定类型的节点。
  // 不能用过滤，否则父级是 CATALOG 时会把其下的 MENU 一并丢掉，导致编辑时父级显示为空。
  return trees.map(t => ({
    ...t,
    disabled: t.menuType !== allowedParentType,
    children: t.children ? markDisabledByType(t.children, allowedParentType) : undefined
  }));
}

const parentMenuOptions = computed(() => {
  if (model.value.menuType === '1') return [];

  let trees = menuTreeRaw.value;
  if (props.operateType === 'edit' && props.rowData) {
    const excludeIds = collectDescendantIds(trees, props.rowData.id);
    excludeIds.add(props.rowData.id);
    trees = filterTree(trees, excludeIds);
  }
  // 菜单(type='2')的父级只能是目录(type='1')；按钮(type='3')的父级只能是菜单(type='2')。
  // 其他类型节点保留显示但标记 disabled，避免用户误选。
  if (model.value.menuType === '2') {
    trees = markDisabledByType(trees, '1');
  } else if (model.value.menuType === '3') {
    trees = markDisabledByType(trees, '2');
  }
  return trees;
});

function createDefaultModel(): Model {
  return {
    menuType: '1',
    menuName: '',
    routePath: '',
    component: '',
    layout: 'base',
    page: '',
    icon: '',
    iconType: '1',
    parentId: 0,
    status: '1',
    keepAlive: false,
    order: 0,
    href: null,
    hideInMenu: false,
    permission: '',
    is_system: '2'
  };
}

type RuleKey = Extract<keyof Model, 'menuName' | 'status' | 'routePath' | 'permission'>;

const rules = computed<Record<RuleKey, App.Global.FormRule>>(() => {
  const base: Record<RuleKey, App.Global.FormRule> = {
    menuName: defaultRequiredRule,
    status: defaultRequiredRule,
    routePath: defaultRequiredRule,
    permission: defaultRequiredRule
  };
  if (model.value.menuType === '3') {
    return {
      ...base,
      routePath: { required: false }
    } as Record<RuleKey, App.Global.FormRule>;
  }
  return {
    ...base,
    permission: { required: false }
  } as Record<RuleKey, App.Global.FormRule>;
});

const disabledMenuType = computed(() => props.operateType !== 'add');

const availableMenuTypeOptions = computed(() => {
  if (props.operateType === 'add') {
    return menuTypeOptions.filter(opt => opt.value !== '3');
  }
  return menuTypeOptions;
});

const localIcons = getLocalIcons();
const localIconOptions = localIcons.map<SelectOption>(item => ({
  label: () => (
    <div class="flex-y-center gap-16px">
      <SvgIcon localIcon={item} class="text-icon" />
      <span>{item}</span>
    </div>
  ),
  value: item
}));

const showLayout = computed(() => !model.value.parentId);

const isButton = computed(() => model.value.menuType === '3');

const pageOptions = computed(() => {
  const allPages = [...props.allPages];

  if (model.value.menuName && !allPages.includes(model.value.menuName)) {
    allPages.unshift(model.value.menuName);
  }

  const opts: CommonType.Option[] = allPages.map(page => ({
    label: page,
    value: page
  }));

  return opts;
});

const layoutOptions = computed<CommonType.Option[]>(() => [
  {
    label: $t('page.manage.menu.layoutBase'),
    value: 'base'
  },
  {
    label: $t('page.manage.menu.layoutBlank'),
    value: 'blank'
  }
]);

function handleInitModel() {
  model.value = createDefaultModel();

  if (!props.rowData) {
    return;
  }

  if (props.operateType === 'addChild') {
    const { id, menuType } = props.rowData;
    model.value.menuType = menuType === '1' ? '2' : '3';
    Object.assign(model.value, { parentId: id });
  }

  if (props.operateType === 'edit') {
    const { component, ...rest } = props.rowData;

    const { layout, page } = getLayoutAndPage(component);

    Object.assign(model.value, rest, { layout, page });
    model.value.permission = props.rowData.permission || '';
  }
}

function closeDrawer() {
  visible.value = false;
}

function openIconLibrary() {
  window.open('https://icon-sets.iconify.design/', '_blank');
}

function handleUpdateRoutePathByMenuName() {
  if (model.value.menuName) {
    model.value.routePath = getRoutePathByRouteName(model.value.menuName);
  } else {
    model.value.routePath = '';
  }
}

function getSubmitParams() {
  const { layout, page, ...params } = model.value;

  if (model.value.menuType === '3') {
    params.routePath = '';
    params.component = '';
    params.icon = '';
    return params;
  }

  const effectiveLayout = model.value.parentId ? '' : layout;
  const component = transformLayoutAndPageToComponent(effectiveLayout, page);

  params.component = component;

  return params;
}

async function handleSubmit() {
  await validate();

  const params = getSubmitParams();

  let error: unknown = null;

  if (props.operateType === 'edit') {
    const result = await fetchUpdateMenu(props.rowData!.id, params);
    error = result.error;
  } else {
    const result = await fetchCreateMenu(params);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(props.operateType === 'edit' ? $t('common.updateSuccess') : $t('common.addSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    getMenuTree();
  }
});

watch(
  () => model.value.menuName,
  () => {
    handleUpdateRoutePathByMenuName();
  }
);
</script>

<template>
  <NModal v-model:show="visible" :title="title" preset="card" class="w-800px">
    <NScrollbar class="h-480px pr-20px">
      <NForm ref="formRef" :model="model" :rules="rules" label-placement="left" :label-width="100">
        <NGrid responsive="screen" item-responsive>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.parentMenu')" path="parentId">
            <NTreeSelect
              v-model:value="model.parentId"
              :options="parentMenuOptions"
              :disabled="model.menuType === '1'"
              key-field="id"
              label-field="label"
              children-field="children"
              :placeholder="$t('page.manage.menu.form.parentMenu')"
              clearable
              default-expand-all
            />
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.menuType')" path="menuType">
            <NRadioGroup v-model:value="model.menuType" :disabled="disabledMenuType">
              <NRadio v-for="item in availableMenuTypeOptions" :key="item.value" :value="item.value" :label="item.label" />
            </NRadioGroup>
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.menuName')" path="menuName">
            <NInput v-model:value="model.menuName" :placeholder="$t('page.manage.menu.form.menuName')" />
          </NFormItemGi>
          <NFormItemGi
            v-if="isButton"
            span="24 m:12"
            :label="$t('page.manage.menu.permission')"
            path="permission"
          >
            <NInput v-model:value="model.permission" :placeholder="$t('page.manage.menu.form.permission')" />
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.routePath')" path="routePath">
            <NInput v-model:value="model.routePath" disabled :placeholder="$t('page.manage.menu.form.routePath')" />
          </NFormItemGi>
          <NFormItemGi v-if="!isButton && showLayout" span="24 m:12" :label="$t('page.manage.menu.layout')" path="layout">
            <NSelect
              v-model:value="model.layout"
              :options="layoutOptions"
              :placeholder="$t('page.manage.menu.form.layout')"
            />
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.page')" path="page">
            <NSelect
              v-model:value="model.page"
              :options="pageOptions"
              :disabled="model.menuType !== '2'"
              :placeholder="$t('page.manage.menu.form.page')"
            />
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.order')" path="order">
            <NInputNumber v-model:value="model.order" class="w-full" :placeholder="$t('page.manage.menu.form.order')" />
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.iconTypeTitle')" path="iconType">
            <NRadioGroup v-model:value="model.iconType">
              <NRadio v-for="item in menuIconTypeOptions" :key="item.value" :value="item.value" :label="item.label" />
            </NRadioGroup>
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.icon')" path="icon">
            <template v-if="model.iconType === '1'">
              <div class="flex-y-center gap-8px w-full">
                <NInput v-model:value="model.icon" :placeholder="$t('page.manage.menu.form.icon')" class="flex-1">
                  <template #suffix>
                    <SvgIcon v-if="model.icon" :icon="model.icon" class="text-icon" />
                  </template>
                </NInput>
                <NButton @click="openIconLibrary()">
                  <icon-ic-round-launch class="text-icon" />
                </NButton>
              </div>
            </template>
            <template v-if="model.iconType === '2'">
              <NSelect
                v-model:value="model.icon"
                :placeholder="$t('page.manage.menu.form.localIcon')"
                :options="localIconOptions"
              />
            </template>
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.menuStatus')" path="status">
            <NRadioGroup v-model:value="model.status">
              <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
            </NRadioGroup>
          </NFormItemGi>
          <NFormItemGi span="24 m:12" :label="$t('page.manage.menu.isSystem')" path="is_system">
            <NRadioGroup v-model:value="model.is_system">
              <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
            </NRadioGroup>
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.keepAlive')" path="keepAlive">
            <NRadioGroup v-model:value="model.keepAlive">
              <NRadio :value="true" :label="$t('common.yesOrNo.yes')" />
              <NRadio :value="false" :label="$t('common.yesOrNo.no')" />
            </NRadioGroup>
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.href')" path="href">
            <NInput v-model:value="model.href" :placeholder="$t('page.manage.menu.form.href')" />
          </NFormItemGi>
          <NFormItemGi v-if="!isButton" span="24 m:12" :label="$t('page.manage.menu.hideInMenu')" path="hideInMenu">
            <NRadioGroup v-model:value="model.hideInMenu">
              <NRadio :value="true" :label="$t('common.yesOrNo.yes')" />
              <NRadio :value="false" :label="$t('common.yesOrNo.no')" />
            </NRadioGroup>
          </NFormItemGi>
        </NGrid>
      </NForm>
    </NScrollbar>
    <template #footer>
      <NSpace justify="end" :size="16">
        <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
        <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
      </NSpace>
    </template>
  </NModal>
</template>

<style scoped></style>
