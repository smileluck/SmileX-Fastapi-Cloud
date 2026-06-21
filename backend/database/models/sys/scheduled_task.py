#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from sqlalchemy import String, Text, Integer, Boolean, BigInteger, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysScheduledTask(Base):
    """定时任务表"""

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="任务名称"
    )
    task_key: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True, comment="任务唯一标识"
    )
    cron_expression: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Cron 表达式"
    )
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None, comment="任务描述"
    )
    trigger_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="cron", comment="触发类型: cron/interval/date"
    )
    trigger_params: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="触发参数 JSON"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, comment="状态: True启用/False禁用"
    )
    module: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None, comment="来源模块"
    )
    function_path: Mapped[str | None] = mapped_column(
        String(200), nullable=True, default=None, comment="函数路径"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, comment="系统任务不可删除"
    )
    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="上次执行时间"
    )
    next_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="下次执行时间"
    )
    last_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None, comment="上次执行状态: success/failed/running"
    )
    timeout: Mapped[int] = mapped_column(
        Integer, nullable=False, default=300, comment="超时时间(秒)"
    )
    max_retries: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="最大重试次数"
    )
    concurrent_policy: Mapped[str] = mapped_column(
        String(20), nullable=False, default="skip", comment="并发策略: skip/replace/run"
    )
