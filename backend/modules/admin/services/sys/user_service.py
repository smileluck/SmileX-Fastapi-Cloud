#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
用户管理服务
处理用户相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Select
from sqlalchemy.orm import joinedload, selectinload, load_only
from typing import List, Optional, Tuple

from database.models.sys.user import SysUser
from database.models.sys.role import SysRole, DataScopeEnum
from core.exception.errors import NotFoundError, ConflictError, ForbiddenError
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from core.security.oauth.jwt import JWTAuthManager
from core.security.password import PasswordHasher
from modules.admin.schemas.sys.user import (
    SysUserCreate,
    SysUserUpdate,
    SysUserPasswordUpdate,
    SysUserQueryParams,
)

logger = logging.getLogger(__name__)

# Super admin username that cannot be modified/deleted
SUPER_ADMIN_USERNAME = "admin"


def _invalidate_user_cache(user_id: int) -> None:
    get_memory_cache().delete(CacheNamespace.USER, str(user_id))


class UserService:
    """
    用户管理服务类
    """

    @staticmethod
    def _apply_user_filters(
        base_query: Select,
        query_params: SysUserQueryParams,
        *,
        data_scope: DataScopeEnum | None = None,
        permitted_dept_ids: set[int] | None = None,
        current_user_id: int | None = None,
    ) -> Select:
        conditions = []
        if query_params.status is not None:
            conditions.append(SysUser.status == query_params.status)
        if query_params.username:
            conditions.append(SysUser.username.like(f"%{query_params.username}%"))
        if query_params.nickname:
            conditions.append(SysUser.nickname.like(f"%{query_params.nickname}%"))
        if query_params.email:
            conditions.append(SysUser.email.like(f"%{query_params.email}%"))
        if query_params.phone:
            conditions.append(SysUser.phone.like(f"%{query_params.phone}%"))
        if query_params.is_superuser is not None:
            conditions.append(SysUser.is_superuser == query_params.is_superuser)
        if query_params.role_ids:
            base_query = base_query.join(SysUser.roles).where(
                SysRole.id.in_(query_params.role_ids)
            )

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 行级数据权限：scope is None 表示不限（超管/ALL）
        if data_scope == DataScopeEnum.SELF:
            base_query = base_query.where(SysUser.id == current_user_id)
        elif permitted_dept_ids is not None:
            base_query = base_query.where(SysUser.dept_id.in_(permitted_dept_ids))

        return base_query.order_by(SysUser.created_at.desc())

    @staticmethod
    def build_user_list_query(
        query_params: SysUserQueryParams,
        *,
        data_scope: DataScopeEnum | None = None,
        permitted_dept_ids: set[int] | None = None,
        current_user_id: int | None = None,
    ) -> Select:
        """
        构建用户列表查询对象（不加载关联角色）

        Args:
            query_params: 查询参数
            data_scope: 数据范围（None=不限）；SELF 时按 current_user_id 过滤
            permitted_dept_ids: 允许可见的部门 ID 集合（None=不限）
            current_user_id: 当前操作用户 ID（SELF 范围使用）

        Returns:
            SQLAlchemy查询对象
        """
        base_query = select(SysUser).options(
            load_only(
                SysUser.id,
                SysUser.username,
                SysUser.nickname,
                SysUser.email,
                SysUser.phone,
                SysUser.avatar,
                SysUser.status,
                SysUser.is_superuser,
                SysUser.last_login_at,
                SysUser.last_login_ip,
                SysUser.dept_id,
                SysUser.created_at,
                SysUser.updated_at,
            )
        )
        return UserService._apply_user_filters(
            base_query,
            query_params,
            data_scope=data_scope,
            permitted_dept_ids=permitted_dept_ids,
            current_user_id=current_user_id,
        )

    @staticmethod
    def build_user_query(
        query_params: SysUserQueryParams,
        *,
        data_scope: DataScopeEnum | None = None,
        permitted_dept_ids: set[int] | None = None,
        current_user_id: int | None = None,
    ) -> Select:
        """
        构建用户查询对象（加载关联角色，用于导出等需要角色信息的场景）

        Args:
            query_params: 查询参数
            data_scope: 数据范围（None=不限）；SELF 时按 current_user_id 过滤
            permitted_dept_ids: 允许可见的部门 ID 集合（None=不限）
            current_user_id: 当前操作用户 ID（SELF 范围使用）

        Returns:
            SQLAlchemy查询对象
        """
        base_query = select(SysUser).options(selectinload(SysUser.roles))
        return UserService._apply_user_filters(
            base_query,
            query_params,
            data_scope=data_scope,
            permitted_dept_ids=permitted_dept_ids,
            current_user_id=current_user_id,
        )

    @staticmethod
    async def get_user_list(
        db: AsyncSession,
        query_params: SysUserQueryParams,
        *,
        data_scope: DataScopeEnum | None = None,
        permitted_dept_ids: set[int] | None = None,
        current_user_id: int | None = None,
    ) -> Tuple[List[SysUser], int]:
        """
        获取用户列表（带分页和查询条件）

        Args:
            db: 数据库会话
            query_params: 查询参数
            data_scope: 数据范围（None=不限）；SELF 时按 current_user_id 过滤
            permitted_dept_ids: 允许可见的部门 ID 集合（None=不限）
            current_user_id: 当前操作用户 ID（SELF 范围使用）

        Returns:
            Tuple[用户列表, 总记录数]
        """
        logger.debug("获取用户列表，查询参数: %s", query_params)

        # 构建查询（列表页不需要角色信息）
        base_query = UserService.build_user_list_query(
            query_params,
            data_scope=data_scope,
            permitted_dept_ids=permitted_dept_ids,
            current_user_id=current_user_id,
        )

        # 统计总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (query_params.page - 1) * query_params.page_size
        paginated_query = base_query.offset(offset).limit(query_params.page_size)

        # 执行查询
        result = await db.execute(paginated_query)
        users = result.scalars().all()

        logger.debug("获取用户列表成功，共 %s 条记录", total)
        return users, total

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> SysUser:
        """
        获取单个用户（包含关联角色）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            用户对象

        Raises:
            NotFoundError: 用户不存在
        """
        logger.debug("获取用户信息，用户ID: %s", user_id)

        result = await db.execute(
            select(SysUser)
            .options(joinedload(SysUser.roles))
            .where(SysUser.id == user_id)
        )
        user = result.unique().scalar_one_or_none()

        if not user:
            logger.warning("用户不存在，用户ID: %s", user_id)
            raise NotFoundError(msg=f"用户 {user_id} 不存在")

        logger.debug("获取用户信息成功，用户名: %s", user.username)
        return user

    @staticmethod
    async def get_user_by_username(
        db: AsyncSession, username: str
    ) -> Optional[SysUser]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            用户对象或None
        """
        result = await db.execute(select(SysUser).where(SysUser.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_create: SysUserCreate) -> SysUser:
        """
        创建用户

        Args:
            db: 数据库会话
            user_create: 用户创建请求模型

        Returns:
            创建后的用户对象

        Raises:
            ConflictError: 用户名/邮箱/手机号已存在
        """
        logger.info("创建用户，用户名: %s", user_create.username)

        # 检查用户名是否已存在
        if await UserService.get_user_by_username(db, user_create.username):
            logger.warning("创建用户失败，用户名已存在: %s", user_create.username)
            raise ConflictError(msg="用户名已存在")

        # 检查邮箱是否已存在
        if user_create.email and user_create.email.strip():
            result = await db.execute(
                select(SysUser).where(SysUser.email == user_create.email)
            )
            if result.scalar_one_or_none():
                logger.warning("创建用户失败，邮箱已存在: %s", user_create.email)
                raise ConflictError(msg="邮箱已存在")

        # 检查手机号是否已存在
        if user_create.phone and user_create.phone.strip():
            result = await db.execute(
                select(SysUser).where(SysUser.phone == user_create.phone)
            )
            if result.scalar_one_or_none():
                logger.warning("创建用户失败，手机号已存在: %s", user_create.phone)
                raise ConflictError(msg="手机号已存在")

        # 加密密码
        user = SysUser(
            username=user_create.username,
            nickname=user_create.nickname,
            email=user_create.email,
            password=PasswordHasher.hash(user_create.password),
            phone=user_create.phone,
            avatar=user_create.avatar,
            status=user_create.status,
            is_superuser=False,
            dept_id=user_create.dept_id,
        )

        # 分配角色
        if user_create.role_ids:
            result = await db.execute(
                select(SysRole).where(SysRole.id.in_(user_create.role_ids))
            )
            roles = result.scalars().all()
            user.roles = roles

        db.add(user)
        await db.commit()
        await db.refresh(user)

        logger.info("创建用户成功，用户ID: %s", user.id)
        return user

    @staticmethod
    async def update_user(
        db: AsyncSession, user_id: int, user_update: SysUserUpdate
    ) -> SysUser:
        """
        更新用户

        Args:
            db: 数据库会话
            user_id: 用户ID
            user_update: 用户更新请求模型

        Returns:
            更新后的用户对象

        Raises:
            NotFoundError: 用户不存在
            ConflictError: 用户名/邮箱/手机号已被其他用户使用
        """
        logger.info("更新用户信息，用户ID: %s", user_id)

        # 获取用户
        user = await UserService.get_user(db, user_id)

        # 保护超级管理员账号不被禁用
        if user.username == SUPER_ADMIN_USERNAME and user_update.status is False:
            logger.warning("更新用户失败，不能禁用超级管理员账号，用户ID: %s", user_id)
            raise ForbiddenError(msg="不能禁用超级管理员账号")

        # 检查用户名是否已被其他用户使用
        if (
            user_update.username
            and user_update.username.strip()
            and user_update.username != user.username
        ):
            result = await db.execute(
                select(SysUser).where(
                    SysUser.username == user_update.username, SysUser.id != user_id
                )
            )
            if result.scalar_one_or_none():
                logger.warning(
                    "更新用户失败，用户名已被其他用户使用: %s", user_update.username
                )
                raise ConflictError(msg="用户名已被其他用户使用")

        # 检查邮箱是否已被其他用户使用
        if (
            user_update.email
            and user_update.email.strip()
            and user_update.email != user.email
        ):
            result = await db.execute(
                select(SysUser).where(
                    SysUser.email == user_update.email, SysUser.id != user_id
                )
            )
            if result.scalar_one_or_none():
                logger.warning(
                    "更新用户失败，邮箱已被其他用户使用: %s", user_update.email
                )
                raise ConflictError(msg="邮箱已被其他用户使用")

        # 检查手机号是否已被其他用户使用
        if (
            user_update.phone
            and user_update.phone.strip()
            and user_update.phone != user.phone
        ):
            result = await db.execute(
                select(SysUser).where(
                    SysUser.phone == user_update.phone, SysUser.id != user_id
                )
            )
            if result.scalar_one_or_none():
                logger.warning(
                    "更新用户失败，手机号已被其他用户使用: %s", user_update.phone
                )
                raise ConflictError(msg="手机号已被其他用户使用")

        # 更新用户信息
        update_data = user_update.model_dump(exclude_unset=True)

        # 处理角色分配
        if "role_ids" in update_data:
            role_ids = update_data.pop("role_ids")
            if role_ids:
                result = await db.execute(
                    select(SysRole).where(SysRole.id.in_(role_ids))
                )
                roles = result.scalars().all()
                user.roles = roles
            else:
                user.roles = []

        # 更新其他字段
        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        _invalidate_user_cache(user_id)
        if "role_ids" in user_update.model_dump(exclude_unset=True):
            get_memory_cache().invalidate(CacheNamespace.PERMISSION)

        logger.info("更新用户信息成功，用户ID: %s", user_id)
        return user

    @staticmethod
    async def assign_roles_to_user(
        db: AsyncSession, user_id: int, role_ids: List[int]
    ) -> SysUser:
        """
        为用户分配角色

        Args:
            db: 数据库会话
            user_id: 用户ID
            role_ids: 角色ID列表

        Returns:
            更新后的用户对象

        Raises:
            NotFoundError: 用户不存在
        """
        logger.info("为用户分配角色，用户ID: %s, 角色ID列表: %s", user_id, role_ids)

        # 获取用户
        user = await UserService.get_user(db, user_id)

        # 获取角色
        if role_ids:
            result = await db.execute(select(SysRole).where(SysRole.id.in_(role_ids)))
            roles = result.scalars().all()
            user.roles = roles
        else:
            user.roles = []

        await db.commit()
        await db.refresh(user)

        _invalidate_user_cache(user_id)
        get_memory_cache().invalidate(CacheNamespace.PERMISSION)

        logger.info("为用户分配角色成功，用户ID: %s", user_id)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """
        删除用户

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 用户不存在
            ForbiddenError: 不能删除超级管理员
        """
        logger.info("删除用户，用户ID: %s", user_id)

        # 获取用户
        user = await UserService.get_user(db, user_id)

        # 检查是否为超级管理员
        if user.is_superuser:
            logger.warning("删除用户失败，不能删除超级管理员，用户ID: %s", user_id)
            raise ForbiddenError(msg="不能删除超级管理员")

        # 基于用户名的额外保护
        if user.username == SUPER_ADMIN_USERNAME:
            logger.warning("删除用户失败，不能删除超级管理员账号，用户ID: %s", user_id)
            raise ForbiddenError(msg="不能删除超级管理员账号")

        await db.delete(user)
        await db.commit()

        _invalidate_user_cache(user_id)
        logger.info("删除用户成功，用户ID: %s", user_id)
        return True

    @staticmethod
    async def batch_delete_users(db: AsyncSession, user_ids: List[int]) -> int:
        """
        批量删除用户

        Args:
            db: 数据库会话
            user_ids: 用户ID列表

        Returns:
            删除的用户数量

        Raises:
            ForbiddenError: 不能删除超级管理员
        """
        logger.info("批量删除用户，用户ID列表: %s", user_ids)

        delete_count = 0
        for user_id in user_ids:
            try:
                await UserService.delete_user(db, user_id)
                delete_count += 1
            except Exception as e:
                logger.error(f"删除用户失败，用户ID: {user_id}, 错误: {str(e)}")
                raise e

        logger.info("批量删除用户成功，共删除 %s 个用户", delete_count)
        return delete_count

    @staticmethod
    async def update_user_password(
        db: AsyncSession,
        user_id: int,
        password_update: SysUserPasswordUpdate,
        current_user: Optional[SysUser] = None,
    ) -> bool:
        """
        修改用户密码

        Args:
            db: 数据库会话
            user_id: 用户ID
            password_update: 密码更新请求模型
            current_user: 当前操作用户（用于验证旧密码）

        Returns:
            是否修改成功

        Raises:
            NotFoundError: 用户不存在
            ForbiddenError: 密码错误或无权限修改超级管理员密码
        """
        logger.info("修改用户密码，用户ID: %s", user_id)

        # 获取用户
        user = await UserService.get_user(db, user_id)

        # 检查是否为超级管理员（只有超级管理员自己可以修改自己的密码）
        if user.is_superuser and (not current_user or current_user.id != user_id):
            logger.warning("修改密码失败，无权限修改超级管理员密码，用户ID: %s", user_id)
            raise ForbiddenError(msg="无权限修改超级管理员密码")

        # 如果提供了旧密码，需要验证
        if password_update.old_password:
            if not PasswordHasher.verify(
                password_update.old_password, user.password
            ):
                logger.warning("修改密码失败，旧密码错误，用户ID: %s", user_id)
                raise ForbiddenError(msg="旧密码错误")

        # 加密新密码
        user.password = PasswordHasher.hash(password_update.new_password)

        await db.commit()

        _invalidate_user_cache(user_id)
        logger.info("修改用户密码成功，用户ID: %s", user_id)
        return True

    @staticmethod
    async def batch_update_users_status(
        db: AsyncSession, user_ids: List[int], status: bool
    ) -> int:
        """
        批量更新用户状态

        Args:
            db: 数据库会话
            user_ids: 用户ID列表
            status: 要设置的状态

        Returns:
            更新的用户数量
        """
        logger.info("批量更新用户状态，用户ID列表: %s, 状态: %s", user_ids, status)

        # 获取用户
        result = await db.execute(select(SysUser).where(SysUser.id.in_(user_ids)))
        users = result.scalars().all()

        # 更新状态
        update_count = 0
        for user in users:
            # 保护超级管理员账号不被禁用
            if user.username == SUPER_ADMIN_USERNAME and not status:
                logger.warning("不能禁用超级管理员账号，用户ID: %s", user.id)
                continue
            user.status = status
            update_count += 1

        await db.commit()

        for user in users:
            _invalidate_user_cache(user.id)

        logger.info("批量更新用户状态成功，共更新 %s 个用户", update_count)
        return update_count
