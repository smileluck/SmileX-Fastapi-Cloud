#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gunicorn 配置文件。

统一进程参数与日志配置，让 Gunicorn 的 access / error 日志与 Python 应用日志
一样按 ``YYYY-MM-DD/`` 目录滚动归档。

注意：Gunicorn 的 error 日志输出到 ``gunicorn-error.log``（而非 ``error.log``），
避免与 ``config/logging_prod.ini`` 中应用根 logger 的 ``error.log`` 共用同一文件——
两个独立的 ``DailyDirFileHandler`` 同时写同一文件会在按天滚动时产生竞态，并使
不同格式的日志行交错混排。``access.log`` 仅 Gunicorn 写入，无冲突，保留原名。
"""

import os
from pathlib import Path

# ---- 进程参数 ----
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:8000")
workers = int(os.environ.get("GUNICORN_WORKERS", 4))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 120))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", 5000))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 500))
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")

# ---- 日志目录 ----
log_dir = Path(os.environ.get("LOG__DIR", "/var/log/smilex_cloud"))
log_dir.mkdir(parents=True, exist_ok=True)

# ---- 日志配置 ----
# 使用 logconfig_dict 覆盖 Gunicorn 默认的 access/error 日志，
# 使它们通过 DailyDirFileHandler 写入并按日期目录滚动。
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "generic": {
            "class": "logging.Formatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(module)s %(lineno)d %(process)d %(thread)d %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "access": {
            "class": "logging.Formatter",
            "format": "%(asctime)s %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "access_file": {
            "class": "core.log.daily_dir_handler.DailyDirFileHandler",
            "formatter": "access",
            "filename": str(log_dir / "access.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 90,
            "encoding": "utf-8",
            "delay": False,
            "utc": False,
        },
        "error_file": {
            "class": "core.log.daily_dir_handler.DailyDirFileHandler",
            "formatter": "generic",
            "filename": str(log_dir / "gunicorn-error.log"),
            "when": "D",
            "interval": 1,
            "backupCount": 90,
            "encoding": "utf-8",
            "delay": False,
            "utc": False,
        },
    },
    "loggers": {
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["access_file"],
            "propagate": False,
        },
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["error_file"],
            "propagate": False,
        },
    },
}
