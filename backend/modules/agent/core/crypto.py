#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体域密钥加密

与 SmileX-Admin-Gin 保持一致的 AES-256-GCM 域隔离加密：
- key = SHA256(domain + material)，domain 为域前缀（agent / mcp 各自独立，密文互不可解）
- material 优先取配置 AGENT.CRYPTO_KEY，未配置回退 JWT.SECRET_KEY
  （更换回退密钥后旧密文不可解，重新保存即恢复）
- 输出 base64(nonce || 密文)；空串原样直通（表示未配置凭证）
- 掩码规则：长度 <= 8 全 *，否则 前3 + **** + 末4
"""
import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from core.config import settings

# 密钥域前缀：不同域各自派生密钥，单域密文泄露不影响其他域
AGENT_DOMAIN = "smilex-agent:"
MCP_DOMAIN = "smilex-mcp:"


def _derive_key(domain: str) -> bytes:
    """按域派生 32 字节 AES 密钥"""
    material = settings.AGENT.CRYPTO_KEY or settings.JWT.SECRET_KEY
    return hashlib.sha256(f"{domain}{material}".encode("utf-8")).digest()


def encrypt_secret(plaintext: str, domain: str = AGENT_DOMAIN) -> str:
    """加密明文，输出 base64(nonce || 密文)；空串原样返回"""
    if not plaintext:
        return ""
    nonce = os.urandom(12)
    cipher = AESGCM(_derive_key(domain)).encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + cipher).decode("ascii")


def decrypt_secret(encrypted: str, domain: str = AGENT_DOMAIN) -> str:
    """解密密文还原明文；空串原样返回；解密失败抛 ValueError"""
    if not encrypted:
        return ""
    try:
        raw = base64.b64decode(encrypted)
        nonce, cipher = raw[:12], raw[12:]
        return AESGCM(_derive_key(domain)).decrypt(nonce, cipher, None).decode("utf-8")
    except Exception as exc:
        raise ValueError(f"secret decrypt failed (domain={domain!r})") from exc


def mask_secret(plaintext: str) -> str:
    """生成展示掩码：<=8 位全 *，否则 前3 + **** + 末4"""
    if not plaintext:
        return ""
    if len(plaintext) <= 8:
        return "*" * len(plaintext)
    return f"{plaintext[:3]}****{plaintext[-4:]}"
