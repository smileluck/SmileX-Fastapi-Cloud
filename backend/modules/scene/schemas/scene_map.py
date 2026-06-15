#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from pydantic import Field, ConfigDict

from pydantic import BaseModel

from app.models.common.base import BaseReqEntity, BaseRespEntity, BoolField


class SceneMapQueryParams(BaseModel):
    """场景地图查询参数"""

    name: str | None = Field(None, description="地图名称")
    group_id: int | None = Field(None, description="分组ID")
    status: BoolField = Field(None, description="状态")


class SceneMapCreate(BaseReqEntity):
    """创建场景地图"""

    name: str = Field(..., description="地图名称")
    group_id: int | None = Field(None, description="分组ID（与group_name二选一）")
    group_name: str | None = Field(None, description="分组名称（不存在时自动创建）")
    image_id: int | None = Field(None, description="地图图片文件ID")
    width: int | None = Field(None, description="地图宽度(像素)")
    height: int | None = Field(None, description="地图高度(像素)")
    resolution: float = Field(0.2, description="分辨率(米/像素)")
    start_point_x: float = Field(0, description="起始点位X坐标")
    start_point_y: float = Field(0, description="起始点位Y坐标")
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class SceneMapUpdate(BaseReqEntity):
    """更新场景地图"""

    name: str | None = Field(None, description="地图名称")
    group_id: int | None = Field(None, description="分组ID")
    image_id: int | None = Field(None, description="地图图片文件ID")
    width: int | None = Field(None, description="地图宽度(像素)")
    height: int | None = Field(None, description="地图高度(像素)")
    resolution: float | None = Field(None, description="分辨率(米/像素)")
    start_point_x: float | None = Field(None, description="起始点位X坐标")
    start_point_y: float | None = Field(None, description="起始点位Y坐标")
    status: BoolField = Field(None, description="状态")


class SceneMapResponseData(BaseRespEntity):
    """场景地图响应数据"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    group_id: int | None
    image_id: int | None
    width: int | None
    height: int | None
    resolution: float | None = Field(None, description="分辨率(米/像素)")
    start_point_x: float = Field(0, description="起始点位X坐标")
    start_point_y: float = Field(0, description="起始点位Y坐标")
    status: bool
    group_name: str | None = Field(None, description="分组名称")
    created_at: datetime | None
    updated_at: datetime | None
