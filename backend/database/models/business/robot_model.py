#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .robot import Robot


class RobotModel(Base):
    """
    机器人型号表
    """

    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="型号名称")
    brand: Mapped[str] = mapped_column(String(100), nullable=False, comment="品牌")
    model: Mapped[str] = mapped_column(String(100), nullable=False, comment="型号标识")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：True-启用，False-禁用")
    sort: Mapped[int] = mapped_column(default=0, comment="排序号")

    robots: Mapped[List["Robot"]] = relationship(
        back_populates="robot_model",
        lazy="noload",
        init=False,
    )
