#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from pydantic import Field, ConfigDict

from app.models.common.base import BaseReqEntity, BaseRespEntity


class SceneMapObjectCreate(BaseReqEntity):
    """创建场景地图物体"""

    map_id: int = Field(..., description="地图ID")
    type: str = Field(..., description="物体类型(字典值)")
    x: float = Field(..., description="X坐标")
    y: float = Field(..., description="Y坐标")
    width: float = Field(0, description="宽度")
    height: float = Field(0, description="高度")
    points: str | None = Field(None, description="多边形顶点(JSON数组)")


class SceneMapObjectUpdate(BaseReqEntity):
    """更新场景地图物体"""

    type: str | None = Field(None, description="物体类型(字典值)")
    x: float | None = Field(None, description="X坐标")
    y: float | None = Field(None, description="Y坐标")
    width: float | None = Field(None, description="宽度")
    height: float | None = Field(None, description="高度")
    points: str | None = Field(None, description="多边形顶点(JSON数组)")


class SceneMapObjectResponseData(BaseRespEntity):
    """场景地图物体响应数据"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    map_id: int
    type: str
    x: float
    y: float
    width: float
    height: float
    points: str | None
    created_at: datetime | None
    updated_at: datetime | None
