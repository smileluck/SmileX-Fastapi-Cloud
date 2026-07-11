# 本地 .log 日志按日期目录滚动

## 需求描述

用户反馈：本地 `.log` 日志需要实现按日期划分的滚动日志；通过生产启动脚本（`deploy/deploy.sh` 安装的 systemd 服务）启动时没有滚动日志。

实际现状：
- Python 应用日志（`info.log`/`error.log`/`app.log`）已使用 `TimedRotatingFileHandler`，按天滚动，但采用 `info.log.YYYY-MM-DD` 后缀形式。
- Gunicorn 自身的 `access.log` / `error.log` 是固定文件，不会滚动。

需求目标：
1. 日志按日期目录归档，例如 `/var/log/smilex_cloud/2026-07-11/access.log`。
2. 完善 `deploy/deploy.sh` 及 systemd 服务，使生产启动路径产生的 `.log` 日志具备该能力。

## 状态

已完成

## 涉及范围

### 后端

- `backend/core/log/daily_dir_handler.py`：新增 `DailyDirFileHandler`，继承 `TimedRotatingFileHandler`，重写 `rotation_filename()`，在滚动时把日志移入 `YYYY-MM-DD/` 子目录。
- `backend/core/log/app_logging.py`：`defaults["log_dir"]` 改用 `log_dir.as_posix()`，避免 Windows 本地开发时反斜杠被 `logging.config.fileConfig` 解析为 unicode 转义而失败。
- `backend/config/logging_prod.ini`：`infoFileHandler` / `errorFileHandler` 的 `class` 改为 `core.log.daily_dir_handler.DailyDirFileHandler`。
- `backend/config/logging_dev.ini`：`devFileHandler` 的 `class` 改为 `core.log.daily_dir_handler.DailyDirFileHandler`，保持本地与生产行为一致。
- `backend/gunicorn.conf.py`：新增 Gunicorn 配置文件，统一进程参数与 `logconfig_dict`，让 `gunicorn.access` / `gunicorn.error` 也通过 `DailyDirFileHandler` 按日期目录滚动。

### 部署

- `deploy/smilex-cloud.service`：`ExecStart` 改为使用 `-c /opt/smilex-cloud/backend/gunicorn.conf.py`，移除 `--access-logfile` / `--error-logfile`。
- `deploy/deploy.env`：新增 `GUNICORN_CONFIG="${BACKEND_DIR}/gunicorn.conf.py"`；移除不再使用的 `ACCESS_LOG` / `ERROR_LOG`。
- `deploy/deploy.sh`：`cmd_setup` 的 `sed` 模板替换中新增 `GUNICORN_CONFIG` 路径替换，移除 `access.log` / `error.log` 路径替换。

### 前端

无

## 约束与备注

- 当前活动日志仍保留在日志根目录（如 `/var/log/smilex_cloud/access.log`），滚动后的历史日志进入日期目录。
- `backupCount` 保持 90 天（prod）/ 14 天（dev），由 `TimedRotatingFileHandler` 自动清理最旧的日期目录。
- Gunicorn 多 worker 同时滚动时仍可能存在竞态，与原有 `TimedRotatingFileHandler` 行为一致；如后续高并发场景出现问题，可再评估 `concurrent-log-handler` 或系统级 `logrotate`。
- 修改后需要重新执行 `deploy/deploy.sh setup`（或 `systemctl daemon-reload && systemctl restart smilex-cloud`）使服务生效。

## 相关文件

- `backend/core/log/daily_dir_handler.py`
- `backend/core/log/app_logging.py`
- `backend/config/logging_prod.ini`
- `backend/config/logging_dev.ini`
- `backend/gunicorn.conf.py`
- `deploy/smilex-cloud.service`
- `deploy/deploy.env`
- `deploy/deploy.sh`

## 记录日期

2026-07-11
