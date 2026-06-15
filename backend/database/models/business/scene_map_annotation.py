#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scene_map import SceneMap


class SceneMapAnnotation(Base):
    """
    场景地图标注信息表
    """

    map_id: Mapped[int] = mapped_column(
        ForeignKey("scene_map.id", ondelete="CASCADE"),
        nullable=False,
        comment="地图ID",
    )
    x: Mapped[float] = mapped_column(nullable=False, comment="X坐标")
    y: Mapped[float] = mapped_column(nullable=False, comment="Y坐标")
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="标注名称")
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="标注类型(字典值)")
    angle: Mapped[float] = mapped_column(default=0, comment="角度(度)")

    map: Mapped["SceneMap"] = relationship(
        back_populates="annotations",
        lazy="noload",
        init=False,
    )
