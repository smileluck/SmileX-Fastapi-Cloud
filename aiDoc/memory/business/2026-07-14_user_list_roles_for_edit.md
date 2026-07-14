# 用户编辑保存角色不生效修复

## 需求描述

用户反馈：用户管理里编辑用户、保存角色时「没有保存成功」——实际是用户原有角色被清空。

## 状态

已完成

## 根因

用户编辑抽屉（`user-operate-drawer.vue`）的角色回填依赖**列表接口返回的 `roles` 字段**：

```js
const rawRow = props.rowData as Api.SystemManage.RawUser;
model.value.roleIds = rawRow.roles ? rawRow.roles.map(r => r.id) : [];
```

但 `GET /admin/sys/user/list` 用的响应 schema 是 `SysUserListResponse`，该 schema **不含 `roles`**（原注释还写着「不包含关联角色数据」）。于是 `rawRow.roles` 恒为 `undefined` → `roleIds = []`：

- 编辑用户时角色多选框**是空的**（即便用户实际有角色）；
- 直接点保存会提交 `role_ids: []`，后端 `update_user` 走 `else: user.roles = []` → **角色被清空**。

注：列表查询 `build_user_list_query` 本来就 `selectinload(SysUser.roles)`（角色已查出），只是被响应 schema 丢掉；前端 `RawUser` 类型与抽屉也都已假设列表带 `roles`。属 schema 与前端契约脱节，非查询/前端逻辑错误。

## 修复

`SysUserListResponse` 增加 `roles: List[SysRoleSimpleResponseForUser] = Field([])`，让列表响应把已加载的角色透传出来。零额外查询（selectinload 已有）、零前端改动。

未同时加 `role_ids`：`SysUser` 模型只有 `roles` 关系、无 `role_ids` 属性；前端 `RawUser` 也只声明 `roles`、抽屉只用 `roles`。加 `role_ids` 会恒为 `[]` 造成误导（Pydantic `from_attributes` 对缺失属性回退默认值，实测不报错，但语义错误，故不加）。

### 后端

- `modules/admin/schemas/sys/user.py`：`SysUserListResponse` 增 `roles` 字段 + 更新 docstring。
- `modules/admin/endpoints/sys/user.py`：修正列表端点处「不加载关联角色」的过时注释（实际已 selectinload）。

### 前端

无。`RawUser.roles` 类型与抽屉 `handleInitModel` 读取 `rowData.roles` 均已就位，列表带 `roles` 后自动生效。

## 约束与备注

- 验证：Pydantic 2.12.5 实测 `from_attributes` 对 ORM 缺失属性回退字段默认值（不抛 ValidationError）；`SysUserListResponse.model_validate(拟态对象)` 正确产出 `roles=[(id,name)...]`。
- 详情端点 `GET /user/{id}`（`SysUserResponseData`，含 `role_ids`/`roles`）前端未调用（无 `fetchGetUserDetail`），其 `role_ids` 实际恒为 `[]`，属既存债务，本次不动。
- 列表响应多带 `roles`（id/name/status）的载荷开销可忽略。

## 相关文件

- `backend/modules/admin/schemas/sys/user.py`（改）
- `backend/modules/admin/endpoints/sys/user.py`（仅改注释）
- `backend/modules/admin/services/sys/user_service.py`（未改，`build_user_list_query` 已 selectinload roles）
- `frontend/src/views/manage/user/modules/user-operate-drawer.vue`（未改，读 `rowData.roles`）
- `frontend/src/views/manage/user/index.vue`（未改，`...user` 透传 roles）
- `frontend/src/typings/api/system-manage.d.ts`（未改，`RawUser` 已声明 `roles?`）

## 记录日期

2026-07-14
