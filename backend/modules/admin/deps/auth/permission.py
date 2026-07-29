#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限校验依赖
用于在API端点上检查当前用户是否具有指定的权限标识
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from database.db_manager import get_session
from database.models.sys.user import SysUser
from database.models.sys.role import SysRole
from database.models.sys.menu import SysMenu, MenuType
from core.exception.errors import ForbiddenError
from core.i18n import t
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from modules.admin.deps.auth.user_manager import current_user


def require_permission(permission_code: str):
    """
    创建一个权限校验依赖项

    Args:
        permission_code: 权限标识码，如 "sys:menu:add"

    Returns:
        FastAPI依赖项函数，校验当前用户是否具有指定权限
    """
    async def _check_permission(
        user: SysUser = Depends(current_user),
        db: AsyncSession = Depends(get_session),
    ) -> SysUser:
        # 超级用户跳过权限检查
        if user.is_superuser:
            return user

        _cache = get_memory_cache()
        cache_key = f"{user.id}:{permission_code}"
        cached_result = _cache.get(CacheNamespace.PERMISSION, cache_key)
        if cached_result is not None:
            if not cached_result:
                raise ForbiddenError(msg=t("auth.no_permission_code", code=permission_code))
            return user

        # 查询用户角色关联的按钮权限中是否包含指定权限码
        stmt = (
            select(SysMenu.permission)
            .join(SysMenu.roles)
            .join(SysRole.users)
            .where(
                SysUser.id == user.id,
                SysMenu.type == MenuType.BUTTON,
                SysMenu.status == True,
                SysRole.status == True,
                SysMenu.permission == permission_code,
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        has_permission = result.scalar_one_or_none() is not None
        _cache.set(CacheNamespace.PERMISSION, cache_key, has_permission, ttl=60)
        if not has_permission:
            raise ForbiddenError(msg=t("auth.no_permission_code", code=permission_code))

        return user

    return _check_permission
