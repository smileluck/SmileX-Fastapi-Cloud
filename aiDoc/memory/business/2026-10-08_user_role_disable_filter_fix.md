<!-- last-updated: 2026-10-08 -->
# 用户/角色管理"禁用筛选不生效"修复（status 布尔桥接断裂）

## 需求描述

用户反馈：用户管理和角色管理的"禁用"筛选不生效。

排查结论：筛选链路（前端 NSelect '1'/'2' → axios → `BoolField` query 解析 → service `status == False` → PG boolean 列 → `BaseRespEntity` 序列化回 '1'/'2'）本身完全正常（TestClient + dev 库事务内实测均通过）。真正的根因是**禁用状态写不进库**：`SysUserCreate` / `SysRoleCreate` / `SysUserBatchUpdateStatus` / `SysRoleBatchUpdateStatus` 四个请求模型的 `status` 用了原生 `bool` 而非 `BoolField`。pydantic v2 的 bool lax 白名单接受 `'1'`（→True）但拒绝 `'2'`，于是前端一切"启用"提交正常、一切"禁用"提交 422（"Input should be a valid boolean"）→ 库里永远没有禁用数据 → 筛"禁用"永远空列表，被感知为"筛选不生效"。

## 状态

已完成（用户/角色范围）；其他模块同类字段待统一修复（见约束与备注）

## 涉及范围

### 后端

- `modules/admin/schemas/sys/user.py`：`SysUserCreate.status` 改 `BoolField` + validator（显式 null 收敛为默认 True，防 NOT NULL 列写 NULL）；`SysUserBatchUpdateStatus.status` 改 `BoolField` + validator（null 拒绝，防批量置 NULL）。
- `modules/admin/schemas/sys/role.py`：`SysRoleCreate` / `SysRoleBatchUpdateStatus` 同样处理；补充 `field_validator` 与 `core.i18n.t` import。
- `core/i18n/locales/zh-CN.yaml`、`en-US.yaml`：新增 `validation.status_required`。
- 更新/查询参数（`SysUserUpdate` / `SysRoleUpdate` / 两个 QueryParams）原本就是 `BoolField`，未动。

### 前端

无需改动（提交的 status 一直是 '1'/'2' 字符串，符合桥接约定）。

## 约束与备注

- **请求模型 status 一律用 `BoolField`，不要用原生 `bool`**：pydantic bool 只认 '1'/'0'/'true'/'false' 等，不认本项目桥接约定的 '2'（禁用）。响应模型不受影响（`BaseRespEntity` 序列化器负责输出）。
- **同类坑存量清单（本次未修，待用户确认后统一处理）**：`dept.py`、`menu.py`、`dict.py`、`app_user.py`、`merchant.py`（admin 模块）及 `modules/agent/schemas/*`（provider/model/skill/knowledge/agent/mcp_server）的 Create / BatchUpdateStatus（部分含 Update）仍有 `status: bool`。若对应前端同样传 '1'/'2' 字符串，"禁用"方向提交会 422。修复前需逐个确认前端契约与 service 对 None 的处理。
- `Create` 模型 validator 把 null 收敛为 True 而非报错：与"缺省即启用"语义一致；`BatchUpdateStatus` 必须null 报错：批量接口无"不改"语义，且 `update().values(status=None)` 会把列刷成 NULL。
- dev 库验证时临时禁用/新建的记录均已恢复或删除（admin 与内置角色"管理员"保持启用）。

## 相关文件

- `backend/modules/admin/schemas/sys/user.py`
- `backend/modules/admin/schemas/sys/role.py`
- `backend/modules/common/schemas/base.py`（BoolField / parse_bool 定义）
- `backend/core/i18n/locales/zh-CN.yaml`、`en-US.yaml`
- `aiDoc/frontend-backend/boundary.md`（status 桥接约定）

## 记录日期

2026-10-08
