# 启动时打印日志文件落地位置

## 需求描述

用户要求：项目启动时打印日志记录的落地位置（日志目录/文件路径），方便定位日志。

## 状态

已完成

## 修复

`core/log/app_logging.py` 的 `setup_logging()`：在 `logging.config.fileConfig(...)` 成功、输出「日志系统初始化完成」之后，动态从 root logger 的 handlers 里收集带 `baseFilename` 的文件 handler，打印：

- 日志目录（解析后的绝对路径 `log_dir`）
- 日志文件（各文件 handler 的 `baseFilename`，dev 为 `app.log`，prod 为 `info.log`/`error.log`）
- 历史日志归档子目录（`log_dir / YYYY-MM-DD`，对应 `DailyDirFileHandler` 的归档规则）

动态读取 handler 而非硬编码文件名，保证 dev/prod 不同 INI 配置下都准确；未配置文件 handler 时提示「仅输出到控制台」。

`setup_logging()` 由 `core/registry/setup_registry.py` 的 `setup_app` 在启动时调用，故该信息出现在启动日志中。

## 涉及范围

### 后端

- `core/log/app_logging.py`：`setup_logging()` 增加日志位置打印。

### 前端

无。

## 约束与备注

- 实测输出（Windows）：
  ```
  日志目录: D:\...\backend\logs
  日志文件: D:\...\backend\logs\app.log
  历史日志按日期归档于: D:\...\backend\logs\YYYY-MM-DD 子目录
  ```
- 日志目录取自 `settings.LOG.DIR`，相对路径基于项目根目录解析（见 `app_logging._PROJECT_ROOT`）。
- Gunicorn 在 prod 下的 access/error 日志由 `gunicorn.conf.py` 单独配置，不在本次打印范围内（本次只覆盖应用 logger）。

## 相关文件

- `backend/core/log/app_logging.py`
- `backend/config/logging_dev.ini`、`backend/config/logging_prod.ini`
- `backend/core/log/daily_dir_handler.py`

## 记录日期

2026-07-13
