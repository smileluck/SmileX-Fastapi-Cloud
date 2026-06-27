#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, field_validator, model_validator, BeforeValidator, AliasChoices
from datetime import datetime
from zoneinfo import ZoneInfo
from app.models.common.base import BaseRespEntity, BaseEntity, BoolField
from app.models.common.page import PageRequest
from database.models.sys.menu import MenuType


def _format_datetime(v):
    if isinstance(v, datetime):
        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


def _menu_type_to_str(v):
    if isinstance(v, MenuType):
        mapping = {MenuType.CATALOG: "1", MenuType.MENU: "2", MenuType.EXTERNAL: "2", MenuType.BUTTON: "3"}
        return mapping.get(v, v.value)
    return v


def _int_icon_type_to_str(v):
    """图标类型统一转为前端约定的字符串 "1"/"2"。"""
    if v is None:
        return "1"
    if isinstance(v, bool):
        return "1"
    if isinstance(v, (int, float)):
        return "2" if int(v) == 2 else "1"
    s = str(v).strip()
    return "2" if s == "2" else "1"


class SysMenuQueryParams(PageRequest):
    """
    系统菜单查询参数模型
    用于菜单列表查询时的筛选条件
    """

    name: Optional[str] = Field(None, description="菜单名称，支持模糊查询")
    status: BoolField = Field(None, description="菜单状态：True-启用，False-禁用")
    type: Optional[MenuType] = Field(None, description="菜单类型")
    is_system: BoolField = Field(None, description="是否为系统内置菜单")

    @field_validator("type", mode="before")
    @classmethod
    def parse_menu_type(cls, v):
        """
        解析菜单类型参数，支持字符串格式转换为 MenuType 枚举
        """
        if v is None:
            return None
        if isinstance(v, MenuType):
            return v
        if isinstance(v, str) and v.strip():
            try:
                return MenuType(v.strip())
            except ValueError:
                return None
        return None


class SysMenuTreeQuery(BaseEntity):
    """
    系统菜单树形查询参数模型
    用于获取菜单树形结构时的筛选条件
    """

    status: BoolField = Field(None, description="菜单状态：True-启用，False-禁用")


class SysMenuCreate(BaseEntity):
    """
    系统菜单创建请求模型
    用于创建新菜单时的请求数据
    """

    parent_id: Optional[int] = Field(None, description="父菜单ID，顶级菜单为None")
    name: str = Field(..., description="菜单名称", max_length=100)
    path: Optional[str] = Field(None, description="路由路径", max_length=255)
    component: Optional[str] = Field(None, description="组件路径", max_length=255)
    redirect: Optional[str] = Field(None, description="重定向路径", max_length=255)
    permission: Optional[str] = Field(None, description="权限标识", max_length=100)
    meta_icon: Optional[str] = Field(None, description="路由图标", max_length=50)
    meta_icon_type: int = Field(1, description="图标类型：1-iconify，2-本地")
    meta_hidden: bool = Field(False, description="是否隐藏菜单")
    meta_affix: bool = Field(False, description="是否固定标签")
    meta_breadcrumb: bool = Field(True, description="是否显示面包屑")
    meta_href: Optional[str] = Field(None, description="外部链接地址", max_length=500)
    meta_keep_alive: bool = Field(False, description="是否缓存路由")
    status: bool = Field(True, description="菜单状态：True-启用，False-禁用")
    type: MenuType = Field(MenuType.MENU, description="菜单类型")
    is_system: bool = Field(False, description="是否为系统内置菜单")
    sort: int = Field(0, description="排序号")


class SysMenuUpdate(BaseEntity):
    """
    系统菜单更新请求模型
    用于更新菜单信息时的请求数据
    """

    parent_id: Optional[int] = Field(None, description="父菜单ID，顶级菜单为None")
    name: Optional[str] = Field(None, description="菜单名称", max_length=100)
    path: Optional[str] = Field(None, description="路由路径", max_length=255)
    component: Optional[str] = Field(None, description="组件路径", max_length=255)
    redirect: Optional[str] = Field(None, description="重定向路径", max_length=255)
    permission: Optional[str] = Field(None, description="权限标识", max_length=100)
    meta_icon: Optional[str] = Field(None, description="路由图标", max_length=50)
    meta_icon_type: Optional[int] = Field(None, description="图标类型：1-iconify，2-本地")
    meta_hidden: Optional[bool] = Field(None, description="是否隐藏菜单")
    meta_affix: Optional[bool] = Field(None, description="是否固定标签")
    meta_breadcrumb: Optional[bool] = Field(None, description="是否显示面包屑")
    meta_href: Optional[str] = Field(None, description="外部链接地址", max_length=500)
    meta_keep_alive: Optional[bool] = Field(None, description="是否缓存路由")
    status: BoolField = Field(None, description="菜单状态：True-启用，False-禁用")
    type: Optional[MenuType] = Field(None, description="菜单类型")
    sort: Optional[int] = Field(None, description="排序号")
    is_system: Optional[bool] = Field(None, description="是否为系统内置菜单")


class SysMenuSimpleResponse(BaseRespEntity):
    """
    系统菜单简单响应模型
    用于只需要展示基本菜单信息的场景
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="菜单ID")
    parent_id: Optional[int] = Field(None, description="父菜单ID")
    name: str = Field(..., description="菜单名称")
    path: Optional[str] = Field(None, description="路由路径")
    type: MenuType = Field(..., description="菜单类型")
    status: bool = Field(..., description="菜单状态")
    is_system: bool = Field(..., description="是否为系统内置菜单")
    sort: int = Field(..., description="排序号")


class SysMenuResponseData(BaseRespEntity):
    """
    系统菜单详细响应模型
    用于展示菜单完整信息
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="菜单ID")
    parentId: Optional[int] = Field(None, validation_alias=AliasChoices("parent_id", "parentId"), description="父菜单ID")
    menuName: str = Field(..., validation_alias=AliasChoices("name", "menuName"), description="菜单名称")
    routeName: Optional[str] = Field(None, validation_alias="name", description="路由名称")
    routePath: Optional[str] = Field(None, validation_alias=AliasChoices("path", "routePath"), description="路由路径")
    component: Optional[str] = Field(None, description="组件路径")
    icon: Optional[str] = Field(None, validation_alias="meta_icon", description="图标")
    iconType: Annotated[str, BeforeValidator(_int_icon_type_to_str)] = Field(
        "1",
        validation_alias=AliasChoices("meta_icon_type", "iconType"),
        description="图标类型：1-iconify，2-本地",
    )
    menuType: Annotated[str, BeforeValidator(_menu_type_to_str)] = Field(..., validation_alias=AliasChoices("type", "menuType"), description="菜单类型：1-目录，2-菜单，3-按钮")
    order: int = Field(..., validation_alias=AliasChoices("sort", "order"), description="排序号")
    i18nKey: Optional[str] = Field(None, description="国际化键")
    keepAlive: bool = Field(False, validation_alias=AliasChoices("meta_keep_alive", "keepAlive"), description="是否缓存")
    constant: bool = Field(False, description="是否常量路由")
    href: Optional[str] = Field(None, validation_alias=AliasChoices("meta_href", "href"), description="外链地址")
    hideInMenu: bool = Field(False, validation_alias=AliasChoices("meta_hidden", "hideInMenu"), description="是否隐藏菜单")
    activeMenu: Optional[str] = Field(None, description="激活的菜单")
    multiTab: bool = Field(True, description="是否多标签")
    fixedIndexInTab: Optional[int] = Field(None, description="固定标签索引")
    query: Optional[dict] = Field(None, description="路由查询参数")
    permission: Optional[str] = Field(None, description="权限标识")
    status: bool = Field(..., description="菜单状态")
    is_system: bool = Field(..., description="是否为系统内置菜单")
    created_at: Annotated[str, BeforeValidator(_format_datetime)] = Field(..., description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")
    children: List["SysMenuResponseData"] = Field(default_factory=list, description="子菜单列表")

    @model_validator(mode="after")
    def set_auto_fields(self):
        if self.i18nKey is None and self.menuName:
            self.i18nKey = f"route.{self.menuName}"
        return self


SysMenuResponseData.model_rebuild()


class SysMenuTreeResponse(BaseRespEntity):
    """
    系统菜单树形响应模型
    用于展示菜单树形结构
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="菜单ID")
    label: str = Field(..., description="菜单标签")
    pId: Optional[int] = Field(None, description="父菜单ID")
    menuType: str = Field("1", description="菜单类型：1-目录, 2-菜单, 3-按钮")
    children: List["SysMenuTreeResponse"] = Field([], description="子菜单列表")


class SysMenuBatchUpdateStatus(BaseEntity):
    """
    系统菜单批量更新状态请求模型
    用于批量启用或禁用菜单
    """

    menu_ids: List[int] = Field(..., description="菜单ID列表")
    status: bool = Field(..., description="要设置的状态：True-启用，False-禁用")
