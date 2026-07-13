# 项目记忆索引

本文件是 `aiDoc/memory/` 的总入口。

## 长期记忆

暂无。

## 业务需求记忆

详细索引见 [business/README.md](./business/README.md)。近期：

- [2026-07-13 新建商户「数据校验错误」修复](./business/2026-07-13_merchant_create_validation_fix.md) — SysMerchantWithSecret.app_secret 必填导致 model_validate(ORM) 抛 ValidationError；改 default=""
- [2026-07-13 开放API测试页 crypto.subtle 报错修复](./business/2026-07-13_openapi_test_crypto_subtle_fallback.md) — HTTP/局域网下 crypto.subtle 为 undefined；新增 hmac-sha256 util（原生优先 + 纯 JS 回退）
- [2026-07-13 启动时打印日志文件落地位置](./business/2026-07-13_print_log_location_on_startup.md) — setup_logging() 动态读取文件 handler，打印日志目录/文件/归档子目录
- [2026-07-13 导出记录弹窗状态标识优化 + 查看全部路由修复](./business/2026-07-13_export_record_ui_and_constant_route.md) — 弹窗状态改 NTag（绿成功/红失败/黄生成中/灰排队）+ 下载按钮补 i18n 文本；export-record 纳入 constant 路由
- [2026-07-11 本地 .log 日志按日期目录滚动](./business/2026-07-11_rolling_logs_by_date.md) — Python 应用日志与 Gunicorn access/error 日志统一按 `YYYY-MM-DD/` 目录滚动
- [2026-07-05 商户管理 + 开放API HMAC 签名鉴权](./business/2026-07-05_merchant_openapi_auth.md) — sys_merchant 表 + 后台 CRUD/重置密钥 + /open/* HMAC-SHA256 签名校验 + /open/demo/ping 示例
- [2026-07-04 用户/角色管理缺陷修复 + 提交类型约束加固](./business/2026-07-04_user_role_manage_hardening.md) — 角色重名查重、create_user 加载 roles 修复 422、前端 flat-request 错误处理、User/Role 请求类型、Dict is_system 对齐、schema 校验加固
- [2026-07-07 异步导出、全局校验、角色表单与登录禁用优化](./business/2026-07-07_export_validation_login_disable.md) — 头部导出记录入口 + 操作日志异步导出 + APScheduler 定时执行/超时清理、WebSocket+轮询状态同步、全局请求参数 trim 与整数防御、角色前后端校验、禁用用户登录拦截、操作日志 total 修复

## 维护说明

- 新增记忆时，在对应目录创建 Markdown 文件，并在此索引中添加条目
- 过时的记忆应及时清理
- 记忆文件应包含日期标记，便于判断时效性
