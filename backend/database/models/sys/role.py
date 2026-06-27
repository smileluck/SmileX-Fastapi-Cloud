#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Boolean, ForeignKey, Enum, Table, Column
from typing import List, Optional
from database.models.base import Base, DataClassBase
from .association_tables import sys_role_menu_association, sys_user_role_association


class DataScopeEnum(str, enum.Enum):
    """
    数据范围枚举：决定角色能看到哪些数据行
    """
    ALL = "ALL"                      # 全部数据
    DEPT_AND_SUB = "DEPT_AND_SUB"    # 本部门 + 子部门
    DEPT_ONLY = "DEPT_ONLY"          # 仅本部门
    SELF = "SELF"                    # 仅本人


class SysRole(Base):
    """
    系统角色表
    存储角色信息及其关联的权限配置
    """

    # 角色基本信息
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="角色名称"
    )
    desc: Mapped[str] = mapped_column(Text, nullable=True, comment="角色描述")
    data_scope: Mapped[DataScopeEnum] = mapped_column(
        Enum(DataScopeEnum, name="sys_role_data_scope"),
        default=DataScopeEnum.SELF,
        comment="数据范围：ALL/DEPT_AND_SUB/DEPT_ONLY/SELF",
    )
    # 关联关系
    # 与用户表的多对多关系
    users: Mapped[List["SysUser"]] = relationship(
        "SysUser",
        secondary=sys_user_role_association,
        back_populates="roles",
        lazy="select",
        default_factory=list,
    )
    # 与菜单表的多对多关系
    menus: Mapped[List["SysMenu"]] = relationship(
        "SysMenu",
        secondary=sys_role_menu_association,
        back_populates="roles",
        lazy="select",
        default_factory=list,
    )
    # 状态信息
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否为默认角色"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否为系统内置角色"
    )
    # 排序字段
    sort: Mapped[int] = mapped_column(default=0, comment="排序号")
