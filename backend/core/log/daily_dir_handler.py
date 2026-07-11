#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按日期目录组织的滚动日志 Handler。

继承 ``logging.handlers.TimedRotatingFileHandler``，在每天滚动时把日志文件移入
``YYYY-MM-DD/`` 子目录，而不是生成 ``.YYYY-MM-DD`` 后缀文件。
"""

import logging.handlers
from pathlib import Path


class DailyDirFileHandler(logging.handlers.TimedRotatingFileHandler):
    """按日期目录存放历史日志的 TimedRotatingFileHandler。

    示例：
        当前活动日志：``/var/log/smilex_cloud/access.log``
        滚动后归档：``/var/log/smilex_cloud/2026-07-11/access.log``
    """

    def rotation_filename(self, default_name: str) -> str:
        """将默认滚动文件名 ``base.log.YYYY-MM-DD`` 转换为 ``YYYY-MM-DD/base.log``。

        Args:
            default_name: 父类计算出的默认滚动文件名，含日期后缀。

        Returns:
            转换后的绝对路径字符串。
        """
        path = Path(default_name)
        # default_name 形如 /path/to/access.log.2026-07-11
        date_part = path.suffix.lstrip(".")  # YYYY-MM-DD
        base_name = path.stem  # access.log
        base_dir = path.parent  # /path/to

        date_dir = base_dir / date_part
        date_dir.mkdir(parents=True, exist_ok=True)

        target = date_dir / base_name
        # 与标准 TimedRotatingFileHandler 行为保持一致：目标已存在时先删除
        if target.exists():
            target.unlink()

        return str(target)
