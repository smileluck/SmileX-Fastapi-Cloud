#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Integer, BigInteger, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task


class TaskPoint(Base):
    """
    任务巡逻点位表
    """

    task_id: Mapped[int] = mapped_column(
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=False,
        comment="所属任务ID",
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, default="wave", comment="运控动作: wave/bow/turn/wait/nod"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, comment="排序"
    )
    point_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None, comment="点位名称"
    )
    annotation_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("scene_map_annotation.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
        comment="关联场景标注ID",
    )
    voice_text: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="语音播报文本"
    )

    task: Mapped["Task"] = relationship(
        back_populates="points",
        lazy="noload",
        init=False,
    )
