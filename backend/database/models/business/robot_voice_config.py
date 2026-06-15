#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Integer, ForeignKey


class RobotVoiceConfig(Base):
    """
    机器人语音配置表
    按机器人存储唤醒词与TTS参数
    """

    robot_id: Mapped[int] = mapped_column(
        ForeignKey("robot.id"),
        nullable=False,
        unique=True,
        comment="机器人ID",
    )
    wake_word: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="唤醒词"
    )
    tts_voice: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="音色"
    )
    tts_speed: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="语速"
    )
    tts_volume: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="音量"
    )
