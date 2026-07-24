# 首页仪表盘

## 需求描述

修复空白首页：原首页 `home/index.vue` 整页被注释，子组件全是 mock 数据。新增聚合接口 `GET /admin/sys/dashboard/summary`，用真实业务数据（用户总数、角色总数、在线用户数、今日登录次数）+ 最近登录时间线 + 最新公告列表替换空白首页。

## 状态

已完成

## 涉及范围

### 后端

- 新增 `modules/admin/endpoints/sys/dashboard.py`：聚合接口端点
- 新增 `modules/admin/services/sys/dashboard_service.py`：聚合查询服务（Redis 缓存 60s）
- 新增 `modules/admin/schemas/sys/dashboard.py`：响应 Schema
- 修改 `modules/admin/endpoints/sys/__init__.py`：注册 dashboard_router
- 修改 `core/middleware/operation_log_middleware.py`：加入白名单（高频接口不计操作日志）

### 前端

- 新增 `src/typings/api/dashboard.d.ts`：TypeScript 类型
- 新增 `src/service/api/dashboard.ts`：API 封装
- 重写 `src/views/home/index.vue`：调用聚合接口，展示完整内容
- 改造 `src/views/home/modules/card-data.vue`：改为接收 props（真实数据）
- 新增 `src/views/home/modules/recent-login.vue`：最近登录时间线（NTimeline）
- 新增 `src/views/home/modules/latest-notice.vue`：最新公告列表（NList）
- 删除 5 个模板遗留组件（header-banner、line-chart、pie-chart、project-news、creativity-banner）
- 更新 i18n 文案（zh-cn.ts、en-us.ts）

## 约束与备注

- 所有已登录用户可访问，不做 data_scope 过滤
- 聚合接口结果 Redis 缓存 60 秒（key: `dashboard:summary`）
- 每个统计字段独立 try-except 优雅降级，单字段失败不影响其他字段
- 在线用户数复用 `OnlineUserService.get_online_count()`（Redis session key 计数）
- 今日登录数按 Asia/Shanghai 时区当日 00:00 起算

## 相关文件

- `backend/modules/admin/endpoints/sys/dashboard.py`
- `backend/modules/admin/services/sys/dashboard_service.py`
- `backend/modules/admin/schemas/sys/dashboard.py`
- `backend/modules/admin/endpoints/sys/__init__.py`
- `backend/core/middleware/operation_log_middleware.py`
- `frontend/src/typings/api/dashboard.d.ts`
- `frontend/src/service/api/dashboard.ts`
- `frontend/src/views/home/index.vue`
- `frontend/src/views/home/modules/card-data.vue`
- `frontend/src/views/home/modules/recent-login.vue`
- `frontend/src/views/home/modules/latest-notice.vue`
- `frontend/src/locales/langs/zh-cn.ts`
- `frontend/src/locales/langs/en-us.ts`

## 记录日期

2026-07-23
