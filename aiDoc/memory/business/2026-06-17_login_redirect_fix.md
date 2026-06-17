# 登录后 redirect 不生效修复

## 需求描述

带 `?redirect=...` 进入 `/login` 后，登录成功仍然跳到首页而不是 redirect 目标页。

根因：`auth.login` 在 `checkTabClear()` 返回 true 时强制把 `needRedirect` 置 false。而 `checkTabClear` 在 `lastLoginUserId` 不存在时（首次登录、清理过 localStorage、刷新后再登录）也会返回 true，于是 redirect 被一并吞掉。

## 状态

已完成

## 涉及范围

### 后端

无

### 前端

- `frontend/src/store/modules/auth/index.ts` 的 `login` 函数

## 约束与备注

- 清 tab 与登录跳转是两件独立的事，不能因为清 tab 就丢掉用户原本要去的页面
- 修复方式：保留 `checkTabClear()` 的清 tab 副作用，但不再用它去覆盖 `redirect` 参数
- `redirectFromLogin` 自身已能在没有 redirect query 时回退到首页，所以无需额外兜底

## 相关文件

- `frontend/src/store/modules/auth/index.ts`
- `frontend/src/hooks/common/router.ts`（`redirectFromLogin` / `toLogin`）
- `frontend/src/router/guard/route.ts`（`getRouteQueryOfLoginRoute` 写入 redirect query）

## 记录日期

2026-06-17
