# 商户管理 + 开放API HMAC 签名鉴权

## 需求描述

为第三方系统提供标准的开放 API 接入能力：管理员在后台创建"商户"并签发 `app_id` / `app_secret` 凭据，第三方使用这对凭据对每个请求做 HMAC-SHA256 签名，服务端校验签名 + 时间戳窗口 + Redis 原子 nonce 防重放后放行。

确认的设计选项：HMAC-SHA256 签名方案；单商户单密钥 + 支持轮换（重置）；**不**绑定多租户（扁平 `sys_merchant` 表）；本次含 1 个示例开放接口 `/open/demo/ping`。

## 状态

已完成

## 签名契约（第三方接入必须严格复现）

请求头：`X-App-Id` / `X-Timestamp`（秒级 Unix 时间戳）/ `X-Nonce`（8-64 字符随机串）/ `X-Signature`（hex 小写）

Canonical String，6 段以 `\n` 连接，顺序固定：

```
METHOD \n PATH \n timestamp \n nonce \n app_id \n sha256(body).hexdigest()
```

- `METHOD`：HTTP 方法大写
- `PATH`：`request.url.path`，**不含 query string**
- 第 6 段：请求 body 字节的 sha256 hex；body 为空时为空串（canonical 末尾保留 `\n`）

`signature = HMAC_SHA256(app_secret, canonical).hexdigest()`。完整契约文档化在 `core/security/openapi/signature.py` 模块 docstring。

## 涉及范围

### 后端

- 配置：`core/config/settings_model.py` 新增 `OpenApiModel`，`core/config/settings.py` 挂载 `OPEN_API`（字段 `SECRET_ENCRYPT_KEY` / `TIMESTAMP_TOLERANCE_SECONDS` / `NONCE_TTL` / `APP_ID_PREFIX`）。**注意**：实际加载的 env 文件是 `.env.dev`（loader 用 `.env.{ENVIR}`），不是 `.env`
- 安全工具：`core/security/openapi/`（`crypto.py` 凭据生成 + Fernet 可逆加密；`signature.py` canonical + HMAC 校验）
- 模型：`database/models/sys/merchant.py` (`SysMerchant`)，`app_secret` 以 Fernet 加密 token 存储（验签需原始 secret，不能单向哈希）；已注册到 `database/models/sys/__init__.py` 与 `alembic/env.py`
- 内存缓存：`core/utils/memory_cache.py` `CacheNamespace.MERCHANT`（按 app_id 缓存 `{id,name,app_id,status,app_secret_encrypted}`，30s TTL，**不缓存明文**，每请求内联解密）
- Schema：`modules/admin/schemas/sys/merchant.py`（含 `SysMerchantWithSecret` / `SysMerchantSecretResetResponse`）
- Service：`modules/admin/services/sys/merchant_service.py` (`MerchantService`)；明文 secret 仅 create/reset 时返回一次
- 后台接口：`modules/admin/endpoints/sys/merchant.py`（`/admin/sys/merchant/...`：list/get/add/put/delete + `/{id}/reset-secret`），权限码 `sys:merchant:list/add/edit/delete/reset-secret`
- 开放API 模块（新增）：`modules/openapi/`（`router.py` 前缀 `/open`，`endpoints/demo.py`，`deps/signature_auth.py` 的 `current_merchant` 依赖）；已在 `main.py` 挂载
- Redis 防重放：用 `RedisPool.get_client().set(key, "1", ex=NONCE_TTL, nx=True)`（**不可用** `core/redis/async_redis.py`，该模块引用了未定义的 `RedisSettings`，是仓库现存坏文件；统一用 `core/redis/redis_pool.py`）
- 错误码：`core/response/response_code.py` 新增 `OPEN_API_*` / `MERCHANT_*`（11021-11030）
- 迁移：`alembic/versions/0008_merchant_openapi.py`（建表 + 幂等播种 manage_merchant 菜单与按钮，关联 `ADMIN_ROLE_ID`，与 0006 同款写法）
- 依赖：`pyproject.toml` 显式新增 `cryptography>=42.0.0`

### 前端

- 页面：`views/manage/merchant/`（`index.vue` 分页表格 + `modules/merchant-search.vue` + `modules/merchant-operate-drawer.vue` + `modules/merchant-secret-result-modal.vue`，密钥一次性弹窗 + 复制按钮 + 警告）
- API：`src/service/api/system-manage.ts` 新增 6 个函数（list/get/create/update/delete + reset-secret）
- 类型：`src/typings/api/system-manage.d.ts`（`Merchant` / `MerchantSearchParams` / `MerchantCreate` / `MerchantUpdate` / `MerchantCreateResult` / `MerchantSecretResetResult`）
- i18n：`zh-cn.ts` / `en-us.ts` 的 `page.manage.merchant.*` + `route.manage_merchant`
- Schema 类型：`src/typings/app.d.ts` 的 `Schema` 增 `merchant` 块（I18nKey 由此派生，必须手改）
- 路由：elegant-router 自动注册 `view.manage_merchant`；本次已同步手改 4 个生成文件（`elegant-router.d.ts` / `imports.ts` / `routes.ts` / `transform.ts`），dev/build 会以相同内容覆盖

## 约束与备注

- `app_secret` 必须可逆加密（HMAC 验签需原始值）；用 Fernet，密钥 `OPEN_API__SECRET_ENCRYPT_KEY` 生产必须替换
- 明文 secret 仅在创建/重置时一次性返回，前端弹窗强提示保存；此后不可查询，只能重置
- nonce 防重放：Redis `SET NX EX`，TTL 须 > 时间戳容差；同一 (app_id, nonce) 在 TTL 内不可复用
- 开放接口 `/open/*` 天然不经过 `OperationLogMiddleware`（只作用于 `/admin/*`），仍受 `RequestAuditMiddleware`(request_id) / `RateLimitMiddleware` 全局约束
- **错误控制已独立化**：`/open/*` 鉴权失败用 `OpenApiError`（`core/exception/errors.py`）+ `openapi_error_handler`（`errors_handler.py`），err_code 映射到语义正确的 4xx（缺头/时间戳/重放/AppId不存在/签名错 → 401；nonce 非法 → 400；商户禁用 → 403），响应结构仍是统一 `{code,msg,data,request_id,err_code}`，日志走 `warning` 不污染 5xx 告警。后台管理侧 11028-11030 仍是 `CustomError`/500
- ADMIN_ROLE_ID 在迁移里条件插入 role_menu；本仓库该 ID 实际不存在（与 dept 同），菜单已播种，靠超管或手动绑角色生效
- 现存坏文件 `core/redis/async_redis.py`（`RedisSettings` 未定义）未被应用加载，勿引用

## 相关文件

- `backend/core/security/openapi/{crypto,signature,__init__}.py`
- `backend/database/models/sys/merchant.py`
- `backend/modules/admin/{schemas,services,endpoints}/sys/merchant.py`
- `backend/modules/openapi/{router.py,endpoints/demo.py,deps/signature_auth.py}`
- `backend/alembic/versions/0008_merchant_openapi.py`
- `backend/.env.dev`（OPEN_API 配置）
- `frontend/src/views/manage/merchant/`
- `frontend/src/service/api/system-manage.ts`
- `frontend/src/typings/{api/system-manage.d.ts, app.d.ts}`

## 记录日期

2026-07-05

---

## 迭代（2026-07-05）：商户开放管理目录 + 开放API调用日志

### 新增/变更

- **新增顶级目录菜单 `merchant-open`（商户开放管理）**：把 `merchant-open_merchant`（原 `manage_merchant`）从 `manage` 目录移到该目录下；前端 .vue 文件同步迁到 `views/merchant-open/merchant/`。elegant-router 由目录名生成路由名时**保留连字符**：目录 `merchant-open/` → 路由前缀 `merchant-open`，子级用下划线分隔（`merchant-open_merchant`、`merchant-open_openapi-log`）。**后端菜单 name 与 component 必须与前端生成的路由名严格一致**（含连字符），否则点击菜单 `router.push({name})` 报 `No match`
- **新增 `sys_openapi_log` 表与 `OpenapiLogMiddleware`**：记录每次 `/open/*` 调用（app_id、method、path、status_code、err_code、msg、client_ip、request_id、latency_ms、merchant_name 冗余）。鉴权失败也记录。中间件用 `BackgroundTask` 在响应发出后异步落库，不阻塞响应；通过缓冲 `body_iterator` 重新打包 Response 来可靠读取 err_code/msg（BaseHTTPMiddleware 默认拿到的是流式响应，`.body` 不可读）
- **后台查询接口**：`/admin/sys/openapi-log/list`、`/{id}`、`/batch`、`/{id}` DELETE，权限码 `sys:openapi-log:list` / `sys:openapi-log:delete`
- **迁移 `0009_openapi_log_and_dir.py`**：建表 + 建目录菜单 + 移动并重命名 merchant 菜单（name/component/path）+ 播种 openapi-log 菜单与按钮

### 关键约束

- elegant-router 类型系统按命名前缀推导父子（`GetChildRouteKey`），且子级 key 不得再含下划线 → 新建目录必须用 `views/<dir>/` 真实目录，子页面用连字符命名（参考 `log_login-log`）
- alembic.ini 不得含中文注释（Windows configparser 默认 GBK，会编解码失败）；同目录迁移/重命名需注意菜单 `parent_id` 外键：先插父目录再 UPDATE 子菜单
- `BaseHTTPMiddleware` 里读响应 body 必须缓冲 `body_iterator` 并重新打包 Response，否则异常处理器返回的响应读不到 err_code

