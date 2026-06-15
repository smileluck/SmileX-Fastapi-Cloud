#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Text, JSON, ForeignKey
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .robot import Robot


class LocationInfo:
    """位置信息数据结构"""

    def __init__(self, x=0.0, y=0.0, angle=0.0, update_at=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.update_at = update_at or datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "update_at": self.update_at.strftime("%Y-%m-%d %H:%M:%S") if self.update_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        update_at = data.get("update_at")
        if isinstance(update_at, str):
            try:
                update_at = datetime.strptime(update_at, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            except ValueError:
                update_at = datetime.now(timezone.utc)
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            angle=data.get("angle", 0.0),
            update_at=update_at,
        )

    @classmethod
    def default_dict(cls):
        return {}


class RobotStatusRecord(Base):
    """
    机器人状态记录表（与机器人一对一）
    """

    robot_id: Mapped[int] = mapped_column(
        ForeignKey("robot.id"), unique=True, nullable=False, comment="机器人ID"
    )
    battery: Mapped[float] = mapped_column(default=0, comment="电量百分比")
    signal: Mapped[int] = mapped_column(default=0, comment="信号强度")
    speed: Mapped[float] = mapped_column(default=0, comment="速度(m/s)")
    location: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="位置信息(JSON)"
    )
    location_info: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default_factory=LocationInfo.default_dict,
        comment="位置信息",
    )

    robot: Mapped["Robot"] = relationship(
        back_populates="status_record",
        lazy="noload",
        init=False,
    )
