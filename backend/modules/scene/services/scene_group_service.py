#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from core.exception.errors import NotFoundError, ConflictError
from database.models.business.scene_group import SceneGroup
from database.utils.timezone import timezone
from modules.scene.schemas.scene_group import (
    SceneGroupCreate,
    SceneGroupUpdate,
    SceneGroupQueryParams,
)


class SceneGroupService:
    """场景分组管理服务"""

    @staticmethod
    def build_query(query_params: SceneGroupQueryParams):
        """构建场景分组查询"""
        conditions = []
        if query_params.name:
            conditions.append(SceneGroup.name.like(f"%{query_params.name}%"))
        if query_params.status is not None:
            conditions.append(SceneGroup.status == query_params.status)

        stmt = select(SceneGroup).where(SceneGroup.deleted_at.is_(None))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(SceneGroup.sort.asc(), SceneGroup.created_at.desc())
        return stmt

    @staticmethod
    async def get_list(
        db: AsyncSession, query_params: SceneGroupQueryParams
    ) -> Tuple[List[SceneGroup], int]:
        """获取分组列表及总数"""
        from sqlalchemy.sql import func

        stmt = SceneGroupService.build_query(query_params)
        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        result = await db.execute(count_stmt)
        total = result.scalar() or 0

        result = await db.execute(stmt)
        items = result.unique().scalars().all()
        return items, total

    @staticmethod
    async def get_tree(db: AsyncSession) -> List[dict]:
        """获取分组树形结构"""
        stmt = (
            select(SceneGroup)
            .where(SceneGroup.deleted_at.is_(None))
            .options(noload(SceneGroup.children))
            .order_by(SceneGroup.sort.asc(), SceneGroup.created_at.desc())
        )
        result = await db.execute(stmt)
        items = result.unique().scalars().all()

        # 构建树形结构
        item_map = {}
        tree = []
        for item in items:
            node = {
                "id": item.id,
                "name": item.name,
                "parent_id": item.parent_id,
                "sort": item.sort,
                "status": item.status,
                "children": [],
            }
            item_map[item.id] = node

        for node in item_map.values():
            parent_id = node["parent_id"]
            if parent_id and parent_id in item_map:
                item_map[parent_id]["children"].append(node)
            else:
                tree.append(node)

        return tree

    @staticmethod
    async def get(db: AsyncSession, group_id: int) -> SceneGroup:
        """获取单个分组"""
        stmt = (
            select(SceneGroup)
            .where(
                SceneGroup.id == group_id,
                SceneGroup.deleted_at.is_(None),
            )
            .options(noload(SceneGroup.children))
        )
        result = await db.execute(stmt)
        group = result.scalar_one_or_none()
        if not group:
            raise NotFoundError(msg=f"场景分组 {group_id} 不存在")
        return group

    @staticmethod
    async def create(db: AsyncSession, group_create: SceneGroupCreate) -> SceneGroup:
        """创建场景分组"""
        # 校验父分组是否存在
        if group_create.parent_id is not None:
            parent = await SceneGroupService.get(db, group_create.parent_id)
            if not parent:
                raise NotFoundError(msg=f"父分组 {group_create.parent_id} 不存在")

        group = SceneGroup(
            name=group_create.name,
            parent_id=group_create.parent_id,
            sort=group_create.sort,
            status=group_create.status,
        )
        db.add(group)
        await db.flush()
        return group

    @staticmethod
    async def update(
        db: AsyncSession, group_id: int, group_update: SceneGroupUpdate
    ) -> SceneGroup:
        """更新场景分组"""
        group = await SceneGroupService.get(db, group_id)

        # 防止循环引用：不能将自己设为父分组
        if group_update.parent_id is not None and group_update.parent_id == group_id:
            raise ConflictError(msg="不能将自身设为父分组")

        update_data = group_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)

        await db.flush()
        return group

    @staticmethod
    async def delete(db: AsyncSession, group_id: int) -> None:
        """删除场景分组（软删除）"""
        group = await SceneGroupService.get(db, group_id)
        group.soft_delete()
        await db.flush()
