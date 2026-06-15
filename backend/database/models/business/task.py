#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean, Text, Date, Time, Table, Column, BigInteger, ForeignKey
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .task_point import TaskPoint
    from .task_execution import TaskExecution
    from .robot import Robot

# 任务-机器人多对多关联表
task_robot_association = Table(
    "task_robot",
    Base.metadata,
    Column("task_id", BigInteger, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True),
    Column("robot_id", BigInteger, ForeignKey("robot.id", ondelete="CASCADE"), primary_key=True),
)


class Task(Base):
    """
    任务表
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="任务名称")
    task_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="任务类型: patrol-巡逻, broadcast-播报"
    )
    broadcast_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="播报文本"
    )
    broadcast_count: Mapped[str | None] = mapped_column(
        String(10), nullable=True, default=None, comment="播报次数: 1/2/3/5/loop"
    )
    schedule_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否启用定时调度"
    )
    schedule_date: Mapped[str | None] = mapped_column(
        Date, nullable=True, default=None, comment="调度日期"
    )
    schedule_start_time: Mapped[str | None] = mapped_column(
        Time, nullable=True, default=None, comment="调度开始时间"
    )
    schedule_repeat_cycle: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None, comment="重复周期: 逗号分隔的星期值 mon,tue,wed,thu,fri,sat,sun"
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="启用状态: True-启用, False-禁用"
    )
    status: Mapped[str] = mapped_column(
        String(20), default="idle", comment="执行状态: idle/running/paused"
    )

    points: Mapped[List["TaskPoint"]] = relationship(
        back_populates="task",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
    executions: Mapped[List["TaskExecution"]] = relationship(
        back_populates="task",
        lazy="noload",
        init=False,
    )
    robots: Mapped[List["Robot"]] = relationship(
        secondary=task_robot_association,
        lazy="noload",
        init=False,
    )
