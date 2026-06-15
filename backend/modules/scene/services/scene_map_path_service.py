#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from core.exception.errors import NotFoundError
from database.models.business.scene_map_path import SceneMapPath
from modules.scene.schemas.scene_map_path import (
    SceneMapPathCreate,
    SceneMapPathUpdate,
)


class SceneMapPathService:
    """场景地图路径管理服务"""

    @staticmethod
    def build_query(map_id: int):
        """构建路径查询（按地图ID过滤）"""
        stmt = (
            select(SceneMapPath)
            .where(SceneMapPath.map_id == map_id, SceneMapPath.deleted_at.is_(None))
            .options(noload(SceneMapPath.map))
            .order_by(SceneMapPath.created_at.desc())
        )
        return stmt

    @staticmethod
    async def get_list(db: AsyncSession, map_id: int) -> List[SceneMapPath]:
        """获取地图下的路径列表"""
        stmt = SceneMapPathService.build_query(map_id)
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get(db: AsyncSession, path_id: int) -> SceneMapPath:
        """获取单个路径"""
        stmt = select(SceneMapPath).where(
            SceneMapPath.id == path_id,
            SceneMapPath.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        path = result.scalar_one_or_none()
        if not path:
            raise NotFoundError(msg=f"地图路径 {path_id} 不存在")
        return path

    @staticmethod
    async def create(
        db: AsyncSession, path_create: SceneMapPathCreate
    ) -> SceneMapPath:
        """创建地图路径"""
        path = SceneMapPath(
            map_id=path_create.map_id,
            start_annotation_id=path_create.start_annotation_id,
            end_annotation_id=path_create.end_annotation_id,
            name=path_create.name,
            points=path_create.points,
        )
        db.add(path)
        await db.flush()
        return path

    @staticmethod
    async def update(
        db: AsyncSession, path_id: int, path_update: SceneMapPathUpdate
    ) -> SceneMapPath:
        """更新地图路径"""
        path = await SceneMapPathService.get(db, path_id)

        update_data = path_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(path, field, value)

        await db.flush()
        return path

    @staticmethod
    async def delete(db: AsyncSession, path_id: int) -> None:
        """删除地图路径"""
        path = await SceneMapPathService.get(db, path_id)
        await db.delete(path)
        await db.flush()
