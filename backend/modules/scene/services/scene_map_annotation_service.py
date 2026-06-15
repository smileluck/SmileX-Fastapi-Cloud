#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from core.exception.errors import NotFoundError
from database.models.business.scene_map_annotation import SceneMapAnnotation
from modules.scene.schemas.scene_map_annotation import (
    SceneMapAnnotationCreate,
    SceneMapAnnotationUpdate,
)


class SceneMapAnnotationService:
    """场景地图标注管理服务"""

    @staticmethod
    def build_query(map_id: int):
        """构建标注查询（按地图ID过滤）"""
        stmt = (
            select(SceneMapAnnotation)
            .where(SceneMapAnnotation.map_id == map_id)
            .options(noload(SceneMapAnnotation.map))
            .order_by(SceneMapAnnotation.created_at.desc())
        )
        return stmt

    @staticmethod
    async def get_list(db: AsyncSession, map_id: int) -> List[SceneMapAnnotation]:
        """获取地图下的标注列表"""
        stmt = SceneMapAnnotationService.build_query(map_id)
        result = await db.execute(stmt)
        return result.unique().scalars().all()

    @staticmethod
    async def get(db: AsyncSession, annotation_id: int) -> SceneMapAnnotation:
        """获取单个标注"""
        stmt = select(SceneMapAnnotation).where(
            SceneMapAnnotation.id == annotation_id,
        )
        result = await db.execute(stmt)
        annotation = result.scalar_one_or_none()
        if not annotation:
            raise NotFoundError(msg=f"地图标注 {annotation_id} 不存在")
        return annotation

    @staticmethod
    async def create(
        db: AsyncSession, annotation_create: SceneMapAnnotationCreate
    ) -> SceneMapAnnotation:
        """创建地图标注"""
        annotation = SceneMapAnnotation(
            map_id=annotation_create.map_id,
            x=annotation_create.x,
            y=annotation_create.y,
            name=annotation_create.name,
            angle=annotation_create.angle,
            type=annotation_create.type,
        )
        db.add(annotation)
        await db.flush()
        return annotation

    @staticmethod
    async def update(
        db: AsyncSession, annotation_id: int, annotation_update: SceneMapAnnotationUpdate
    ) -> SceneMapAnnotation:
        """更新地图标注"""
        annotation = await SceneMapAnnotationService.get(db, annotation_id)

        update_data = annotation_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(annotation, field, value)

        await db.flush()
        return annotation

    @staticmethod
    async def delete(db: AsyncSession, annotation_id: int) -> None:
        """删除地图标注"""
        annotation = await SceneMapAnnotationService.get(db, annotation_id)
        await db.delete(annotation)
        await db.flush()
