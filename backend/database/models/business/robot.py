#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Integer, Enum as SaEnum, ForeignKey
from typing import TYPE_CHECKING, List
import enum

if TYPE_CHECKING:
    from .robot_model import RobotModel
    from .robot_status_record import RobotStatusRecord
    from .robot_event_log import RobotEventLog
    from .scene_map import SceneMap


class RobotStatus(str, enum.Enum):
    """机器人状态枚举"""

    ONLINE = "online"
    OFFLINE = "offline"
    INACTIVE = "inactive"


class Robot(Base):
    """
    机器人表
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="机器人名称")
    model_id: Mapped[int] = mapped_column(
        ForeignKey("robot_model.id"),
        nullable=False,
        comment="型号ID",
    )
    serial_number: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="序列号"
    )
    map_id: Mapped[int | None] = mapped_column(
        ForeignKey("scene_map.id"),
        nullable=True,
        default=None,
        comment="绑定场景地图ID",
    )
    status: Mapped[RobotStatus] = mapped_column(
        SaEnum(RobotStatus, values_callable=lambda e: [x.value for x in e]),
        default=RobotStatus.INACTIVE,
        comment="状态：online-在线，offline-离线，inactive-未激活",
    )
    speed_level: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None, comment="速度等级：normal-正常速度,slow-慢速,low-低速"
    )
    battery_threshold: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None, comment="电量报警阈值(%)"
    )

    robot_model: Mapped["RobotModel"] = relationship(
        back_populates="robots",
        lazy="noload",
        init=False,
    )
    map: Mapped["SceneMap"] = relationship(
        lazy="noload",
        init=False,
    )
    status_record: Mapped["RobotStatusRecord"] = relationship(
        back_populates="robot",
        lazy="noload",
        uselist=False,
        init=False,
    )
    event_logs: Mapped[List["RobotEventLog"]] = relationship(
        back_populates="robot",
        lazy="noload",
        init=False,
    )
