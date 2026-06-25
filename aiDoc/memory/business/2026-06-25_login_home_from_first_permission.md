# 登录后默认跳转改为权限列表第一个页面

## 需求描述

用户登录成功后，默认跳转页由原来的固定 `/home` 改为「当前用户权限列表中的第一个可访问页面」。

不同角色看到的首页可能不同：管理员可能落到工作台，普通业务用户可能落到其有权限的第一个业务页面。

## 状态

已完成

## 涉及范围

### 后端

- `backend/modules/admin/services/sys/route_service.py`
  - 新增 `_first_page_route_name(routes)` 静态方法：深度优先遍历路由树，跳过外链和纯目录，返回第一个具有 `component` 的叶子路由 `name`
  - `get_user_routes` 不再硬编码 `home="home"`，改为 `home = _first_page_route_name(routes) or "home"`

### 前端

无需改动。前端在 `initDynamicAuthRoute` 中已经信任后端返回的 `home` 字段（`setRouteHome(home)` + `handleUpdateRootRouteRedirect(home)`），路由守卫会在跳转到 `root` 之前完成 auth route 初始化，所以新的 `home` 会先生效。

## 约束与备注

- 「第一个可访问页面」= 与左侧菜单同序（按 `SysMenu.sort, SysMenu.id` 排序）深度优先搜索得到的第一个非外链、非空目录的叶子节点
- 跳过 `meta.href`（外链）—— 这类路由 `component` 为 `None`
- 跳过纯目录（无 `component`）—— 会递归进入其 children 找到第一个真实页面
- 兜底：当用户没有任何菜单权限（普通用户 `menu_ids` 为空）或所有路由均无 component 时，回退到 `"home"`
- 仅对动态路由模式（`VITE_AUTH_ROUTE_MODE=dynamic`）生效；静态模式仍走 `VITE_ROUTE_HOME` 环境变量

## 相关文件

- `backend/modules/admin/services/sys/route_service.py`
- `frontend/src/store/modules/route/index.ts`（消费 `home` 字段，无需改动）
- `frontend/src/hooks/common/router.ts`（`redirectFromLogin` → `toHome` → `root` 重定向链路，无需改动）

## 记录日期

2026-06-25
