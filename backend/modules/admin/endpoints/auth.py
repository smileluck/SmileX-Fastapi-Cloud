#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging

from fastapi import APIRouter, Depends, Request, Body
from pydantic import BaseModel, Field
from redis import Redis
from database.models.sys.user import SysUser
from core.config import settings
from core.i18n import t
from core.response import (
    ResponseModel,
    response_base,
)
from core.exception.errors import CustomError
from core.utils.ip_utils import get_real_client_ip
from modules.admin.deps.auth.user_manager import (
    UserManager,
    get_user_manager,
    current_user,
)
from core.security.oauth.jwt import JWTAuthManager, oauth2_scheme
from modules.admin.services.sys.online_user_service import OnlineUserService
from modules.admin.schemas.auth import (
    LoginPwdModel,
    LoginResponseData,
    UserInfoResponseData,
)
from core.security.rate_limit import limit_by_ip
from modules.admin.services.sys.rate_limit_service import RateLimitService
from modules.admin.services.captcha_service import CaptchaService
from modules.admin.schemas.captcha import (
    CaptchaVerifyRequest,
    CaptchaImageData,
    CaptchaVerifyResponse,
    CaptchaCheckResponse,
)
from core.security.rate_limit_config import RateLimitConfigProvider

logger = logging.getLogger(__name__)

# 创建认证路由
router = APIRouter(prefix="/auth", tags=["admin接口/认证"])


async def _write_login_log(username: str, ip: str | None, status: bool, detail: str, user_agent: str | None):
    """异步写入登录日志"""
    try:
        from database import get_session
        from modules.admin.services.sys.login_log_service import LoginLogService

        async for db in get_session():
            await LoginLogService.create_log(
                db=db,
                username=username,
                ip=ip,
                status=status,
                detail=detail,
                user_agent=user_agent,
            )
    except Exception as e:
        logger.error(f"写入登录日志失败: {e}")


# ---------------------------------------------------------------------------
# 滑块验证码端点
# ---------------------------------------------------------------------------


@router.get(
    "/captcha",
    response_model=ResponseModel[CaptchaImageData],
    summary="获取滑块验证码",
    description="生成滑块拼图验证码图片，返回背景图、拼图块及位置信息",
)
async def get_captcha(request: Request):
    await limit_by_ip(request=request, action="captcha", limit=10, window_seconds=60, scope="admin")
    data = await CaptchaService.generate_captcha()
    return response_base.success(data=data, msg=t("auth.captcha_success"))


@router.post(
    "/captcha/verify",
    response_model=ResponseModel[CaptchaVerifyResponse],
    summary="验证滑块位置",
    description="验证用户拖动滑块的位置是否正确，正确则返回验证码令牌",
)
async def verify_captcha(request: Request, req: CaptchaVerifyRequest = Body(...)):
    await limit_by_ip(request=request, action="captcha_verify", limit=20, window_seconds=60, scope="admin")
    token = await CaptchaService.verify_captcha(req.captcha_id, req.slide_x)
    return response_base.success(
        data=CaptchaVerifyResponse(captcha_token=token),
        msg=t("auth.verify_success"),
    )


@router.get(
    "/captcha/check",
    response_model=ResponseModel[CaptchaCheckResponse],
    summary="检查是否需要验证码",
    description="根据当前IP的登录失败次数判断是否需要滑块验证",
)
async def check_captcha(request: Request):
    ip = get_real_client_ip(request)
    fail_count = await CaptchaService.get_failure_count(ip)
    threshold = await RateLimitConfigProvider.get(
        "rate_limit.captcha_trigger_threshold", settings.RATE_LIMIT.CAPTCHA_TRIGGER_THRESHOLD
    )
    return response_base.success(
        data=CaptchaCheckResponse(required=fail_count >= threshold, fail_count=fail_count),
    )


# ---------------------------------------------------------------------------
# 登录端点
# ---------------------------------------------------------------------------


@router.post(
    "/login",
    response_model=ResponseModel[LoginResponseData],
    summary="后台用户登录接口",
    description="通过用户名和密码登录系统，获取访问令牌和刷新令牌",
)
async def login(
    request: Request,
    login_pwd: LoginPwdModel = Body(..., description="登录请求参数"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    用户登录接口
    接收用户名和密码，返回JWT令牌
    """
    username = login_pwd.username
    ip = get_real_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    await limit_by_ip(
        request=request,
        action="admin_login",
        limit=10,
        window_seconds=60,
        scope="admin",
        extra_suffix=username.lower(),
    )

    # 滑块验证码检查
    fail_count = await CaptchaService.get_failure_count(ip)
    threshold = await RateLimitConfigProvider.get(
        "rate_limit.captcha_trigger_threshold", settings.RATE_LIMIT.CAPTCHA_TRIGGER_THRESHOLD
    )
    if fail_count >= threshold:
        from core.exception.errors import CustomErrorCode

        if not login_pwd.captcha_token:
            raise CustomError(error=CustomErrorCode.CAPTCHA_REQUIRED)
        if not await CaptchaService.validate_captcha_token(login_pwd.captcha_token):
            raise CustomError(error=CustomErrorCode.CAPTCHA_INVALID)

    try:
        password = login_pwd.password
        tokens = await user_manager.login_by_password(
            username=username,
            password=password,
            ip=ip,
            user_agent=user_agent,
        )
        asyncio.create_task(
            _write_login_log(username, ip, True, "登录成功", user_agent)
        )
        asyncio.create_task(RateLimitService.clear_login_failure(ip))
        return response_base.success(
            data=tokens,
            msg=t("auth.login_success"),
        )
    except CustomError as e:
        asyncio.create_task(
            _write_login_log(username, ip, False, e.msg, user_agent)
        )
        asyncio.create_task(RateLimitService.record_login_failure(ip, username))
        raise


@router.get(
    "/users/me",
    response_model=ResponseModel[UserInfoResponseData],
    summary="获取当前后台用户信息",
    description="获取当前登录后台用户的详细信息",
)
async def get_current_info(
    user: SysUser = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    user_info = await user_manager.get_user_info(user.id)
    return response_base.success(
        data=user_info,
        msg=t("auth.user_info_success"),
    )


@router.post(
    "/logout",
    response_model=ResponseModel,
    summary="退出登录",
    description="登出当前会话，清除服务端 session，使当前 access token 立即失效",
)
async def logout(
    token: str = Depends(oauth2_scheme),
    user: SysUser = Depends(current_user),
):
    """退出登录

    current_user 依赖已完成验签，这里以 unverified 方式取 session_id/tenant_id，
    调 OnlineUserService.kick_user 删除 Redis session 并清内存缓存。
    """
    payload = JWTAuthManager.decode_token_unverified(token)
    session_id = payload.get("session_id")
    tenant_id = int(payload.get("tenant_id", 0)) if payload.get("tenant_id") else 0
    if session_id:
        await OnlineUserService.kick_user(
            user_id=user.id, session_id=session_id, role="admin", tenant_id=tenant_id
        )
    return response_base.success(msg=t("auth.logout_success"))
