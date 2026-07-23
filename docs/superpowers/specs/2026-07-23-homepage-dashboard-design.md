# 首页仪表盘设计

> 日期：2026-07-23
> 状态：已确认，待实现

## 背景与动机

当前系统首页（`frontend/src/views/home/index.vue`）整页被 HTML 注释包裹，用户登录后看到空白页。子组件（`card-data.vue`、`line-chart.vue` 等）全部使用硬编码 mock 数据（访问量 9725、营业额 1026 等），内容与「云原生智能机器人管理平台」的定位无关。

后端 `monitor_service.py` 已有真实的系统指标采集（CPU/内存/磁盘）和 API 统计，但未接入首页。

本设计目标：**用真实业务数据替换空白首页，提供有意义的统计概览和动态信息流。**

## 范围

- 新增后端聚合接口 `GET /admin/sys/dashboard/summary`
- 重写前端首页，展示业务统计卡片 + 动态活动流（最近登录 + 最新公告）
- 清理模板遗留的无关组件

不在本次范围内：
- 系统资源监控（已在 `/monitor` 页实现）
- API 趋势图表（已在 `/monitor` 页实现）
- 用户间私信 / 独立消息中心

## 后端设计

### 新增文件

| 文件 | 职责 |
|------|------|
| `backend/modules/admin/endpoints/sys/dashboard.py` | `GET /admin/sys/dashboard/summary` 端点 |
| `backend/modules/admin/services/sys/dashboard_service.py` | 聚合查询逻辑 |
| `backend/modules/admin/schemas/sys/dashboard.py` | Pydantic 响应 Schema |

### 路由注册

在 `backend/modules/admin/endpoints/sys/__init__.py` 中注册 `dashboard_router`，挂载前缀 `/admin/sys/dashboard`。

### 接口契约

```
GET /admin/sys/dashboard/summary
```

无需请求参数。需 JWT 鉴权（复用现有 DependsPermission），所有已登录用户可访问，不做 data_scope 过滤。

**响应结构：**

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "stats": {
      "user_count": 128,
      "role_count": 8,
      "online_count": 5,
      "today_login_count": 23
    },
    "recent_logins": [
      {
        "username": "admin",
        "ip": "192.168.1.1",
        "status": true,
        "login_time": "2026-07-23T10:30:00+08:00",
        "location": "本地"
      }
    ],
    "latest_notices": [
      {
        "id": "1234567890",
        "title": "系统维护通知",
        "type": "announcement",
        "created_at": "2026-07-22T15:00:00+08:00"
      }
    ]
  },
  "request_id": "xxx",
  "err_code": null
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `stats.user_count` | int | 系统用户总数（排除软删除） |
| `stats.role_count` | int | 角色总数 |
| `stats.online_count` | int | 当前在线用户数（Redis 会话计数） |
| `stats.today_login_count` | int | 今日登录次数（Asia/Shanghai 当日 00:00 起算） |
| `recent_logins` | array | 最近 10 条登录记录，按时间倒序 |
| `recent_logins[].username` | string | 登录用户名 |
| `recent_logins[].ip` | string | 登录 IP |
| `recent_logins[].status` | bool | 登录是否成功（true=成功） |
| `recent_logins[].login_time` | datetime | 登录时间（带时区） |
| `recent_logins[].location` | string | IP 归属地（复用现有 ip_utils） |
| `latest_notices` | array | 最新 5 条已发布公告，按创建时间倒序 |
| `latest_notices[].id` | string | 公告 ID（雪花 ID 字符串） |
| `latest_notices[].title` | string | 公告标题 |
| `latest_notices[].type` | string | 公告类型（announcement/system/operation/approval） |
| `latest_notices[].created_at` | datetime | 创建时间（带时区） |

### 数据来源

全部复用现有 Service 和 Model，不新增查询逻辑：

| 数据 | 来源 | 说明 |
|------|------|------|
| `user_count` | `SysUser` 表 `select(func.count())` | 过滤 `deleted_at IS NULL` |
| `role_count` | `SysRole` 表 `select(func.count())` | 过滤 `deleted_at IS NULL` |
| `online_count` | Redis `scan_iter` 会话 key | 统计 `session:*` 模式的 key 数量 |
| `today_login_count` | `SysLoginLog` 表 count | `created_at >= 今日00:00 (Asia/Shanghai)` |
| `recent_logins` | `SysLoginLog` 表 | `order_by(created_at desc).limit(10)` |
| `latest_notices` | `SysNotice` 表 | `status=已发布`，`order_by(created_at desc).limit(5)` |

### 缓存策略

- 聚合结果用 Redis 缓存 60 秒，key：`dashboard:summary`
- 缓存 miss 时执行聚合查询，写入缓存
- 缓存命中直接返回缓存数据
- 目的：首页是高频访问页面，避免每次加载都打 6 次数据库查询

## 前端设计

### 布局结构

```
┌─────────────────────────────────────────────┐
│  欢迎横幅（显示当前用户昵称 + 今日日期）          │
├──────────┬──────────┬──────────┬─────────────┤
│ 用户总数  │ 角色数量  │ 在线用户  │ 今日登录数   │
│ (图标)   │ (图标)   │ (图标)   │ (图标)      │
│  128     │   8      │    5     │    23       │
├──────────────────────┬──────────────────────┤
│  最近登录 (时间线)     │  最新公告 (列表)       │
│  ● admin  10:30 ✓    │  · 系统维护通知  7/22  │
│  ● user1  10:25 ✓    │  · 版本更新说明  7/21  │
│  ● user2  10:20 ✗    │  · ...                │
└──────────────────────┴──────────────────────┘
```

- 欢迎横幅：全宽
- 统计卡片：4 列响应式网格（移动端 1 列，平板 2 列，桌面 4 列）
- 活动流：2 列响应式网格（左 14/24 宽放登录时间线，右 10/24 宽放公告列表）

### 组件变更

| 操作 | 文件 | 说明 |
|------|------|------|
| 重写 | `frontend/src/views/home/index.vue` | 取消注释，替换为真实布局，调用聚合接口 |
| 修改 | `frontend/src/views/home/modules/card-data.vue` | 改为接收 props（真实数据），保留渐变卡片 + CountTo 数字动画 |
| 新增 | `frontend/src/views/home/modules/recent-login.vue` | 最近登录时间线（NTimeline，成功绿色/失败红色） |
| 新增 | `frontend/src/views/home/modules/latest-notice.vue` | 最新公告列表（NList + NTag 类型标签） |
| 删除 | `header-banner.vue` | 模板遗留，内容无关 |
| 删除 | `line-chart.vue` | mock 折线图，无真实数据源 |
| 删除 | `pie-chart.vue` | mock 饼图，无真实数据源 |
| 删除 | `project-news.vue` | mock 项目新闻 |
| 删除 | `creativity-banner.vue` | 模板装饰横幅 |

### 新增前端文件

| 文件 | 职责 |
|------|------|
| `frontend/src/service/api/dashboard.ts` | `fetchDashboardSummary()` 请求封装 |
| `frontend/src/typings/api/dashboard.d.ts` | `DashboardSummary` TypeScript 类型声明 |

### card-data.vue 改动细节

- 移除硬编码的 mock 数据（visitCount、turnover、downloadCount、dealCount）
- 改为通过 props 接收 4 个统计值（userCount、roleCount、onlineCount、todayLoginCount）
- 保留渐变背景色 + SvgIcon + CountTo 动画的 UI 设计
- 图标与配色映射：
  - 用户总数：`ant-design:user-outlined`，紫色调
  - 角色数量：`ant-design:team-outlined`，蓝色调
  - 在线用户：`ant-design:online-outlined`，绿色调
  - 今日登录：`ant-design:login-outlined`，橙色调

### recent-login.vue 设计

- 使用 NaiveUI `NTimeline` 组件
- 每条记录显示：用户名 + IP + 时间（相对时间如「10分钟前」）+ 状态图标（成功绿色 ✓ / 失败红色 ✗）
- 空数据显示 `NEmpty`

### latest-notice.vue 设计

- 使用 NaiveUI `NList` 组件
- 每条显示：类型标签（NTag，不同颜色区分 announcement/system/operation）+ 标题 + 发布时间
- 空数据显示 `NEmpty`

### i18n

补充 `page.home.*` 相关文案（中英文）：
- `page.home.welcome`：欢迎语模板（含用户名占位）
- `page.home.userCount`：用户总数
- `page.home.roleCount`：角色数量
- `page.home.onlineCount`：在线用户
- `page.home.todayLoginCount`：今日登录
- `page.home.recentLogin`：最近登录
- `page.home.latestNotice`：最新公告
- `page.home.loginSuccess`：登录成功
- `page.home.loginFailed`：登录失败
- `page.home.noData`：暂无数据

## 错误处理与边界

### 优雅降级

- `online_count` 依赖 Redis，若 Redis 不可用 → 返回 `0` 并记录 WARNING 日志
- 每个 stats 字段独立 try-except，单个查询失败时该字段返回 `0`，不影响其他字段
- `recent_logins` / `latest_notices` 查询失败时返回 `[]`
- 前端组件对接收到的数据做空值防护

### 边界情况

| 场景 | 行为 |
|------|------|
| 全新部署（无用户/日志/公告） | 所有数字为 0，列表为空，卡片显示 0，时间线/列表显示空态 |
| Redis 宕机 | `online_count` 为 0，其余正常；缓存不生效，每次直查 DB |
| 某个查询超时 | 该字段降级为 0 或 []，其余字段正常返回 |

### 时区

- `today_login_count` 按 `Asia/Shanghai` 时区当日 00:00 起算
- 复用 `backend/database/utils/timezone.py` 的 `get_shanghai_now()` 工具函数

## 性能

- 聚合接口 Redis 缓存 60 秒，正常情况下每分钟最多 1 次完整聚合查询
- 6 次子查询均为简单的 count 或 limit 查询，单次耗时 < 10ms
- 前端仅在进入首页时请求 1 次，不做轮询
