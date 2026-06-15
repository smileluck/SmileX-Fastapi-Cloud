#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .robot import Robot


class RobotEventLog(Base):
    """
    机器人事件日志表
    """

    robot_id: Mapped[int] = mapped_column(
        ForeignKey("robot.id"), nullable=False, comment="机器人ID"
    )
    event_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="事件类型：task-任务，alarm-告警"
    )
    event_status: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="事件状态：normal-正常，abnormal-异常"
    )
    event_content: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="事件内容"
    )

    robot: Mapped["Robot"] = relationship(
        back_populates="event_logs",
        lazy="noload",
        init=False,
    )
