#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback
from typing import Any, Callable, Dict, Optional, Type, Union
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi.exceptions import RequestValidationError, ValidationException
from pydantic import ValidationError
from core.exception.errors import (
    BaseExceptionMixin,
    CustomError,
    OpenApiError,
    ForbiddenError,
    GatewayError,
    NotFoundError,
    RequestError,
    ServerError,
    TokenError,
    AuthorizationError,
    ConflictError,
    HTTPError,
)
from core.response.response_schema import response_base, ResponseModel
from core.response.response_code import (
    CustomErrorCode,
    CustomResponseCode,
    StandardResponseCode,
)
from core.i18n import t
from logging import getLogger
from core.utils.track_id import get_request_trace_id

logger = getLogger(__name__)

# Pydantic V2 常见错误类型到 i18n key 的映射
PYDANTIC_ERROR_MSG_MAP = {
    "int_parsing": "pydantic.int_parsing",
    "int_type": "pydantic.int_parsing",
    "missing": "pydantic.missing",
    "string_too_long": "pydantic.string_too_long",
    "string_too_short": "pydantic.string_too_short",
    "value_error": None,  # 使用原始 msg（校验器已自行翻译）
}


def _translate_pydantic_msg(error: dict) -> str:
    """把 Pydantic 默认英文错误翻译为当前请求语言；无法识别时返回原始 msg"""
    error_type = error.get("type")
    mapped = PYDANTIC_ERROR_MSG_MAP.get(error_type)
    if mapped is not None:
        return t(mapped)
    # 兜底：优先使用 ctx.error 里的自定义错误（校验器已自行翻译）
    if "ctx" in error and "error" in error["ctx"]:
        return str(error["ctx"]["error"])
    return error.get("msg") or t("pydantic.validation_failed")


def setup_exception_global_handlers(app: FastAPI) -> None:
    # 注册404路由未找到处理器
    @app.exception_handler(404)
    async def not_found_route_handler(
        request: Request, exc: Exception
    ) -> ORJSONResponse:
        """\处理路由未找到的情况"""
        return await not_found_error_handler(
            request, NotFoundError(msg=t("error.route_not_found"))
        )

    # 自定义Pydantic验证异常处理器
    @app.exception_handler(RequestValidationError)
    async def global_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> ORJSONResponse:
        return await validation_exception_handler(request, exc)

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """
        全局捕获ValueError异常，并返回标准化的JSON响应
        """
        request_id = get_request_trace_id(request)
        # 构建响应
        response = ResponseModel(
            code=StandardResponseCode.HTTP_400,
            msg=str(exc),
            request_id=request_id,
        )
        # 记录日志
        logger.error(
            f"请求异常: path={request.url.path}, method={request.method}, "
            f"msg={response.msg}"
        )
        return ORJSONResponse(
            status_code=StandardResponseCode.HTTP_400, content=response.model_dump()
        )


def setup_exception_handlers(app: FastAPI) -> None:
    """
    设置全局异常处理器
    Args:
        app: FastAPI 应用实例
    """
    # 注册自定义异常处理器
    app.exception_handler(BaseExceptionMixin)(base_exception_handler)
    app.exception_handler(RequestError)(request_error_handler)
    app.exception_handler(ForbiddenError)(forbidden_error_handler)
    app.exception_handler(NotFoundError)(not_found_error_handler)
    app.exception_handler(ServerError)(server_error_handler)
    app.exception_handler(GatewayError)(gateway_error_handler)
    app.exception_handler(TokenError)(token_error_handler)
    app.exception_handler(AuthorizationError)(authorization_error_handler)
    app.exception_handler(ConflictError)(conflict_error_handler)
    app.exception_handler(CustomError)(custom_error_handler)
    app.exception_handler(OpenApiError)(openapi_error_handler)
    # 注册FastAPI内置异常处理器
    app.exception_handler(HTTPException)(http_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(ValidationError)(pydantic_validation_error_handler)
    # 注册通用异常处理器（捕获所有未处理的异常）
    app.exception_handler(Exception)(generic_exception_handler)


async def base_exception_handler(
    request: Request, exc: BaseExceptionMixin
) -> ORJSONResponse:
    """
    基础异常处理器
    Args:
        request: FastAPI 请求对象
        exc: 基础异常实例
    Returns:
        统一格式的JSON响应
    """
    request_id = get_request_trace_id(request)
    # 记录日志
    logger.error(
        f"请求异常: path={request.url.path}, method={request.method}, "
        f"code={exc.code}, msg={exc.msg}, request_id={request_id}"
    )
    # 构建响应
    response = ResponseModel(
        code=exc.code,
        err_code=exc.err_code.code if hasattr(exc, "err_code") else None,
        msg=exc.msg or t(getattr(exc, "default_msg_key", "error.request_exception")),
        data=exc.data,
        request_id=request_id,
    )
    return ORJSONResponse(status_code=exc.code, content=response.model_dump())


async def request_error_handler(request: Request, exc: RequestError) -> ORJSONResponse:
    """
    请求异常处理器
    """
    return await base_exception_handler(request, exc)


async def forbidden_error_handler(
    request: Request, exc: ForbiddenError
) -> ORJSONResponse:
    """
    禁止访问异常处理器
    """
    return await base_exception_handler(request, exc)


async def not_found_error_handler(
    request: Request, exc: NotFoundError
) -> ORJSONResponse:
    """
    资源不存在异常处理器
    """
    return await base_exception_handler(request, exc)


async def server_error_handler(request: Request, exc: ServerError) -> ORJSONResponse:
    """
    服务器异常处理器
    """
    request_id = get_request_trace_id(request)
    # 记录详细错误日志（包括堆栈信息）
    logger.error(
        f"服务器内部错误: path={request.url.path}, method={request.method}, "
        f"msg={exc.msg}, request_id={request_id}\n{traceback.format_exc()}"
    )
    err_code = None
    msg = exc.msg or t("response.http_500")
    if hasattr(exc, "err_code"):
        err_code = exc.err_code.code
        msg = exc.err_code.msg or msg
    # 构建响应
    response = ResponseModel(
        code=StandardResponseCode.HTTP_500,
        err_code=exc.err_code.code if hasattr(exc, "err_code") else None,
        msg=msg,
        data=exc.data,
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=StandardResponseCode.HTTP_500, content=response.model_dump()
    )


async def gateway_error_handler(request: Request, exc: GatewayError) -> ORJSONResponse:
    """
    网关异常处理器
    """
    return await base_exception_handler(request, exc)


async def token_error_handler(request: Request, exc: TokenError) -> ORJSONResponse:
    """
    Token异常处理器
    """
    request_id = get_request_trace_id(request)
    # 记录日志
    logger.warning(
        f"Token验证失败: path={request.url.path}, method={request.method}, "
        f"msg={exc.detail}, request_id={request_id}"
    )
    # 构建响应
    response = ResponseModel(
        code=StandardResponseCode.HTTP_401,
        msg=exc.detail or t("error.unauthorized"),
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=StandardResponseCode.HTTP_401,
        content=response.model_dump(),
        headers=exc.headers,
    )


async def authorization_error_handler(
    request: Request, exc: AuthorizationError
) -> ORJSONResponse:
    """
    授权异常处理器
    """
    return await base_exception_handler(request, exc)


async def conflict_error_handler(
    request: Request, exc: ConflictError
) -> ORJSONResponse:
    """
    资源冲突异常处理器
    """
    return await base_exception_handler(request, exc)


async def custom_error_handler(request: Request, exc: CustomError) -> ORJSONResponse:
    """
    自定义异常处理器
    """
    request_id = get_request_trace_id(request)
    # 记录日志
    logger.error(
        f"自定义异常: path={request.url.path}, method={request.method}, "
        f"code={exc.code}, msg={exc.msg}, request_id={request_id}"
    )
    # 确保data不为None，以避免响应验证错误
    data = exc.data if exc.data is not None else {}
    # 构建响应
    response = ResponseModel(
        code=CustomResponseCode.HTTP_500.code,
        err_code=exc.code,
        msg=exc.msg or t("error.server_error"),
        data=data,
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=CustomResponseCode.HTTP_500.code, content=response.model_dump()
    )


async def openapi_error_handler(request: Request, exc: OpenApiError) -> ORJSONResponse:
    """
    开放API 鉴权异常处理器

    把 err_code 映射到语义正确的 4xx HTTP 状态（鉴权失败默认 401，
    nonce 非法 400，商户禁用 403），响应结构保持统一。
    用 warning 级日志（预期的客户端错误），避免污染 5xx 错误率统计。
    """
    request_id = get_request_trace_id(request)
    logger.warning(
        f"开放API鉴权失败: path={request.url.path}, method={request.method}, "
        f"http_status={exc.http_status}, err_code={exc.err_code.code}, "
        f"msg={exc.msg}, request_id={request_id}"
    )
    data = exc.data if exc.data is not None else {}
    response = ResponseModel(
        code=exc.http_status,
        err_code=exc.err_code.code,
        msg=exc.msg or exc.err_code.msg,
        data=data,
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=exc.http_status, content=response.model_dump()
    )


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> ORJSONResponse:
    """
    FastAPI HTTP异常处理器
    """
    request_id = get_request_trace_id(request)
    # 记录日志
    logger.error(
        f"HTTP异常: path={request.url.path}, method={request.method}, "
        f"status_code={exc.status_code}, detail={exc.detail}, request_id={request_id}"
    )
    # 构建响应
    response = ResponseModel(
        code=exc.status_code,
        err_code=exc.status_code,
        msg=str(exc.detail) if exc.detail else t("error.http_exception"),
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
        headers=exc.headers if exc.headers else {},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> ORJSONResponse:
    """
    请求参数验证异常处理器
    """
    request_id = get_request_trace_id(request)
    # 格式化验证错误信息
    errors = []
    for error in exc.errors():
        errors.append(_translate_pydantic_msg(error))
        break
    # 记录日志
    logger.warning(
        f"请求参数验证失败: path={request.url.path}, method={request.method}, "
        f"errors={errors}, request_id={request_id}"
    )
    # 构建响应
    response = ResponseModel(
        code=StandardResponseCode.HTTP_422,
        msg=errors[0] or t("pydantic.validation_failed"),
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=StandardResponseCode.HTTP_422, content=response.model_dump()
    )


async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> ORJSONResponse:
    """
    Pydantic模型验证异常处理器
    """
    request_id = get_request_trace_id(request)
    # 格式化验证错误信息
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error.get("loc", []))
        message = error.get("msg") or t("error.validation_error")
        errors.append(f"{field}: {message}")
    # 记录日志
    logger.warning(
        f"模型验证失败: path={request.url.path}, method={request.method}, "
        f"errors={errors}, request_id={request_id}"
    )
    # 构建响应
    response = ResponseModel(
        code=StandardResponseCode.HTTP_422,
        msg=t("error.validation_failed"),
        data={"errors": errors},
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=StandardResponseCode.HTTP_422, content=response.model_dump()
    )


async def generic_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    """
    通用异常处理器（捕获所有未处理的异常）
    """
    request_id = get_request_trace_id(request)
    # 记录详细错误日志（包括堆栈信息）
    logger.error(
        f"未捕获的异常: path={request.url.path}, method={request.method}, "
        f"exception_type={type(exc).__name__}, message={str(exc)}, "
        f"request_id={request_id}\n{traceback.format_exc()}"
    )
    # 构建响应
    response = ResponseModel(
        code=StandardResponseCode.HTTP_500,
        msg=t("response.http_500"),
        request_id=request_id,
    )
    return ORJSONResponse(
        status_code=StandardResponseCode.HTTP_500, content=response.model_dump()
    )
