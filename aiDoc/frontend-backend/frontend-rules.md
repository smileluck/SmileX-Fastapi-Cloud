<!-- last-updated: 2026-10-02 -->
# 前端开发规范

## 基础规则

- HTTP 请求统一走 `@sa/axios` 封装（`packages/axios/`），通过 `frontend/src/service/request/` 调用
- 全局状态使用 Pinia（`frontend/src/store/`），禁止在组件中直接操作全局变量
- 路由必须配置完整元数据（权限、标题、图标），使用项目内置异步路由机制
- 所有变量、函数参数、返回值必须有明确的 TypeScript 类型声明

## 命名规范

| 对象 | 规范 | 示例 |
|------|------|------|
| 文件名 | `kebab-case` | `system-manage.ts`、`user-detail.vue` |
| 组件名 | `PascalCase` | `UserTable`、`RoleForm` |
| 变量名 | `camelCase` | `userInfo`、`currentPage` |
| 常量名 | `UPPER_SNAKE_CASE` | `MAX_PAGE_SIZE` |
| API 函数 | `fetch` 前缀 | `fetchGetUserList`、`fetchCreateUser` |
| 类型名 | `PascalCase` | `UserInfo`、`PageParams` |

## TypeScript 要求

- API 响应类型定义在 `frontend/src/typings/api/<domain>.d.ts`，放在 `Api` 命名空间下
- 公共类型（分页、状态等）定义在 `frontend/src/typings/api/common.d.ts`
- i18n 类型约束在 `frontend/src/typings/app.d.ts` 的 `App.I18n.Schema`
- 修改数据结构时必须同步更新对应类型声明
- 提交前执行 `pnpm typecheck` 确保类型安全

### 禁止与限制

- **禁止 `any`**：变量声明、函数参数、返回值不允许使用 `any`。错误对象用 `unknown`，无法确定的类型用具体联合类型或泛型
- **禁止 `as any` 断言**：类型不匹配时应修复根因（补全类型定义、调整函数签名），不使用 `as any` 绕过
- **禁止 `@ts-ignore`**：修复类型错误，不压制检查
- **禁止在模板中直接访问 `window`**：应在 `<script setup>` 中定义函数包装后调用

### 字面量类型保留

TS 函数返回值中字面量类型会被拓宽（`'gauge'` → `string`），导致无法匹配 ECharts、NaiveUI 等联合类型。使用 `as const` 保留字面量：

```typescript
// ECharts 选项中的 type 字段
{ type: 'gauge' as const, ... }
{ type: 'line' as const, ... }
{ trigger: 'axis' as const }

// NaiveUI 表格列的 align 字段
{ key: 'name', align: 'center' as const, ... }
```

### transform 回调类型

列表页的 `transform` 回调中，API 数据会经过 `booleanToEnableStatus` 等转换。若类型在转换前后不变（如 `Role.status` 始终为 `EnableStatus`），用具体类型标注参数；若转换改变字段类型（如 `User.roles` → `userRoles`），在 `frontend/src/typings/api/` 中定义 `RawXxx` 类型用于回调参数：

```typescript
// 类型不变的 transform — 使用具体类型
result.data.map((role: Api.SystemManage.Role) => ({ ... }))

// 类型变化的 transform — 使用 Raw 类型
result.data.map((user: Api.SystemManage.RawUser) => ({ ... }))
```

### 表单验证器

- 未使用的参数以 `_` 前缀命名（如 `_rule`），不要用 `any`
- 若需要类型标注，使用 `App.Global.FormRule`

```typescript
// 正确
validator: (_rule: App.Global.FormRule, value: string) => { ... }

// 错误
validator: (rule: any, value: string) => { ... }
```

### 类型复用

- 复用项目已有类型别名：`App.Global.FormRule`、`Api.Common.EnableStatus`、`NaiveUI.ThemeColor` 等
- ECharts 选项类型统一使用 `ECOption`（来自 `@/hooks/common/echarts`）
- `Common.CommonRecord` 的泛型参数中不要重复定义 `status` 字段（会产生交叉冲突），若需覆盖 `status` 类型应使用 `Omit`

## 组件规范

- 公共组件放在 `frontend/src/components/`
- 页面级组件放在对应页面的 `modules/` 目录
- Props 必须使用 TypeScript 接口定义（`defineProps<{ ... }>()`）
- 每个页面必须有独立文件夹，包含主 `.vue` 文件
- 相关子组件放在 `modules/` 子目录

### 搜索表单标准模式

列表页的搜索表单统一使用以下 NaiveUI 组件组合：

- `NCard` 包裹，`size="small"` `class="card-wrapper"`
- `NCollapse` + `NCollapseItem` 折叠容器，标题使用 `$t('common.search')`
- `NForm label-placement="left" :label-width="80"` 左对齐标签
- `NGrid responsive="screen" item-responsive` 响应式网格
- `NFormItemGi span="24 s:12 m:6" class="pr-24px"` 表单项，小屏 2 列、中屏 4 列
- 按钮行 `NFormItemGi span="24 m:12"`，`NSpace justify="end"` 右对齐
- 重置按钮：`icon-ic-round-refresh` 图标
- 搜索按钮：`icon-ic-round-search` 图标，`type="primary" ghost`
- 重置逻辑使用 `jsonClone(toRaw(model.value))` + `Object.assign`

参考实现：`frontend/src/views/manage/config/modules/config-search.vue`

## 页面规范

新增页面时必须完成：

1. 在 `frontend/src/views/<name>/` 创建文件夹和 `.vue` 文件
2. 在 `frontend/src/locales/langs/zh-cn.ts` 和 `en-us.ts` 添加翻译
3. 在 `frontend/src/typings/app.d.ts` 更新 `App.I18n.Schema` 类型
4. 运行 `pnpm gen-route` 自动生成路由

## 样式规范

- 样式优先级：UnoCSS > SCSS > 内联样式（避免使用内联样式）
- 遵循 NaiveUI 的设计模式，保持视觉一致性
- 主题控制通过 CSS 变量实现
- 全局样式放在 `frontend/src/styles/`

## 国际化规范

- 所有用户可见文本必须通过 i18n 键引用
- 新增键必须同时添加到 `zh-cn.ts` 和 `en-us.ts`
- 新增模块时必须更新 `App.I18n.Schema` 类型约束
- 模板中使用 `$t('key')` 或 `{{ $t('key') }}`

### 键的引用与定义

- **引用已有 `common.*` 键前，必须先在 `zh-cn.ts` / `en-us.ts` 中确认该 key 已存在**
  - 当前 `common` 命名空间已有的 key：index、operate、action、add、edit、delete、confirmDelete、search、reset、refresh、saveSuccess、updateSuccess、deleteSuccess、addSuccess、loadDataFailed、pleaseSelect、selectAtLeastOne、yesOrNo、keywordSearch、config、confirm、cancel、close、check、selectAll、expandColumn、columnSetting、batchDelete、backToHome、back、warning、error、noData、pleaseCheckValue、modify、modifySuccess、update、updateFailed、userCenter、changePassword、tip、trigger、switch、lookForward、logout、logoutConfirm
  - **若不在上述列表中，不允许直接写 `$t('common.xxx')`，必须走页面级 key**
- **页面级文本统一使用 `page.manage.<module>.<field>` 或 `page.<module>.<field>` 命名**，不混用 `common.*`
  - 例如：列表标题 `page.manage.announcement.title`、状态列 `page.manage.announcement.status`、搜索表单 label `page.manage.announcement.form.title`
  - 表单 placeholder 统一格式：`$t('page.manage.xxx.form.xxx')`
- **新增/修改 i18n 键后，必须执行 `pnpm typecheck`**，利用 `App.I18n.Schema` 类型约束捕获未定义键

## 环境变量

- 前缀 `VITE_*`，通过 `import.meta.env.VITE_*` 访问
- 环境配置文件：`.env`、`.env.test`、`.env.prod`

## 常用脚本

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 开发模式（测试环境） |
| `pnpm dev:prod` | 开发模式（生产环境） |
| `pnpm build` | 构建生产版本 |
| `pnpm build:test` | 构建测试版本 |
| `pnpm typecheck` | TypeScript 类型检查 |
| `pnpm lint` | ESLint 代码检查与修复 |
| `pnpm gen-route` | 自动生成路由 |
| `pnpm commit:zh` | 交互式 Git 提交 |

## 代码注释

- API 封装函数必须有 JSDoc 注释
- 复杂组件必须有功能描述注释
- 关键业务逻辑必须有行内注释
- 类型声明文件必须有清晰的注释说明
