#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean, ForeignKey, Integer, Float
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .scene_group import SceneGroup
    from .scene_map_annotation import SceneMapAnnotation
    from .scene_map_object import SceneMapObject
    from .scene_map_path import SceneMapPath
    from database.models.sys.file import SysFile


class SceneMap(Base):
    """
    场景地图表
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="地图名称")
    group_id: Mapped[int | None] = mapped_column(
        ForeignKey("scene_group.id"),
        nullable=True,
        default=None,
        comment="分组ID",
    )
    image_id: Mapped[int | None] = mapped_column(
        ForeignKey("sys_file.id"),
        nullable=True,
        default=None,
        comment="地图图片文件ID",
    )
    width: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None, comment="地图宽度(像素)"
    )
    height: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None, comment="地图高度(像素)"
    )
    resolution: Mapped[float] = mapped_column(
        Float, default=0.2, comment="分辨率(米/像素)，如0.2表示1像素=20厘米"
    )
    start_point_x: Mapped[float] = mapped_column(
        Float, default=0, comment="起始点位X坐标"
    )
    start_point_y: Mapped[float] = mapped_column(
        Float, default=0, comment="起始点位Y坐标"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )

    group: Mapped["SceneGroup"] = relationship(
        back_populates="maps",
        lazy="noload",
        init=False,
    )
    image: Mapped["SysFile"] = relationship(
        lazy="noload",
        init=False,
    )
    annotations: Mapped[List["SceneMapAnnotation"]] = relationship(
        back_populates="map",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
    objects: Mapped[List["SceneMapObject"]] = relationship(
        back_populates="map",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
    paths: Mapped[List["SceneMapPath"]] = relationship(
        back_populates="map",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
