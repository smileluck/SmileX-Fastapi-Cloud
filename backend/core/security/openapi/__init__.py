#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""开放API 安全工具：凭据生成/加解密 + HMAC 签名"""
from .crypto import (
    generate_app_id,
    generate_app_secret,
    encrypt_secret,
    decrypt_secret,
)
from .signature import (
    HEADER_APP_ID,
    HEADER_TIMESTAMP,
    HEADER_NONCE,
    HEADER_SIGNATURE,
    build_canonical_string,
    compute_signature,
    verify_signature,
    is_valid_nonce,
)

__all__ = [
    "generate_app_id",
    "generate_app_secret",
    "encrypt_secret",
    "decrypt_secret",
    "HEADER_APP_ID",
    "HEADER_TIMESTAMP",
    "HEADER_NONCE",
    "HEADER_SIGNATURE",
    "build_canonical_string",
    "compute_signature",
    "verify_signature",
    "is_valid_nonce",
]
