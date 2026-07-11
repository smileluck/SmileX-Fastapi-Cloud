# 项目记忆索引

本文件是 `aiDoc/memory/` 的总入口。

## 长期记忆

暂无。

## 业务需求记忆

详细索引见 [business/README.md](./business/README.md)。近期：

- [2026-07-11 本地 .log 日志按日期目录滚动](./business/2026-07-11_rolling_logs_by_date.md) — Python 应用日志与 Gunicorn access/error 日志统一按 `YYYY-MM-DD/` 目录滚动
- [2026-07-05 商户管理 + 开放API HMAC 签名鉴权](./business/2026-07-05_merchant_openapi_auth.md) — sys_merchant 表 + 后台 CRUD/重置密钥 + /open/* HMAC-SHA256 签名校验 + /open/demo/ping 示例
- [2026-07-04 用户/角色管理缺陷修复 + 提交类型约束加固](./business/2026-07-04_user_role_manage_hardening.md) — 角色重名查重、create_user 加载 roles 修复 422、前端 flat-request 错误处理、User/Role 请求类型、Dict is_system 对齐、schema 校验加固
- [2026-07-07 异步导出、全局校验、角色表单与登录禁用优化](./business/2026-07-07_export_validation_login_disable.md) — 头部导出记录入口 + 操作日志异步导出 + APScheduler 定时执行/超时清理、WebSocket+轮询状态同步、全局请求参数 trim 与整数防御、角色前后端校验、禁用用户登录拦截、操作日志 total 修复

## 维护说明

- 新增记忆时，在对应目录创建 Markdown 文件，并在此索引中添加条目
- 过时的记忆应及时清理
- 记忆文件应包含日期标记，便于判断时效性
