# 导出记录弹窗状态标识优化 + 查看全部路由修复

## 需求描述

用户提出 2 条导出记录功能的优化/修复需求：

1. 导出记录弹窗（头部 `ExportRecordCenter` Popover）：
   - 下载按钮缺少 i18n 文本（原先仅为图标按钮，无可见文字）。
   - 状态不再用简单图标标识，改为 `tag + 文字`：绿色=生成成功（completed）、红色=失败（failed）、黄色=生成中（processing）、灰色=排队中（pending）。
2. 弹窗「查看全部」按钮点击无效：动态路由模式下后端菜单不返回 `hideInMenu` 路由，导致 `export-record` 路由未注册，跳转落空。需将路由纳入前端 constant 路由列表，保证始终注册。

## 状态

已完成

## 涉及范围

### 后端

无。

### 前端

- `layouts/modules/global-header/components/export-record-center.vue`：
  - `statusMap` 去掉 `icon` 字段，仅保留 `label` + `type`（pending=default、processing=warning、completed=success、failed=error）。
  - 列表项状态由 `SvgIcon + NTooltip` 改为 `NTag`（带文字）。
  - 下载按钮由图标按钮（`NTooltip` 包裹的 `SvgIcon`）改为文本按钮，显示 `$t('common.actions.download')`（注意：下载文案在 `common.actions.download` 下，**不是** `common.download`；后者不存在，会渲染成原始 key）。全量列表页 `views/export-record/index.vue` 的下载按钮同 Bug，一并改掉。
  - 删除仅服务于状态图标的 `.text-success/.text-warning/.text-error/.text-default` 死样式。
- `build/plugins/router.ts`：`onRouteMetaGen` 的 `constantRoutes` 列表追加 `'export-record'`，作为常量路由的持久声明（`pnpm gen-route` 重新生成后仍生效）。
- `router/elegant/routes.ts`：由 elegant-router 监听 `build/plugins/router.ts` 变更自动重新生成，`export-record.meta` 已带 `constant: true`（同时保留 `hideInMenu`/`keepAlive`，证明生成器会与现有 meta 合并）。

## 约束与备注

- 项目鉴权路由模式为 **dynamic**（`.env` → `VITE_AUTH_ROUTE_MODE=dynamic`）：auth 路由由后端菜单接口返回；`hideInMenu` 路由不在菜单中，故不会下发，必须靠 `constant: true` 才能在 `initConstantRoute` 中注册。
- constant 路由绕过登录校验（`needLogin = !to.meta.constant`）；`export-record` 仍渲染在 `layout.base` 内，且页面接口需登录态，实际入口（头部「查看全部」）仅在登录后可见，行为正常。
- `i18nKey` 派生自 `src/typings/app.d.ts` 中**手工维护**的 `Schema` 类型，并非自动从 locale 生成。`exportTask.*` 等键在 locale 中存在（运行时 `$t` 正常解析）但未写入 `Schema`，导致 `pnpm typecheck` 报 `I18nKey` 不匹配——此为既有技术债（覆盖 notification/role/scheduler 等多个模块），本次未顺手修补，保持与现有约定一致。
- ⚠️ 下载文案的正确 key 是 `common.actions.download`（locale 与 `Schema` 一致）。`common.download` 是错误 key，既不在 locale 也不在 `Schema`，运行时会原样渲染成字符串 `common.download`。
- 状态颜色与全量列表页 `views/export-record/index.vue` 的 `statusMap` 保持一致。

## 相关文件

- `frontend/src/layouts/modules/global-header/components/export-record-center.vue`
- `frontend/build/plugins/router.ts`
- `frontend/src/router/elegant/routes.ts`（自动生成）
- `frontend/src/typings/app.d.ts`（既有 `Schema` 技术债，未改）

## 记录日期

2026-07-13
