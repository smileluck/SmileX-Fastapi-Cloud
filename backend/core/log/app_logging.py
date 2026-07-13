#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import io
import logging
import logging.config
from pathlib import Path
from core.config import settings

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_ENV_INI_MAP = {
    "dev": "logging_dev.ini",
    "test": "logging_dev.ini",
    "prod": "logging_prod.ini",
}


def setup_logging():
    # Windows 控制台默认编码非 UTF-8，重新配置以支持中文输出
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    env = settings.ENVIR.lower()
    ini_name = _ENV_INI_MAP.get(env, "logging_dev.ini")
    config_path = _PROJECT_ROOT / "config" / ini_name

    # 日志目录：优先使用 settings.LOG.DIR，相对路径基于项目根目录解析
    log_dir = Path(settings.LOG.DIR)
    if not log_dir.is_absolute():
        log_dir = _PROJECT_ROOT / log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    try:
        logging.config.fileConfig(
            str(config_path),
            disable_existing_loggers=False,
            encoding="utf8",
            defaults={
                "env": env,
                "log_dir": log_dir.as_posix(),
            },
        )
        logging.info(f"日志系统初始化完成，当前环境: {env}")
        # 打印日志落地位置，便于启动时定位日志文件
        log_files = sorted(
            {
                getattr(h, "baseFilename", None)
                for h in logging.getLogger().handlers
                if getattr(h, "baseFilename", None)
            }
        )
        if log_files:
            logging.info("日志目录: %s", log_dir)
            logging.info("日志文件: %s", ", ".join(log_files))
            logging.info("历史日志按日期归档于: %s 子目录", log_dir / "YYYY-MM-DD")
        else:
            logging.info("日志仅输出到控制台（未配置文件 handler）")
    except Exception as e:
        logging.basicConfig(level=logging.DEBUG if env == "dev" else logging.INFO)
        logging.error(f"日志配置加载失败: {str(e)}，已启用基础配置")
