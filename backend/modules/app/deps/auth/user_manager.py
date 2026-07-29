#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Union, Dict, Any, Tuple
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, update, func
from sqlalchemy.sql.functions import cube
from core.config import settings
from database import get_session
from core.exception import CustomError, TokenError
from core.response import CustomErrorCode
from logging import getLogger
from core.security.oauth.jwt import JWTAuthManager, Token, oauth2_scheme
from core.redis import get_redis_util
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from fastapi.concurrency import run_in_threadpool
from core.utils.session_utils import generate_session_id
from core.security.oauth.user_manager import base_user_manager, build_session_key
import random
from database.models.business.user import AppUser  # 导入 AppUser 类
from modules.app.schemas.auth import (
    UserInfoModel,
    UserLoginResponseModel,
    CurrentRobotModel,
    UserInfoUpdateModel,
    UserPushSettingModel,
)
from datetime import datetime, timezone
from core.response import (
    response_base,
)

import aiohttp
import uuid

logger = getLogger(__name__)

# 定义缺失的变量
CLOUD_FUNC_URL = "https://example.com/api/push"  # 占位符 URL


# 创建占位符 AliyunSMS 类
class AliyunSMS:
    """阿里云短信服务占位符类"""

    def send_login_code(self, phone: str, code: str):
        """发送登录验证码"""
        logger.info(f"模拟发送登录验证码: {code} 到 {phone}")

    def send_alarm_notification(self, phone: str, name: str, address: str, device: str):
        """发送报警通知"""
        logger.info(f"模拟发送报警通知到 {phone}: {name}, {address}, {device}")


class UserManager:
    """
    用户管理器类
    负责用户的创建、认证、密码重置等操作
    """

    jwt_manager: JWTAuthManager

    def __init__(self, session: AsyncSession):
        self.jwt_manager = JWTAuthManager()
        self.session = session

    async def check_code(self, phone: str, code: str) -> None:
        """
        TODO 需要从redis等获取验证码
        检查验证码是否正确，不正确则抛出异常
        """
        if code != "123456":
            raise CustomError(
                error=CustomErrorCode.USER_CAPTCHA_ERROR,
            )

    async def register_by_phone(self, phone: str, code: str) -> AppUser:
        """
        手机号注册
        """
        # 验证手机号格式
        if not phone.isdigit() or len(phone) != 11:
            raise CustomError(
                error=CustomErrorCode.USER_PHONE_FORMAT_ERROR,
            )
        # 检查手机号是否已存在
        existing_user = await self.get_by_phone(phone)
        if existing_user:
            raise CustomError(
                error=CustomErrorCode.USER_EXIST,
            )
        # 检查验证码
        await self.check_code(phone, code)
        # 创建用户,通过sqlalchemy
        user = AppUser(
            phone_area_code="86",
            name=phone,
            phone=phone,
            client_ids=[],
        )
        self.session.add(user)
        await self.session.commit()
        await self.on_after_register(user)
        return user

    async def get_by_phone(self, phone: str) -> Optional[AppUser]:
        """
        根据手机号获取用户
        """
        stmt = select(AppUser).where(AppUser.phone == phone)
        result = await self.session.scalars(stmt)
        user = result.one_or_none()
        return user

    async def update_push_setting(
        self, user_id: int, push_setting: UserPushSettingModel
    ) -> UserPushSettingModel:
        """更新用户推送设置"""
        stmt = (
            update(AppUser)
            .where(AppUser.id == user_id)
            .values(
                app_alarm=push_setting.app_alarm,
                sms_alarm=push_setting.sms_alarm,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def bind_client_id(self, user_id: str, client_id: str) -> None:
        """
        绑定推送ID到用户
        """
        await self.session.execute(
            update(AppUser).values(
                client_ids=func.array_remove(AppUser.client_ids, client_id)
            )
        )
        # 绑定客户端ID到用户
        stmt = (
            update(AppUser)
            .where(AppUser.id == user_id)
            .values(
                client_ids=[client_id],
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def send_app_notification(self, alert_data) -> None:
        """
        发送app通知
        Args:
            alert_data: 报警数据
        """
        try:
            async for db in get_conn():
                stmt = select(AppUser.client_ids).where(
                    AppUser.id == alert_data["user_id"]
                )
                result = await db.execute(stmt)
                client_ids = result.scalar_one_or_none()
            if not client_ids or len(client_ids) == 0:
                logger.warning(
                    f"用户 {alert_data['user_id']} 无 client_ids，不发送推送"
                )
                return
            for cid in client_ids:
                unique_id = str(uuid.uuid4())[:8]  # 取UUID前8位
                data = {
                    "clientId": cid,
                    "title": alert_data["device_name"] + "告警" + unique_id,
                    "content": "尊敬的用户, 您在<"
                    + alert_data["location"]
                    + ">区域的<"
                    + alert_data["device_name"]
                    + ">已触发告警，请立即核实情况，确保安全！"
                    + unique_id,
                    "payload": {
                        "robot_id": alert_data["robot_id"],
                        "user_scope": alert_data["user_scope"],
                    },
                }
                logger.info(f"发送 uniPush2.0 推送: {data}")
                async with aiohttp.ClientSession() as http:
                    async with http.post(CLOUD_FUNC_URL, json=data, timeout=5) as resp:
                        if resp.status != 200:
                            logger.error(
                                f"uniPush2.0 推送失败: {resp.status} {await resp.text()}"
                            )
                        result = await resp.json()
                        logger.info(f"uniPush2.0 推送成功: {result}")
            return True
        except Exception as e:
            logger.error(f"发送app通知异常: {e}")

    async def login_by_phone(self, phone: str, code: str) -> UserLoginResponseModel:
        """
        验证用户凭据
        通过手机号查找用户并验证验证码
        Args:
            phone: 手机号
            code: 验证码
        Returns:
            Token: 访问令牌
        """
        if not phone or not code:
            raise CustomError(
                msg="手机号和验证码不能为空",
                error=CustomErrorCode.USER_LOGIN_FAILED,
            )
        # 验证密码
        await self.check_code(phone, code)
        # 按手机号查询用户
        stmt = select(AppUser).where(AppUser.phone == phone)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        # 首次登录
        is_first_login = user is None
        if is_first_login:
            user = await self.register_by_phone(phone=phone, code=code)
        # 禁用账号拦截：后台禁用后不允许登录
        if not user.status:
            raise CustomError(
                msg="账号已被禁用，请联系管理员",
                error=CustomErrorCode.USER_LOGIN_FAILED,
            )
        tokens = await base_user_manager.create_token(user_id=user.id, user_role="app", username=user.username)
        await base_user_manager.on_after_login(user=user)
        # 如果不是首次登录，则获取机器人id

        response_model = UserLoginResponseModel(
            robot=CurrentRobotModel(),
            **tokens.model_dump(),
        )
        return response_model

    async def refresh_token(self, refresh_token: str) -> Token:
        """
        刷新access token
        Args:
            refresh_token: 刷新令牌
        Returns:
            Token: 新的访问令牌和刷新令牌
        """
        try:
            user_id, session_id = await self.verify_token_session(
                refresh_token, _type="refresh"
            )
            payload = self.jwt_manager.decode_token(refresh_token)
            username = payload.get("username")
            # 创建新的token
            return await base_user_manager.create_token(
                user_id=user_id, user_role="app", session_id=session_id, username=username
            )
        except Exception as e:
            logger.error(f"刷新token失败: {str(e)}")
            raise TokenError()

    async def verify_token_session(
        self, token: str, _type: str = "access"
    ) -> Tuple[int, str]:
        """
        验证token中的session_id是否有效
        Args:
            token: JWT令牌
        Returns:
            user_id: 用户id
            session_id: 会话id
        """
        payload = self.jwt_manager.decode_token(token)
        session_id = payload.get("session_id")
        user_id = payload.get("user_id")
        user_role = payload.get("role")
        if payload.get("scope") != _type:
            raise TokenError()
        if not user_id:
            raise TokenError()
        if not session_id:
            raise TokenError()
        if not user_role:
            raise TokenError()
        # jti 黑名单校验：每次直查 Redis，不进内存缓存，保证吊销即时生效
        jti = payload.get("jti")
        if jti and await base_user_manager.is_token_revoked(jti):
            raise TokenError(msg="令牌已被吊销")
        cache_key = build_session_key(user_role, int(user_id))
        # 检查内存缓存
        _cache = get_memory_cache()
        session_ck = f"{cache_key}:{session_id}"
        cached_valid = _cache.get(CacheNamespace.SESSION, session_ck)
        if cached_valid is not None:
            return int(user_id), session_id
        # 从 Redis 验证（Hash 结构）
        local_session_meta = await get_redis_util().hget(cache_key, session_id)
        if local_session_meta is not None:
            _cache.set(CacheNamespace.SESSION, session_ck, True, ttl=5)
            return int(user_id), session_id
        # Fallback: 兼容旧格式（纯字符串存储），过渡期使用
        try:
            local_session_id = await get_redis_util().get(cache_key)
        except Exception:
            local_session_id = None
        if local_session_id is not None and local_session_id == session_id:
            _cache.set(CacheNamespace.SESSION, session_ck, True, ttl=5)
            return int(user_id), session_id
        raise TokenError()

    async def on_after_register(self, user: AppUser, request: Optional[Request] = None):
        """
        用户注册后的回调
        可以在这里实现用户注册后的额外逻辑，如发送欢迎邮件等
        Args:
            user: 注册的用户对象
            request: 请求对象（可选）
        """
        logger.info(f"用户 {user.id} 注册成功")
        # 这里可以添加注册成功后的逻辑，如发送邮件通知等

    async def logout(self, user_id: int, session_id: str):
        """
        退出登录，删除指定会话
        """
        cache_key = build_session_key("app", user_id)
        get_memory_cache().delete(CacheNamespace.SESSION, f"{cache_key}:{session_id}")
        await get_redis_util().hdel(cache_key, session_id)

    async def current_user(self, token: str) -> AppUser:
        """
        获取当前认证的用户
        这是一个直接可用的FastAPI依赖项，封装了JWTAuthManager.current_user方法，
        用于在路由处理函数中验证并获取当前已认证的用户信息。
        Args:
            token: 通过OAuth2密码流程获取的JWT令牌
            db: 数据库会话依赖
        Returns:
            AppUser: 当前认证用户的数据库模型实例
        """
        user_id, _ = await self.verify_token_session(token)
        user = await self.session.execute(select(AppUser).where(AppUser.id == user_id))
        user = user.scalars().first()
        if user is None:
            raise TokenError()
        # 账号已被后台禁用：即便 session 仍在，也拒绝鉴权
        if not user.status:
            raise TokenError(msg="账号已被禁用")
        return user

    async def get_verification_code(self, phone: str) -> None:
        """
        获取手机验证码
        生成验证码并通过短信发送给用户，同时将验证码存入redis
        Args:
            phone: 接收验证码的手机号
        """
        # 验证手机号格式
        if not phone.isdigit() or len(phone) != 11:
            raise CustomError(
                error=CustomErrorCode.USER_PHONE_FORMAT_ERROR,
            )
        # 检查60秒内是否已发送过验证码
        redis_key_check = f"app:user_code_send_check:{phone}"
        if await get_redis_util().get(redis_key_check):
            raise CustomError(
                error=CustomErrorCode.USER_SMS_SEND_TOO_FAST,
            )
        # 生成6位验证码
        code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        # 调用阿里云短信服务发送验证码
        try:
            aliyun_sms = AliyunSMS()
            aliyun_sms.send_login_code(phone, code)
        except Exception as e:
            logger.error(f"发送短信验证码失败，手机号: {phone}, 错误: {str(e)}")
            raise CustomError(
                error=CustomErrorCode.USER_SMS_SEND_ERROR,
            )
        # 设置60秒的发送限制标记
        await get_redis_util().set(redis_key_check, "1", 60)
        # 将验证码存入redis，设置有效期为5分钟
        redis_key = f"app:user_code:{phone}"
        await get_redis_util().set(redis_key, code, 300)

    async def send_alarm_notification(
        self, phone: str, name: str, address: str, device: str
    ) -> None:
        """
        发送报警通知短信
        模仿验证码逻辑，并加入redis限流和手机号校验
        Args:
            phone: 接收报警短信的手机号
            name: 用户名
            address: 报警地址，如 “样板间”
            device: 报警设备，如 “门窗传感器”
        """
        # phone = str(13025410881)
        # 限流，60秒内不能重复发报警短信
        redis = get_redis_util()
        redis_key_check = f"app:alarm_send_check:{phone}"
        # 原子操作：只允许一个请求成功
        locked = await redis.set_nx_ex(redis_key_check, "1", 60)
        if not locked:
            raise CustomError(CustomErrorCode.USER_SMS_SEND_TOO_FAST)
        # 3. 发送阿里云短信
        try:
            aliyun_sms = AliyunSMS()
            await run_in_threadpool(
                aliyun_sms.send_alarm_notification, phone, name, address, device
            )
        except Exception as e:
            logger.error(f"发送报警短信失败，手机号: {phone}, 错误: {str(e)}")
            await redis.delete(redis_key_check)
            raise CustomError(
                error=CustomErrorCode.USER_SMS_SEND_ERROR,
            )
        # 4. 设置60秒发送限制
        redis_alarm_log = f"app:alarm_history:{phone}"
        alarm_msg = f"{address}:{device}"
        await redis.lpush(redis_alarm_log, alarm_msg)
        await redis.expire(redis_alarm_log, 60)  # 保存 60 秒
        logger.info(f"报警短信已发送 | 手机: {phone} | 信息: {alarm_msg}")

    async def get_user_info(self, user_id: int) -> UserInfoModel:
        """
        获取用户信息
        Args:
            user_id: 用户ID
        Returns:
            Optional[AppUser]: 用户对象，如果未找到则返回None
        """
        stmt = select(AppUser).where(AppUser.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalars().first()
        if not user:
            raise CustomError(
                error=CustomErrorCode.USER_NOT_FOUND,
            )

        user_info = UserInfoModel(
            id=user.id,
            phone=user.phone,
            bind_wechat=user.wx_openid is not None,
        )
        return user_info


async def update_user_info(
    db: AsyncSession, user_id: int, update_data: dict
) -> UserInfoUpdateModel | None:
    """更新用户信息（PostgreSQL + SQLAlchemy异步版）"""
    try:
        # 过滤掉值为 None 的字段
        update_fields = {k: v for k, v in update_data.items() if v is not None}
        if not update_fields:
            return None
        update_fields["updated_at"] = datetime.now(timezone.utc)
        stmt = (
            update(AppUser)
            .where(AppUser.id == user_id)
            .values(**update_fields)
            .returning(AppUser.id, AppUser.name, AppUser.phone)
        )
        row = (await db.execute(stmt)).fetchone()
        await db.commit()
        if not row:
            return None
        return UserInfoUpdateModel(**row._mapping)
    except Exception as e:
        await db.rollback()
        logger.error(f"更新用户信息失败: {e}")
        return None


async def get_user_manager(user_db: AsyncSession = Depends(get_session)):
    """
    获取用户管理器实例
    Args:
        user_db: 用户数据库实例
    Yields:
        UserManager: 用户管理器实例
    """
    yield UserManager(user_db)


async def current_user(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> AppUser:
    """
    获取当前认证用户的数据库模型实例
    Args:
        user_manager: 用户管理器实例
        token: 通过OAuth2密码流程获取的JWT令牌
    Returns:
        AppUser: 当前认证用户的数据库模型实例
    """
    return await user_manager.current_user(token)
