#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
应用用户（AppUser）管理服务
参照 UserService 的写法，去掉角色/部门/数据权限/超管保护；
禁用/改密/删除时吊销该用户在 C 端的全部 session，保证后台操作即时生效。
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Select
from sqlalchemy.orm import load_only
from typing import List, Optional, Tuple

from database.models.business.user import AppUser
from core.exception.errors import NotFoundError, ConflictError
from core.security.password import PasswordHasher
from modules.admin.services.sys.online_user_service import OnlineUserService
from modules.admin.schemas.sys.app_user import (
    AppUserCreate,
    AppUserUpdate,
    AppUserPasswordUpdate,
    AppUserQueryParams,
)

logger = logging.getLogger(__name__)


async def _revoke_app_user_sessions(user_id: int) -> None:
    """吊销 AppUser 在 C 端的全部会话（改密/禁用/删除后调用，使旧 token 立即失效）。"""
    try:
        await OnlineUserService.kick_all_sessions(user_id, role="app")
    except Exception as e:
        # 吊销失败不应阻断主流程，仅记日志
        logger.error("吊销 AppUser[%s] 会话失败: %s", user_id, e)


class AppUserService:
    """应用用户管理服务类"""

    @staticmethod
    def _apply_app_user_filters(base_query: Select, query_params: AppUserQueryParams) -> Select:
        conditions = []
        if query_params.name:
            conditions.append(AppUser.name.like(f"%{query_params.name}%"))
        if query_params.phone:
            conditions.append(AppUser.phone.like(f"%{query_params.phone}%"))
        if query_params.phone_code:
            conditions.append(AppUser.phone_code == query_params.phone_code)
        if query_params.email:
            conditions.append(AppUser.email.like(f"%{query_params.email}%"))
        if query_params.status is not None:
            conditions.append(AppUser.status == query_params.status)
        if query_params.wx_openid:
            # 传入 wx_openid 时按"已绑定微信"筛选（openid 非空）
            conditions.append(AppUser.wx_openid.is_not(None))

        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.order_by(AppUser.created_at.desc())

    @staticmethod
    def build_app_user_list_query(query_params: AppUserQueryParams) -> Select:
        """构建应用用户列表查询对象"""
        base_query = select(AppUser).options(
            load_only(
                AppUser.id,
                AppUser.name,
                AppUser.phone_code,
                AppUser.phone,
                AppUser.email,
                AppUser.avatar,
                AppUser.status,
                AppUser.wx_openid,
                AppUser.last_login_at,
                AppUser.last_login_ip,
                AppUser.created_at,
                AppUser.updated_at,
            )
        )
        return AppUserService._apply_app_user_filters(base_query, query_params)

    @staticmethod
    async def get_app_user(db: AsyncSession, user_id: int) -> AppUser:
        """获取单个应用用户

        Raises:
            NotFoundError: 用户不存在
        """
        logger.debug("获取应用用户信息，用户ID: %s", user_id)

        result = await db.execute(select(AppUser).where(AppUser.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.warning("应用用户不存在，用户ID: %s", user_id)
            raise NotFoundError(msg=f"应用用户 {user_id} 不存在")

        return user

    @staticmethod
    async def get_app_user_by_phone(
        db: AsyncSession, phone_code: str, phone: str
    ) -> Optional[AppUser]:
        """根据 (phone_code, phone) 组合查询应用用户"""
        result = await db.execute(
            select(AppUser).where(
                AppUser.phone_code == phone_code, AppUser.phone == phone
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_app_user(db: AsyncSession, user_create: AppUserCreate) -> AppUser:
        """创建应用用户

        Raises:
            ConflictError: 手机号/邮箱已存在
        """
        logger.info("创建应用用户，手机号: %s %s", user_create.phone_code, user_create.phone)

        # (phone_code, phone) 组合查重
        if await AppUserService.get_app_user_by_phone(db, user_create.phone_code, user_create.phone):
            logger.warning("创建应用用户失败，手机号已存在: %s", user_create.phone)
            raise ConflictError(msg="该手机号已存在")

        # email 非空时查重
        if user_create.email and user_create.email.strip():
            existing = await db.execute(select(AppUser).where(AppUser.email == user_create.email))
            if existing.scalar_one_or_none():
                logger.warning("创建应用用户失败，邮箱已存在: %s", user_create.email)
                raise ConflictError(msg="该邮箱已存在")

        # password 选填：留空则只允许短信登录
        user = AppUser(
            name=user_create.name,
            phone_code=user_create.phone_code,
            phone=user_create.phone,
            password=PasswordHasher.hash(user_create.password) if user_create.password else "",
            email=user_create.email,
            avatar=user_create.avatar,
            status=user_create.status,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info("创建应用用户成功，用户ID: %s", user.id)
        return user

    @staticmethod
    async def update_app_user(
        db: AsyncSession, user_id: int, user_update: AppUserUpdate
    ) -> AppUser:
        """更新应用用户

        Raises:
            NotFoundError: 用户不存在
            ConflictError: 手机号/邮箱已被其他用户使用
        """
        logger.info("更新应用用户信息，用户ID: %s", user_id)

        user = await AppUserService.get_app_user(db, user_id)

        # 计算目标 (phone_code, phone)，用于组合查重
        target_phone_code = (
            user_update.phone_code if user_update.phone_code is not None else user.phone_code
        )
        target_phone = user_update.phone if user_update.phone is not None else user.phone
        if (
            user_update.phone_code is not None or user_update.phone is not None
        ) and (target_phone_code, target_phone) != (user.phone_code, user.phone):
            existing = await db.execute(
                select(AppUser).where(
                    AppUser.phone_code == target_phone_code,
                    AppUser.phone == target_phone,
                    AppUser.id != user_id,
                )
            )
            if existing.scalar_one_or_none():
                logger.warning("更新应用用户失败，手机号已被其他用户使用: %s", target_phone)
                raise ConflictError(msg="该手机号已被其他用户使用")

        # email 查重（排除自身）
        if user_update.email and user_update.email.strip() and user_update.email != user.email:
            existing = await db.execute(
                select(AppUser).where(
                    AppUser.email == user_update.email, AppUser.id != user_id
                )
            )
            if existing.scalar_one_or_none():
                logger.warning("更新应用用户失败，邮箱已被其他用户使用: %s", user_update.email)
                raise ConflictError(msg="该邮箱已被其他用户使用")

        update_data = user_update.model_dump(exclude_unset=True)

        # 记录是否本次将禁用（用于改完后吊销 session）
        new_status = update_data.get("status")
        status_disabling = new_status is False and user.status is True

        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        if status_disabling:
            await _revoke_app_user_sessions(user_id)

        logger.info("更新应用用户信息成功，用户ID: %s", user_id)
        return user

    @staticmethod
    async def delete_app_user(db: AsyncSession, user_id: int) -> bool:
        """删除应用用户

        Raises:
            NotFoundError: 用户不存在
        """
        logger.info("删除应用用户，用户ID: %s", user_id)

        user = await AppUserService.get_app_user(db, user_id)

        await db.delete(user)
        await db.commit()

        await _revoke_app_user_sessions(user_id)
        logger.info("删除应用用户成功，用户ID: %s", user_id)
        return True

    @staticmethod
    async def batch_delete_app_users(db: AsyncSession, user_ids: List[int]) -> int:
        """批量删除应用用户"""
        logger.info("批量删除应用用户，用户ID列表: %s", user_ids)

        delete_count = 0
        for user_id in user_ids:
            try:
                await AppUserService.delete_app_user(db, user_id)
                delete_count += 1
            except Exception as e:
                logger.error("删除应用用户失败，用户ID: %s, 错误: %s", user_id, e)
                raise e

        logger.info("批量删除应用用户成功，共删除 %s 个", delete_count)
        return delete_count

    @staticmethod
    async def batch_update_app_users_status(
        db: AsyncSession, user_ids: List[int], status: bool
    ) -> int:
        """批量更新应用用户状态（禁用时吊销 session）"""
        logger.info("批量更新应用用户状态，用户ID列表: %s, 状态: %s", user_ids, status)

        result = await db.execute(select(AppUser).where(AppUser.id.in_(user_ids)))
        users = result.scalars().all()

        update_count = 0
        disabled_ids: List[int] = []
        for user in users:
            if not status and user.status is True:
                disabled_ids.append(user.id)
            user.status = status
            update_count += 1

        await db.commit()

        for uid in disabled_ids:
            await _revoke_app_user_sessions(uid)

        logger.info("批量更新应用用户状态成功，共更新 %s 个", update_count)
        return update_count

    @staticmethod
    async def update_app_user_password(
        db: AsyncSession, user_id: int, password_update: AppUserPasswordUpdate
    ) -> bool:
        """重置应用用户密码（改密后吊销 session，旧 token 失效）

        Raises:
            NotFoundError: 用户不存在
        """
        logger.info("重置应用用户密码，用户ID: %s", user_id)

        user = await AppUserService.get_app_user(db, user_id)
        user.password = PasswordHasher.hash(password_update.new_password)

        await db.commit()

        await _revoke_app_user_sessions(user_id)
        logger.info("重置应用用户密码成功，用户ID: %s", user_id)
        return True
