#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .robot import Robot


class TaskExecution(Base):
    """
    任务执行记录表
    """

    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联任务ID",
    )
    task_name: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="快照: 任务名称"
    )
    task_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="快照: 任务类型"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending",
        comment="执行状态: pending/running/paused/completed/failed/cancelled",
    )
    progress: Mapped[int] = mapped_column(
        Integer, default=0, comment="进度百分比 0-100"
    )
    current_position: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None, comment="当前执行位置"
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="开始时间"
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None, comment="结束时间"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="错误信息"
    )
    robot_id: Mapped[int | None] = mapped_column(
        ForeignKey("robot.id"), nullable=True, default=None, comment="执行机器人ID"
    )
    triggered_by: Mapped[str] = mapped_column(
        String(20), default="manual", comment="触发方式: manual/schedule"
    )

    task: Mapped["Task"] = relationship(
        back_populates="executions",
        lazy="noload",
        init=False,
    )
    robot: Mapped["Robot | None"] = relationship(
        lazy="noload",
        init=False,
    )
