#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List
from pydantic import Field, model_validator
from modules.common.schemas.base import BaseEntity, BaseRespEntity, BoolField
from plugins.multi_tenant.schemas.tenant_config import (
    TenantJwtConfig,
    TenantConfigSchema,
    parse_tenant_config,
    serialize_tenant_config,
)


class TenantCreate(BaseEntity):
    """创建租户请求"""

    name: str = Field(..., description="租户名称", min_length=1, max_length=100)
    code: str = Field(..., description="租户编码", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="租户描述")
    contact_name: Optional[str] = Field(None, description="联系人")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    contact_phone: Optional[str] = Field(None, description="联系手机")
    max_users: int = Field(100, description="最大用户数")
    jwt_config: Optional[TenantJwtConfig] = Field(None, description="JWT配置（为空则使用全局配置）")


class TenantUpdate(BaseEntity):
    """更新租户请求"""

    name: Optional[str] = Field(None, description="租户名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="租户描述")
    contact_name: Optional[str] = Field(None, description="联系人")
    contact_email: Optional[str] = Field(None, description="联系邮箱")
    contact_phone: Optional[str] = Field(None, description="联系手机")
    max_users: Optional[int] = Field(None, description="最大用户数")
    jwt_config: Optional[TenantJwtConfig] = Field(None, description="JWT配置（为空则使用全局配置）")


class TenantQueryParams(BaseEntity):
    """租户查询参数"""

    name: Optional[str] = Field(None, description="租户名称（模糊匹配）")
    code: Optional[str] = Field(None, description="租户编码（模糊匹配）")
    status: BoolField = Field(None, description="状态筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(100, ge=1, le=200, description="每页条数")


class TenantResponse(BaseRespEntity):
    """租户响应数据"""

    id: int = Field(..., description="租户ID")
    name: str
    code: str
    description: Optional[str] = None
    status: bool = True
    config: Optional[str] = None
    jwt_config: Optional[TenantJwtConfig] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    max_users: int = 100

    @model_validator(mode="before")
    @classmethod
    def parse_config(cls, values):
        if isinstance(values, dict):
            config_str = values.get("config")
            if config_str and not values.get("jwt_config"):
                parsed = parse_tenant_config(config_str)
                if parsed.jwt:
                    values["jwt_config"] = parsed.jwt
        return values


class TenantListResponse(BaseRespEntity):
    """租户列表项"""

    id: int = Field(..., description="租户ID")
    name: str
    code: str
    description: Optional[str] = None
    status: bool = True
    contact_name: Optional[str] = None
    max_users: int = 100


class TenantSimpleResponse(BaseRespEntity):
    """租户简要信息（用于选择器）"""

    id: int = Field(..., description="租户ID")
    name: str
    code: str
    status: bool = True


class TenantConfigResponse(BaseRespEntity):
    """租户配置响应"""

    tenant_id: int = Field(..., description="租户ID")
    jwt_config: Optional[TenantJwtConfig] = Field(None, description="JWT配置")
    login_url: Optional[str] = Field(None, description="登录URL")


class TenantConfigUpdate(BaseEntity):
    """更新租户配置请求"""

    jwt_config: Optional[TenantJwtConfig] = Field(None, description="JWT配置（为空则使用全局配置）")
    login_url: Optional[str] = Field(None, description="登录URL")


class TenantAssignUser(BaseEntity):
    """分配用户到租户"""

    user_id: int = Field(..., description="用户ID")
    role: str = Field("member", description="租户角色：owner, admin, member")


class TenantUserInfo(BaseRespEntity):
    """租户中的用户信息"""

    id: int = Field(..., description="用户ID")
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: bool = True
    tenant_role: str = "member"


class SelectTenantRequest(BaseEntity):
    """选择租户请求"""

    tenant_id: int = Field(..., description="租户ID")
