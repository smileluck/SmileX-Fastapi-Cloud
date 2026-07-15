# 关于我们页面（前端常驻路由 + 构建时 Git 历史）

## 需求描述

新增「关于我们」页面：左右两栏布局，左侧展示项目介绍（定位、技术栈、核心特性），右侧展示本仓库的 Git 提交历史。

## 状态

已完成

## 涉及范围

### 后端

无。纯前端实现，不涉及后端接口、数据库或跨栈契约变更。

### 前端

- 新增页面 `src/views/about/index.vue`（NGrid 左右栏：左 SystemLogo + 项目介绍 + 技术栈 NTag + 特性列表；右 NTimeline 渲染 Git 提交）
- 新增 vite 插件 `build/plugins/git-log.ts`：buildStart 调 `git log` 采集最近 50 条提交，经 virtual module `virtual:smilex-git-log` 暴露；无 git 时 `available:false` 优雅降级
- 新增类型声明 `src/typings/git-log.d.ts`
- `build/plugins/index.ts` 注册 `setupGitLogPlugin()`
- `build/plugins/router.ts` 的 `onRouteMetaGen` 将 `about` 加入 `constantRoutes`，并补 `icon` / `order=9999`
- i18n：`zh-cn.ts` / `en-us.ts` 增 `route.about` + `page.about.*`；`app.d.ts` 补 `page.about` 类型

## 约束与备注

- 路由**不走动态菜单**：通过 elegant-router 的 `onRouteMetaGen` 标记为 `constant` 常驻路由，自动进侧边栏（无需后端菜单返回），`order=9999` 置底
- 入口为**侧边栏固定菜单项**，登录后在后台框架（base layout）内访问
- Git 历史**构建时生成**（非实时）：dev 启动 / build 各采集一次；生产环境无 `.git` 时右侧显示空态，不报错
- `route.about` 类型由 gen-route 生成的 `RouteKey` 经 `Record<I18nRouteKey, string>` 自动覆盖，无需手改 `app.d.ts` 的 route
- 验证：`pnpm build:test` 通过（elegant 生成 about 路由 + git-log 插件工作）；`pnpm typecheck` 通过

## 相关文件

- `frontend/src/views/about/index.vue`
- `frontend/build/plugins/git-log.ts`
- `frontend/src/typings/git-log.d.ts`
- `frontend/build/plugins/index.ts`
- `frontend/build/plugins/router.ts`
- `frontend/src/locales/langs/zh-cn.ts`、`frontend/src/locales/langs/en-us.ts`
- `frontend/src/typings/app.d.ts`

## 记录日期

2026-07-15
