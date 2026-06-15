#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Tuple

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload, joinedload

from core.exception.errors import NotFoundError
from database.models.business.scene_map import SceneMap
from database.models.business.scene_group import SceneGroup
from modules.scene.services.scene_group_service import SceneGroupService
from database.utils.timezone import timezone
from modules.scene.schemas.scene_map import (
    SceneMapCreate,
    SceneMapUpdate,
    SceneMapQueryParams,
)


class SceneMapService:
    """场景地图管理服务"""

    @staticmethod
    def build_query(query_params: SceneMapQueryParams):
        """构建场景地图查询（关联分组名称）"""
        conditions = []
        if query_params.name:
            conditions.append(SceneMap.name.like(f"%{query_params.name}%"))
        if query_params.group_id is not None:
            conditions.append(SceneMap.group_id == query_params.group_id)
        if query_params.status is not None:
            conditions.append(SceneMap.status == query_params.status)

        stmt = (
            select(SceneMap)
            .where(SceneMap.deleted_at.is_(None))
            .options(noload(SceneMap.annotations), noload(SceneMap.objects))
        )
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(SceneMap.created_at.desc())
        return stmt

    @staticmethod
    async def get_list_with_group_name(
        db: AsyncSession, query_params: SceneMapQueryParams
    ) -> Tuple[List[dict], int]:
        """获取地图列表（含分组名称）及总数"""
        from sqlalchemy.sql import func

        stmt = SceneMapService.build_query(query_params)

        # 计算总数
        count_stmt = stmt.with_only_columns(func.count()).order_by(None)
        result = await db.execute(count_stmt)
        total = result.scalar() or 0

        # 获取数据
        result = await db.execute(stmt)
        maps = result.unique().scalars().all()

        # 批量获取分组名称
        group_ids = {m.group_id for m in maps if m.group_id is not None}
        group_map = {}
        if group_ids:
            group_stmt = select(SceneGroup).where(
                SceneGroup.id.in_(group_ids),
                SceneGroup.deleted_at.is_(None),
            )
            group_result = await db.execute(group_stmt)
            for g in group_result.scalars().all():
                group_map[g.id] = g.name

        # 组装结果
        items = []
        for m in maps:
            item_dict = {
                "id": m.id,
                "name": m.name,
                "group_id": m.group_id,
                "image_id": m.image_id,
                "width": m.width,
                "height": m.height,
                "resolution": m.resolution,
                "start_point_x": m.start_point_x,
                "start_point_y": m.start_point_y,
                "status": m.status,
                "group_name": group_map.get(m.group_id) if m.group_id else None,
                "created_at": m.created_at,
                "updated_at": m.updated_at,
            }
            items.append(item_dict)

        return items, total

    @staticmethod
    async def get(db: AsyncSession, map_id: int) -> SceneMap:
        """获取单个地图（含标注和物体）"""
        stmt = (
            select(SceneMap)
            .where(
                SceneMap.id == map_id,
                SceneMap.deleted_at.is_(None),
            )
            .options(
                noload(SceneMap.group),
                noload(SceneMap.image),
            )
        )
        result = await db.execute(stmt)
        map_obj = result.scalar_one_or_none()
        if not map_obj:
            raise NotFoundError(msg=f"场景地图 {map_id} 不存在")
        return map_obj

    @staticmethod
    async def _resolve_group_id(db: AsyncSession, map_create: SceneMapCreate) -> int | None:
        """解析分组ID：优先使用group_id，否则按group_name查找或自动创建"""
        if map_create.group_id is not None:
            return map_create.group_id
        if not map_create.group_name:
            return None

        # 按名称查找已有分组
        stmt = select(SceneGroup).where(
            SceneGroup.name == map_create.group_name,
            SceneGroup.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if existing:
            return existing.id

        # 自动创建分组
        from modules.scene.schemas.scene_group import SceneGroupCreate
        group_create = SceneGroupCreate(name=map_create.group_name, status=True)
        group_obj = await SceneGroupService.create(db, group_create)
        return group_obj.id

    @staticmethod
    async def create(db: AsyncSession, map_create: SceneMapCreate) -> SceneMap:
        """创建场景地图"""
        group_id = await SceneMapService._resolve_group_id(db, map_create)
        map_obj = SceneMap(
            name=map_create.name,
            group_id=group_id,
            image_id=map_create.image_id,
            width=map_create.width,
            height=map_create.height,
            resolution=map_create.resolution,
            start_point_x=map_create.start_point_x,
            start_point_y=map_create.start_point_y,
            status=map_create.status,
        )
        db.add(map_obj)
        await db.flush()
        return map_obj

    @staticmethod
    async def update(
        db: AsyncSession, map_id: int, map_update: SceneMapUpdate
    ) -> SceneMap:
        """更新场景地图"""
        map_obj = await SceneMapService.get(db, map_id)

        update_data = map_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(map_obj, field, value)

        await db.flush()
        return map_obj

    @staticmethod
    async def delete(db: AsyncSession, map_id: int) -> None:
        """删除场景地图（软删除）"""
        map_obj = await SceneMapService.get(db, map_id)
        map_obj.soft_delete()
        await db.flush()
