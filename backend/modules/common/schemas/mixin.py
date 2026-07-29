#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, field_validator, Field, field_serializer
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
# 定义 Pydantic 基础模型，处理时间转换
class DateTimeResponseMixin(BaseModel):
    created_at: datetime = Field(
        ...,
        description="创建时间",
    )
    updated_at: datetime | None = Field(
        None,
        description="更新时间",
    )
    finish_at: datetime | None = Field(
        None,
        description="完成时间",
    )
    # 自定义 created_at 序列化器
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime, _info) -> str:
        # 转换为上海时区并格式化
        local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
        return local_time.strftime("%Y-%m-%d %H:%M:%S")
    # 自定义 updated_at 序列化器（处理 None 情况）
    @field_serializer('updated_at')
    def serialize_updated_at(self, value: datetime | None, _info) -> str | None:
        if value:
            local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None
    @field_serializer('finish_at')
    def serialize_finish_at(self, value: datetime | None, _info) -> str | None:
        if value:
            local_time = value.astimezone(ZoneInfo("Asia/Shanghai"))
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        return None
    class Config:
        from_attributes = True  # 支持从 SQLAlchemy 模型实例加载数据