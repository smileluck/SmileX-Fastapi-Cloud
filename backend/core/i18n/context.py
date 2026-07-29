#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请求级语言上下文

镜像 plugins/multi_tenant/deps/tenant_context.py 的写法，
在纯 ASGI 中间件（RequestContextMiddleware）中按请求 set / reset，
使 endpoint / service / Pydantic 校验器都能通过 get_current_language() 拿到当前语言。
"""
import contextvars
from typing import Optional

from core.config import settings

# 默认值取配置中的默认语言；无请求上下文时（如 import 期）也能返回一个合法语言
language_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "language", default=settings.I18N.DEFAULT_LANGUAGE
)


def get_current_language() -> str:
    """获取当前请求的语言（无请求上下文时返回默认语言）"""
    return language_ctx.get()


def set_current_language(lang: str) -> contextvars.Token:
    """设置当前请求的语言，返回 token 用于重置"""
    return language_ctx.set(lang)


def reset_language(token: contextvars.Token) -> None:
    """重置语言上下文"""
    language_ctx.reset(token)
