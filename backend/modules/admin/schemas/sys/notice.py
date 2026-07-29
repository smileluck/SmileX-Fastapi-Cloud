#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知管理 Schema
"""

from typing import Optional, List
from pydantic import Field, ConfigDict, field_validator
from datetime import datetime

from modules.common.schemas.base import BaseRespEntity, BaseEntity, BoolField
from modules.common.schemas.page import PageRequest
from core.security.sanitize import sanitize_rich_text


class SysNoticeQueryParams(PageRequest):
    """
    通知查询参数模型
    """
    title: Optional[str] = Field(None, description="通知标题，支持模糊查询")
    type: Optional[str] = Field(None, description="通知类型")
    target_type: Optional[str] = Field(None, description="推送范围")
    status: BoolField = Field(None, description="状态：True-已发布，False-草稿")
    priority: Optional[str] = Field(None, description="优先级")
    sender_id: Optional[int] = Field(None, description="发送者用户ID")


class SysNoticeCreate(BaseEntity):
    """
    通知创建请求模型
    """
    title: str = Field(..., description="通知标题", max_length=200)
    content: str = Field(..., description="通知内容（支持HTML）")
    type: str = Field(default="system", description="通知类型")
    target_type: str = Field(default="all", description="推送范围")
    target_role_ids: Optional[List[int]] = Field(None, description="目标角色ID列表")
    target_user_ids: Optional[List[int]] = Field(None, description="目标用户ID列表")
    priority: str = Field(default="normal", description="优先级")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        allowed = {"announcement", "system", "operation", "approval"}
        if v not in allowed:
            raise ValueError(f"通知类型必须是以下之一: {allowed}")
        return v

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v):
        return sanitize_rich_text(v)

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v):
        allowed = {"all", "role", "user"}
        if v not in allowed:
            raise ValueError(f"推送范围必须是以下之一: {allowed}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        allowed = {"low", "normal", "high", "urgent"}
        if v not in allowed:
            raise ValueError(f"优先级必须是以下之一: {allowed}")
        return v

    @field_validator("target_role_ids")
    @classmethod
    def validate_target_role_ids(cls, v, info):
        values = info.data
        if values.get("target_type") == "role" and not v:
            raise ValueError("按角色推送时必须指定目标角色ID列表")
        return v

    @field_validator("target_user_ids")
    @classmethod
    def validate_target_user_ids(cls, v, info):
        values = info.data
        if values.get("target_type") == "user" and not v:
            raise ValueError("按用户推送时必须指定目标用户ID列表")
        return v


class SysNoticeUpdate(BaseEntity):
    """
    通知更新请求模型
    仅草稿状态可编辑
    """
    title: Optional[str] = Field(None, description="通知标题", max_length=200)
    content: Optional[str] = Field(None, description="通知内容")
    type: Optional[str] = Field(None, description="通知类型")
    target_type: Optional[str] = Field(None, description="推送范围")
    target_role_ids: Optional[List[int]] = Field(None, description="目标角色ID列表")
    target_user_ids: Optional[List[int]] = Field(None, description="目标用户ID列表")
    priority: Optional[str] = Field(None, description="优先级")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        if v is None:
            return v
        allowed = {"announcement", "system", "operation", "approval"}
        if v not in allowed:
            raise ValueError(f"通知类型必须是以下之一: {allowed}")
        return v

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v):
        if v is None:
            return v
        return sanitize_rich_text(v)

    @field_validator("target_type")
    @classmethod
    def validate_target_type(cls, v):
        if v is None:
            return v
        allowed = {"all", "role", "user"}
        if v not in allowed:
            raise ValueError(f"推送范围必须是以下之一: {allowed}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        if v is None:
            return v
        allowed = {"low", "normal", "high", "urgent"}
        if v not in allowed:
            raise ValueError(f"优先级必须是以下之一: {allowed}")
        return v


class SysNoticeListResponse(BaseRespEntity):
    """
    通知列表响应模型
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="通知ID")
    title: str = Field(..., description="通知标题")
    type: str = Field(..., description="通知类型")
    target_type: str = Field(..., description="推送范围")
    sender_id: int = Field(..., description="发送者用户ID")
    sender_name: str = Field(..., description="发送者名称")
    priority: str = Field(..., description="优先级")
    status: bool = Field(..., description="状态")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class SysNoticeResponse(BaseRespEntity):
    """
    通知详情响应模型
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="通知ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(..., description="通知类型")
    target_type: str = Field(..., description="推送范围")
    target_role_ids: Optional[List[int]] = Field(None, description="目标角色ID列表")
    target_user_ids: Optional[List[int]] = Field(None, description="目标用户ID列表")
    sender_id: int = Field(..., description="发送者用户ID")
    sender_name: str = Field(..., description="发送者名称")
    priority: str = Field(..., description="优先级")
    status: bool = Field(..., description="状态")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class MyNoticeQueryParams(PageRequest):
    """
    我的通知查询参数
    """
    is_read: BoolField = Field(None, description="是否已读")
    type: Optional[str] = Field(None, description="通知类型")


class MyNoticeResponse(BaseRespEntity):
    """
    我的通知响应模型
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="通知ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(..., description="通知类型")
    sender_name: str = Field(..., description="发送者名称")
    priority: str = Field(..., description="优先级")
    is_read: bool = Field(..., description="是否已读")
    read_at: Optional[datetime] = Field(None, description="阅读时间")
    published_at: Optional[datetime] = Field(None, description="发布时间")
    created_at: datetime = Field(..., description="创建时间")


class BatchReadRequest(BaseEntity):
    """
    批量标记已读请求
    """
    notice_ids: List[int] = Field(..., description="通知ID列表")
