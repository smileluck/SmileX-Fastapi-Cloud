# 数据权限（行级可见性）— 角色数据范围

## 需求描述

管理系统中需要按"职位层级"控制不同用户能看见的数据行：
- 总监/超管：全部数据
- 部门主管：本部门及子部门
- 部门员工：仅本部门
- 普通用户：仅本人

采用"角色 + 数据范围"方案（RuoYi 式），在 `SysRole` 上配置 `data_scope` 枚举，引入部门树 `SysDept`，在 Service 查询层注入过滤条件。

支持的数据范围类型：`ALL` / `DEPT_AND_SUB` / `DEPT_ONLY` / `SELF`（首期不含 CUSTOM）。

## 状态

已完成（首期：通用框架 + 用户管理示范）

## 涉及范围

### 后端

**新增/修改模型：**
- `backend/database/models/sys/dept.py`（新增）：`SysDept` 树形模型（parent_id 自引用、name、code、status、sort）
- `backend/database/models/sys/role.py`：新增 `DataScopeEnum` 枚举 + `SysRole.data_scope` 字段
- `backend/database/models/sys/user.py`：新增 `SysUser.dept_id` 字段
- `backend/database/models/sys/__init__.py`：导出 `SysDept`、`DataScopeEnum`

**新增 Service：**
- `backend/modules/admin/services/sys/data_scope_service.py`：
  - `DataScopeService.get_effective_scope(db, user) -> DataScopeEnum | None`：聚合用户所有启用角色的 data_scope，取最宽（None=不限）
  - `DataScopeService.get_permitted_dept_ids(db, user, scope) -> set[int] | None`：根据 scope 算可见部门集合；SELF 返回空集合（走 user.id 过滤）
- `backend/modules/admin/services/sys/dept_service.py`：部门 CRUD + 树构建（在 Pydantic 层组装，避免 lazy="noload" 问题）

**改造：**
- `backend/modules/admin/services/sys/user_service.py`：`_apply_user_filters` / `build_user_list_query` / `build_user_query` / `get_user_list` 增加 `data_scope` / `permitted_dept_ids` / `current_user_id` 三个 kwargs
- `backend/modules/admin/endpoints/sys/user.py`：`/admin/sys/user/list` 注入 `current_user`，先算 scope 再传给 Service
- `backend/modules/admin/services/sys/role_service.py`：`create_role` / `update_role` 持久化 `data_scope`，复用 `_invalidate_permission_cache()` 失效缓存

**新增 Endpoint：**
- `backend/modules/admin/endpoints/sys/dept.py`：`/admin/sys/dept/{list,tree,tree-select,{id},add,{id},batch,batch/status,{id}}`
- 路由注册到 `backend/modules/admin/endpoints/sys/__init__.py`

**Schema：**
- `backend/modules/admin/schemas/sys/dept.py`（新增）：`SysDeptCreate` / `SysDeptUpdate` / `SysDeptQueryParams` / `SysDeptResponseData` / `SysDeptTreeResponse` / `SysDeptBatchUpdateStatus`
- `backend/modules/admin/schemas/sys/role.py`：`SysRoleCreate` / `SysRoleUpdate` / `SysRoleListResponse` / `SysRoleResponseData` 加 `data_scope` 字段
- `backend/modules/admin/schemas/sys/user.py`：`SysUserCreate` / `SysUserUpdate` / `SysUserListResponse` / `SysUserResponseData` 加 `dept_id` 字段

**Alembic 迁移：**
- `backend/alembic/versions/0004_data_scope_permission.py`：建 sys_dept 表 + 创建 `sys_role_data_scope` enum 类型（必须显式 `.create()`，不能仅在 add_column 中声明）+ 加 `sys_role.data_scope` 列（server_default='SELF'）+ 加 `sys_user.dept_id` 列与外键

### 前端

- `frontend/src/typings/api/system-manage.d.ts`：新增 `DataScope` 类型 + `Dept` / `DeptTree` / `DeptSearchParams` / `DeptList` / `DeptCreate` / `DeptUpdate` / `DeptBatchUpdateStatus` 类型；`Role` 加 `data_scope`；`User` 加 `dept_id`
- `frontend/src/service/api/system-manage.ts`：
  - `fetchCreateUser` / `fetchUpdateUser` 传递 `dept_id`
  - `fetchCreateRole` / `fetchUpdateRole` 传递 `data_scope`（默认 `'SELF'`）
  - 新增 `fetchGetDeptList` / `fetchGetDeptTree` / `fetchGetDeptTreeSelect` / `fetchGetDept` / `fetchCreateDept` / `fetchUpdateDept` / `fetchDeleteDept` / `fetchBatchDeleteDept` / `fetchBatchUpdateDeptStatus`
- `frontend/src/views/manage/user/modules/user-operate-drawer.vue`：表单加"所属部门" `NTreeSelect`
- `frontend/src/views/manage/role/modules/role-operate-drawer.vue`：表单加"数据范围" `NRadioGroup`
- `frontend/src/views/manage/role/index.vue`：列表加"数据范围"列（带 NTag）
- `frontend/src/views/manage/dept/index.vue`（新增）：树形部门管理页（参考 menu 管理的树形写法）
- `frontend/src/views/manage/dept/modules/dept-operate-drawer.vue`（新增）：部门编辑抽屉
- `frontend/src/router/elegant/{imports,routes}.ts` + `frontend/src/typings/elegant-router.d.ts`：注册 `manage_dept` 路由
- `frontend/src/locales/langs/{zh-cn,en-us}.ts`：新增 `manage_dept` 文案

## 关键设计决策

1. **scope is None 表示不限**：超管（`is_superuser=True`）或角色 data_scope 含 `ALL` 时，`get_effective_scope` 返回 None，Service 不加任何过滤
2. **多角色取最宽**：用户多个角色的 data_scope 取并集中最宽的（ALL > DEPT_AND_SUB > DEPT_ONLY > SELF）
3. **SELF 的特殊处理**：用户管理模块的 SELF 直接 `where(SysUser.id == current_user_id)`，不依赖 `created_by`
4. **DEPT_AND_SUB 子部门递归**：首期用"查全部 dept 后内存 BFS"实现，避免引入 CTE 复杂度
5. **缓存复用 PERMISSION namespace**：角色/部门变更时调用 `_invalidate_permission_cache()`（与现有 menu 权限缓存共用 namespace）
6. **权限码**：`sys:dept:list` / `sys:dept:add` / `sys:dept:edit` / `sys:dept:delete`（需通过菜单管理手动添加到 sys_menu 表并分配给角色）

## 验证方式

1. 运行 `alembic upgrade head`，确认 sys_dept 表、sys_role.data_scope 列、sys_user.dept_id 列创建成功
2. 后端启动：`python main.py` 或项目启动脚本
3. 前端启动：`pnpm dev`（或项目脚本）
4. 种子数据：建一棵部门树 + 几个不同 data_scope 的角色 + 分属不同部门的用户
5. 用不同角色登录访问 `/admin/sys/user/list`，断言可见范围符合预期
6. 验证 `total` 与 `records` 数量一致（共用同一份 base_query）

## 不在首期范围内

- CUSTOM 自定义部门集合（`sys_role_dept` 关联表）
- 写操作（创建/更新/删除）的数据权限校验
- 其他业务模块（订单/工单等）的数据权限接入
- 数据导出接口的数据权限（首期只管列表）

## 记录日期

2026-06-25
