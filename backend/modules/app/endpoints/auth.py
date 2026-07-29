#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Body, Depends, Request, Response, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from database.models.business.user import AppUser
from sqlalchemy.orm import Session
from modules.app.deps.auth.user_manager import (
    UserManager,
    get_user_manager,
    current_user,
    update_user_info,
)
from core.security.oauth.jwt import Token, JWTAuthManager, oauth2_scheme
from core.i18n import t
from core.response import (
    ResponseModel,
    response_base,
    CustomResponseCode,
    CustomErrorCode,
)
from logging import getLogger

logger = getLogger(__name__)
from modules.app.schemas.auth import (
    LoginModel,
    RefreshTokenModel,
    SmsCodeModel,
    UserInfoModel,
    UserLoginResponseModel,
    UserInfoUpdateModel,
    ClientIDModel,
    UserPushSettingModel,
)
from database import get_session
from core.security.rate_limit import limit_by_ip

# 创建认证路由
router = APIRouter(
    prefix="/auth",
    tags=["APP接口/认证管理"],
)


# 登录路由
@router.post(
    "/login",
    response_model=ResponseModel[UserLoginResponseModel],
    summary="用户登录接口",
    description="通过手机号和验证码登录系统，获取访问令牌和刷新令牌",
)
async def login(
    request: Request,
    login_model: LoginModel = Body(..., description="登录请求参数"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    用户登录接口
    接收手机号和验证码，返回JWT令牌
    Args:
        request: 请求对象
        response: 响应对象
        user_manager: 用户管理器
        jwt_manager: JWT认证管理器
    Returns:
        ResponseModel: 包含访问令牌和刷新令牌的响应
    Examples:
        {
            "phone": "13800000000",
            "code": "123456"
        }
    """
    phone = login_model.phone
    await limit_by_ip(
        request=request,
        action="app_login",
        limit=12,
        window_seconds=60,
        scope="app",
        extra_suffix=phone,
    )
    code = login_model.code
    tokens = await user_manager.login_by_phone(phone=phone, code=code)
    return response_base.success(
        data=tokens,
        msg=t("auth.login_success"),
    )


# 绑定客户端ID路由
@router.post(
    "/push",
    response_model=ResponseModel[dict],
    summary="用户推送接口",
    description="绑定客户端ID用于推送消息",
)
async def push(
    client_id_model: ClientIDModel = Body(..., description="客户端ID请求参数"),
    user: AppUser = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    用户推送接口
    绑定客户端ID到当前用户，用于后续消息推送
    Args:
        client_id_model: 包含客户端ID的请求模型
        user: 当前登录的用户
        user_manager: 用户管理器
    Returns:
        ResponseModel: 绑定结果
    Examples:
        {
            "client_id": "device-token-123456"
        }
    """
    client_id = client_id_model.client_id
    # 绑定客户端ID到用户
    await user_manager.bind_client_id(user.id, client_id)
    return response_base.success(msg=t("auth.client_id_bind_success"), data={"client_id": client_id})


# # 注册路由（可选，根据需求决定是否启用）
# @router.post(
#     "/register",
#     response_model=ResponseModel,
#     summary="用户注册接口",
#     description="通过手机号和验证码注册新用户",
# )
# async def register(
#     login_model: LoginModel = Body(..., description="注册请求参数"),
#     user_manager: UserManager = Depends(get_user_manager),
# ):
#     """
#     用户注册接口
#     接收用户名、密码等信息，创建新用户
#     Args:
#         request: 请求对象
#         user_manager: 用户管理器
#     Returns:
#         ResponseModel: 注册结果
#     example:
#         {
#             "code": "123456",
#             "phone": "13800000000"
#         }
#     """
#     phone = login_model.phone
#     code = login_model.code
#     if not phone or not code:
#         return response_base.fail(
#             res=CustomResponseCode.HTTP_400, msg="手机号和验证码不能为空"
#         )
#     # 注册用户
#     await user_manager.register_by_phone(phone=phone, code=code)
#     return response_base.success()
# 获取当前登录用户信息
@router.get(
    "/users/me",
    response_model=ResponseModel[UserInfoModel],
    summary="获取当前用户信息",
    description="获取当前登录用户的详细信息",
)
async def get_current_user_info(
    user: AppUser = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    获取当前登录用户信息
    需要有效的JWT令牌
    Args:
        user: 当前登录的用户对象
    Returns:
        ResponseModel: 用户信息
    """
    user_info = await user_manager.get_user_info(user.id)
    return response_base.success(
        data=user_info,
    )


@router.post(
    "/users/push-setting",
    response_model=ResponseModel[UserPushSettingModel],
    summary="更新当前用户推送设置",
    description="更新当前登录用户的推送设置",
)
async def update_push_setting(
    push_setting: UserPushSettingModel,
    user: AppUser = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    更新当前用户推送设置
    需要有效的JWT令牌
    Args:
        push_setting: 包含推送设置的请求模型
        user: 当前登录的用户对象
    """
    # 调用 user_manager 更新推送设置
    await user_manager.update_push_setting(user.id, push_setting)
    return response_base.success(msg=t("auth.push_setting_updated"), data=push_setting)


@router.put(
    "/users/me",
    response_model=ResponseModel[UserInfoUpdateModel],
    summary="更新当前用户信息",
    description="更新当前登录用户的信息",
)
async def update_current_user_info(
    user_update: UserInfoUpdateModel,
    db: Session = Depends(get_session),
):
    """更新当前登录用户信息"""
    try:
        user_id = user_update.id
        # 用 Pydantic v2 推荐的 model_dump
        update_data = user_update.model_dump(exclude_unset=True)
        # 调用你的 user_manager 更新逻辑
        update_info = await update_user_info(db, user_id, update_data)
        return response_base.success(msg=t("auth.user_info_update_success"), data=update_info)
    except Exception as e:
        return ResponseModel(code=500, msg=t("auth.user_info_update_failed", error=str(e)))


# 刷新令牌路由
@router.post(
    "/refresh",
    response_model=ResponseModel[Token],
    summary="刷新访问令牌",
    description="使用有效的刷新令牌获取新的访问令牌",
)
async def refresh_token(
    refresh_token_model: RefreshTokenModel = Body(..., description="刷新令牌请求参数"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    刷新访问令牌
    使用有效的刷新令牌获取新的访问令牌
    Args:
        request: 请求对象，包含刷新令牌
        jwt_manager: JWT认证管理器
    Returns:
        ResponseModel: 包含新访问令牌的响应
    """
    refresh_token = refresh_token_model.refresh_token
    # 解码刷新令牌获取用户信息
    tokens = await user_manager.refresh_token(refresh_token)
    return response_base.success(
        data=tokens,
        msg=t("auth.token_refresh_success"),
    )


# 获取短信验证码路由
@router.post(
    "/sms-code",
    response_model=ResponseModel,
    summary="获取短信验证码",
    description="向指定手机号发送短信验证码，用于登录或注册验证",
)
async def get_sms_code(
    request: Request,
    sms_code_model: SmsCodeModel = Body(..., description="获取短信验证码请求参数"),
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    获取短信验证码接口
    接收手机号，发送短信验证码
    Args:
        sms_code_model: 包含手机号的请求模型
        user_manager: 用户管理器
    Returns:
        ResponseModel: 获取验证码结果
    Examples:
        {
            "phone": "13800000000"
        }
    """
    await limit_by_ip(
        request=request,
        action="sms_code",
        limit=6,
        window_seconds=60,
        scope="app",
        extra_suffix=sms_code_model.phone,
    )
    await user_manager.get_verification_code(phone=sms_code_model.phone)
    return response_base.success(msg=t("auth.sms_sent_success"))


@router.post(
    "/logout",
    response_model=ResponseModel,
    summary="退出登录",
    description="登出当前会话，清除服务端 session，使当前 access token 立即失效",
)
async def logout(
    token: str = Depends(oauth2_scheme),
    user: AppUser = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    """退出登录

    current_user 依赖已完成验签，这里以 unverified 方式取 session_id，
    调 UserManager.logout 删除 Redis session 并清内存缓存。
    """
    payload = JWTAuthManager.decode_token_unverified(token)
    session_id = payload.get("session_id")
    if session_id:
        await user_manager.logout(user.id, session_id)
    return response_base.success(msg=t("auth.logout_success"))
