#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from core.exception.errors import NotFoundError
from database.models.business.scene_map_object import SceneMapObject
from modules.scene.schemas.scene_map_object import (
    SceneMapObjectCreate,
    SceneMapObjectUpdate,
)


class SceneMapObjectService:
    """场景地图物体管理服务"""

    @staticmethod
    def build_query(map_id: int):
        """构建物体查询（按地图ID过滤）"""
        stmt = (
            select(SceneMapObject)
            .where(SceneMapObject.map_id == map_id)
            .options(noload(SceneMapObject.map))
            .order_by(SceneMapObject.created_at.desc())
        )
        return stmt

    @staticmethod
    async def get_list(db: AsyncSession, map_id: int) -> List[SceneMapObject]:
        """获取地图下的物体列表"""
        stmt = SceneMapObjectService.build_query(map_id)
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get(db: AsyncSession, object_id: int) -> SceneMapObject:
        """获取单个物体"""
        stmt = select(SceneMapObject).where(
            SceneMapObject.id == object_id,
        )
        result = await db.execute(stmt)
        obj = result.scalar_one_or_none()
        if not obj:
            raise NotFoundError(msg=f"地图物体 {object_id} 不存在")
        return obj

    @staticmethod
    async def create(
        db: AsyncSession, object_create: SceneMapObjectCreate
    ) -> SceneMapObject:
        """创建地图物体"""
        obj = SceneMapObject(
            map_id=object_create.map_id,
            type=object_create.type,
            x=object_create.x,
            y=object_create.y,
            width=object_create.width,
            height=object_create.height,
            points=object_create.points,
        )
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def update(
        db: AsyncSession, object_id: int, object_update: SceneMapObjectUpdate
    ) -> SceneMapObject:
        """更新地图物体"""
        obj = await SceneMapObjectService.get(db, object_id)

        update_data = object_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(obj, field, value)

        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, object_id: int) -> None:
        """删除地图物体"""
        obj = await SceneMapObjectService.get(db, object_id)
        await db.delete(obj)
        await db.flush()
