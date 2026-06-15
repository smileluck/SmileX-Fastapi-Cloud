#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import String, Text


class RobotFaceRecognition(Base):
    """
    机器人人脸识别TTS配置表
    存储人员人像与对应的语音播报内容
    """

    person_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="人员名称"
    )
    photo_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="人像图片URL"
    )
    broadcast_text: Mapped[str] = mapped_column(
        Text(), nullable=False, comment="语音播报内容"
    )
