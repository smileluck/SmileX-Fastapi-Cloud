<!-- last-updated: 2026-06-03 -->
# 多租户 JWT 配置 + 登录自动选择租户

- **日期**: 2026-06-01
- **状态**: 开发中
- **类型**: 功能增强

## 需求描述

增强多租户插件：

1. **租户 JWT 配置**: 每个租户可独立配置 JWT 密钥、签名算法、token 有效期。混合模式：配置了则使用租户配置，未配置则回退到全局配置。
2. **登录自动选择租户**: 用户名密码登录后，自动选择用户的第一个租户（或上次登录的租户）。上次选择的租户通过 Redis + DB 双写持久化。

## 关键决策

- **JWT 混合验证**: `decode_token` 新增 `secret_key`/`algorithm` 可选参数，向后兼容。租户密钥验证由调用方（`verify_token_session`）负责。
- **租户配置存储**: 使用 `sys_tenant.config` JSON Text 列，不新增数据库列。
- **上次租户持久化**: Redis（`USER_LAST_TENANT:{user_id}`）+ `sys_user.last_tenant_id` 双写。
- **中间件兼容**: 全局密钥解码失败时，从未验证 payload 提取 `tenant_id`（中间件仅设置上下文，不做密码学验证）。

## 涉及范围

### 后端

- `plugins/multi_tenant/schemas/tenant_config.py` — 新增 TenantJwtConfig / TenantConfigSchema
- `plugins/multi_tenant/schemas/tenant.py` — TenantCreate/Update/Response 增加 jwt_config
- `plugins/multi_tenant/services/tenant_service.py` — JWT config 解析/缓存，last tenant 持久化
- `core/security/oauth/jwt.py` — create/decode 方法支持 per-tenant key/algorithm/lifetime
- `core/security/oauth/user_manager.py` — create_token 支持 secret_key/algorithm/access_lifetime + extra_claims
- `modules/admin/deps/auth/user_manager.py` — 登录自动选择租户 + 混合验证
- `modules/admin/schemas/auth.py` — LoginResponseData 增加 tenant_id/tenants
- `plugins/multi_tenant/endpoints/auth.py` — select-tenant 使用租户 JWT 配置 + 保存 last tenant
- `plugins/multi_tenant/middleware/tenant_middleware.py` — 兼容租户签名 token
- `database/models/sys/user.py` — 新增 last_tenant_id 列
- `alembic/versions/h1i2j3k4l5m6_add_last_tenant_id_to_sys_user.py` — 迁移

## 记录日期

2026-06-01
