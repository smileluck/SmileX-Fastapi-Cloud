#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Boolean, BigInteger, ForeignKey, DateTime, Table, Column
from typing import List, Optional
from datetime import datetime
from .association_tables import sys_user_role_association


class SysUser(Base):
    """
    系统用户表
    存储系统管理用户的基本信息和认证凭证
    """

    # 用户基本信息
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False, comment="用户名"
    )
    password: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="密码（bcrypt加密存储）"
    )
    nickname: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="用户昵称"
    )
    email: Mapped[str] = mapped_column(String(100), nullable=True, comment="邮箱")
    phone: Mapped[str] = mapped_column(String(20), nullable=True, comment="手机号")
    # 状态信息
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否为超级管理员", server_default=None
    )
    # 登录信息
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="最后登录时间",
        server_default=None,
        default=None,
    )
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="最后登录IP",
        server_default=None,
        default=None,
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="头像URL", server_default=None, default=None
    )
    last_tenant_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, default=None, comment="最后选择的租户ID",
        server_default=None,
    )
    dept_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("sys_dept.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        default=None,
        comment="所属部门ID",
    )
    # 关联关系
    # 与角色表的多对多关系
    roles: Mapped[List["SysRole"]] = relationship(
        secondary=sys_user_role_association,
        back_populates="users",
        lazy="select",
        init=False,
    )
