# 操作日志：白名单补充高频轮询/状态接口

## 需求描述

用户反馈：「记录操作日志时，轮询接口不要频繁记录」。此前已白名单 export/task/list、monitor 等显式轮询，但仍有高频非操作类读取混入操作日志。

## 状态

已完成

## 依据（直接查 sys_operation_log 近 3 小时 Top）

```
20  GET /admin/sys/merchant/list        # 业务列表，用户主动测试产生，保留
13  GET /admin/sys/route/getPermissions  # 鉴权基础设施，每次初始化都调 → 纯噪音
11  GET /admin/sys/notice/my/unread-count # 通知铃铛状态读取（弹窗/WS 触发）
 6  PUT /admin/sys/merchant/{id}/reset-secret  # 真实操作，保留
```

## 修复

`core/middleware/operation_log_middleware.py` 的 `WHITELIST_PREFIXES` 追加：

- `/admin/sys/route` —— route 模块**仅有 GET**（getPermissions / isRouteExist 等），整前缀安全；属鉴权/路由探测基础设施，非用户操作。
- `/admin/sys/notice/my/unread-count` —— 通知未读数，高频状态读取。
- `/admin/sys/notice/my/list` —— 「我的通知」列表，弹窗打开 / WS 事件触发。

**刻意不全前缀 `/admin/sys/notice`**：notice 模块含写操作（add / publish / update / delete / batch / my 标记已读），这些是真实用户操作，需保留记录；只排除 `my/unread-count`、`my/list` 两个高频读。

## 验证

`_is_whitelisted` 用 10 条路径断言全部通过：

| path | 结果 |
|---|---|
| /admin/sys/route/getPermissions、/route/isRouteExist | 白名单 ✓ |
| /admin/sys/notice/my/unread-count、/my/list | 白名单 ✓ |
| /admin/sys/notice/my/read-all、/my/{id}/read | 保留（标记已读） |
| /admin/sys/notice/add、/notice/list | 保留（通知管理） |
| /admin/sys/merchant/list | 保留（业务列表） |
| /admin/sys/export/task/list | 白名单（既有） |

## 涉及范围

### 后端

- `core/middleware/operation_log_middleware.py`：`WHITELIST_PREFIXES` 追加 3 条。

### 前端

无。

## 约束与备注

- 只排除「高频非操作类读」。业务列表（如 merchant/list）仍记录——用户要的是「轮询接口」不刷屏，不是「读操作全不记」。
- `WHITELIST_SUFFIXES` / `WHITELIST_PATTERNS` 仍为空，预留给未来带动态路径参数的高频轮询（如 `/{id}/status` 轮询）。
- 改动为模块级常量，需重启后端进程生效（`main.py` 以 `reload=True` 运行时会自动重载）。
- 历史日志已写入的记录不会被回删，仅影响后续请求。

## 相关文件

- `backend/core/middleware/operation_log_middleware.py`
- `backend/modules/admin/endpoints/sys/route.py`、`notice.py`（确认仅 GET / 含写操作的依据）

## 记录日期

2026-07-13
