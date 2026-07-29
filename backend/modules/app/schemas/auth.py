#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import BaseModel, field_validator, Field
import re
from core.security.oauth.jwt import Token
from core.i18n import t


class LoginModel(BaseModel):
    """登录模型"""

    phone: str = Field(..., description="用户手机号")
    code: str = Field(..., description="短信验证码")

    @field_validator("phone")
    def phone_validator(cls, v):
        """验证手机号，示例：验证是否为中国大陆手机号"""
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError(t("auth.phone_cn_invalid"))
        return v

    @field_validator("code")
    def code_validator(cls, v):
        """验证短信验证码，示例：验证是否为6位数字"""
        if not re.match(r"^\d{6}$", v):
            raise ValueError(t("auth.sms_code_invalid"))
        return v


class RefreshTokenModel(BaseModel):
    """刷新token的模型"""

    refresh_token: str = Field(..., description="刷新令牌")

    @field_validator("refresh_token")
    def refresh_token_validator(cls, v):
        """验证刷新token是否为空"""
        if not v.strip():
            raise ValueError(t("auth.refresh_token_required"))
        return v


class SmsCodeModel(BaseModel):
    """短信验证码模型"""

    phone: str = Field(..., description="用户手机号")

    @field_validator("phone")
    def phone_validator(cls, v):
        """验证手机号，示例：验证是否为中国大陆手机号"""
        if not re.match(r"^1[3-9]\d{9}$", v):
            raise ValueError(t("auth.phone_cn_invalid"))
        return v


class CurrentRobotModel(BaseModel):
    """当前使用的机器人模型"""

    id: Optional[int] = Field(None, description="当前使用的机器人ID")
    name: Optional[str] = Field(None, description="当前使用的机器人名称")
    wifi_status: Optional[bool] = Field(False, description="当前使用的机器人WiFi状态")
    serial_number: Optional[str] = Field(None, description="当前使用的机器人序列号")


class UserInfoModel(BaseModel):
    """用户信息模型"""

    id: int = Field(..., description="用户ID")
    phone: str = Field(..., description="用户手机号")
    bind_wechat: bool = Field(..., description="是否绑定微信")


class UserInfoUpdateModel(BaseModel):
    """用户信息更新模型"""

    id: int = (Field(..., description="用户ID"),)
    name: Optional[str] = Field(None, description="用户名称")
    phone: Optional[str] = Field(None, description="用户手机号")


class UserPushSettingModel(BaseModel):
    """用户推送设置模型"""

    sms_alarm: Optional[bool] = Field(None, description="是否开启短信报警")
    app_alarm: Optional[bool] = Field(None, description="是否开启应用内报警")


class UserLoginResponseModel(Token):
    """用户登录响应模型"""

    robot: CurrentRobotModel = Field(
        CurrentRobotModel(), description="当前使用的机器人信息"
    )


class ClientIDModel(BaseModel):
    """客户端ID模型"""

    client_id: str = Field(..., description="客户端ID")
