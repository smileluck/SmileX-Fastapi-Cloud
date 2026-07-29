#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
权限管理服务
处理权限相关的业务逻辑
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from database.models.sys.permission import SysPermission
from core.exception.errors import NotFoundError, ConflictError
from core.i18n import t
from modules.admin.schemas.sys.permission import (
    SysPermissionCreate,
    SysPermissionUpdate,
)


class PermissionService:
    """
    权限管理服务类
    """

    @staticmethod
    async def get_permission_list(
        db: AsyncSession,
        category: Optional[str] = None,
        status: Optional[bool] = None,
    ) -> List[SysPermission]:
        query = select(SysPermission)
        if category:
            query = query.where(SysPermission.category == category)
        if status is not None:
            query = query.where(SysPermission.status == status)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create_permission(
        db: AsyncSession,
        permission_in: SysPermissionCreate,
    ) -> SysPermission:
        # 检查权限编码是否已存在
        result = await db.execute(
            select(SysPermission).where(SysPermission.code == permission_in.code)
        )
        if result.scalar_one_or_none():
            raise ConflictError(msg=t("permission.code_exist"))

        permission = SysPermission(**permission_in.model_dump())
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        return permission

    @staticmethod
    async def update_permission(
        db: AsyncSession,
        permission_id: int,
        permission_in: SysPermissionUpdate,
    ) -> SysPermission:
        result = await db.execute(
            select(SysPermission).where(SysPermission.id == permission_id)
        )
        existing_permission = result.scalar_one_or_none()
        if not existing_permission:
            raise NotFoundError(msg=t("permission.not_found", id=permission_id))

        update_data = permission_in.model_dump(exclude_unset=True)

        # 如果更新了 code，检查是否重复
        if "code" in update_data:
            code_result = await db.execute(
                select(SysPermission).where(
                    SysPermission.code == update_data["code"],
                    SysPermission.id != permission_id,
                )
            )
            if code_result.scalar_one_or_none():
                raise ConflictError(msg=t("permission.code_exist"))

        for key, value in update_data.items():
            setattr(existing_permission, key, value)

        await db.commit()
        await db.refresh(existing_permission)
        return existing_permission

    @staticmethod
    async def delete_permission(db: AsyncSession, permission_id: int) -> bool:
        result = await db.execute(
            select(SysPermission).where(SysPermission.id == permission_id)
        )
        permission = result.scalar_one_or_none()
        if not permission:
            raise NotFoundError(msg=t("permission.not_found", id=permission_id))

        await db.delete(permission)
        await db.commit()
        return True
