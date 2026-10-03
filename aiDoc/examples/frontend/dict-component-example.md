<!-- last-updated: 2026-06-04 -->
# 字典通用组件使用示例

## 用途

展示前端字典通用组件的典型使用方式。当业务页面需要展示或选择字典数据时，直接使用这些组件，不需要手动调用字典 API。

## useDict Composable

```typescript
import { useDict } from '@/hooks/business/dict';

// 基础用法：按 code 加载字典项
const { items, options, loading, getLabelByValue, refresh } = useDict('gender');

// items: Ref<DictItem[]> — 字典项列表
// options: ComputedRef<{ label: string; value: string }[]> — NSelect 可用格式
// loading: Ref<boolean> — 加载状态
// getLabelByValue('1') => '男'，未找到时返回原值
// refresh() — 清除缓存重新加载
```

模块级缓存：同一 code 只请求一次 API，多组件共享数据。

## DictSelect 下拉选择

```vue
<template>
  <!-- 基础用法 -->
  <DictSelect dict-code="gender" v-model:value="form.gender" />

  <!-- 带默认值 + 可清空 + 多选 -->
  <DictSelect
    dict-code="status"
    v-model:value="form.status"
    multiple
    clearable
    placeholder="请选择状态"
  />

  <!-- 透传 NSelect 原生属性 -->
  <DictSelect dict-code="type" v-model:value="form.type" filterable />
</template>
```

## DictTag 标签展示

```vue
<template>
  <!-- 基础用法 -->
  <DictTag dict-code="status" :value="row.status" />

  <!-- 指定 NTag 类型 -->
  <DictTag dict-code="gender" value="1" type="primary" />
  <DictTag dict-code="gender" value="2" type="error" />
</template>
```

## DictText 文本展示

```vue
<template>
  <!-- 表格列 / 详情页中展示 label 文本 -->
  <DictText dict-code="gender" :value="user.gender" />
</template>
```

## 在表格中使用

```vue
<template>
  <NDataTable :columns="columns" :data="data" />
</template>

<script setup lang="ts">
// 方式一：使用 DictTag / DictText 组件（JSX，推荐）
const columns = [
  {
    key: 'gender_tag',
    title: '性别 (DictTag)',
    render: row => <DictTag dictCode="gender" value={row.gender} type="primary" />,
  },
  {
    key: 'gender_text',
    title: '性别 (DictText)',
    render: row => <DictText dictCode="gender" value={row.gender} />,
  },
];

// 方式二：使用 useDict composable + 纯文本渲染
import { useDict } from '@/hooks/business/dict';
const { getLabelByValue } = useDict('gender');

const columns2 = [
  {
    key: 'gender_text',
    title: '性别',
    render: row => <span>{getLabelByValue(row.gender)}</span>,
  },
];
</script>
```

## 关键点

- 组件放在 `frontend/src/components/custom/` 下，自动注册，无需手动 import
- `dict-code` 是必填 prop，对应后端 `sys_dict.code`
- 未找到字典值时，DictTag/DictText 回退显示 value 原值
- useDict 内部调用 `fetchGetDictItemsByDictCode(code)`，后端仅返回启用的字典项
- **在 NDataTable 自定义列渲染时，必须使用 column 的 `render` 函数（JSX 语法），不能使用模板插槽**

## 参考文件

- composable: `frontend/src/hooks/business/dict.ts`
- 组件: `frontend/src/components/custom/dict-select.vue`
- 组件: `frontend/src/components/custom/dict-tag.vue`
- 组件: `frontend/src/components/custom/dict-text.vue`
- 演示页: `frontend/src/views/demo/dict/index.vue`
- 后端模型: `backend/database/models/sys/dict.py`
- 后端接口: `backend/modules/admin/endpoints/sys/dict.py`
