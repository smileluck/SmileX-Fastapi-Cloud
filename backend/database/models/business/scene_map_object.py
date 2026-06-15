#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scene_map import SceneMap


class SceneMapObject(Base):
    """
    场景地图物体信息表
    """

    map_id: Mapped[int] = mapped_column(
        ForeignKey("scene_map.id", ondelete="CASCADE"),
        nullable=False,
        comment="地图ID",
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, comment="物体类型(字典值)")
    x: Mapped[float] = mapped_column(nullable=False, comment="X坐标")
    y: Mapped[float] = mapped_column(nullable=False, comment="Y坐标")
    width: Mapped[float] = mapped_column(default=0, comment="宽度")
    height: Mapped[float] = mapped_column(default=0, comment="高度")
    points: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None, comment="多边形顶点(JSON数组)"
    )

    map: Mapped["SceneMap"] = relationship(
        back_populates="objects",
        lazy="noload",
        init=False,
    )
