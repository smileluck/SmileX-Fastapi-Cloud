#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from pydantic import Field, ConfigDict

from app.models.common.base import BaseReqEntity, BaseRespEntity


class SceneMapAnnotationCreate(BaseReqEntity):
    """创建场景地图标注"""

    map_id: int = Field(..., description="地图ID")
    x: float = Field(..., description="X坐标")
    y: float = Field(..., description="Y坐标")
    name: str = Field(..., description="标注名称")
    angle: float = Field(0, description="角度(度)")
    type: str = Field(..., description="标注类型(字典值)")


class SceneMapAnnotationUpdate(BaseReqEntity):
    """更新场景地图标注"""

    x: float | None = Field(None, description="X坐标")
    y: float | None = Field(None, description="Y坐标")
    name: str | None = Field(None, description="标注名称")
    angle: float | None = Field(None, description="角度(度)")
    type: str | None = Field(None, description="标注类型(字典值)")


class SceneMapAnnotationResponseData(BaseRespEntity):
    """场景地图标注响应数据"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    map_id: int
    x: float
    y: float
    name: str
    angle: float
    type: str
    created_at: datetime | None
    updated_at: datetime | None
