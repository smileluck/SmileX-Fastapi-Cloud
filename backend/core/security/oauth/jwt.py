#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, TypeVar
import uuid
import jwt
import logging
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from pydantic import BaseModel
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from pydantic import Field


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
token_type = "Bearer"

logger = logging.getLogger(__name__)


class TokenData(BaseModel):
    """JWT令牌数据模型"""

    username: Optional[str] = Field(None, description="用户名")
    user_id: Optional[str] = Field(None, description="用户ID")
    scope: Optional[str] = Field(None, description="令牌作用域")


class Token(BaseModel):
    """令牌响应模型"""

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    expires_in: int = Field(..., description="令牌过期时间（秒）")
    refresh_token: str = Field(..., description="刷新令牌")


# 定义用户模型类型变量
t = TypeVar("t")


class JWTAuthManager:
    """JWT认证管理器"""

    @classmethod
    def create_access_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        access_lifetime: Optional[int] = None,
    ) -> str:
        """
        创建访问令牌
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            secret_key: 签名密钥（为空则使用全局配置）
            algorithm: 签名算法（为空则使用全局配置）
            access_lifetime: 有效期秒数（为空则使用全局配置）
        Returns:
            str: 编码后的JWT令牌
        """
        try:
            to_encode = data.copy()
            _key = secret_key or settings.JWT.SECRET_KEY
            _alg = algorithm or settings.JWT.ALGORITHM
            _lifetime = access_lifetime or settings.JWT.ACCESS_LIFETIME
            # 设置过期时间
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(seconds=_lifetime)
            to_encode.update(
                {
                    "exp": expire,
                    "iat": datetime.now(timezone.utc),
                    "aud": settings.JWT.AUDIENCE,
                    "iss": "spatialtemporal-ai-cloud",
                    "jti": uuid.uuid4().hex,
                }
            )
            encoded_jwt = jwt.encode(to_encode, _key, algorithm=_alg)
            return encoded_jwt
        except Exception as e:
            logger.exception("创建访问令牌异常: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="令牌创建失败"
            )

    @classmethod
    def create_refresh_token(
        cls,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> str:
        """
        创建刷新令牌
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            secret_key: 签名密钥（为空则使用全局配置）
            algorithm: 签名算法（为空则使用全局配置）
        Returns:
            str: 编码后的刷新令牌
        """
        try:
            to_encode = data.copy()
            _key = secret_key or settings.JWT.SECRET_KEY
            _alg = algorithm or settings.JWT.ALGORITHM
            # 设置过期时间，通常刷新令牌有效期更长
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(
                    seconds=settings.JWT.REFRESH_LIFETIME
                )
            to_encode.update(
                {
                    "exp": expire,
                    "iat": datetime.now(timezone.utc),
                    "aud": settings.JWT.AUDIENCE,
                    "iss": "spatialtemporal-ai-cloud",
                    "type": "refresh",
                    "jti": uuid.uuid4().hex,
                }
            )
            encoded_jwt = jwt.encode(to_encode, _key, algorithm=_alg)
            return encoded_jwt
        except Exception as e:
            logger.exception("创建刷新令牌异常: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="刷新令牌创建失败",
            )

    @classmethod
    def decode_token(
        cls,
        token: str,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        解码JWT令牌
        Args:
            token: JWT令牌字符串
            secret_key: 签名密钥（为空则使用全局配置）
            algorithm: 签名算法（为空则使用全局配置）
        Returns:
            Dict[str, Any]: 解码后的令牌数据
        Raises:
            HTTPException: 令牌无效或已过期
        """
        _key = secret_key or settings.JWT.SECRET_KEY
        _alg = algorithm or settings.JWT.ALGORITHM
        try:
            payload = jwt.decode(
                token,
                _key,
                algorithms=[_alg],
                audience=settings.JWT.AUDIENCE,
                options={"verify_signature": True},
            )
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": token_type},
            )
        except DecodeError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌格式错误",
                headers={"WWW-Authenticate": token_type},
            )
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌",
                headers={"WWW-Authenticate": token_type},
            )
        except Exception as e:
            logger.exception("令牌解码异常: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌验证失败",
                headers={"WWW-Authenticate": token_type},
            )

    @classmethod
    def decode_token_unverified(cls, token: str) -> Dict[str, Any]:
        """解码JWT令牌但不验证签名（仅用于提取 tenant_id 等非敏感信息）"""
        try:
            return jwt.decode(
                token,
                options={"verify_signature": False},
                audience=settings.JWT.AUDIENCE,
            )
        except Exception:
            return {}

    @classmethod
    def create_tokens(
        cls,
        user_data: Dict[str, Any],
        extra_claims: Optional[Dict[str, Any]] = None,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
        access_lifetime: Optional[int] = None,
    ) -> Token:
        """
        创建访问令牌和刷新令牌
        Args:
            user_data: 用户数据
            extra_claims: 额外声明（如 tenant_id），可选
            secret_key: 签名密钥（为空则使用全局配置）
            algorithm: 签名算法（为空则使用全局配置）
            access_lifetime: 有效期秒数（为空则使用全局配置）
        Returns:
            Token: 包含访问令牌和刷新令牌的响应模型
        """
        # 创建访问令牌的数据
        access_token_data = {
            "user_id": str(user_data.get("id", "")),
            "username": user_data.get("username", ""),
            "session_id": user_data.get("session_id", ""),
            "scope": "access",
            "role": user_data.get("role", ""),
        }
        # 创建刷新令牌的数据
        refresh_token_data = {
            "user_id": str(user_data.get("id", "")),
            "username": user_data.get("username", ""),
            "session_id": user_data.get("session_id", ""),
            "scope": "refresh",
            "role": user_data.get("role", ""),
        }
        if extra_claims:
            access_token_data.update(extra_claims)
            refresh_token_data.update(extra_claims)
        # 创建访问令牌和刷新令牌
        access_token = cls.create_access_token(
            access_token_data,
            secret_key=secret_key,
            algorithm=algorithm,
            access_lifetime=access_lifetime,
        )
        refresh_token = cls.create_refresh_token(
            refresh_token_data,
            secret_key=secret_key,
            algorithm=algorithm,
        )
        _lifetime = access_lifetime or settings.JWT.ACCESS_LIFETIME
        return Token(
            access_token=access_token,
            token_type=token_type,
            expires_in=_lifetime,
            refresh_token=refresh_token,
        )

    @classmethod
    def create_preview_token(
        cls,
        file_id: int,
        user_id: int,
        session_id: str,
        expires_seconds: int = 300,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> str:
        """创建短期、绑定单文件的预览令牌。

        用于文件在线预览（<img>/<video> src 无法携带 Authorization 头），
        替代直接把 access token 放进 URL query，缩小令牌泄露面。

        Args:
            file_id: 绑定的文件 ID（预览时校验一致）
            user_id: 申请者用户 ID
            session_id: 申请者会话 ID
            expires_seconds: 有效期秒数，默认 300（5 分钟）
            secret_key: 签名密钥（多租户下传租户密钥）
            algorithm: 签名算法

        Returns:
            str: 预览令牌（scope=preview）
        """
        payload = {
            "file_id": str(file_id),
            "user_id": str(user_id),
            "session_id": session_id,
            "scope": "preview",
        }
        return cls.create_access_token(
            payload,
            expires_delta=timedelta(seconds=expires_seconds),
            secret_key=secret_key,
            algorithm=algorithm,
        )

    @classmethod
    def decode_preview_token(
        cls,
        token: str,
        secret_key: Optional[str] = None,
        algorithm: Optional[str] = None,
    ) -> Dict[str, Any]:
        """解码预览令牌（验签 + 验过期 + 验 aud）。"""
        return cls.decode_token(token, secret_key=secret_key, algorithm=algorithm)
