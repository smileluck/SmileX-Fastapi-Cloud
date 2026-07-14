# 密码复杂度策略：6-20 位且至少含字母+数字

## 需求描述

用户要求：新增用户密码、修改密码统一限制为 **6-20 位，且至少包含英文+数字**。

## 状态

已完成

## 策略要点（关键：登录与写入分离）

`REG_PWD` 原为 `/^\w{6,18}$/`（允许字母/数字/下划线，但不强制混合），且**登录表单复用了它**。若直接收紧 `REG_PWD`，全数字/全字母的旧密码、种子密码（如 `123456`）会被登录前端拦截、无法登录。故：

- **写入路径**（新建/修改/注册/重置）用收紧后的 `REG_PWD`。
- **登录**改为「仅非空」校验，不校验格式，避免拦截旧密码；格式校验交给写入侧与后端。

## 修复

### 前端

- `constants/reg.ts`：`REG_PWD = /^(?=.*[A-Za-z])(?=.*\d)\w{6,20}$/`（6-20 位，≥1 字母 + ≥1 数字，下划线仍允许）。
- `locales/langs/{zh-cn,en-us}.ts`：`form.pwd.invalid` 文案改为描述新策略（`密码格式不正确，需6-20位，且至少包含字母和数字` / `6-20 characters, must include both letters and numbers`）。
- `hooks/common/form.ts`：`formRules.pwd`/`patternRules.pwd` 仍用 `REG_PWD`（现收紧）→ 注册/重置自动生效，无需改。
- `views/_builtin/login/modules/pwd-login.vue`：登录密码规则由 `formRules.pwd` 改为 `[defaultRequiredRule]`（仅非空）。
- `views/manage/user/modules/user-operate-drawer.vue`（新建）：`password`、`confirmPassword` 原来的 `min/max 6-20` 规则改为 `pattern: REG_PWD`（导入 `REG_PWD`）。
- `views/manage/user/modules/user-password-drawer.vue`（修改密码）：`newPassword` 原来的 `min:6` 改为 `pattern: REG_PWD`（导入 `REG_PWD`）。

### 后端

- `modules/admin/schemas/sys/user.py`：新增模块级 `PASSWORD_PATTERN`（同前端）+ `validate_password_complexity(value)`。
  - `SysUserCreate.password` 加 `@field_validator("password")` 调用之（原已有 `min_length=6, max_length=20`）。
  - `SysUserPasswordUpdate.new_password` 加 `@field_validator("new_password")`，并修 `max_length=100 → 20`（原来不一致）。
- 登录后端 `LoginPwdModel.password` 不加策略（登录只验密码哈希，不应限制格式）。

## 验证

- 后端 `validate_password_complexity` 8 条用例全过：`abc123/Password1/a1bcde` 通过；`123456/abcdef/23位/ab12/______` 拒绝；`SysUserCreate(password='123456')` 端到端被拒。
- 前端 `pnpm typecheck` 退出码 0，0 报错。

## 涉及范围

### 前端

`constants/reg.ts`、`locales/langs/{zh-cn,en-us}.ts`、`hooks/common/form.ts`（未改代码，仅受益于 REG_PWD 收紧）、`views/_builtin/login/modules/pwd-login.vue`、`views/manage/user/modules/{user-operate-drawer,user-password-drawer}.vue`

### 后端

`modules/admin/schemas/sys/user.py`

## 约束与备注

- 前后端用同一正则 `^(?=.*[A-Za-z])(?=.*\d)\w{6,20}$`，保证口径一致。
- 登录**不**校验密码格式是有意为之：避免旧/种子密码被前端拦截；真实校验在写入侧 + 后端。
- 注册/重置走 `formRules.pwd`，自动继承新策略；若后续禁用注册/重置，无影响。

## 相关文件

- `frontend/src/constants/reg.ts`
- `frontend/src/views/_builtin/login/modules/pwd-login.vue`
- `frontend/src/views/manage/user/modules/user-operate-drawer.vue`、`user-password-drawer.vue`
- `backend/modules/admin/schemas/sys/user.py`

## 记录日期

2026-07-14
