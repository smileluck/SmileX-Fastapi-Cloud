#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, BeforeValidator
from datetime import datetime
from zoneinfo import ZoneInfo
from modules.common.schemas.base import BaseRespEntity, BaseEntity, BaseReqEntity, BoolField
from modules.common.schemas.page import PageRequest
from database.models.sys.role import DataScopeEnum


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class SysRoleQueryParams(PageRequest):
    """
    系统角色查询参数模型
    用于角色列表分页查询时的筛选条件
    """

    name: Optional[str] = Field(None, description="角色名称，支持模糊查询")
    status: BoolField = Field(None, description="角色状态：True-启用，False-禁用")
    is_system: BoolField = Field(None, description="是否为系统内置角色")


class SysRoleCreate(BaseReqEntity):
    """
    系统角色创建请求模型
    用于创建新角色时的请求数据
    """

    name: str = Field(..., description="角色名称", min_length=1, max_length=20)
    desc: Optional[str] = Field(None, description="角色描述", max_length=200)
    status: bool = Field(True, description="角色状态：1-启用，2-禁用")
    sort: int = Field(0, description="排序号", ge=0)
    data_scope: DataScopeEnum = Field(DataScopeEnum.SELF, description="数据范围：ALL/DEPT_AND_SUB/DEPT_ONLY/SELF")
    menu_ids: List[int] = Field([], description="菜单ID列表")


class SysRoleUpdate(BaseReqEntity):
    """
    系统角色更新请求模型
    用于更新角色信息时的请求数据
    """

    name: Optional[str] = Field(None, description="角色名称", max_length=20)
    desc: Optional[str] = Field(None, description="角色描述", max_length=200)
    status: BoolField = Field(None, description="角色状态：True-启用，False-禁用")
    sort: Optional[int] = Field(None, description="排序号", ge=0)
    data_scope: Optional[DataScopeEnum] = Field(None, description="数据范围：ALL/DEPT_AND_SUB/DEPT_ONLY/SELF")
    menu_ids: Optional[List[int]] = Field(None, description="菜单ID列表")


class SysRoleSimpleResponse(BaseRespEntity):
    """
    系统角色简单响应模型
    用于只需要展示基本角色信息的场景
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    status: bool = Field(..., description="角色状态")


class SysRoleListResponse(BaseRespEntity):
    """
    系统角色列表响应模型
    用于角色列表展示，不包含关联菜单数据
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    desc: Optional[str] = Field(None, description="角色描述")
    status: bool = Field(True, description="角色状态：1-启用，2-禁用")
    data_scope: DataScopeEnum = Field(DataScopeEnum.SELF, description="数据范围")
    is_default: bool = Field(..., description="是否为默认角色")
    is_system: bool = Field(..., description="是否为系统内置角色")
    sort: int = Field(..., description="排序号")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")


class SysRoleResponseData(BaseRespEntity):
    """
    系统角色详细响应模型
    用于展示角色完整信息，包括关联的菜单
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    name: str = Field(..., description="角色名称")
    desc: Optional[str] = Field(None, description="角色描述")
    status: bool = Field(True, description="角色状态：1-启用，2-禁用")
    data_scope: DataScopeEnum = Field(DataScopeEnum.SELF, description="数据范围")
    is_default: bool = Field(..., description="是否为默认角色")
    is_system: bool = Field(..., description="是否为系统内置角色")
    sort: int = Field(..., description="排序号")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")
    menu_ids: List[int] = Field([], description="菜单ID列表")


class SysRoleBatchUpdateStatus(BaseReqEntity):
    """
    系统角色批量更新状态请求模型
    用于批量启用或禁用角色
    """

    role_ids: List[int] = Field(..., description="角色ID列表")
    status: bool = Field(..., description="要设置的状态：True-启用，False-禁用")


class SysRoleAssignMenu(BaseReqEntity):
    """
    系统角色分配菜单权限请求模型
    用于为角色分配菜单权限
    """

    menu_ids: List[int] = Field(..., description="菜单ID列表")
