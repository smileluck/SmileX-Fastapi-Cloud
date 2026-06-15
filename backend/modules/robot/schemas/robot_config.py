#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import Field, ConfigDict, field_validator
from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel

from app.models.common.base import BaseRespEntity, BaseReqEntity


def normalize_file_preview_path(value: str | None) -> str | None:
    if not value:
        return value
    parsed = urlsplit(value)
    return parsed.path if parsed.path.endswith("/preview") else value


class RobotVoiceConfigSchema(BaseReqEntity):
    """
    机器人语音合成配置请求模型
    """

    robot_id: int = Field(..., description="机器人ID")
    wake_word: str = Field(..., description="唤醒词", min_length=4, max_length=6)
    tts_voice: str = Field(..., description="音色", max_length=50)
    tts_speed: int = Field(..., description="语速")
    tts_volume: int = Field(..., description="音量")


class RobotVoiceConfigResponse(BaseRespEntity):
    """
    机器人语音合成配置响应模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(None, description="配置ID")
    robot_id: Optional[int] = Field(None, description="机器人ID")
    wake_word: Optional[str] = Field(None, description="唤醒词")
    tts_voice: Optional[str] = Field(None, description="音色")
    tts_speed: Optional[int] = Field(None, description="语速")
    tts_volume: Optional[int] = Field(None, description="音量")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class RobotFaceRecognitionCreate(BaseReqEntity):
    """
    人脸识别TTS配置创建请求模型
    """

    person_name: str = Field(..., description="人员名称", max_length=100)
    photo_url: str = Field(..., description="人像图片URL", max_length=255)
    broadcast_text: str = Field(..., description="语音播报内容")

    @field_validator("photo_url", mode="before")
    @classmethod
    def normalize_photo_url(cls, value: str | None) -> str | None:
        return normalize_file_preview_path(value)


class RobotFaceRecognitionUpdate(BaseReqEntity):
    """
    人脸识别TTS配置更新请求模型
    """

    person_name: Optional[str] = Field(None, description="人员名称", max_length=100)
    photo_url: Optional[str] = Field(None, description="人像图片URL", max_length=255)
    broadcast_text: Optional[str] = Field(None, description="语音播报内容")

    @field_validator("photo_url", mode="before")
    @classmethod
    def normalize_photo_url(cls, value: str | None) -> str | None:
        return normalize_file_preview_path(value)


class RobotFaceRecognitionResponse(BaseRespEntity):
    """
    人脸识别TTS配置响应模型
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="配置ID")
    person_name: str = Field(..., description="人员名称")
    photo_url: str = Field(..., description="人像图片URL")
    broadcast_text: str = Field(..., description="语音播报内容")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class TestWakeWordRequest(BaseModel):
    """
    测试唤醒词请求模型
    """

    text: str = Field(..., description="要测试的唤醒词文本")


class TestTTSRequest(BaseModel):
    """
    测试TTS请求模型
    """

    voice: str = Field(..., description="音色")
    speed: int = Field(..., description="语速")
    volume: int = Field(..., description="音量")
    text: str = Field(..., description="要播报的文本")
