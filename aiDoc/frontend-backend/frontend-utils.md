<!-- last-updated: 2026-10-02 -->
# 前端工具函数复用规则

## 核心原则

开发任何前端功能前，**必须**先检查并复用现有工具函数。禁止在页面或组件中重复实现已有能力。

---

## 应用级工具（`frontend/src/utils/`）

### Status 转换（强制使用）

- `frontend/src/utils/status.ts`
- `enableStatusToBoolean()`：`"1"`/`"2"` → `boolean`，**所有向后端发送 status 字段的场景必须使用**
- `booleanToEnableStatus()`：`boolean` → `"1"`/`"2"`

### 本地存储（强制使用）

- `frontend/src/utils/storage.ts`
- `localStg`：类型安全的 localStorage 封装，**所有本地存储操作必须使用**

### 其他工具

| 文件 | 说明 |
|------|------|
| `frontend/src/utils/common.ts` | 通用辅助函数 |
| `frontend/src/utils/icon.ts` | 图标处理 |
| `frontend/src/utils/service.ts` | `getServiceBaseURL()` 等服务相关工具 |
| `frontend/src/utils/agent.ts` | Agent 相关工具 |

---

## 工作区子包（`packages/`）

### `@sa/axios`（强制使用）

- 所有 HTTP 请求**必须**通过此包封装的请求方法
- 提供 `createFlatRequest`、`createRequest` 等工厂方法
- 内置拦截器、错误处理、Token 管理

### `@sa/utils`

| 导出 | 说明 | 使用场景 |
|------|------|----------|
| `crypto` | 加密工具 | 敏感数据处理 |
| `nanoid` | 唯一 ID 生成 | 需要前端生成唯一标识时**必须使用** |
| `klona` | 深拷贝 | 需要深拷贝对象时**必须使用** |
| `storage` | 存储工具 | 底层存储操作 |

### `@sa/hooks`

- Vue 组合式函数库
- 实现通用 UI 交互逻辑时先查看此包是否有现成的 Hook

### `@sa/materials`

- UI 组件库
- 实现通用 UI 模式时先查看此包是否有现成组件

### `@sa/color`

- 颜色工具函数
- 主题和颜色相关操作使用此包

### `@sa/uno-preset`

- UnoCSS 预设规则
- 通过 `uno.config.ts` 引用，不直接在页面中使用

### `@sa/alova`

- Alova 请求库封装
- 如需使用 Alova 替代 Axios，使用此包

### `@sa/scripts`

- 构建与开发脚本
- 通过 `pnpm` 命令调用

---

## 强制使用场景清单

| 场景 | 必须使用的工具 |
|------|---------------|
| HTTP 请求 | `@sa/axios`（通过 `frontend/src/service/request/`） |
| Status 字段转换（前端→后端） | `enableStatusToBoolean()`（`frontend/src/utils/status.ts`） |
| Status 字段转换（后端→前端） | `booleanToEnableStatus()`（`frontend/src/utils/status.ts`） |
| 本地存储读写 | `localStg`（`frontend/src/utils/storage.ts`） |
| 深拷贝对象 | `klona`（`@sa/utils`） |
| 生成唯一 ID | `nanoid`（`@sa/utils`） |
| 加密操作 | `crypto`（`@sa/utils`） |
