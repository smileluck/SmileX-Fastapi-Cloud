#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any
from fastapi import HTTPException
from enum import Enum
from core.response import StandardResponseCode, CustomErrorCode


class BaseExceptionMixin(Exception):
    """基础异常混入类"""

    code: int
    err_code: CustomErrorCode

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        self.msg = msg
        self.data = data


class HTTPError(HTTPException):
    """HTTP 异常"""

    def __init__(
        self, *, code: int, msg: Any = None, headers: dict[str, Any] | None = None
    ):
        super().__init__(status_code=code, detail=msg, headers=headers)


class CustomError(BaseExceptionMixin):
    """自定义异常"""

    def __init__(
        self,
        *,
        error: CustomErrorCode,
        msg: str = None,
        data: Any = None,
    ):
        self.code = error.code
        super().__init__(msg=msg or error.msg, data=data)


class OpenApiError(BaseExceptionMixin):
    """
    开放API 鉴权异常

    与 CustomError 的区别：把 err_code 映射到语义正确的 4xx HTTP 状态，
    避免鉴权失败被当作 5xx 服务器错误（污染错误率告警、触发网关/客户端误重试）。
    响应结构仍保持统一 `{code, msg, data, request_id, err_code}`。

    默认 401；OPEN_API_INVALID_NONCE -> 400；OPEN_API_MERCHANT_DISABLED -> 403。
    """

    # err_code -> HTTP 状态码（未列出的鉴权失败默认 401）
    _STATUS_MAP = {
        CustomErrorCode.OPEN_API_INVALID_NONCE: 400,
        CustomErrorCode.OPEN_API_MERCHANT_DISABLED: 403,
    }

    def __init__(
        self,
        *,
        error: CustomErrorCode,
        msg: str = None,
        data: Any = None,
    ):
        self.err_code = error
        self.http_status = self._STATUS_MAP.get(error, 401)
        self.code = self.http_status
        super().__init__(msg=msg or error.msg, data=data)


class RequestError(BaseExceptionMixin):
    """请求异常"""

    def __init__(
        self,
        *,
        code: int = StandardResponseCode.HTTP_400,
        msg: str = "Bad Request",
        data: Any = None,
    ):
        self.code = code
        super().__init__(msg=msg, data=data)


class ForbiddenError(BaseExceptionMixin):
    """禁止访问异常"""

    code = StandardResponseCode.HTTP_403

    def __init__(self, *, msg: str = "Forbidden", data: Any = None):
        super().__init__(msg=msg, data=data)


class NotFoundError(BaseExceptionMixin):
    """资源不存在异常"""

    code = StandardResponseCode.HTTP_404

    def __init__(self, *, msg: str = "Not Found", data: Any = None):
        super().__init__(msg=msg, data=data)


class ServerError(BaseExceptionMixin):
    """服务器异常"""

    code = StandardResponseCode.HTTP_500

    def __init__(
        self,
        *,
        msg: str = "Internal Server Error",
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class GatewayError(BaseExceptionMixin):
    """网关异常"""

    code = StandardResponseCode.HTTP_502

    def __init__(
        self,
        *,
        msg: str = "Bad Gateway",
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class AuthorizationError(BaseExceptionMixin):
    """授权异常"""

    code = StandardResponseCode.HTTP_403

    def __init__(
        self,
        *,
        msg: str = "Permission Denied",
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class TokenError(HTTPError):
    """Token 异常"""

    code = StandardResponseCode.HTTP_401

    def __init__(
        self, *, msg: str = "Not Authenticated", headers: dict[str, Any] | None = None
    ):
        super().__init__(
            code=self.code, msg=msg, headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class ConflictError(BaseExceptionMixin):
    """资源冲突异常"""

    code = StandardResponseCode.HTTP_409

    def __init__(
        self,
        *,
        msg: str = "Conflict",
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class ValidationError(BaseExceptionMixin):
    """验证异常"""

    code = StandardResponseCode.HTTP_422

    def __init__(
        self,
        *,
        msg: str = "Validation Error",
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)
