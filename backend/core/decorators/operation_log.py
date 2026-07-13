#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
操作日志装饰器
用于标注端点的语义分类（模块/动作/描述），由操作日志中间件统一读取并写入。

本装饰器不再自行写库：它只把 module/action/description 标记到 request.state，
真正的日志写入由 OperationLogMiddleware 完成，避免同一请求被重复记录。
"""
from functools import wraps
from typing import Callable

from fastapi import Request


def log_operation(
    module: str,
    action: str,
    description: str | None = None,
):
    """
    操作日志装饰器（仅标记分类）

    用法:
        @log_operation(module="user", action="create", description="创建用户")
        async def create_user(request: Request, ...):
            ...

    要求被装饰的端点参数中包含 Request 对象（FastAPI 以 kwargs 注入）。
    标记发生在调用真实函数之前，因此即使端点抛异常，分类信息也已写入 request.state，
    中间件仍能正确分类。
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            if request is not None:
                request.state.oplog_module = module
                request.state.oplog_action = action
                request.state.oplog_description = description
            return await func(*args, **kwargs)

        return wrapper

    return decorator
