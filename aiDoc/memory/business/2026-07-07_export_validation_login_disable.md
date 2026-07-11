# 异步导出、全局校验、角色表单与登录禁用优化

## 需求描述

用户提出 13 条后台管理优化需求，核心包括：

1. 异步导出：头部栏增加导出记录入口（最近 5 条 + 红点提醒 + 全量列表），操作日志页接入异步导出。
2. 导出任务调度：移除提交后立即执行，改为 APScheduler 每分钟定时执行；增加超时失败与过期清理。
3. 状态同步：WebSocket 实时推送 + 30 秒轮询兜底。
4. 全局请求响应基类：请求类继承 `BaseReqEntity`，响应类继承 `BaseRespEntity`；全局 trim 空字符串/仅空格串。
5. 整数参数防御：`page`/`page_size` 及可选整数查询字段空值收敛，Pydantic `int_parsing` 英文错误转为中文。
6. 角色表单校验：`name` 最大 20 字符，`desc` 最大 200 字符；前后端同步校验。
7. 禁用用户不允许登录，且 current_user 校验禁用状态；禁用角色权限过滤已存在，保持现状。
8. 操作日志分页 `total` 错误修复，导出任务轮询接口不计入操作日志。

## 状态

已完成

## 涉及范围

### 后端

- `app/models/common/base.py`：`BaseReqEntity` 增加 `mode="before"` 全局 trim 与空值收敛；`BaseRespEntity` 的 `status`/`is_system` 序列化器增加 `bool` 类型保护；`parse_optional_int` 中文错误提示。
- `app/models/common/page.py`：`PageRequest` 继承 `BaseReqEntity`；`page`/`page_size` 增加 `BeforeValidator` 防御空值/非法字符串；`get_paginated_results` count 改为子查询。
- `core/exception/errors_handler.py`：`validation_exception_handler` 增加 Pydantic error type 中文映射。
- `core/middleware/operation_log_middleware.py`：白名单仅保留 `/admin/sys/export/task/list` 不记录；新增 `WHITELIST_SUFFIXES`/`WHITELIST_PATTERNS` 机制但当前置空，仅用于后续真正的高频轮询接口。
- `core/response/response_code.py`：新增 `USER_DISABLED`。
- `core/websocket/__init__.py`：新增全局 `set_connection_manager` / `get_connection_manager`。
- `main.py`： lifespan 中注册全局 WebSocket manager 并导入 `modules.scheduler.tasks.export_task`。
- `modules/admin/deps/auth/user_manager.py`：`login_by_password` 与 `current_user` 增加 `user.status` 校验。
- `modules/admin/endpoints/sys/export_task.py`：列表接口支持 `status` 筛选，返回标准分页结构。
- `modules/admin/schemas/sys/export_task.py`：继承 `BaseReqEntity`/`BaseRespEntity`。
- `modules/admin/schemas/sys/operation_log.py`：继承 `BaseReqEntity`/`BaseRespEntity`，`user_id` 改用 `OptionalIntField`。
- `modules/admin/schemas/sys/role.py`：`name` 最大 20、`desc` 最大 200，相关请求模型继承 `BaseReqEntity`。
- `modules/admin/services/sys/export_task_service.py`：移除提交后立即执行；新增 `process_pending_tasks`、`timeout_and_cleanup_tasks`、WebSocket 推送。
- `modules/admin/services/sys/operation_log_service.py`：查询追加 `deleted_at.is_(None)`。
- `modules/scheduler/tasks/export_task.py`：新增两个系统级每分钟定时任务。

### 前端

- `service/api/export-task.ts`、`typings/api/export-task.d.ts`：新增导出任务 API 与类型。
- `core/utils/excel_export.py`：`ExportColumn` 新增 `number_format`，`build_excel_bytes` 由 write_only 改为普通模式以应用单元格数值格式。
- `modules/admin/exports/operation_log_export.py`、`role_export.py`、`user_export.py`：`id`/`user_id`/`sort`/`response_code`/`elapsed_ms` 等数值列增加 `number_format`。
- `layouts/modules/global-header/components/export-record-center.vue`：弹窗样式优化，标题旁显示状态图标，completed 任务显示下载图标按钮，头部增加「查看全部」；触发图标增加 `NTooltip` 提示。
- `layouts/modules/global-header/components/notification-center.vue`：触发图标增加 `NTooltip` 提示。
- `views/export-record/index.vue`：全量导出记录列表页。
- `layouts/modules/global-header/index.vue`：引入导出记录组件。
- `hooks/common/websocket.ts`：增加 `export_task` 事件分发。
- `views/log/operation-log/index.vue`：增加异步导出按钮。
- `hooks/common/form.ts`：新增 `createMaxLengthRule`。
- `views/manage/role/modules/role-operate-drawer.vue`：`name`/`desc` 长度校验。
- `locales/langs/zh-cn.ts`、`en-us.ts`：导出记录与角色表单 i18n。
- `router/elegant/routes.ts`、`imports.ts`：手动添加 `export-record` 路由（运行 `pnpm gen-route` 后会自动同步）。
- `service/api/index.ts`：导出 `export-task`。

## 约束与备注

- 导出按钮仅放在「操作日志」页面；导出任务超时阈值：pending 30 分钟、processing 30 分钟、completed/failed 保留 7 天。
- 单实例下 APScheduler `max_instances=1` + 数据库行锁保证不并发；多实例场景建议后续加 Redis 分布式锁。
- 路由文件为手动添加，实际部署前需执行 `pnpm gen-route` 重新生成 elegant-router 类型与路由。
- `BaseReqEntity` 全局 trim 会影响所有请求模型，需重点回归表单提交与查询参数。

## 相关文件

- 后端：`backend/app/models/common/{base,page}.py`、`backend/core/exception/errors_handler.py`、`backend/core/middleware/operation_log_middleware.py`、`backend/core/websocket/__init__.py`、`backend/main.py`、`backend/modules/admin/{deps/auth/user_manager,endpoints/sys/export_task,schemas/sys/{export_task,operation_log,role},services/sys/{export_task,operation_log}}.py`、`backend/modules/scheduler/tasks/export_task.py`
- 前端：`frontend/src/service/api/export-task.ts`、`frontend/src/typings/api/export-task.d.ts`、`frontend/src/layouts/modules/global-header/**`、`frontend/src/views/export-record/index.vue`、`frontend/src/views/log/operation-log/index.vue`、`frontend/src/views/manage/role/modules/role-operate-drawer.vue`、`frontend/src/hooks/common/{form,websocket}.ts`、`frontend/src/router/elegant/{routes,imports}.ts`、`frontend/src/locales/langs/{zh-cn,en-us}.ts`

## 记录日期

2026-07-07
