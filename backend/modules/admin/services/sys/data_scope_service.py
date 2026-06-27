#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据权限服务
基于角色 data_scope 计算当前用户可见的数据范围（部门集合）。
"""
import logging
from typing import Optional, Set

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.sys.user import SysUser
from database.models.sys.role import SysRole, DataScopeEnum
from database.models.sys.dept import SysDept

logger = logging.getLogger(__name__)


class DataScopeService:
    """
    数据权限服务

    用户的可见数据范围 = 其所有启用角色 data_scope 的最宽并集（ALL > DEPT_AND_SUB > DEPT_ONLY > SELF）。
    超管（is_superuser=True）直接旁路，返回 None 表示不限。
    """

    _PRIORITY = {
        DataScopeEnum.ALL: 4,
        DataScopeEnum.DEPT_AND_SUB: 3,
        DataScopeEnum.DEPT_ONLY: 2,
        DataScopeEnum.SELF: 1,
    }

    @staticmethod
    async def get_effective_scope(
        db: AsyncSession, user: SysUser
    ) -> Optional[DataScopeEnum]:
        """
        聚合用户所有启用角色的 data_scope，取最宽。

        Returns:
            None 表示不限（超管或角色含 ALL）；否则返回最宽的 DataScopeEnum。
        """
        if user.is_superuser:
            return None

        result = await db.execute(
            select(SysUser)
            .options(selectinload(SysUser.roles))
            .where(SysUser.id == user.id)
        )
        user_with_roles = result.unique().scalar_one()

        best: Optional[DataScopeEnum] = None
        best_priority = 0
        for role in user_with_roles.roles:
            if not role.status:
                continue
            priority = DataScopeService._PRIORITY.get(role.data_scope, 0)
            if priority == 4:
                return None
            if priority > best_priority:
                best_priority = priority
                best = role.data_scope
        return best

    @staticmethod
    async def get_permitted_dept_ids(
        db: AsyncSession,
        user: SysUser,
        scope: Optional[DataScopeEnum],
    ) -> Optional[Set[int]]:
        """
        根据 scope 算可见部门 ID 集合。

        Returns:
            None 表示不限（ALL/超管）；
            空集合表示无 dept 维度可见（SELF，调用方需自行按 user.id 过滤）；
            非空集合表示白名单 dept_id。
        """
        if scope is None:
            return None

        if scope == DataScopeEnum.SELF:
            return set()

        if user.dept_id is None:
            logger.warning(
                "用户 %s 的 data_scope=%s 但未配置 dept_id，将无法看到任何部门数据",
                user.id, scope,
            )
            return set()

        if scope == DataScopeEnum.DEPT_ONLY:
            return {user.dept_id}

        # DEPT_AND_SUB：本部门 + 子部门
        result = await db.execute(select(SysDept.id, SysDept.parent_id))
        parent_map: dict[int, Optional[int]] = {row[0]: row[1] for row in result.all()}

        permitted: Set[int] = {user.dept_id}
        queue = [user.dept_id]
        while queue:
            current = queue.pop()
            for dept_id, parent_id in parent_map.items():
                if parent_id == current and dept_id not in permitted:
                    permitted.add(dept_id)
                    queue.append(dept_id)
        return permitted
