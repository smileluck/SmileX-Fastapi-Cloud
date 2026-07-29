#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目配置文件
包含数据库连接、API端口、认证密钥等配置
"""
import os
from typing import List, Literal
from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from .settings_model import (
    DatabaseModel,
    DatatimeModel,
    ServiceModel,
    LogModel,
    TraceIdModel,
    JWTModel,
    RedisPoolModel,
    LocalUploadModel,
    StorageModel,
    SecurityModel,
    MCPModel,
    RateLimitModel,
    PluginModel,
    OpenApiModel,
    I18nModel,
)


# ------------------------------
# 1. 基础配置（所有环境共用）
# ------------------------------
class GlobalSetting(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",  # 加载项目根目录的.env文件
        env_file_encoding="utf-8",  # 避免中文乱码
        case_sensitive=False,  # 不区分环境变量大小写（如DB_HOST和db_host均可
        env_nested_delimiter="__",  # 基于__分割环境变量
    )
    # 环境配置
    ENVIR: Literal["dev", "test", "prod"] = Field(..., description="当前环境标识")
    # 日志配置
    LOG: LogModel = LogModel()
    # 安全配置
    SECURITY: SecurityModel = SecurityModel()
    # 项目基本配置
    SERVICE: ServiceModel = ServiceModel()
    # 日期配置
    DATETIME: DatatimeModel = DatatimeModel()
    # TraceId
    TRACE_ID: TraceIdModel = TraceIdModel()
    # JWT配置
    JWT: JWTModel = JWTModel()
    # 数据库配置
    DATABASE: DatabaseModel
    # Redis配置
    REDIS: RedisPoolModel = RedisPoolModel()
    # 本地上传配置
    UPLOAD_LOCAL: LocalUploadModel = LocalUploadModel()
    # 存储平台配置
    STORAGE: StorageModel = StorageModel()
    # MCP 配置
    MCP: MCPModel = MCPModel()
    # 限流配置
    RATE_LIMIT: RateLimitModel = RateLimitModel()
    # 插件配置
    PLUGINS: PluginModel = PluginModel()
    # 开放API（商户 HMAC 签名鉴权）配置
    OPEN_API: OpenApiModel = OpenApiModel()
    # 国际化配置
    I18N: I18nModel = I18nModel()
