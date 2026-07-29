#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database.models.base import Base, DataClassBase, snowflake_id_key
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, text
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY


class AppUser(Base):
    """
    用户表 - 存储用户信息
    """

    name: Mapped[str] = mapped_column(String(255), comment="用户名")
    phone_code: Mapped[str] = mapped_column(
        String(10), comment="手机号区号，如：+86、+1 等", nullable=False
    )
    phone: Mapped[str] = mapped_column(String(13), comment="手机号")
    password: Mapped[str] = mapped_column(
        String(255), comment="密码哈希值", nullable=True, default=""
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="邮箱", default=None
    )
    wx_openid: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="微信 openid", default=None
    )
    wx_unionid: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="微信 unionid", default=None
    )
    # 状态信息
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="头像URL", default=None
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
