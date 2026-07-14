#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Union
from pydantic import Field, ConfigDict, field_validator, model_validator
from datetime import datetime
import re
from app.models.common.base import BaseRespEntity, BaseEntity, BoolField
from app.models.common.page import PageRequest

# 密码复杂度策略：6-20 位，且至少包含字母和数字（与前端 REG_PWD 保持一致）
PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)\w{6,20}$")


def validate_password_complexity(value: str) -> str:
    """校验密码复杂度：6-20 位，且必须同时包含字母和数字"""
    if not PASSWORD_PATTERN.match(value or ""):
        raise ValueError("密码需6-20位，且至少包含字母和数字")
    return value


class SysUserQueryParams(PageRequest):
    """
    系统用户查询参数模型
    用于用户列表分页查询时的筛选条件
    """

    username: Optional[str] = Field(None, description="用户名，支持模糊查询")
    nickname: Optional[str] = Field(None, description="用户昵称，支持模糊查询")
    email: Optional[str] = Field(None, description="邮箱，支持模糊查询")
    phone: Optional[str] = Field(None, description="手机号，支持模糊查询")
    status: BoolField = Field(None, description="用户状态：True-启用，False-禁用")
    is_superuser: BoolField = Field(None, description="是否为超级管理员")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")

    @field_validator("role_ids", mode="before")
    @classmethod
    def parse_role_ids(cls, v):
        """
        解析 role_ids 参数，支持逗号分隔的字符串格式
        """
        if v is None:
            return None
        if isinstance(v, list):
            return v
        if isinstance(v, str) and v.strip():
            return [int(r.strip()) for r in v.split(",") if r.strip()]
        return None


class SysUserCreate(BaseEntity):
    """
    系统用户创建请求模型
    用于创建新用户时的请求数据
    """

    username: str = Field(
        ..., description="用户名，必须唯一", min_length=4, max_length=20
    )
    password: str = Field(..., description="密码", min_length=6, max_length=20)
    nickname: str = Field(..., description="用户昵称", max_length=100)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    phone: Optional[str] = Field(None, description="手机号", max_length=20)
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(True, description="用户状态：True-启用，False-禁用")
    role_ids: List[int] = Field([], description="角色ID列表")
    dept_id: Optional[int] = Field(None, description="所属部门ID")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """
        验证邮箱格式
        """
        if v:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, v):
                raise ValueError("邮箱格式不正确")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """
        验证手机号格式
        """
        if v:
            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, v):
                raise ValueError("手机号格式不正确")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """验证密码复杂度：6-20 位，且必须同时包含字母和数字"""
        return validate_password_complexity(v)


class SysUserUpdate(BaseEntity):
    """
    系统用户更新请求模型
    用于更新用户信息时的请求数据
    """

    username: Optional[str] = Field(
        None, description="用户名", min_length=4, max_length=20
    )
    nickname: Optional[str] = Field(None, description="用户昵称", max_length=100)
    email: Optional[str] = Field(None, description="邮箱", max_length=100)
    phone: Optional[str] = Field(None, description="手机号", max_length=20)
    avatar: Optional[str] = Field(None, description="头像URL")
    status: BoolField = Field(None, description="用户状态：True-启用，False-禁用")
    role_ids: Optional[List[int]] = Field(None, description="角色ID列表")
    dept_id: Optional[int] = Field(None, description="所属部门ID")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """
        验证邮箱格式
        """
        if v:
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, v):
                raise ValueError("邮箱格式不正确")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        """
        验证手机号格式
        """
        if v:
            phone_pattern = r"^1[3-9]\d{9}$"
            if not re.match(phone_pattern, v):
                raise ValueError("手机号格式不正确")
        return v


class SysUserPasswordUpdate(BaseEntity):
    """
    系统用户密码更新请求模型
    用于重置或修改用户密码
    """

    old_password: Optional[str] = Field(None, description="旧密码")
    new_password: str = Field(..., description="新密码", min_length=6, max_length=20)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        """验证新密码复杂度：6-20 位，且必须同时包含字母和数字"""
        return validate_password_complexity(v)


class SysUserSimpleResponse(BaseRespEntity):
    """
    系统用户简单响应模型
    用于只需要展示基本用户信息的场景
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(..., description="用户状态")


class SysRoleSimpleResponseForUser(BaseRespEntity):
    """
    用于用户响应中的角色简单模型
    """

    model_config = ConfigDict(from_attributes=True)
    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    status: bool = Field(..., description="角色状态")


class SysUserListResponse(BaseRespEntity):
    """
    系统用户列表响应模型
    用于用户列表展示，含关联角色（编辑抽屉需按角色ID回填；roles 已由列表查询 selectinload，零额外开销）
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_superuser: bool = Field(..., description="是否为超级管理员")
    status: bool = Field(..., description="用户状态")
    dept_id: Optional[int] = Field(None, description="所属部门ID")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    roles: List[SysRoleSimpleResponseForUser] = Field([], description="角色列表")


class SysUserResponseData(BaseRespEntity):
    """
    系统用户详细响应模型
    用于展示用户完整信息，包括关联的角色
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: str = Field(..., description="用户昵称")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_superuser: bool = Field(..., description="是否为超级管理员")
    status: bool = Field(..., description="用户状态")
    dept_id: Optional[int] = Field(None, description="所属部门ID")
    last_login_at: Optional[datetime] = Field(None, description="最后登录时间")
    last_login_ip: Optional[str] = Field(None, description="最后登录IP")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    role_ids: List[int] = Field([], description="角色ID列表")
    roles: List[SysRoleSimpleResponseForUser] = Field([], description="角色列表")


class SysUserBatchUpdateStatus(BaseEntity):
    """
    系统用户批量更新状态请求模型
    用于批量启用或禁用用户
    """

    user_ids: List[int] = Field(..., description="用户ID列表")
    status: bool = Field(..., description="要设置的状态：True-启用，False-禁用")
