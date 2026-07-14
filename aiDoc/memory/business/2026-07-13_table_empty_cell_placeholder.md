# 表格空字段统一显示为 "-"

## 需求描述

用户要求：「所有表格展示的空字段，默认使用 - 表示」。此前各列空值展示不统一（有的 `|| '-'`、有的 `?? '-'`、有的直接空白），且需逐列手写。

## 状态

已完成

## 方案

在共享表格 hook 的列加工环节统一注入默认 render，避免逐表逐列修改。

### 1. 中心化注入（覆盖 16/20 表格）

`hooks/common/table.ts`：

- 新增导出 `tableCellText(value)`：`null / undefined / ''` → `"-"`；`0`、`false` 等 falsy 合法值原样保留（`String(value)`）。
- 新增内部 `withEmptyPlaceholder(col)`：仅对「有 `key`、无 `type`、无自定义 `render`」的普通数据列注入 `render: row => tableCellText(row[key])`；选择列 / 展开列 / 已有 render 的列不动。
- 在 `getColumns` 加工列时对每个列套一层 `withEmptyPlaceholder`。

因 `useNaiveTable` / `useNaivePaginatedTable` 的列都经 `getColumns` 产出，所有走 hook 的表格（user / role / dict / config / file / ip-blacklist / announcement / merchant / openapi-log / operation-log / login-log / online-user / scheduler task/log / export-record / scheduler task-execution-log）自动生效。

### 2. 内联表格（不走 hook）手工补

- `views/manage/menu/index.vue`：`routeName`、`routePath`（按钮/目录这两列常为空）加 `render: row => tableCellText(row.xxx)`，并导入 `tableCellText`。
- `views/manage/dept/index.vue`：无需改——`name` 是树形 tree-key（加 render 会破坏缩进，且始终有值）、`code` 已有 `|| '-'`、`sort` 是数字恒有值。
- `views/demo/dict`、`views/demo/upload`：示例页，数据恒有值，无空字段缺口，未改。

## 设计取舍

- **只注入无 render 的列**：自定义 render（状态 tag、操作按钮、序号列等）保持作者原意，不被覆盖。需要空值占位的自定义 render 可直接调用 `tableCellText`。
- **保留 0 / false**：用 `=== null/undefined/''` 判断而非 falsy，避免 `0` 被误显为 "-"。
- 树形表的 tree-key 列不加 render（会破坏展开/缩进），其空值由既有 render 或数据本身保证。

## 验证

`pnpm typecheck` 退出码 0，0 报错。逻辑：普通空数据列显示 "-"，0/false 保留，自定义 render 不受影响。

## 涉及范围

### 前端

- `src/hooks/common/table.ts`：新增 `tableCellText` / `withEmptyPlaceholder`，`getColumns` 套用。
- `src/views/manage/menu/index.vue`：`routeName` / `routePath` 加 render。

### 后端

无。

## 相关文件

- `frontend/src/hooks/common/table.ts`
- `frontend/src/views/manage/menu/index.vue`

## 记录日期

2026-07-13
