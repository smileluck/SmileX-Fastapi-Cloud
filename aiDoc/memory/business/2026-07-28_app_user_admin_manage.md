# 应用用户（AppUser）后台管理

## 需求描述

为 C 端应用用户（`AppUser`，手机号+短信登录）增加完整的后台管理能力：列表/详情/新增/编辑/删除/批量删除/批量启停/改密。放在 `admin` 模块下，复用现有 RBAC 权限体系，并打通前端管理页面。**不新建"应用(Application)"模型**，仅围绕现有 `AppUser`。

## 状态

已完成

## 涉及范围

### 后端

- 模型：`AppUser` 加 `status` / `avatar` / `last_login_at` / `last_login_ip` 四个字段（对齐 `SysUser`）；不加 `is_superuser/roles/dept_id`，C 端用户不参与后台 RBAC。
- 迁移：`0003` 给 `app_user` 加列 + `(phone_code, phone)` 唯一索引；`0004` 新增"业务管理"顶级目录(CATALOG) + "应用用户管理"菜单挂其下 + 4 个权限按钮种子（不分配角色，由运维勾选）。
- 分层：新增 `schemas/sys/app_user.py`、`services/sys/app_user_service.py`、`endpoints/sys/app_user.py`，路由前缀 `/admin/sys/app-user/*`，权限码 `sys:app_user:list/add/edit/delete`。严格参照 SysUser 范式（`@staticmethod async`、统一响应/分页）。
- C 端联动：`modules/app/deps/auth/user_manager.py` 的 `login_by_phone` 与 `current_user` 加 `status` 检查，使后台"禁用"真正阻断 C 端登录。
- session 吊销：禁用/改密/删除时复用 `OnlineUserService.kick_all_sessions(user_id, role="app")`，使旧 token 立即失效。

### 前端

- 类型：`typings/api/system-manage.d.ts` 新增 `AppUser` 系列。
- API：`service/api/system-manage.ts` 新增 `fetchGetAppUserList` 等 8 个函数（`/admin/sys/app-user/*`）。
- 页面：`views/business/app-user/`（`index.vue` + 搜索/操作抽屉/改密抽屉三子组件），整体仿 `views/manage/user/`；归"业务管理"顶级目录（与"系统管理"并列的 CATALOG）。
- i18n：页面文案 `page.manage.appUser.*`（保留，命名空间与物理目录无关）；路由标题 `route.business` + `route.business_app-user`（zh/en）。
- 路由：目录从 `manage/app-user` 移到 `business/app-user` 后，elegant 插件自动重生 `business` 父路由 + `business_app-user` 子路由（imports/transform/routes/types 四文件）。

## 约束与备注

- **password 选填**：后台新增时密码留空 → 该用户只能短信登录；Service 中 `if payload.password:` 才 hash。
- **禁用语义**：禁用会踢该用户全部设备（session 全清），UI 需提示操作者。
- **(phone_code, phone) 唯一**：业务层组合查重 + DB 唯一索引双保险。
- **不修复 C 端历史偏差**：`register_by_phone`/`login_by_phone` 引用了 `phone_area_code/client_ids/username` 等 AppUser 不存在的字段（既有 bug），本任务不扩大范围，仅改 status 检查两处。
- **last_login_* 暂为空**：字段已建，C 端 `on_after_login` 未埋点，列表显示为空属预期，后续单独优化。
- **菜单 name 须与路由名一致（含连字符）**：目录 `app-user` → 路由名 `business_app-user`（连字符）；菜单 `name` 必须用同款连字符，否则前端按菜单名找不到组件与 i18n（参照 `manage_ip-blacklist` 先例）。BUTTON 的 name 仅作权限点标识，不影响路由。

## 相关文件

- `backend/database/models/business/user.py`
- `backend/alembic/versions/0003_app_user_admin_fields.py`
- `backend/alembic/versions/0004_seed_app_user_menu.py`
- `backend/modules/admin/schemas/sys/app_user.py`
- `backend/modules/admin/services/sys/app_user_service.py`
- `backend/modules/admin/endpoints/sys/app_user.py`
- `backend/modules/app/deps/auth/user_manager.py`（status 检查）
- `frontend/src/views/business/app-user/`（index + 3 子组件）
- `frontend/src/service/api/system-manage.ts`
- `frontend/src/typings/api/system-manage.d.ts`

## 记录日期

2026-07-28
