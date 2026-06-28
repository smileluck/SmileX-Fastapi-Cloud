<script setup lang="ts">
import { computed, h, ref, shallowRef, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions, menuTypeRecord } from '@/constants/business';
import { fetchCreateRole, fetchUpdateRole, fetchGetAssignMenuTree, fetchGetRole } from '@/service/api';
import { useFormRules, useNaiveForm } from '@/hooks/common/form';
import { $t } from '@/locales';
import { booleanToEnableStatus } from '@/utils/status';
import { NTag } from 'naive-ui';

defineOptions({
  name: 'RoleOperateDrawer'
});

interface Props {
  /** the type of operation */
  operateType: NaiveUI.TableOperateType;
  /** the edit row data */
  rowData?: Api.SystemManage.Role | null;
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
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: $t('page.manage.role.addRole'),
    edit: $t('page.manage.role.editRole')
  };
  return titles[props.operateType];
});

type Model = Pick<Api.SystemManage.Role, 'name' | 'desc' | 'status' | 'data_scope'>;

const model = ref(createDefaultModel());

function createDefaultModel(): Model {
  return {
    name: '',
    desc: '',
    status: '1',
    data_scope: 'SELF'
  };
}

const dataScopeOptions: { label: string; value: Api.SystemManage.DataScope }[] = [
  { label: $t('page.manage.role.dataScopes.ALL'), value: 'ALL' },
  { label: $t('page.manage.role.dataScopes.DEPT_AND_SUB'), value: 'DEPT_AND_SUB' },
  { label: $t('page.manage.role.dataScopes.DEPT_ONLY'), value: 'DEPT_ONLY' },
  { label: $t('page.manage.role.dataScopes.SELF'), value: 'SELF' }
];

type RuleKey = Exclude<keyof Model, 'desc'>;

const rules: Record<RuleKey, App.Global.FormRule> = {
  name: defaultRequiredRule,
  status: defaultRequiredRule,
  data_scope: defaultRequiredRule
};

const roleId = computed(() => props.rowData?.id || -1);

const isEdit = computed(() => props.operateType === 'edit');

// Menu tree
const menuTree = shallowRef<Api.SystemManage.MenuTree[]>([]);
const menuChecks = ref<number[]>([]);
const menuExpandedKeys = ref<number[]>([]);

const tagTypeMap: Record<string, NaiveUI.ThemeColor> = {
  '1': 'default',
  '2': 'primary',
  '3': 'warning'
};

function getTranslatedLabel(node: Api.SystemManage.MenuTree): string {
  const i18nKey = `route.${node.label}` as App.I18n.I18nKey;
  return $t(i18nKey);
}

function renderMenuLabel({ option }: { option: Record<string, unknown> }) {
  const node = option as unknown as Api.SystemManage.MenuTree;
  const tagType = tagTypeMap[node.menuType];
  const displayLabel = getTranslatedLabel(node);

  if (node.menuType === '3') {
    return h(
      'span',
      { class: 'flex items-center gap-8px' },
      {
        default: () => [
          h(NTag, { type: tagType, size: 'small', bordered: false }, { default: () => $t(menuTypeRecord[node.menuType]) }),
          displayLabel
        ]
      }
    );
  }

  return displayLabel;
}

async function loadMenuTree() {
  const { error, data } = await fetchGetAssignMenuTree();
  if (!error) {
    menuTree.value = data;
  }
}

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

async function loadRoleMenuIds() {
  if (isEdit.value && roleId.value > 0) {
    const { error, data } = await fetchGetRole(roleId.value);
    if (!error && data) {
      menuChecks.value = data.menu_ids || [];
      menuExpandedKeys.value = getAncestorKeys(menuTree.value, menuChecks.value);
    }
  } else {
    menuChecks.value = [];
    menuExpandedKeys.value = [];
  }
}

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.desc = clonedData.desc || '';
    model.value.status = booleanToEnableStatus(clonedData.status);
    model.value.data_scope = clonedData.data_scope || 'SELF';
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  let error: unknown = null;

  const submitData = {
    ...model.value,
    menu_ids: menuChecks.value
  };

  if (isEdit.value) {
    const result = await fetchUpdateRole(roleId.value, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateRole(submitData);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? $t('common.updateSuccess') : $t('common.addSuccess'));
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, async () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    await loadMenuTree();
    await loadRoleMenuIds();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="360">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem :label="$t('page.manage.role.roleName')" path="name">
          <NInput v-model:value="model.name" :placeholder="$t('page.manage.role.form.roleName')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.role.roleStatus')" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.manage.role.roleDesc')" path="desc">
          <NInput v-model:value="model.desc" :placeholder="$t('page.manage.role.form.roleDesc')" />
        </NFormItem>
        <NFormItem :label="$t('page.manage.role.dataScope')" path="data_scope">
          <NRadioGroup v-model:value="model.data_scope">
            <NRadio v-for="item in dataScopeOptions" :key="item.value" :value="item.value" :label="item.label" />
          </NRadioGroup>
        </NFormItem>
        <NFormItem :label="$t('page.manage.role.menuAuth')" class="flex-1-hidden">
          <NTree
            v-model:checked-keys="menuChecks"
            v-model:expanded-keys="menuExpandedKeys"
            :data="menuTree"
            key-field="id"
            checkable
            cascade
            expand-on-click
            virtual-scroll
            block-line
            :render-label="renderMenuLabel"
            class="flex-1-hidden w-full"
          />
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">{{ $t('common.cancel') }}</NButton>
          <NButton type="primary" @click="handleSubmit">{{ $t('common.confirm') }}</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
