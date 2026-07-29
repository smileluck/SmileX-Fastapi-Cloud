# 前后端边界与数据契约

## 责任边界

| 层面 | 后端负责 | 前端负责 |
|------|----------|----------|
| 数据验证 | 请求参数校验、业务规则验证 | 表单验证、输入格式化 |
| 业务逻辑 | 全部业务逻辑 | 仅页面交互逻辑 |
| 数据存储 | 数据库读写、缓存管理 | 本地存储（localStorage） |
| 响应结构 | 统一响应格式 | 响应解析与展示 |
| 状态管理 | 会话状态（Redis） | 页面状态（Pinia） |
| 路由 | API 路由注册 | 页面路由与守卫 |

共享行为通过明确的 API 契约实现，不依赖隐式耦合。

---

## 统一响应结构

### 普通响应

```json
{
  "code": 200,
  "msg": "成功",
  "data": { ... },
  "request_id": "uuid-string",
  "err_code": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | `number` | HTTP 状态码 |
| `msg` | `string` | 响应消息 |
| `data` | `T \| null` | 响应数据 |
| `request_id` | `string \| null` | 请求追踪 ID |
| `err_code` | `number \| null` | 业务错误码 |

### 分页响应

```json
{
  "code": 200,
  "msg": "成功",
  "data": {
    "records": [ ... ],
    "page": 1,
    "page_size": 10,
    "total": 100,
    "total_pages": 10
  },
  "request_id": "uuid-string",
  "err_code": null
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `records` | `T[]` | 当前页数据 |
| `page` | `number` | 当前页码（从 1 开始） |
| `page_size` | `number` | 每页条数（最大 200） |
| `total` | `number` | 总记录数 |
| `total_pages` | `number` | 总页数 |

---

## 字段命名

- API 请求和响应中字段名统一使用 `snake_case`
- 前端 TypeScript 类型定义与后端字段名保持一致
- 示例：`created_at`、`page_size`、`user_name`

---

## Status 字段桥接

这是前后端类型转换中最关键的约定。

### 转换流程

```
前端（展示/编辑）          后端（存储/逻辑）
"1" / "2"                True / False
    │                        │
    │ 前端发送请求            │ 数据库存储
    │ enableStatusToBoolean()│
    ├───────────────────────>│ bool
    │                        │
    │ 前端接收响应            │ BaseRespEntity 序列化
    │                        │ @field_serializer("status")
    │<───────────────────────┤ "1" / "2"
```

### 后端处理

- **存储类型**：`bool`（`True` = 启用，`False` = 禁用）
- **反序列化**（前端→后端）：`BoolField` 使用 `parse_bool` 处理
  - `"1"` / `"true"` / `"yes"` → `True`
  - `"2"` / `"false"` / `"no"` → `False`
  - 空值 → `None`
- **序列化**（后端→前端）：`BaseRespEntity` 的 `@field_serializer("status")`
  - `True` → `"1"`
  - `False` → `"2"`
- 定义位置：`modules/common/schemas/base.py`

### 前端处理

- **TypeScript 类型**：`EnableStatus`（`"1" | "2"`）
- **发送请求时**：使用 `enableStatusToBoolean()` 将 `"1"`/`"2"` 转为 `boolean`
- **接收响应时**：后端已自动转换为 `"1"`/`"2"` 字符串
- **转换函数**：`src/utils/status.ts`

### `is_system` 字段

与 `status` 字段处理方式相同：`BaseRespEntity` 自动序列化 `is_system`（`True` → `"1"`，`False` → `"2"`）。

---

## 时间字段桥接

### 后端 → 前端（响应序列化）

| 层面 | 类型 | 格式 |
|------|------|------|
| 后端数据库 | `datetime`（带时区） | UTC 存储 |
| 后端序列化 | `string` | `Asia/Shanghai`，`YYYY-MM-DD HH:mm:ss` |
| 前端接收 | `string` | `YYYY-MM-DD HH:mm:ss` |

序列化由 `BaseEntity` 的 `json_encoders` 自动处理（`modules/common/schemas/base.py`）。

### 前端 → 后端（请求参数）

| 层面 | 类型 | 格式示例 |
|------|------|----------|
| 前端选择 | `number`（时间戳） | NDatePicker 返回毫秒时间戳 |
| 前端发送 | `string` | `2026-05-21T16:39:23+08:00`（本地时间 + 时区偏移） |
| 后端解析 | `datetime` | `fromisoformat()` → `astimezone(UTC)` → UTC datetime |

**强制规则**：

1. **前端发送时间参数时，必须携带时区偏移**：使用 `dayjs(val).format()` 生成 `YYYY-MM-DDTHH:mm:ssZ` 格式（如 `+08:00`），禁止使用 `new Date(val).toISOString()` —— 后者会转为 UTC 导致与用户选择不一致
2. **后端解析时间参数时，必须区分有无时区**：
   ```python
   dt = datetime.fromisoformat(time_str)
   result = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
   ```
   禁止直接使用 `.replace(tzinfo=timezone.utc)` —— 对带时区偏移的字符串会丢失转换

**原因**：用户在前端选择 `2026-05-21 16:39:23`，API 传参也应体现为 `16:39:23+08:00`，而非 UTC 时间 `08:39:23Z`。

---

## 数据权限（行级可见性）

### 后端

- `SysRole.data_scope` 字段：枚举 `DataScopeEnum`（`ALL` / `DEPT_AND_SUB` / `DEPT_ONLY` / `SELF`），默认 `SELF`，序列化为字符串
- `SysUser.dept_id` 字段：可空外键，关联 `sys_dept.id`
- `DataScopeService.get_effective_scope(db, user)`：聚合用户角色的 data_scope，返回 `DataScopeEnum | None`（None=不限，超管/含 ALL 角色）
- `DataScopeService.get_permitted_dept_ids(db, user, scope)`：返回 `set[int] | None`
  - `None` → 不加任何 dept 过滤（ALL/超管）
  - 空集合 → Service 走 `where(id == user.id)`（SELF）
  - 非空集合 → Service 走 `where(dept_id.in_(...))`（DEPT_AND_SUB / DEPT_ONLY）

### 前端

- `Api.SystemManage.DataScope` 类型：`'ALL' | 'DEPT_AND_SUB' | 'DEPT_ONLY' | 'SELF'`
- 角色编辑表单使用 `NRadioGroup` 单选数据范围；提交时直接传字符串（后端 pydantic 接收 `DataScopeEnum`）
- 用户编辑表单使用 `NTreeSelect` 选择部门，提交 `dept_id: number | null`

### 接入新模块的方式

业务模块要接入数据权限，需在 Service 的 `build_*_query()` 增加：
```python
def build_xxx_query(
    query_params,
    *,
    data_scope: DataScopeEnum | None = None,
    permitted_dept_ids: set[int] | None = None,
    current_user_id: int | None = None,
) -> Select:
    # ... 原有过滤 ...
    if data_scope == DataScopeEnum.SELF:
        base_query = base_query.where(Xxx.created_by == current_user_id)
    elif permitted_dept_ids is not None:
        base_query = base_query.where(Xxx.dept_id.in_(permitted_dept_ids))
    return base_query
```

Endpoint 注入 `current_user` 后调用 `DataScopeService` 算出 scope 与 permitted_dept_ids，传给 Service。

---

## 开放API（商户 HMAC 签名鉴权）

`/open/*` 路由面向第三方系统，**不走** 后台管理员 JWT 鉴权与操作日志中间件（`OperationLogMiddleware` 只作用于 `/admin/*`），改用商户 `app_id/app_secret` 的 HMAC-SHA256 签名鉴权。后台管理侧（`/admin/sys/merchant/*`）仍是普通 JWT + 权限码管理。

### 签名请求头

| Header | 说明 |
|---|---|
| `X-App-Id` | 商户 AppId |
| `X-Timestamp` | 秒级 Unix 时间戳（允许偏移见 `OPEN_API__TIMESTAMP_TOLERANCE_SECONDS`，默认 300s） |
| `X-Nonce` | 客户端随机串，8-64 字符，TTL 内（`OPEN_API__NONCE_TTL`，默认 600s）不可复用 |
| `X-Signature` | HMAC-SHA256 hex 小写 |

### Canonical String（客户端必须严格复现）

6 段以 `\n` 连接，顺序固定，body 为空时第 6 段为空串（末尾保留 `\n`）：

```
METHOD \n PATH \n timestamp \n nonce \n app_id \n sha256(body).hexdigest()
```

- `PATH` 用 `request.url.path`，**不含 query string**
- 完整契约见 `backend/core/security/openapi/signature.py` 模块 docstring

### 商户凭据

- `app_id` 公开标识；`app_secret` 在库中以 Fernet 加密存储（验签需原始值，不能单向哈希），密钥 `OPEN_API__SECRET_ENCRYPT_KEY`
- 明文 `app_secret` **仅在创建/重置密钥时一次性返回**，前端弹窗强提示保存；此后不可查询，只能重置
- 后台响应 `SysMerchantResponseData` 继承 `BaseRespEntity`，`status` 已序列化为 `"1"/"2"`，前端列表无需再做 bool 转换

### 错误码（`err_code`，区间 11021-11030）

`/open/*` 鉴权错误经独立的 `OpenApiError` + `openapi_error_handler` 处理，映射到语义正确的 4xx HTTP 状态（响应结构仍是统一 `{code, msg, data, request_id, err_code}`，只是 `code` = HTTP 状态码而非 500）。日志用 `warning` 级，不污染 5xx 错误率统计。

| err_code | HTTP | 含义 |
|---|---|---|
| 11021 | 401 | 缺少必要的签名请求头 |
| 11022 | 401 | 请求时间戳超出允许范围 |
| 11023 | 400 | Nonce 非法（格式/长度） |
| 11024 | 401 | 请求不可重放（Nonce 已被使用） |
| 11025 | 401 | AppId 不存在 |
| 11026 | 403 | 商户已禁用 |
| 11027 | 401 | 签名校验失败 |

后台管理侧的 11028（商户不存在）/ 11029（商户编码已存在）/ 11030（AppId 冲突）仍走 `CustomError`（HTTP 500 + body err_code），与 captcha/rate-limit 等现有模块一致，前端按 `err_code` 判断。

---

## 文件预览鉴权（preview token）

`GET /admin/sys/file/{id}/preview` 供 `<img>/<video>` 直接通过 src 访问，浏览器不会携带 `Authorization` 头，因此**不能复用 access token**（否则令牌会进入 URL 日志/Referer 造成泄露）。改为两步：

1. **换令牌**：前端先调 `POST /admin/sys/file/{id}/preview-token`（需登录 + `sys:file:list` 权限），后端签发**短期（默认 5 分钟）、绑定 file_id** 的预览令牌（JWT，`scope=preview`），返回 `{ preview_token, expires_in }`。
2. **访问预览**：前端以 `GET /admin/sys/file/{id}/preview?token=<preview_token>` 访问；后端校验 `scope=preview` 且 token 内 `file_id` 与 URL 一致，否则返回 401/403。

| 项 | 值 |
|---|---|
| 换令牌接口 | `POST /admin/sys/file/{id}/preview-token` |
| 响应 data | `{ preview_token: string, expires_in: number }`；有效期由后端 `JWT__PREVIEW_TOKEN_EXPIRES` 配置（默认 300 秒） |
| 预览接口鉴权 | query `token`，需 `scope=preview` + file_id 绑定 |
| 前端封装 | `fetchGetPreviewToken`、`getFilePreviewUrl(fileId, previewToken)`（`src/service/api/file.ts`）；组件 `views/manage/file/modules/file-preview-modal.vue` 打开时异步换 token |
| 已知妥协 | 预览令牌有效期内即使用户登出仍可用（短 exp 缓解；强一致需 preview_file 内查 Redis session） |

前端调用点必须**先换 token 再拼 URL**，禁止直接把 access token 放进 preview URL。

---

## 变更规则

- 破坏性接口变更（字段名/类型/结构改变）必须记录变更说明
- Swagger 注释必须与真实实现保持一致
- 前端 API 封装统一放在 `src/service/api/`
- 跨栈变更必须同步更新 `aiDoc/frontend-backend/` 下的文档

## 完成前检查清单

- [ ] 后端响应结构与前端类型定义匹配
- [ ] 字段名 `snake_case` 一致
- [ ] Status 字段桥接正确（`enableStatusToBoolean()` + `BaseRespEntity` 序列化）
- [ ] 时间字段格式正确（`YYYY-MM-DD HH:mm:ss`）
- [ ] Swagger 注释与实现一致
- [ ] 分页参数和返回格式符合 `ResponsePageModel` 规范
