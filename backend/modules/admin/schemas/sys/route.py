#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field


class RouteMetaResponse(BaseModel):
    """路由元信息响应模型"""

    title: str = Field(..., description="路由标题")
    i18nKey: str | None = Field(None, description="国际化键")
    icon: str | None = Field(None, description="路由图标")
    localIcon: str | None = Field(None, description="本地 SVG 图标名（meta_icon_type=2 时使用）")
    order: int | None = Field(None, description="排序号")
    hideInMenu: bool | None = Field(None, description="是否隐藏菜单")
    keepAlive: bool | None = Field(None, description="是否缓存路由")
    href: str | None = Field(None, description="外部链接")


class MenuRouteResponse(BaseModel):
    """菜单路由响应模型"""

    id: str = Field(..., description="路由ID")
    name: str = Field(..., description="路由名称")
    path: str = Field(..., description="路由路径")
    component: str | None = Field(None, description="组件路径")
    redirect: str | None = Field(None, description="重定向路径")
    meta: RouteMetaResponse = Field(..., description="路由元信息")
    children: list["MenuRouteResponse"] | None = Field(None, description="子路由")


class UserRouteResponse(BaseModel):
    """用户路由响应模型"""

    routes: list[MenuRouteResponse] = Field(..., description="路由列表")
    home: str = Field(default="home", description="首页路由名称")
    buttons: list[str] = Field(default_factory=list, description="按钮权限标识列表")
