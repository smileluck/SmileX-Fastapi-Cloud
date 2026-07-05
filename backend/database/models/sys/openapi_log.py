#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysOpenapiLog(Base):
    """
    开放API调用日志表
    记录每一次 /open/* 请求的调用信息（含鉴权失败），用于运营审计与异常排查
    """

    # 构造必填字段
    app_id: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True, comment="调用方 AppId（来自请求头，可能不存在）"
    )
    method: Mapped[str] = mapped_column(String(10), nullable=False, comment="HTTP方法")
    path: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, comment="请求路径"
    )

    # 可选字段（带默认值，构造时可省略）
    merchant_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None, comment="商户名称（冗余，便于展示；可能为空）"
    )
    status_code: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="HTTP响应状态码"
    )
    err_code: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, index=True, comment="业务错误码（成功为空）"
    )
    msg: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, default=None, comment="响应消息"
    )
    client_ip: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, default=None, comment="客户端IP"
    )
    request_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, default=None, index=True, comment="请求追踪ID"
    )
    latency_ms: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, default=None, comment="请求耗时(毫秒)"
    )
