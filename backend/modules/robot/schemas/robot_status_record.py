#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Optional, Any
from pydantic import Field, ConfigDict, field_validator
from datetime import datetime

from pydantic import BaseModel

from app.models.common.base import BaseRespEntity


class RobotStatusRecordQueryParams(BaseModel):
    """
    机器人状态记录查询参数模型
    用于状态记录列表分页查询时的筛选条件
    """

    robot_id: int = Field(..., description="机器人ID（必填）")


class LocationInfoData(BaseModel):
    """
    位置信息结构
    与前端 Api.Robot.LocationInfo 契约保持一致
    """

    x: Optional[float] = Field(None, description="x 坐标")
    y: Optional[float] = Field(None, description="y 坐标")
    angle: Optional[float] = Field(None, description="角度")
    update_at: Optional[str] = Field(None, description="更新时间")


class RobotStatusRecordResponseData(BaseRespEntity):
    """
    机器人状态记录响应模型
    用于展示状态记录完整信息
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="记录ID")
    robot_id: int = Field(..., description="机器人ID")
    battery: float = Field(..., description="电量百分比")
    signal: int = Field(..., description="信号强度")
    speed: float = Field(..., description="速度(m/s)")
    location: Optional[str] = Field(None, description="位置信息(JSON)")
    location_info: Optional[LocationInfoData] = Field(
        None, description="位置信息：{x, y, angle, update_at}"
    )
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    @field_validator("location_info", mode="before")
    @classmethod
    def _normalize_location_info(cls, v: Any) -> Any:
        # 兼容历史脏数据：location_info 被错误写入为 JSON 字符串标量（如 '"{}"'）
        # asyncpg 经 json.loads 解析后得到 Python str，这里再尝试解析为 dict
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
            except (ValueError, TypeError):
                return None
            return parsed if isinstance(parsed, dict) else None
        return v
