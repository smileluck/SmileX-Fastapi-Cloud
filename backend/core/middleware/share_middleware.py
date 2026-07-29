from fastapi import FastAPI, Request
import contextvars
import uvicorn

from core.config import settings
from core.i18n import resolve_language, set_current_language, reset_language

request_ctx = contextvars.ContextVar("request", default=None)


# 2. 定义自定义中间件类（适配add_middleware的写法）
class RequestContextMiddleware:
    """
    自定义请求上下文中间件：将request绑定到contextvars，实现全局共享

    同时按 Accept-Language 头解析当前请求语言并写入 language ContextVar，
    使 endpoint / service / Pydantic 校验器 / 异常处理器都能取到当前语言。
    该中间件在 setup_registry 中最后注册（最外层），请求进入时最先执行，
    因此外层中间件（限流、请求体限制等）产出的错误响应也能正确翻译。
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # 仅处理HTTP请求（排除WebSocket等）
        if scope["type"] == "http":
            # 构建Request对象（Starlette的Request初始化方式）
            request = Request(scope, receive)
            # 将request存入上下文变量，记录token用于后续清理
            request_token = request_ctx.set(request)
            # 解析并设置当前请求语言
            lang = resolve_language(
                request.headers.get("accept-language"),
                settings.I18N.SUPPORTED_LANGUAGES,
                settings.I18N.DEFAULT_LANGUAGE,
            )
            lang_token = set_current_language(lang)
            try:
                # 执行后续中间件/路由处理
                await self.app(scope, receive, send)
            finally:
                # 无论是否异常，都清理上下文（避免协程泄漏）
                reset_language(lang_token)
                request_ctx.reset(request_token)
        else:
            # 非HTTP请求直接放行
            await self.app(scope, receive, send)
