# NaiveUI 组件级主题配置

## 需求描述

现有主题系统只能配置颜色/布局/水印等全局项，无法配置 NaiveUI 单个组件。需求：

1. 主题抽屉新增「组件」Tab，每个 NaiveUI 组件可**单独启用**（默认空/禁用）
2. 每个组件的属性可单独配置（表单字段 + 高级 JSON5 混合编辑器）
3. 组件类型与属性表用 **codegen 从 `GlobalThemeOverrides` 类型生成**（不手写子集），覆盖全部 ~60+ 组件
4. 支持 zh-CN / en-US i18n
5. 持久化在前端 localStorage（不动后端）

## 状态

已完成（代码 + typecheck + scoped lint 通过；待用户手动 `pnpm dev` 浏览器冒烟）

## 涉及范围

### 后端

无（纯前端功能）

### 前端

- Codegen：`frontend/scripts/gen-theme-catalog.ts`（TS Compiler API 解析 naive-ui 公开类型声明），`pnpm gen-theme-catalog` 重新生成，产物提交到仓库
- 产物：`theme-drawer/modules/component/theme-catalog.generated.ts`（92 组件 / 2217 属性，`common` 置顶）
- Store：`theme/index.ts` 新增 `componentConfig` ref + 6 setter + `componentConfigJson` + 即时 deep watch 持久化；`shared.ts` 新增 `initComponentConfig()` / `buildComponentOverrides()`；`getNaiveTheme()` 改 options 对象第三参（preset/component 两层覆盖）
- 合并优先级（defu 第一参数优先）：**用户组件配置 > 预设 > 自动派生**
- UI：`theme-drawer/modules/component/`（index / component-editor / prop-fields / advanced-json / prop-meta.ts / component-label.ts）；theme-drawer/index.vue 加第 5 个 Tab；**抽屉宽度桌面端 40%、移动端 90vw**（2026-07-27 迭代）
- 组件 Tab 桌面端为左右双栏（左侧 210px 可搜索组件列表 + 启用圆点标识 + 选中高亮，右侧编辑器），移动端退化为下拉选择（2026-07-27 迭代）
- 属性按 key 推断分组（颜色/尺寸/字体/其他）与控件类型（NColorPicker/NInputNumber/NInput），三种控件均带 clearable 清空；尺寸类文本输入（`needsUnitHint`：size/radius/padding/margin/width/height/gap/offset/border/lineHeight/letterSpacing）显示 `px / rem` 后缀单位提示（2026-07-27 迭代）

## 约束与备注

- localStorage 键 `themeCompOverrides`（storage.d.ts `Local` 命名空间登记）；**dev 与 prod 都从 localStorage 读**（不像 `initThemeSettings()` 有 dev 绕过——组件配置没有源码真源，localStorage 就是真源）
- 空字段 = 删 key（`Reflect.deleteProperty`），保证 defu 干净回落（空 = 继承）
- Pinia setup store 的 `$reset()` 对独立 ref 是空操作：`resetStore()` 已显式调 `clearComponentConfig()` + `setNaiveThemeOverrides(undefined)`
- 属性 key（如 `colorPrimary`/`borderRadiusMedium`）不翻译，是 NaiveUI 技术标识；只翻译组件名（`theme.componentConfig.components` 用 `Record<string, string>` 索引签名，未收录组件回落原始英文名）与 chrome 文案
- i18n 三文件锁步：zh-cn.ts + en-us.ts + app.d.ts `App.I18n.Schema`，由 `pnpm typecheck` 把关
- codegen 只消费 naive-ui 的**公开 .d.ts 类型声明**，不读实现源码（遵守 AGENTS.md 不读 node_modules 约束）；naive-ui 升级后需重跑脚本
- 顺带修复：`views/manage/dept/index.vue` 既有 typecheck 错误（`RowKey[]` vs `number[]`，来自提交 96d6e80a，与本需求无关）
- 全仓 `pnpm lint` 有 274 个**既有**问题（scheduler/、monitor/、merchant-open/ 等未触碰文件），本次改动文件 scoped lint 全绿

## 相关文件

- `frontend/scripts/gen-theme-catalog.ts`
- `frontend/src/layouts/modules/theme-drawer/modules/component/`（index.vue、modules/component-editor.vue、modules/prop-fields.vue、modules/advanced-json.vue、prop-meta.ts、component-label.ts、theme-catalog.generated.ts）
- `frontend/src/layouts/modules/theme-drawer/index.vue`
- `frontend/src/store/modules/theme/index.ts`、`shared.ts`
- `frontend/src/typings/app.d.ts`、`storage.d.ts`
- `frontend/src/locales/langs/zh-cn.ts`、`en-us.ts`
- `frontend/package.json`（`gen-theme-catalog` 脚本）

## 记录日期

2026-07-27
