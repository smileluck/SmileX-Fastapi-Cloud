#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控服务
"""
import asyncio
import logging
import platform
from datetime import datetime, timedelta, timezone

import psutil
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case

from database.models.sys.operation_log import SysOperationLog

logger = logging.getLogger(__name__)

# 预热 psutil CPU 使用率基线，避免首次调用返回 0.0
# psutil.cpu_percent(interval=None) 需要前一次采样作为基准，首次调用无基准会返回 0
try:
    psutil.cpu_percent(interval=None)
    psutil.cpu_percent(interval=None, percpu=True)
except Exception as exc:  # pragma: no cover
    logger.warning("CPU 使用率基线预热失败: %s", exc)


class MonitorService:
    """系统监控服务类"""

    @staticmethod
    def _bytes_to_gb(n: int) -> int:
        """将字节转换为GB（取整）"""
        return round(n / (1024 ** 3))

    @staticmethod
    def _bytes_to_mb(n: int) -> int:
        """将字节转换为MB（取整）"""
        return round(n / (1024 ** 2))

    @staticmethod
    def _collect_system_metrics() -> dict:
        """同步收集系统指标（在线程中执行）"""
        # CPU: 非阻塞调用，首次可能返回0
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
        if cpu_percent == 0.0 and cpu_percent_per_core:
            cpu_percent = round(sum(cpu_percent_per_core) / len(cpu_percent_per_core), 1)

        # 内存
        mem = psutil.virtual_memory()
        memory = {
            "total": MonitorService._bytes_to_gb(mem.total),
            "used": MonitorService._bytes_to_gb(mem.used),
            "free": MonitorService._bytes_to_gb(mem.available),
            "percent": mem.percent,
            "total_mb": MonitorService._bytes_to_mb(mem.total),
            "used_mb": MonitorService._bytes_to_mb(mem.used),
            "free_mb": MonitorService._bytes_to_mb(mem.available),
        }

        # 磁盘（取根分区）
        disk = psutil.disk_usage("/")
        disk_info = {
            "total": MonitorService._bytes_to_gb(disk.total),
            "used": MonitorService._bytes_to_gb(disk.used),
            "free": MonitorService._bytes_to_gb(disk.free),
            "percent": disk.percent,
            "total_mb": MonitorService._bytes_to_mb(disk.total),
            "used_mb": MonitorService._bytes_to_mb(disk.used),
        }

        # 系统信息
        boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        process_count = len(psutil.pids())
        python_version = platform.python_version()

        return {
            "cpu_percent": cpu_percent,
            "cpu_percent_per_core": cpu_percent_per_core,
            "memory": memory,
            "disk": disk_info,
            "boot_time": boot_time,
            "process_count": process_count,
            "python_version": python_version,
            "os_name": platform.platform(),
            "cpu_count": psutil.cpu_count(logical=True),
        }

    @staticmethod
    async def get_system_metrics() -> dict:
        """
        获取系统实时指标

        Returns:
            包含CPU、内存、磁盘等系统信息的字典
        """
        return await asyncio.to_thread(MonitorService._collect_system_metrics)

    @staticmethod
    async def get_api_stats(db: AsyncSession, minutes: int = 60) -> list[dict]:
        """
        从操作日志中聚合API统计信息

        Args:
            db: 数据库会话
            minutes: 查询最近多少分钟的数据

        Returns:
            按分钟聚合的API统计列表
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        time_bucket = func.date_trunc("minute", SysOperationLog.created_at).label("time_bucket")

        stmt = (
            select(
                time_bucket,
                func.avg(SysOperationLog.elapsed_ms).label("avg_elapsed_ms"),
                func.count(SysOperationLog.id).label("request_count"),
                func.sum(
                    case(
                        (SysOperationLog.response_code >= 400, 1),
                        else_=0,
                    )
                ).label("error_count"),
            )
            .where(
                SysOperationLog.created_at >= cutoff,
            )
            .group_by(time_bucket)
            .order_by(time_bucket)
        )

        result = await db.execute(stmt)
        rows = result.all()

        stats = []
        for row in rows:
            bucket_dt = row.time_bucket
            request_count = row.request_count
            error_count = row.error_count or 0
            error_rate = round((error_count / request_count) * 100, 2) if request_count > 0 else 0.0

            stats.append({
                "timestamp": bucket_dt.strftime("%H:%M"),
                "avg_elapsed_ms": round(row.avg_elapsed_ms or 0, 2),
                "request_count": request_count,
                "error_count": error_count,
                "error_rate": error_rate,
            })

        return stats
