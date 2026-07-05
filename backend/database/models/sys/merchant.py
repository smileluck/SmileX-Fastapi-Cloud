#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base
from database.utils.timezone import timezone


class SysMerchant(Base):
    """
    系统商户表
    用于开放API接口的 HMAC 签名授权鉴证，每个商户持有一对 app_id / app_secret
    """

    # 以下为构造必填/可空字段（无默认值，须排在带默认值字段之前）
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="商户名称")
    code: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True, comment="商户编码"
    )
    contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="联系人姓名"
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(30), nullable=True, comment="联系电话"
    )
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="联系邮箱"
    )
    app_id: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="商户AppId（公开标识）"
    )
    app_secret_encrypted: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="app_secret（Fernet 加密后的 token，验签时解密）",
    )
    remark: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="备注")

    # 带默认值字段
    status: Mapped[bool] = mapped_column(
        Boolean, default=True, comment="状态：True-启用，False-禁用"
    )
    sort: Mapped[int] = mapped_column(default=0, comment="排序号")

    # 不参与构造
    secret_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        init=False,
        default=None,
        comment="密钥最近一次重置时间",
    )

    __table_args__ = (
        UniqueConstraint("app_id", name="uk_sys_merchant_app_id"),
    )

    def touch_secret(self) -> None:
        """更新密钥重置时间为当前时刻"""
        self.secret_updated_at = timezone.now()
