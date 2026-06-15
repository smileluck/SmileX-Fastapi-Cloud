#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from pydantic import Field, ConfigDict

from app.models.common.base import BaseReqEntity, BaseRespEntity


class SceneMapPathCreate(BaseReqEntity):
    """创建场景地图路径"""

    map_id: int = Field(..., description="地图ID")
    start_annotation_id: int = Field(..., description="起始标注ID")
    end_annotation_id: int = Field(..., description="结束标注ID")
    name: str | None = Field(None, description="路径名称")
    points: str | None = Field(None, description="中间路径点(JSON数组)")


class SceneMapPathUpdate(BaseReqEntity):
    """更新场景地图路径"""

    start_annotation_id: int | None = Field(None, description="起始标注ID")
    end_annotation_id: int | None = Field(None, description="结束标注ID")
    name: str | None = Field(None, description="路径名称")
    points: str | None = Field(None, description="中间路径点(JSON数组)")


class SceneMapPathResponseData(BaseRespEntity):
    """场景地图路径响应数据"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    map_id: int
    start_annotation_id: int
    end_annotation_id: int
    name: str | None
    points: str | None
    created_at: datetime | None
    updated_at: datetime | None
