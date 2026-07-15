# 项目记忆索引

本文件是 `aiDoc/memory/` 的总入口。

## 长期记忆

暂无。

## 业务需求记忆

详细索引见 [business/README.md](./business/README.md)。近期：

- [2026-07-15 关于我们页面（前端常驻路由 + 构建时 Git 历史）](./business/2026-07-15_about_page.md) — 左右布局：左项目介绍，右 NTimeline 展示 Git 提交；about 经 `onRouteMetaGen` 标 constant 进侧边栏固定菜单（不走动态菜单）；Git 历史由自研 vite 插件构建时采集、经 virtual module 暴露，无 git 空态；纯前端不动后端
- [2026-07-14 密码复杂度策略：6-20 位且至少含字母+数字](./business/2026-07-14_password_complexity_policy.md) — 收紧 REG_PWD 用于写入侧，登录改仅非空；后端加 validator（修 new_password max 100→20）
- [2026-07-14 调度器时区修复 + create_superuser naive 时间](./business/2026-07-14_scheduler_timezone_fix.md) — APScheduler/cron 默认按服务器本地时区，UTC 服务器偏移 8h；三处显式固定 Asia/Shanghai
- [2026-07-14 用户编辑保存角色不生效修复](./business/2026-07-14_user_list_roles_for_edit.md) — 列表响应 SysUserListResponse 缺 roles，编辑抽屉无法回填 → 保存提交 role_ids:[] 清空角色；补 roles 字段（selectinload 已有，零额外查询）
- [2026-07-13 新建商户「数据校验错误」修复](./business/2026-07-13_merchant_create_validation_fix.md) — SysMerchantWithSecret.app_secret 必填导致 model_validate(ORM) 抛 ValidationError；改 default=""
- [2026-07-13 开放API测试页 crypto.subtle 报错修复](./business/2026-07-13_openapi_test_crypto_subtle_fallback.md) — HTTP/局域网下 crypto.subtle 为 undefined；新增 hmac-sha256 util（原生优先 + 纯 JS 回退）
- [2026-07-13 启动时打印日志文件落地位置](./business/2026-07-13_print_log_location_on_startup.md) — setup_logging() 动态读取文件 handler，打印日志目录/文件/归档子目录
- [2026-07-13 i18n Schema 补全 + 类型清理](./business/2026-07-13_i18n_schema_and_type_cleanup.md) — app.d.ts 补 exportTask 等；修 dict/blob/角色选择 value/number[]/bordered；typecheck 38→0
- [2026-07-13 操作日志白名单补充高频轮询接口](./business/2026-07-13_operation_log_whitelist_polling.md) — 白名单追加 route / notice-my 读；写操作与业务列表保留
- [2026-07-13 表格空字段统一显示为 "-"](./business/2026-07-13_table_empty_cell_placeholder.md) — table hook getColumns 注入默认 render，16 表自动生效；menu 手工补
- [2026-07-13 导出记录弹窗状态标识优化 + 查看全部路由修复](./business/2026-07-13_export_record_ui_and_constant_route.md) — 弹窗状态改 NTag（绿成功/红失败/黄生成中/灰排队）+ 下载按钮补 i18n 文本；export-record 纳入 constant 路由
- [2026-07-11 本地 .log 日志按日期目录滚动](./business/2026-07-11_rolling_logs_by_date.md) — Python 应用日志与 Gunicorn access/error 日志统一按 `YYYY-MM-DD/` 目录滚动
- [2026-07-05 商户管理 + 开放API HMAC 签名鉴权](./business/2026-07-05_merchant_openapi_auth.md) — sys_merchant 表 + 后台 CRUD/重置密钥 + /open/* HMAC-SHA256 签名校验 + /open/demo/ping 示例
- [2026-07-04 用户/角色管理缺陷修复 + 提交类型约束加固](./business/2026-07-04_user_role_manage_hardening.md) — 角色重名查重、create_user 加载 roles 修复 422、前端 flat-request 错误处理、User/Role 请求类型、Dict is_system 对齐、schema 校验加固
- [2026-07-07 异步导出、全局校验、角色表单与登录禁用优化](./business/2026-07-07_export_validation_login_disable.md) — 头部导出记录入口 + 操作日志异步导出 + APScheduler 定时执行/超时清理、WebSocket+轮询状态同步、全局请求参数 trim 与整数防御、角色前后端校验、禁用用户登录拦截、操作日志 total 修复

## 维护说明

- 新增记忆时，在对应目录创建 Markdown 文件，并在此索引中添加条目
- 过时的记忆应及时清理
- 记忆文件应包含日期标记，便于判断时效性
