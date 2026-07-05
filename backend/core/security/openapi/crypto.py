#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API 商户凭据生成与可逆加密工具

HMAC 签名校验需要原始 app_secret 重新计算摘要，因此 app_secret 不能单向哈希存储，
必须可逆加密。这里使用 cryptography.Fernet（对称 AEAD）对 app_secret 加密落库。
"""
import secrets
from functools import lru_cache
from uuid import uuid4

from cryptography.fernet import Fernet

from core.config import settings


def generate_app_id(prefix: str | None = None) -> str:
    """生成全局唯一的 AppId：前缀 + 16 位 hex（大写）"""
    return f"{prefix or settings.OPEN_API.APP_ID_PREFIX}{uuid4().hex[:16].upper()}"


def generate_app_secret() -> str:
    """生成 32 字节 url-safe 的随机 app_secret（明文，仅返回给客户端一次）"""
    return secrets.token_urlsafe(32)


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    """懒加载 Fernet 实例。密钥未配置时直接抛错，避免静默失败。"""
    key = settings.OPEN_API.SECRET_ENCRYPT_KEY
    if not key:
        raise RuntimeError(
            "OPEN_API__SECRET_ENCRYPT_KEY 未配置，无法加解密 app_secret。"
            "请在 .env 中设置一个 Fernet 密钥（Fernet.generate_key() 生成）"
        )
    return Fernet(key.encode())


def encrypt_secret(plaintext: str) -> str:
    """加密 app_secret 明文，返回 Fernet token 字符串"""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(token: str) -> str:
    """解密 Fernet token，返回 app_secret 明文"""
    return _fernet().decrypt(token.encode("utf-8")).decode("utf-8")
