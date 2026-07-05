#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API HMAC-SHA256 签名工具

============================== 签名契约（客户端必须严格复现） ==============================

请求头：
    X-App-Id     : 商户 AppId
    X-Timestamp  : 秒级 Unix 时间戳（字符串）
    X-Nonce      : 客户端生成的随机串（8-64 字符，同一时间窗口内不可重复）
    X-Signature  : HMAC-SHA256 签名（hex 小写）

Canonical String（参与签名的待签字符串），6 个字段以 "\\n" 连接，顺序固定：

    METHOD \\n PATH \\n timestamp \\n nonce \\n app_id \\n body_sha256_hex

说明：
    - METHOD        : HTTP 方法，大写（GET/POST/PUT/DELETE ...）
    - PATH          : 请求路径 request.url.path，不含 query string
    - timestamp     : 与 X-Timestamp 一致
    - nonce         : 与 X-Nonce 一致
    - app_id        : 与 X-App-Id 一致
    - body_sha256_hex: 请求 body 字节的 sha256 hex digest；
                      body 为空时该字段为空字符串（canonical 末尾保留一个 "\\n"）

示例（GET 请求，无 body）：
    canonical = "GET\\n/open/demo/ping\\n1700000000\\nabc123\\nSMXxxxxxxxx\\n"
    signature = hmac_sha256(app_secret, canonical).hexdigest()

=========================================================================================
"""
import hashlib
import hmac
from typing import Optional

# 签名相关请求头
HEADER_APP_ID = "X-App-Id"
HEADER_TIMESTAMP = "X-Timestamp"
HEADER_NONCE = "X-Nonce"
HEADER_SIGNATURE = "X-Signature"

_NONCE_MIN_LEN = 8
_NONCE_MAX_LEN = 64


def build_canonical_string(
    method: str,
    path: str,
    body_bytes: bytes,
    timestamp: str,
    nonce: str,
    app_id: str,
) -> str:
    """按契约拼接 canonical string。"""
    body_hash = hashlib.sha256(body_bytes).hexdigest() if body_bytes else ""
    return "\n".join(
        [
            method.upper(),
            path,
            timestamp,
            nonce,
            app_id,
            body_hash,
        ]
    )


def compute_signature(canonical: str, app_secret: str) -> str:
    """用 app_secret 对 canonical 计算 HMAC-SHA256，返回 hex 小写"""
    return hmac.new(
        app_secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def verify_signature(expected: str, provided: str) -> bool:
    """常量时间比较签名，避免时序攻击"""
    if not expected or not provided:
        return False
    return hmac.compare_digest(expected, provided)


def is_valid_nonce(nonce: Optional[str]) -> bool:
    """nonce 非空且长度在 8-64 之间"""
    return bool(nonce) and _NONCE_MIN_LEN <= len(nonce) <= _NONCE_MAX_LEN
