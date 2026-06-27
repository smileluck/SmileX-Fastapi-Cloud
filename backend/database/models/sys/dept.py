#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Boolean, ForeignKey
from typing import List, Optional


class SysDept(Base):
    """
    系统部门表
    树形结构，用于行级数据权限的范围计算
    """

    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sys_dept.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="父部门ID，顶级部门为NULL",
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    code: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True, comment="部门编码"
    )
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )
    sort: Mapped[int] = mapped_column(default=0, comment="排序号")

    children: Mapped[List["SysDept"]] = relationship(
        back_populates="parent",
        lazy="noload",
        cascade="all, delete-orphan",
        init=False,
    )
    parent: Mapped[Optional["SysDept"]] = relationship(
        back_populates="children",
        remote_side="SysDept.id",
        lazy="noload",
        init=False,
    )
