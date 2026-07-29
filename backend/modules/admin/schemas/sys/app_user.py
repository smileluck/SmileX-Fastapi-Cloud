#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用用户（AppUser）管理相关 Schema
复用 sys/user.py 的密码复杂度策略与邮箱/手机号正则，保持口径一致。
"""
import re
from typing import Optional, List
from pydantic import Field, ConfigDict, field_validator
from datetime import datetime

from modules.common.schemas.base import BaseEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest
from modules.admin.schemas.sys.user import validate_password_complexity

# 邮箱/手机号正则与 SysUser 保持一致（AppUser 的 phone 同为 11 位中国号）
_EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
_PHONE_PATTERN = r"^1[3-9]\d{9}$"


class AppUserQueryParams(PageRequest):
    """
    应用用户查询参数模型
    """

    name: Optional[str] = Field(None, description="用户名，支持模糊查询")
    phone: Optional[str] = Field(None, description="手机号，支持模糊查询")
    phone_code: Optional[str] = Field(None, description="手机号区号")
    email: Optional[str] = Field(None, description="邮箱，支持模糊查询")
    status: BoolField = Field(None, description="用户状态：True-启用，False-禁用")
    wx_openid: Optional[str] = Field(None, description="微信 openid（传入则筛选已绑定微信的用户）")


class AppUserCreate(BaseEntity):
    """
    应用用户创建请求模型
    password 选填：留空表示该用户仅可通过短信验证码登录。
    """

    name: str = Field(..., description="用户名", max_length=255)
    phone_code: str = Field(..., description="手机号区号，如：86、+86、1 等", max_length=10)
    phone: str = Field(..., description="手机号（11 位）", max_length=13)
    password: Optional[str] = Field(
        None, description="密码（选填，留空则只能短信登录）", max_length=20
    )
    email: Optional[str] = Field(None, description="邮箱", max_length=255)
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(True, description="用户状态：True-启用，False-禁用")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(_EMAIL_PATTERN, v):
            raise ValueError("邮箱格式不正确")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(_PHONE_PATTERN, v):
            raise ValueError("手机号格式不正确")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """密码选填：仅在非空时校验复杂度"""
        if not v:
            return v
        return validate_password_complexity(v)


class AppUserUpdate(BaseEntity):
    """
    应用用户更新请求模型
    不含 password：改密走专用的 /password 接口。
    """

    name: Optional[str] = Field(None, description="用户名", max_length=255)
    phone_code: Optional[str] = Field(None, description="手机号区号", max_length=10)
    phone: Optional[str] = Field(None, description="手机号", max_length=13)
    email: Optional[str] = Field(None, description="邮箱", max_length=255)
    avatar: Optional[str] = Field(None, description="头像URL")
    status: BoolField = Field(None, description="用户状态：True-启用，False-禁用")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(_EMAIL_PATTERN, v):
            raise ValueError("邮箱格式不正确")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(_PHONE_PATTERN, v):
            raise ValueError("手机号格式不正确")
        return v


class AppUserPasswordUpdate(BaseEntity):
    """
    应用用户密码重置请求模型
    后台改密不需要旧密码（与 SysUser 的可选 old_password 不同）。
    """

    new_password: str = Field(..., description="新密码", min_length=6, max_length=20)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        return validate_password_complexity(v)


class AppUserBatchUpdateStatus(BaseEntity):
    """
    应用用户批量更新状态请求模型
    """

    user_ids: List[int] = Field(..., description="用户ID列表")
    status: bool = Field(..., description="要设置的状态：True-启用，False-禁用")


class AppUserListResponse(BaseRespEntity):
    """
    应用用户列表响应模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    phone_code: str = Field(..., description="手机号区号")
    phone: str = Field(..., description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(..., description="用户状态")
    wx_openid: Optional[str] = Field(None, description="微信 openid")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class AppUserResponseData(BaseRespEntity):
    """
    应用用户详细响应模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户名")
    phone_code: str = Field(..., description="手机号区号")
    phone: str = Field(..., description="手机号")
    email: Optional[str] = Field(None, description="邮箱")
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(..., description="用户状态")
    wx_openid: Optional[str] = Field(None, description="微信 openid")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
