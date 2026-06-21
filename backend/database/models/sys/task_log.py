#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import String, Text, Integer, BigInteger, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysScheduledTaskLog(Base):
    """定时任务执行日志表"""

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, index=True, comment="任务ID"
    )
    task_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="任务名称(冗余)"
    )
    task_key: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="任务标识(冗余)"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running",
        comment="状态: running/success/failed/timeout",
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="开始时间"
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="结束时间"
    )
    duration_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True, default=None, comment="耗时(毫秒)"
    )
    result: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="执行结果"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="错误信息"
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="重试次数"
    )
    triggered_by: Mapped[str] = mapped_column(
        String(20), nullable=False, default="scheduler", comment="触发方式: scheduler/manual"
    )
