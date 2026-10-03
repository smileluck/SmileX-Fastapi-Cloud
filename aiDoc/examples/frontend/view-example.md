<!-- last-updated: 2026-10-02 -->
# 前端页面组件示例

## 用途

展示如何组织一个标准的页面组件。

## 核心原则

- 每个页面有独立文件夹
- 主文件为 `index.vue`
- 子组件放在 `modules/` 子目录
- 共享逻辑放在 `shared.ts` 中
- 使用 NaiveUI 组件库

## 目录结构

```
src/views/manage/user/
├── index.vue              # 主页面（表格 + 搜索 + 分页）
├── modules/
│   ├── UserOperateDrawer.vue  # 新增/编辑抽屉组件
│   └── UserDetailModal.vue    # 详情弹窗组件
└── shared.ts              # 共享类型和工具函数
```

## 示例

### 主页面 `index.vue`

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { NButton, NDataTable, NSpace, NPagination } from 'naive-ui';
import { fetchGetUserList, fetchDeleteUser } from '@/service/api/system-manage';
import { useTable } from '@/hooks/common/table';
import UserOperateDrawer from './modules/UserOperateDrawer.vue';

const { data, loading, pagination, getData } = useTable(fetchGetUserList);
const operateDrawerVisible = ref(false);
const editingRow = ref<Api.SystemManage.UserInfo | null>(null);

function handleAdd() {
  editingRow.value = null;
  operateDrawerVisible.value = true;
}

function handleEdit(row: Api.SystemManage.UserInfo) {
  editingRow.value = row;
  operateDrawerVisible.value = true;
}

async function handleDelete(row: Api.SystemManage.UserInfo) {
  await fetchDeleteUser(row.id);
  await getData();
}
</script>

<template>
  <div class="h-full flex-col-stretch gap-16px overflow-hidden lt-sm:gap-12px">
    <NDataTable :columns="columns" :data="data" :loading="loading" />
    <NPagination v-model:page="pagination.page" :page-count="pagination.totalPages" />
  </div>
</template>
```

### 搜索表单 `modules/search.vue`（含 i18n 示例）

```vue
<template>
  <NFormItem
    :label="$t('page.manage.announcement.form.title')"
    path="title"
  >
    <NInput
      v-model:value="model.title"
      :placeholder="$t('page.manage.announcement.form.titlePlaceholder')"
      clearable
    />
  </NFormItem>
  <NFormItem
    :label="$t('page.manage.announcement.form.status')"
    path="status"
  >
    <NSelect
      v-model:value="model.status"
      :placeholder="$t('page.manage.announcement.form.statusPlaceholder')"
      :options="[
        { label: $t('page.manage.announcement.status.published'), value: '1' },
        { label: $t('page.manage.announcement.status.draft'), value: '2' }
      ]"
    />
  </NFormItem>
</template>
```

对应 locale 定义（`zh-cn.ts` / `en-us.ts`）：

```ts
page: {
  manage: {
    announcement: {
      title: '通知公告列表',
      form: {
        title: '通知标题',
        titlePlaceholder: '请输入通知标题',
        status: '状态',
        statusPlaceholder: '请选择状态'
      },
      status: {
        published: '已发布',
        draft: '草稿'
      }
    }
  }
}
```

**注意**：
- 页面级文本全部放在 `page.manage.xxx.*` 下，不直接使用 `common.*`
- 若需引用 `common.*`（如 `common.search`、`common.reset`），必须先确认该 key 在 `common` 命名空间中已存在
- 新增键必须同时添加到 `zh-cn.ts`、`en-us.ts` 和 `frontend/src/typings/app.d.ts` 的 `App.I18n.Schema`

## 关键点

- 页面组件只负责布局和交互，业务逻辑通过 API 函数调用
- 使用 NaiveUI 组件库（`NDataTable`、`NForm`、`NModal` 等）
- 子组件通过 `defineEmits` 和 `defineProps` 与父组件通信
- 状态管理使用 `ref` / `reactive`（组件内）或 Pinia（跨组件）

## 真实参考文件

- `frontend/src/views/manage/`
- `frontend/src/views/home/`
