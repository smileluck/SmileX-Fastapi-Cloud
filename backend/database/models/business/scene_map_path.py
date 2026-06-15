#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scene_map import SceneMap
    from .scene_map_annotation import SceneMapAnnotation


class SceneMapPath(Base):
    """
    场景地图路径表
    """

    map_id: Mapped[int] = mapped_column(
        ForeignKey("scene_map.id", ondelete="CASCADE"),
        nullable=False,
        comment="地图ID",
    )
    start_annotation_id: Mapped[int] = mapped_column(
        ForeignKey("scene_map_annotation.id", ondelete="CASCADE"),
        nullable=False,
        comment="起始标注ID",
    )
    end_annotation_id: Mapped[int] = mapped_column(
        ForeignKey("scene_map_annotation.id", ondelete="CASCADE"),
        nullable=False,
        comment="结束标注ID",
    )
    name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=None, comment="路径名称"
    )
    points: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="中间路径点(JSON数组)"
    )

    map: Mapped["SceneMap"] = relationship(
        back_populates="paths",
        lazy="noload",
        init=False,
    )
