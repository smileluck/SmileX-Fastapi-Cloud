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
- 定义位置：`app/models/common/base.py`

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

序列化由 `BaseEntity` 的 `json_encoders` 自动处理（`app/models/common/base.py`）。

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
