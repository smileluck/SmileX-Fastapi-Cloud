<!-- last-updated: 2026-10-02 -->
# API 限流 / IP 黑名单

## 需求描述

基于 Redis 在中间件层为后端接口增加多维度限流和 IP 黑名单能力，防止暴力破解和接口滥用；黑名单可由后台管理界面维护或在登录连续失败时自动加入。

## 状态

已完成（含第二阶段：动态配置 + 前端管理页）

## 涉及范围

### 后端

- 配置：`core/config/settings_model.py` 新增 `RateLimitModel`、`RateLimitPathRuleModel`；`core/config/settings.py` 挂载 `RATE_LIMIT`
- 中间件：`core/middleware/rate_limit_middleware.py`，在 `core/registry/setup_registry.py` 中注册
- 限流工具：`core/security/rate_limit.py` 扩展黑名单、登录失败计数、多维度限流函数
- 模型：`database/models/sys/ip_blacklist.py` (`SysIpBlacklist`)
- Schema：`modules/admin/schemas/sys/ip_blacklist.py`
- Service：
  - `modules/admin/services/sys/ip_blacklist_service.py`（CRUD + warmup + auto_block）
  - `modules/admin/services/sys/rate_limit_service.py`（登录失败统计、warmup 入口）
- Endpoint：`modules/admin/endpoints/sys/ip_blacklist.py`（`/admin/sys/ip-blacklist/...`）
- 入口：`main.py` lifespan 调用 `RateLimitService.warmup_blacklist()`
- 登录失败接入：`modules/admin/endpoints/auth.py` 登录失败/成功分支调用 `record_login_failure` / `clear_login_failure`
- 错误码：`error_codes.md` + `core/response/response_code.py` 新增 `RATE_LIMIT_EXCEEDED(10901)`、`IP_BLOCKED(10902)`
- 动态配置：`core/security/rate_limit_config.py`（RateLimitConfigProvider，30s TTL 内存缓存，从 SysConfig 读 rate_limit.* 配置）
- 缓存失效：`modules/admin/services/sys/config_service.py` 写操作触发 `RateLimitConfigProvider.invalidate()`
- 迁移：`alembic/versions/a3b4c5d6e7f8_seed_ip_blacklist_menu_and_config.py`（菜单 + 按钮权限 + rate_limit 默认配置行）

### 前端

- 页面：`views/manage/ip-blacklist/`（index.vue + search + drawer）
- API：`frontend/src/service/api/system-manage.ts`（4 个 API 函数）
- 类型：`frontend/src/typings/api/system-manage.d.ts`（IpBlacklist + search + create + batch delete）
- i18n：`zh-cn.ts` / `en-us.ts` 的 `page.manage.ipBlacklist` 键 + `route.manage_ip-blacklist`
- 路由：elegant-router 自动注册 `manage_ip-blacklist`

## 约束与备注

- 中间件返回 429 时使用项目统一响应结构 `{code, msg, data, request_id, err_code}`，附加 `Retry-After` 头
- Redis 故障时中间件**失败放行**，避免雪崩；黑名单同步失败仅记录日志
- 永久黑名单也带有兜底 TTL（`BLACKLIST_REDIS_TTL`），到期由下次 warmup 重新写入
- 限流维度顺序：IP 黑名单 → 全局 IP → 用户 → 路径细粒度；任一命中即 429
- 权限点：`sys:blacklist:list / add / remove`，菜单与角色绑定由 DBA / 菜单管理界面维护，不在代码中自动注入

## 相关文件

- `backend/core/config/settings_model.py`
- `backend/core/config/settings.py`
- `backend/core/security/rate_limit.py`
- `backend/core/middleware/rate_limit_middleware.py`
- `backend/core/registry/setup_registry.py`
- `backend/core/response/response_code.py`
- `backend/database/models/sys/ip_blacklist.py`
- `backend/modules/admin/schemas/sys/ip_blacklist.py`
- `backend/modules/admin/services/sys/ip_blacklist_service.py`
- `backend/modules/admin/services/sys/rate_limit_service.py`
- `backend/modules/admin/endpoints/sys/ip_blacklist.py`
- `backend/modules/admin/endpoints/sys/__init__.py`
- `backend/modules/admin/endpoints/auth.py`
- `backend/main.py`
- `error_codes.md`

## 记录日期

2026-05-24
