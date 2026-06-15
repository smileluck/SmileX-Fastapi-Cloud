#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List, Optional

from pydantic import Field, ConfigDict

from pydantic import BaseModel

from app.models.common.base import BaseReqEntity, BaseRespEntity, BoolField


class SceneGroupQueryParams(BaseModel):
    """场景分组查询参数"""

    name: str | None = Field(None, description="分组名称")
    status: BoolField = Field(None, description="状态")


class SceneGroupCreate(BaseReqEntity):
    """创建场景分组"""

    name: str = Field(..., description="分组名称")
    parent_id: int | None = Field(None, description="父分组ID")
    sort: int = Field(0, description="排序号")
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class SceneGroupUpdate(BaseReqEntity):
    """更新场景分组"""

    name: str | None = Field(None, description="分组名称")
    parent_id: int | None = Field(None, description="父分组ID")
    sort: int | None = Field(None, description="排序号")
    status: BoolField = Field(None, description="状态")


class SceneGroupResponseData(BaseRespEntity):
    """场景分组响应数据"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    sort: int
    status: bool
    created_at: datetime | None
    updated_at: datetime | None


class SceneGroupTreeResponse(BaseRespEntity):
    """场景分组树形响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    sort: int
    status: bool
    children: List["SceneGroupTreeResponse"] = Field(default_factory=list)
