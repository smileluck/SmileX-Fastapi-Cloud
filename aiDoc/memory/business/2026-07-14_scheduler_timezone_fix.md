# 调度器时区修复 + create_superuser naive 时间

## 需求描述

用户要求排查系统时区转换问题。审计后修复发现的两处：APScheduler 未固定时区、create_superuser 存 naive 时间。

## 状态

已完成

## 审计结论（已逐处核对）

- 🔴 **APScheduler 时区**：`AsyncIOScheduler` 未传 `timezone`，`CronTrigger.from_crontab` 默认取**服务器本地时区**（`tzlocal`）。`.env`/`deploy.sh`/systemd/Dockerfile 均未设 `TZ`，云端 UTC 服务器上 cron `0 9 * * *` 会按 09:00 UTC（=17:00 上海）触发，整体偏移 8 小时且随部署漂移。
- 🟡 **create_superuser.py**：`last_login_at=datetime.now()` 为 naive，写入 `DateTime(timezone=True)` 列被按会话时区解释。
- ✅ 正确：JWT（全 UTC `exp/iat`）、IP 黑名单（全 UTC `now` + 防御性 naive→UTC）、导出任务超时（全 UTC aware 比较）、限流（Redis TTL 相对秒，与时区无关）、DB 模型（`timezone.now()` 上海 aware，PG 存瞬时，响应 `astimezone(Shanghai)` 归一化）。
- ⚪ 文件名时间戳 `datetime.now().strftime(...)`（导出/操作日志）naive 无害，未改。

## 修复

### `modules/scheduler/core/scheduler.py`

- 新增 `from zoneinfo import ZoneInfo` 与 `from database.utils.timezone import DEFAULT_TIMEZONE`。
- `AsyncIOScheduler(timezone=ZoneInfo(DEFAULT_TIMEZONE), job_defaults={...})` —— 固定调度器时区为 Asia/Shanghai。
- `_build_trigger`：`CronTrigger.from_crontab(expr, timezone=ZoneInfo(DEFAULT_TIMEZONE))` —— 实际 job 的 cron 按上海解释（`from_crontab` 默认本地时区，必须显式传）。
- `preview_cron`：同样显式传 `timezone=ZoneInfo(DEFAULT_TIMEZONE)`，保证预览与实际触发一致。

> 关键点：仅设调度器 `timezone=` 不够 —— `from_crontab` 创建的 trigger 自带本地时区，加入调度器后不被覆盖，故三处（scheduler / build / preview）都要显式固定。

### `scripts/create_superuser.py`

- `from datetime import datetime` → `datetime, timezone`；`last_login_at=datetime.now()` → `datetime.now(timezone.utc)`。

## 验证

- `CronTrigger.from_crontab('0 9 * * *')` 默认 tz = 本机本地时区（开发机上海、UTC 服务器则 UTC）→ 印证 bug。
- `CronTrigger.from_crontab('0 9 * * *', timezone=ZoneInfo(DEFAULT_TIMEZONE))` → Asia/Shanghai，`next_fire_time = 09:00:00+08:00`。
- 调度器实例 `SchedulerManager()._scheduler.timezone == Asia/Shanghai`。
- 两文件 `py_compile` 通过。

## 约束与备注

- 固定到 `DEFAULT_TIMEZONE`（Asia/Shanghai），与用户在调度界面填写 cron 的预期一致。
- 改动改变既有 cron 的触发时区（若旧任务是在 UTC 服务器上建的，改后按上海时间重算 next_run）—— 这是修正为正确语义，非回归。
- 部署仍建议显式设 `TZ=Asia/Shanghai`（systemd/Docker），作为系统级兜底；本次用代码固定保证不依赖部署。

## 涉及范围

### 后端

- `modules/scheduler/core/scheduler.py`、`scripts/create_superuser.py`

### 前端

无。

## 相关文件

- `backend/modules/scheduler/core/scheduler.py`
- `backend/scripts/create_superuser.py`
- `backend/database/utils/timezone.py`（`DEFAULT_TIMEZONE` 来源，未改）

## 记录日期

2026-07-14
