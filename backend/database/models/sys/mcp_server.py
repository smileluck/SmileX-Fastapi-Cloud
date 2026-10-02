#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysMcpServer(Base):
    """
    外部 MCP 服务器接入配置表
    智能体以 "mcp:<code>:<tool>" 格式引用其工具；token 仅存 AES-GCM 密文
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="服务名称")
    code: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True, comment="服务编码（禁用冒号，供 mcp:<code>:<tool> 引用）"
    )
    base_url: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="消息端点地址（streamable_http）或事件流端点（sse）"
    )
    transport: Mapped[str] = mapped_column(
        String(20), default="streamable_http", comment="传输协议：streamable_http / sse"
    )
    headers: Mapped[Optional[str]] = mapped_column(Text, default=None, comment="自定义请求头 JSON 数组文本")
    token_enc: Mapped[Optional[str]] = mapped_column(
        String(512), default=None, comment="鉴权 Token 密文（AES-256-GCM base64）"
    )
    token_mask: Mapped[Optional[str]] = mapped_column(String(32), default=None, comment="鉴权 Token 掩码（仅展示用）")
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("code", name="uk_sys_mcp_server_code"),
    )
