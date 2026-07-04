# 用户/角色管理缺陷修复 + 全模块提交类型约束加固

## 需求描述

用户反馈 4 个问题并要求一次性修复：

1. 完善前后端提交类型约束（全模块 + 后端 schema 校验加固）。
2. 角色管理：新增同名角色应抛出异常（而非靠 DB 唯一约束抛生硬 IntegrityError）。
3. 新增用户成功后报「数据验证失败」。
4. 接口报错弹窗后，页面仍提示保存/删除成功。

## 状态

已完成

## 涉及范围

### 后端

- `modules/admin/services/sys/role_service.py`：`create_role` / `update_role` 新增角色名重名检查，命中抛 `ConflictError(msg="角色名称已存在")`；更新时排除自身 id。
- `modules/admin/services/sys/user_service.py`：`create_user` 末尾改为 `joinedload(SysUser.roles)` 重查后返回，避免响应序列化触发异步懒加载导致 422。`update_user` 无需改（入口已 `get_user` 加载 roles）。
- `modules/admin/services/sys/dict_service.py`：`update_dict` 对非超管屏蔽 `is_system` 置 True（与 `create_dict` 一致）。
- Schema 校验加固：
  - `schemas/sys/role.py`：`name` 加 `min_length=1`，`sort` 加 `ge=0`。
  - `schemas/sys/dept.py`：`name` 加 `min_length=1`，`sort` 加 `ge=0`。
  - `schemas/sys/menu.py`：`name` 加 `min_length=1`，`sort` 加 `ge=0`，`meta_icon_type` 加 `ge=1, le=2`。
  - `schemas/sys/dict.py`：`SysDictCreate/Update` 新增 `is_system` 字段（对齐前端，使既有 `getattr(dict_in,'is_system',False)` 逻辑生效）；`name/code` 加 `min_length=1`，DictItem `value/label` 加 `min_length=1`，`sort` 加 `ge=0`。
  - `modules/scheduler/schemas/scheduled_task.py`：`trigger_type` / `concurrent_policy` 改为 `Literal[...]` 枚举；`name/task_key` 加长度；`cron_expression` 加 `min_length=1`；`timeout` 加 `ge=1`，`max_retries` 加 `ge=0`。

### 前端

- `typings/api/system-manage.d.ts`：新增 `RoleCreateRequest`/`RoleUpdateRequest`、`UserCreateRequest`/`UserUpdateRequest`（替代 `Partial<Role> & {...}` 与 `UserCreate & { role_ids? }` 的松散拼接），逐字段对齐后端 schema；`status` 允许 `null`（表单模型实际可为 null，`enableStatusToBoolean` 兼容）。
- `service/api/system-manage.ts`：`fetchCreateRole/UpdateRole`、`fetchCreateUser/UpdateUser` 改用上述专用请求类型。
- `views/manage/user/modules/user-operate-drawer.vue`：`handleSubmit` 由 `try/catch` 改为 `{ error }` 解构（flat request 不抛异常），并移除重复错误 toast；payload 去掉未使用的 `userRoles`。
- `views/manage/user/modules/user-password-drawer.vue`：同样改 `{ error }` 解构，移除重复错误 toast。
- `views/manage/user/index.vue`：`handleDelete` / `handleBatchDelete` 改 `{ error }` 解构；批量删除任一失败即停止，不再误触发刷新。

## 约束与备注

- 根因：前端 `createFlatRequest`（`packages/axios/src/index.ts`）**永不抛异常**，错误返回 resolved `{data:null,error}`；故调用方必须显式判断 `error`，`try/catch` 永不进入 catch 分支。本次未重构该函数（影响全局），仅修正用户管理侧调用方。
- 未做的部分（避免无关大改 / 规避存量数据风险）：
  - Menu/Dept/DictItem/Config/Scheduler 的 update 类型保留 `Partial<*Create>`（与后端「更新 schema 字段全可选」语义一致，属合理惯用法）。
  - `code/key` 类格式正则、cron 表达式解析、IP 格式正则未加（可能拒掉存量数据编辑），留待按需逐字段评估。
- 预存在（非本次引入）的 typecheck 报错：`hooks/business/dict.ts` 缺 `Ref` import、`user-operate-drawer.vue:169` `AllRole` 上访问 `code`、`scheduler/log|task/index.vue` 的 `string[]→number[]` 转换——均与本次改动无关，未处理。

## 相关文件

- 后端：`backend/modules/admin/services/sys/{role,user,dict}_service.py`、`backend/modules/admin/schemas/sys/{role,dept,menu,dict}.py`、`backend/modules/scheduler/schemas/scheduled_task.py`
- 前端：`frontend/src/typings/api/system-manage.d.ts`、`frontend/src/service/api/system-manage.ts`、`frontend/src/views/manage/user/**`

## 记录日期

2026-07-04
