<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { jsonClone } from '@sa/utils';
import { enableStatusOptions } from '@/constants/business';
import { useNaiveForm } from '@/hooks/common/form';
import { fetchCreateSceneGroup, fetchUpdateSceneGroup, fetchGetSceneGroupTree } from '@/service/api';

defineOptions({
  name: 'SceneGroupOperateDrawer'
});

interface Props {
  operateType: NaiveUI.TableOperateType;
  rowData?: Api.Scene.SceneGroup | null;
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

const title = computed(() => {
  const titles: Record<NaiveUI.TableOperateType, string> = {
    add: '新增场景分组',
    edit: '编辑场景分组'
  };
  return titles[props.operateType];
});

interface GroupModel {
  name: string;
  parent_id: number | null;
  sort: number;
  status: Api.Common.EnableStatus;
}

const model = ref<GroupModel>(createDefaultModel());

function createDefaultModel(): GroupModel {
  return {
    name: '',
    parent_id: null,
    sort: 0,
    status: '1'
  };
}

const rules = {
  name: { required: true, message: '请输入分组名称', trigger: 'blur' }
};

const treeData = ref<Api.Scene.SceneGroupTreeNode[]>([]);

async function loadTree() {
  const { data } = await fetchGetSceneGroupTree();
  treeData.value = data || [];
}

/** 收集指定节点的所有后代ID（包括自身） */
function collectDescendantIds(nodes: Api.Scene.SceneGroupTreeNode[], id: number): Set<number> {
  const ids = new Set<number>();
  function walk(list: Api.Scene.SceneGroupTreeNode[]) {
    for (const node of list) {
      if (node.id === id) {
        ids.add(node.id);
        if (node.children) walk(node.children);
        continue;
      }
      if (node.children) walk(node.children);
    }
  }
  walk(nodes);
  return ids;
}

/** 过滤掉指定ID集合中的节点 */
function filterTree(nodes: Api.Scene.SceneGroupTreeNode[], excludeIds: Set<number>): Api.Scene.SceneGroupTreeNode[] {
  return nodes
    .filter(n => !excludeIds.has(n.id))
    .map(n => ({
      ...n,
      children: n.children ? filterTree(n.children, excludeIds) : undefined
    }));
}

/** 编辑时排除自身及子节点，防止循环引用 */
const treeOptions = computed(() => {
  let trees = treeData.value;
  if (props.operateType === 'edit' && props.rowData) {
    const excludeIds = collectDescendantIds(trees, props.rowData.id);
    trees = filterTree(trees, excludeIds);
  }
  return trees;
});

function treeSelectOptions(nodes: Api.Scene.SceneGroupTreeNode[]): { key: number; label: string; children?: any }[] {
  return nodes.map(node => ({
    key: node.id,
    label: node.name,
    children: node.children ? treeSelectOptions(node.children) : undefined
  }));
}

const parentOptions = computed(() => treeSelectOptions(treeOptions.value));

const groupId = computed(() => props.rowData?.id || -1);
const isEdit = computed(() => props.operateType === 'edit');

function handleInitModel() {
  model.value = createDefaultModel();

  if (props.operateType === 'edit' && props.rowData) {
    const clonedData = jsonClone(props.rowData);
    model.value.name = clonedData.name || '';
    model.value.parent_id = clonedData.parent_id ?? null;
    model.value.sort = clonedData.sort ?? 0;
    model.value.status = clonedData.status ?? '1';
  }
}

function closeDrawer() {
  visible.value = false;
}

async function handleSubmit() {
  await validate();

  const submitData = {
    name: model.value.name,
    parent_id: model.value.parent_id,
    sort: model.value.sort,
    status: model.value.status
  };

  let error: unknown = null;

  if (isEdit.value) {
    const result = await fetchUpdateSceneGroup(groupId.value, submitData);
    error = result.error;
  } else {
    const result = await fetchCreateSceneGroup(submitData);
    error = result.error;
  }

  if (!error) {
    window.$message?.success(isEdit.value ? '修改成功' : '新增成功');
    closeDrawer();
    emit('submitted');
  }
}

watch(visible, () => {
  if (visible.value) {
    handleInitModel();
    restoreValidation();
    loadTree();
  }
});
</script>

<template>
  <NDrawer v-model:show="visible" display-directive="show" :width="480">
    <NDrawerContent :title="title" :native-scrollbar="false" closable>
      <NForm ref="formRef" :model="model" :rules="rules">
        <NFormItem label="分组名称" path="name">
          <NInput v-model:value="model.name" placeholder="请输入分组名称" maxlength="100" show-count />
        </NFormItem>
        <NFormItem label="上级分组" path="parent_id">
          <NTreeSelect
            v-model:value="model.parent_id"
            :options="parentOptions"
            key-field="key"
            label-field="label"
            children-field="children"
            placeholder="请选择上级分组（留空为顶级）"
            clearable
            default-expand-all
          />
        </NFormItem>
        <NFormItem label="排序" path="sort">
          <NInputNumber v-model:value="model.sort" placeholder="请输入排序值" :min="0" class="w-full" />
        </NFormItem>
        <NFormItem label="状态" path="status">
          <NRadioGroup v-model:value="model.status">
            <NRadio v-for="item in enableStatusOptions" :key="item.value" :value="item.value">
              {{ item.label }}
            </NRadio>
          </NRadioGroup>
        </NFormItem>
      </NForm>
      <template #footer>
        <NSpace :size="16">
          <NButton @click="closeDrawer">取消</NButton>
          <NButton type="primary" @click="handleSubmit">确认</NButton>
        </NSpace>
      </template>
    </NDrawerContent>
  </NDrawer>
</template>

<style scoped></style>
