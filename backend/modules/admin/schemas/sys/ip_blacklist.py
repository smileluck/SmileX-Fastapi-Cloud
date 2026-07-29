#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from core.i18n import t
from modules.common.schemas.base import BaseEntity


class IpBlacklistQueryParams(BaseEntity):
    """IP 黑名单查询参数"""

    ip: Optional[str] = Field(None, description="IP 模糊匹配")
    type: Optional[str] = Field(None, description="类型：permanent / temporary")


class IpBlacklistCreateRequest(BaseEntity):
    """新增 IP 黑名单"""

    ip: str = Field(..., description="IP 地址", max_length=64)
    type: str = Field("permanent", description="类型：permanent / temporary")
    reason: Optional[str] = Field(None, description="加入原因", max_length=255)
    ttl_seconds: Optional[int] = Field(
        None,
        description="过期时长(秒)。仅 temporary 时生效；与 expire_at 二选一",
        ge=1,
    )
    expire_at: Optional[datetime] = Field(
        None,
        description="过期时间点(ISO8601)。仅 temporary 时生效；优先级高于 ttl_seconds",
    )

    @field_validator("type")
    @classmethod
    def _check_type(cls, v: str) -> str:
        if v not in ("permanent", "temporary"):
            raise ValueError(t("validation.ip_blacklist_type"))
        return v


class IpBlacklistBatchDeleteRequest(BaseEntity):
    """批量删除"""

    ids: List[int] = Field(..., description="主键列表")


class IpBlacklistResponse(BaseEntity):
    """IP 黑名单列表项"""

    id: int
    ip: str
    type: str
    reason: Optional[str]
    expire_at: Optional[datetime]
    creator_id: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
