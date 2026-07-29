#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any
from fastapi import HTTPException
from enum import Enum
from core.response import StandardResponseCode, CustomErrorCode
from core.i18n import t


class BaseExceptionMixin(Exception):
    """基础异常混入类

    每个异常子类通过 default_msg_key 声明默认文案的 i18n key。
    未显式传 msg 时在构造期按当前请求语言翻译（构造发生在请求任务内）。
    """

    code: int
    err_code: CustomErrorCode
    default_msg_key: str = "error.request_exception"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        self.msg = msg if msg is not None else t(self.default_msg_key)
        self.data = data


class HTTPError(HTTPException):
    """HTTP 异常"""

    default_msg_key: str = "error.http_exception"

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
        self.err_code = error
        self.default_msg_key = error.key
        super().__init__(msg=msg, data=data)


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
        self.default_msg_key = error.key
        super().__init__(msg=msg, data=data)


class RequestError(BaseExceptionMixin):
    """请求异常"""

    code = StandardResponseCode.HTTP_400
    default_msg_key = "error.bad_request"

    def __init__(
        self,
        *,
        code: int = StandardResponseCode.HTTP_400,
        msg: str = None,
        data: Any = None,
    ):
        self.code = code
        super().__init__(msg=msg, data=data)


class ForbiddenError(BaseExceptionMixin):
    """禁止访问异常"""

    code = StandardResponseCode.HTTP_403
    default_msg_key = "response.http_403"

    def __init__(self, *, msg: str = None, data: Any = None):
        super().__init__(msg=msg, data=data)


class NotFoundError(BaseExceptionMixin):
    """资源不存在异常"""

    code = StandardResponseCode.HTTP_404
    default_msg_key = "response.http_404"

    def __init__(self, *, msg: str = None, data: Any = None):
        super().__init__(msg=msg, data=data)


class ServerError(BaseExceptionMixin):
    """服务器异常"""

    code = StandardResponseCode.HTTP_500
    default_msg_key = "response.http_500"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class GatewayError(BaseExceptionMixin):
    """网关异常"""

    code = StandardResponseCode.HTTP_502
    default_msg_key = "error.bad_gateway"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class AuthorizationError(BaseExceptionMixin):
    """授权异常"""

    code = StandardResponseCode.HTTP_403
    default_msg_key = "error.permission_denied"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class TokenError(HTTPError):
    """Token 异常"""

    code = StandardResponseCode.HTTP_401
    default_msg_key = "error.unauthorized"

    def __init__(
        self, *, msg: str = None, headers: dict[str, Any] | None = None
    ):
        resolved = msg if msg is not None else t(self.default_msg_key)
        super().__init__(
            code=self.code, msg=resolved, headers=headers or {"WWW-Authenticate": "Bearer"}
        )


class ConflictError(BaseExceptionMixin):
    """资源冲突异常"""

    code = StandardResponseCode.HTTP_409
    default_msg_key = "error.conflict"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)


class ValidationError(BaseExceptionMixin):
    """验证异常"""

    code = StandardResponseCode.HTTP_422
    default_msg_key = "error.validation_failed"

    def __init__(
        self,
        *,
        msg: str = None,
        data: Any = None,
    ):
        super().__init__(msg=msg, data=data)
