#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Union, Dict, Any, Tuple, List
from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from core.config import settings
from database.models.sys.user import SysUser
from database import get_session
from core.exception import CustomError, TokenError
from core.response import CustomErrorCode
from core.security.oauth.user_manager import base_user_manager, BaseUserManager, build_session_key, build_session_key_legacy
from core.security.oauth.jwt import JWTAuthManager, Token, oauth2_scheme
from core.security.password import PasswordHasher
from core.redis import get_redis_util
from core.middleware.share_middleware import request_ctx
from core.utils.ip_utils import get_real_client_ip
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from datetime import datetime, timedelta, timezone


import logging

logger = logging.getLogger(__name__)


def _is_multi_tenant_enabled() -> bool:
    """Check if multi_tenant plugin is enabled."""
    return "multi_tenant" in settings.PLUGINS.ENABLED


class UserManager(BaseUserManager):
    """
    用户管理器类
    负责用户的创建、认证、密码重置等操作
    """

    jwt_manager: JWTAuthManager

    def __init__(self, session: AsyncSession):
        self.session = session
        self.jwt_manager = JWTAuthManager()

    async def login_by_password(
        self, username: str, password: str, ip: str = "", user_agent: str = ""
    ) -> Optional[Dict[str, str]]:
        """
        密码登录
        """
        if not username or not password:
            raise CustomError(
                msg="用户名和密码不能为空",
                error=CustomErrorCode.USER_LOGIN_FAILED,
            )
        stmt = select(SysUser).where(SysUser.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise CustomError(
                msg="用户名不存在",
                error=CustomErrorCode.USER_LOGIN_FAILED,
            )

        pwd_match = PasswordHasher.verify(
            password=password,
            hashed_password=user.password,
        )

        if not pwd_match:
            raise CustomError(
                msg="密码错误",
                error=CustomErrorCode.USER_LOGIN_FAILED,
            )

        # 校验用户是否被禁用
        if not user.status:
            raise CustomError(
                msg="用户已被禁用",
                error=CustomErrorCode.USER_DISABLED,
            )

        # 自动选择租户
        tenant_id = 0
        tenant_list = []
        secret_key = None
        algorithm = None
        access_lifetime = None

        if _is_multi_tenant_enabled():
            tenant_id, tenant_list, secret_key, algorithm, access_lifetime = (
                await self._auto_select_tenant(user.id)
            )

        # 生成JWT令牌（含 tenant_id 和租户 JWT 配置）
        tokens = await self.create_token(
            user_id=user.id, user_role="admin", username=user.username,
            ip=ip, user_agent=user_agent, tenant_id=tenant_id,
            secret_key=secret_key, algorithm=algorithm, access_lifetime=access_lifetime,
        )
        await self.on_after_login(user=user)

        response_model = {
            **tokens.model_dump(),
            "tenant_id": tenant_id if tenant_id else None,
            "tenants": tenant_list if tenant_list else None,
        }

        # 保存最后选择的租户
        if tenant_id and _is_multi_tenant_enabled():
            from plugins.multi_tenant.services.tenant_service import TenantService
            await TenantService.save_last_tenant(self.session, user.id, tenant_id)

        await self.session.commit()
        return response_model

    async def _auto_select_tenant(self, user_id: int):
        """
        自动选择租户：优先使用上次登录的租户，否则使用第一个租户。
        Returns: (tenant_id, tenant_list, secret_key, algorithm, access_lifetime)
        """
        from plugins.multi_tenant.services.tenant_service import TenantService

        tenants = await TenantService.get_user_tenants(self.session, user_id)
        if not tenants:
            return 0, [], None, None, None

        tenant_list = [
            {"id": t.id, "name": t.name, "code": t.code}
            for t in tenants
        ]

        # 优先使用上次选择的租户
        selected = None
        last_tid = await TenantService.get_last_tenant(user_id, db=self.session)
        if last_tid:
            for t in tenants:
                if t.id == last_tid:
                    selected = t
                    break
        if not selected:
            selected = tenants[0]

        # 查找租户 JWT 配置
        jwt_config = await TenantService.get_tenant_jwt_config_cached(selected.id)
        secret_key = jwt_config.secret_key if jwt_config else None
        algorithm = jwt_config.algorithm if jwt_config else None
        access_lifetime = jwt_config.access_lifetime if jwt_config else None

        return selected.id, tenant_list, secret_key, algorithm, access_lifetime

    async def on_after_login(self, user: SysUser):
        """
        用户登录后的回调
        """
        logger.info(f"用户 {user.id} 登录成功")

        request: Request = request_ctx.get()

        if request is not None:
            user.last_login_ip = get_real_client_ip(request)
            user.last_login_at = datetime.now(timezone.utc)

    async def current_user(self, token: str) -> SysUser:
        """
        获取当前认证的用户（同一请求内缓存，避免重复查询）
        """
        request: Request = request_ctx.get()
        if request is not None:
            cached = getattr(request.state, "_cached_current_user", None)
            if cached is not None:
                return cached

        user_id, _ = await self.verify_token_session(token)
        _cache = get_memory_cache()
        user = _cache.get(CacheNamespace.USER, str(user_id))
        if user is None:
            user = await self.session.execute(select(SysUser).where(SysUser.id == user_id))
            user = user.scalars().first()
            if user is None:
                raise TokenError()
            if not user.status:
                raise TokenError()
            self.session.expunge(user)
            _cache.set(CacheNamespace.USER, str(user_id), user, ttl=30)

        if request is not None:
            request.state._cached_current_user = user
        return user

    async def verify_token_session(
        self, token: str, _type: str = "access"
    ) -> Tuple[int, str]:
        """
        验证token中的session_id是否有效
        """
        # 优先复用中间件已解码的 JWT payload，避免重复解码
        request: Request = request_ctx.get()
        cached_payload = None
        if request is not None:
            cached_payload = getattr(request.state, "_jwt_payload", None)
            cached_token = getattr(request.state, "_jwt_raw_token", None)
            if cached_token != token:
                cached_payload = None

        payload = cached_payload if cached_payload is not None else self.jwt_manager.decode_token(token)
        session_id = payload.get("session_id")
        user_id = payload.get("user_id")
        user_role = payload.get("role")
        tenant_id = int(payload.get("tenant_id", 0)) if payload.get("tenant_id") else 0
        if payload.get("scope") != _type:
            raise TokenError()
        if not user_id:
            raise TokenError()
        if not session_id:
            raise TokenError()
        if not user_role:
            raise TokenError()

        # 混合验证：如果租户有自定义密钥，用租户密钥重新验证
        if tenant_id and _is_multi_tenant_enabled():
            payload = await self._verify_with_tenant_key(token, payload, tenant_id)

        # 新格式 key
        cache_key = build_session_key(user_role, int(user_id), tenant_id=tenant_id)
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

        # Fallback: 兼容旧格式 key（JWT_SESSION:admin123），过渡期使用
        legacy_key = build_session_key_legacy(user_role, int(user_id))
        if legacy_key != cache_key:
            legacy_meta = await get_redis_util().hget(legacy_key, session_id)
            if legacy_meta is not None:
                _cache.set(CacheNamespace.SESSION, f"{legacy_key}:{session_id}", True, ttl=5)
                return int(user_id), session_id
            try:
                legacy_sid = await get_redis_util().get(legacy_key)
            except Exception:
                legacy_sid = None
            if legacy_sid is not None and legacy_sid == session_id:
                _cache.set(CacheNamespace.SESSION, f"{legacy_key}:{session_id}", True, ttl=5)
                return int(user_id), session_id

        raise TokenError()

    async def _verify_with_tenant_key(self, token: str, payload: dict, tenant_id: int) -> dict:
        """用租户自定义密钥验证 token（混合模式）"""
        from plugins.multi_tenant.services.tenant_service import TenantService
        jwt_config = await TenantService.get_tenant_jwt_config_cached(tenant_id)
        if jwt_config and jwt_config.secret_key:
            try:
                payload = self.jwt_manager.decode_token(
                    token,
                    secret_key=jwt_config.secret_key,
                    algorithm=jwt_config.algorithm,
                )
            except Exception:
                # 租户密钥验证失败，回退到全局密钥（payload 已经通过全局密钥解码）
                pass
        return payload

    async def get_user_info(self, user_id: int):
        """
        获取用户信息，包含角色列表
        """
        stmt = (
            select(SysUser)
            .options(joinedload(SysUser.roles))
            .where(SysUser.id == user_id)
        )
        result = await self.session.execute(stmt)
        user = result.unique().scalars().first()
        if not user:
            raise CustomError(
                error=CustomErrorCode.USER_NOT_FOUND,
            )

        def format_datetime(dt):
            if dt:
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            return None

        # 收集角色 code 列表
        roles: List[str] = [role.name for role in user.roles if role.status]

        user_info = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "phone": user.phone,
            "avatar": user.avatar,
            "is_superuser": user.is_superuser,
            "status": user.status,
            "last_login_at": format_datetime(user.last_login_at),
            "last_login_ip": user.last_login_ip,
            "roles": roles,
        }
        return user_info


async def get_user_manager(
    user_db: AsyncSession = Depends(get_session),
):
    """
    获取用户管理器实例
    """
    yield UserManager(user_db)


async def current_user(
    token: str = Depends(oauth2_scheme),
    user_manager: UserManager = Depends(get_user_manager),
) -> SysUser:
    """
    获取当前认证用户的数据库模型实例
    """
    return await user_manager.current_user(token)
