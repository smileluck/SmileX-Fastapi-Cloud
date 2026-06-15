#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean, ForeignKey
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .scene_map import SceneMap


class SceneGroup(Base):
    """
    场景分组表
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="分组名称")
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("scene_group.id", ondelete="CASCADE"),
        nullable=True,
        default=None,
        comment="父分组ID",
    )
    sort: Mapped[int] = mapped_column(default=0, comment="排序号")
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )

    children: Mapped[List["SceneGroup"]] = relationship(
        back_populates="parent",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
    parent: Mapped["SceneGroup"] = relationship(
        back_populates="children",
        remote_side="SceneGroup.id",
        lazy="noload",
        init=False,
    )
    maps: Mapped[List["SceneMap"]] = relationship(
        back_populates="group",
        lazy="noload",
        init=False,
    )
