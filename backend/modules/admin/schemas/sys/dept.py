#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, BeforeValidator
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.common.base import BaseRespEntity, BaseEntity, BoolField
from app.models.common.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class SysDeptQueryParams(PageRequest):
    """
    系统部门查询参数模型
    """

    name: Optional[str] = Field(None, description="部门名称，支持模糊查询")
    code: Optional[str] = Field(None, description="部门编码，支持模糊查询")
    status: BoolField = Field(None, description="部门状态：True-启用，False-禁用")


class SysDeptCreate(BaseEntity):
    """
    系统部门创建请求模型
    """

    parent_id: Optional[int] = Field(None, description="父部门ID，顶级部门为None")
    name: str = Field(..., description="部门名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="部门编码", max_length=100)
    status: bool = Field(True, description="部门状态：True-启用，False-禁用")
    sort: int = Field(0, description="排序号", ge=0)


class SysDeptUpdate(BaseEntity):
    """
    系统部门更新请求模型
    """

    parent_id: Optional[int] = Field(None, description="父部门ID，顶级部门为None")
    name: Optional[str] = Field(None, description="部门名称", min_length=1, max_length=100)
    code: Optional[str] = Field(None, description="部门编码", max_length=100)
    status: BoolField = Field(None, description="部门状态：True-启用，False-禁用")
    sort: Optional[int] = Field(None, description="排序号", ge=0)


class SysDeptTreeResponse(BaseRespEntity):
    """
    系统部门树形响应模型
    用于下拉选择、角色配置等场景
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="部门ID")
    label: str = Field(..., description="部门名称")
    pId: Optional[int] = Field(None, description="父部门ID")
    status: bool = Field(True, description="部门状态")
    children: List["SysDeptTreeResponse"] = Field(default_factory=list, description="子部门列表")


SysDeptTreeResponse.model_rebuild()


class SysDeptResponseData(BaseRespEntity):
    """
    系统部门详细响应模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="部门ID")
    parent_id: Optional[int] = Field(None, description="父部门ID")
    name: str = Field(..., description="部门名称")
    code: Optional[str] = Field(None, description="部门编码")
    status: bool = Field(True, description="部门状态")
    sort: int = Field(..., description="排序号")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")
    children: List["SysDeptResponseData"] = Field(default_factory=list, description="子部门列表")


SysDeptResponseData.model_rebuild()


class SysDeptBatchUpdateStatus(BaseEntity):
    """
    系统部门批量更新状态请求模型
    """

    dept_ids: List[int] = Field(..., description="部门ID列表")
    status: bool = Field(..., description="要设置的状态：True-启用，False-禁用")
