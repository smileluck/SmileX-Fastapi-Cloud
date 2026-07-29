#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统监控 Schema
"""

from typing import Optional, List
from pydantic import Field, BaseModel
from datetime import datetime

from modules.common.schemas.base import BaseEntity


class MemoryInfo(BaseModel):
    """内存信息"""
    total: int = Field(..., description="总内存(GB)")
    used: int = Field(..., description="已用内存(GB)")
    free: int = Field(..., description="可用内存(GB)")
    percent: float = Field(..., description="使用率(%)")
    total_mb: int = Field(..., description="总内存(MB)")
    used_mb: int = Field(..., description="已用内存(MB)")
    free_mb: int = Field(..., description="可用内存(MB)")


class DiskInfo(BaseModel):
    """磁盘信息"""
    total: int = Field(..., description="总磁盘(GB)")
    used: int = Field(..., description="已用磁盘(GB)")
    free: int = Field(..., description="可用磁盘(GB)")
    percent: float = Field(..., description="使用率(%)")
    total_mb: int = Field(..., description="总磁盘(MB)")
    used_mb: int = Field(..., description="已用磁盘(MB)")


class SystemMetricsResponse(BaseEntity):
    """系统指标响应模型"""
    cpu_percent: float = Field(..., description="CPU使用率(%)")
    cpu_percent_per_core: list[float] = Field(..., description="每核CPU使用率(%)")
    memory: MemoryInfo = Field(..., description="内存信息")
    disk: DiskInfo = Field(..., description="磁盘信息")
    boot_time: datetime = Field(..., description="系统启动时间")
    process_count: int = Field(..., description="进程数量")
    python_version: str = Field(..., description="Python版本")
    os_name: str = Field(..., description="操作系统")
    cpu_count: int = Field(..., description="CPU核心数")


class ApiStatsQueryParams(BaseEntity):
    """API统计查询参数"""
    minutes: int = Field(default=60, ge=1, le=1440, description="查询最近多少分钟的数据，默认60，最大1440")


class ApiStatsResponse(BaseEntity):
    """API统计响应模型"""
    timestamp: str = Field(..., description="时间窗口(格式: HH:MM)")
    avg_elapsed_ms: float = Field(..., description="平均响应时间(ms)")
    request_count: int = Field(..., description="请求总数")
    error_count: int = Field(..., description="错误数")
    error_rate: float = Field(..., description="错误率(%)")
