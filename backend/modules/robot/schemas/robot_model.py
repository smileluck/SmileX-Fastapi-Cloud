#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import Field, ConfigDict
from datetime import datetime

from pydantic import BaseModel

from app.models.common.base import BaseRespEntity, BaseReqEntity, BoolField


class RobotModelQueryParams(BaseModel):
    """
    机器人型号查询参数模型
    用于型号列表分页查询时的筛选条件
    """

    name: Optional[str] = Field(None, description="型号名称，支持模糊查询")
    brand: Optional[str] = Field(None, description="品牌，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class RobotModelCreate(BaseReqEntity):
    """
    机器人型号创建请求模型
    用于创建新型号时的请求数据
    """

    name: str = Field(..., description="型号名称", max_length=100)
    brand: str = Field(..., description="品牌", max_length=100)
    model: str = Field(..., description="型号标识", max_length=100)
    status: bool = Field(True, description="状态：True-启用，False-禁用")
    sort: int = Field(0, description="排序号")


class RobotModelUpdate(BaseReqEntity):
    """
    机器人型号更新请求模型
    用于更新型号信息时的请求数据
    """

    name: Optional[str] = Field(None, description="型号名称", max_length=100)
    brand: Optional[str] = Field(None, description="品牌", max_length=100)
    model: Optional[str] = Field(None, description="型号标识", max_length=100)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")
    sort: Optional[int] = Field(None, description="排序号")


class RobotModelResponseData(BaseRespEntity):
    """
    机器人型号响应模型
    用于展示型号完整信息
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="型号ID")
    name: str = Field(..., description="型号名称")
    brand: str = Field(..., description="品牌")
    model: str = Field(..., description="型号标识")
    status: bool = Field(..., description="状态")
    sort: int = Field(..., description="排序号")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
