# i18n Schema 补全 + 类型清理

## 需求描述

用户要求「修复 i18n 异常，补全类型」。此前 `pnpm typecheck` 有 38 处报错，分两类：i18n Schema 类型缺字段、以及其他类型错误。本次全部清理为 0 报错。

## 状态

已完成

## 一、i18n Schema 补全（`src/typings/app.d.ts`）

`App.I18n.Schema` 是**手工维护**的 locale 镜像类型（`I18nKey` 由它派生），locale 文件 `const local: App.I18n.Schema` 强制要求二者一致。补全以下缺失字段：

- 新增顶层 `exportTask` 块（title/tooltip/taskName/moduleKey/status.{title,pending,processing,completed,failed}/totalRows/fileSize/errorMessage/createdAt/finishedAt/noRecords/viewAll/asyncExport/submitSuccess/submitFailed/downloadFailed），与 locale 完全对齐。
- `notification` 增加 `tooltip: string`。
- `page.manage.role.form` 增加 `nameMaxLength`、`descMaxLength`。

修好后：locale 文件不再报 excess property，`$t('exportTask.*')` / `$t('notification.tooltip')` / `$t('page.manage.role.form.nameMaxLength')` 等全部成为合法 `I18nKey`。

## 二、其他类型错误修复

- `hooks/business/dict.ts`：vue 导入漏了 `Ref`，导致 `as Ref<...>` 失效 → `items` 退化为 any → `.map(item => ...)` 的 item 隐式 any。补 `type Ref` 导入，连带修复 4 处报错。
- `service/api/export-task.ts`：`fetchDownloadExportFile` 原用 `request<Blob>({ responseType:'blob' })`，而 `request` 是 `createFlatRequest`（transform 读 `response.data.data` JSON 包络），不支持 blob。改为参考 `service/api/file.ts` 的直传模式：`axios.get(..., { responseType:'blob', headers:{Authorization} })`，并包成 `{ data: Blob|null, error: AxiosError|null }` 返回，兼容既有调用方的 `const { error, data } = await ...`。
- `views/manage/user/modules/user-operate-drawer.vue`：**潜在 Bug**——角色多选 `value: item.code`，但提交时 `roleNamesToIds(model.value.userRoles)` 按 `r.name === name` 匹配（且 `roleOptions` 类型是 `Option<string>`）。用 code 当 value 会导致 name→id 查不到，**角色分配静默失败**。改为 `value: item.name`（`AllRole = Pick<Role,'id'|'name'>` 本就有 name，无需改 AllRole）。
- `views/scheduler/{log,task}/index.vue`：`checkedRowKeys.value as number[]` 失败（`checkedRowKeys` 是 `shallowRef<string[]>`）。改为 `.map(Number)` 真正转成 `number[]`。
- `layouts/.../export-record-center.vue`：失败原因 `NTag` 的 `bordered="false"`（字符串）改为 `:bordered="false"`（布尔）。

## 涉及范围

### 前端

- `src/typings/app.d.ts`（Schema 补全）
- `src/hooks/business/dict.ts`、`src/service/api/export-task.ts`、`src/views/manage/user/modules/user-operate-drawer.vue`、`src/views/scheduler/log/index.vue`、`src/views/scheduler/task/index.vue`、`src/layouts/modules/global-header/components/export-record-center.vue`

### 后端

无。

## 约束与备注

- `App.I18n.Schema` 仍是手工维护；后续新增 locale key 必须同步进 Schema，否则 locale 文件 excess property 报错 + `$t` 类型不匹配。
- 角色选择器用「名称」作为 value 是历史设计（`roleNamesToIds` 按 name→id）；若后续想用 id 直传，需一并改 `roleNamesToIds` 与 `Option<number>`。
- 验证：`pnpm typecheck` 退出码 0，0 报错（修复前 38 处）。

## 相关文件

- `frontend/src/typings/app.d.ts`
- `frontend/src/locales/langs/{zh-cn,en-us}.ts`（未改，受益于 Schema 补全）
- `frontend/src/hooks/business/dict.ts`
- `frontend/src/service/api/export-task.ts`
- `frontend/src/views/manage/user/modules/user-operate-drawer.vue`
- `frontend/src/views/scheduler/{log,task}/index.vue`
- `frontend/src/layouts/modules/global-header/components/export-record-center.vue`

## 记录日期

2026-07-13
