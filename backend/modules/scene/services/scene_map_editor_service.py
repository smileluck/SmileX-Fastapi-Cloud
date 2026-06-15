#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exception.errors import NotFoundError, ValidationError
from database.models.business.scene_map import SceneMap
from database.models.business.scene_map_annotation import SceneMapAnnotation
from database.models.business.scene_map_path import SceneMapPath
from database.models.business.scene_map_object import SceneMapObject
from modules.scene.schemas.scene_map_editor import EditorSaveRequest


class SceneMapEditorService:
    """场景地图编辑器服务"""

    @staticmethod
    async def get_editor_data(db: AsyncSession, map_id: int) -> SceneMap:
        """获取编辑器完整数据（地图 + 标注 + 路径 + 物体）"""
        stmt = (
            select(SceneMap)
            .where(
                SceneMap.id == map_id,
                SceneMap.deleted_at.is_(None),
            )
            .options(
                selectinload(SceneMap.annotations),
                selectinload(SceneMap.paths),
                selectinload(SceneMap.objects),
            )
        )
        result = await db.execute(stmt)
        map_obj = result.unique().scalar_one_or_none()
        if not map_obj:
            raise NotFoundError(msg=f"场景地图 {map_id} 不存在")
        return map_obj

    @staticmethod
    async def save_editor_data(
        db: AsyncSession, map_id: int, save_request: EditorSaveRequest
    ) -> None:
        """批量保存编辑器数据"""

        # 校验地图存在
        stmt = select(SceneMap).where(
            SceneMap.id == map_id,
            SceneMap.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        map_obj = result.scalar_one_or_none()
        if not map_obj:
            raise NotFoundError(msg=f"场景地图 {map_id} 不存在")

        # 校验至少1个导航点
        nav_types = {"navigation", "导航点"}
        has_nav = any(a.type in nav_types for a in save_request.annotations)
        if not has_nav and save_request.annotations:
            raise ValidationError(msg="地图至少需要包含1个导航点")

        # 删除已删除的标注
        if save_request.deleted_annotation_ids:
            stmt = select(SceneMapAnnotation).where(
                SceneMapAnnotation.id.in_(save_request.deleted_annotation_ids),
                SceneMapAnnotation.map_id == map_id,
            )
            result = await db.execute(stmt)
            for ann in result.scalars().all():
                await db.delete(ann)

        # 删除已删除的路径
        if save_request.deleted_path_ids:
            stmt = select(SceneMapPath).where(
                SceneMapPath.id.in_(save_request.deleted_path_ids),
                SceneMapPath.map_id == map_id,
            )
            result = await db.execute(stmt)
            for path in result.scalars().all():
                await db.delete(path)

        # 删除已删除的物体
        if save_request.deleted_object_ids:
            stmt = select(SceneMapObject).where(
                SceneMapObject.id.in_(save_request.deleted_object_ids),
                SceneMapObject.map_id == map_id,
            )
            result = await db.execute(stmt)
            for obj in result.scalars().all():
                await db.delete(obj)

        # 新建/更新标注
        for item in save_request.annotations:
            if item.id:
                stmt = select(SceneMapAnnotation).where(
                    SceneMapAnnotation.id == item.id,
                    SceneMapAnnotation.map_id == map_id,
                )
                result = await db.execute(stmt)
                ann = result.scalar_one_or_none()
                if ann:
                    ann.x = item.x
                    ann.y = item.y
                    ann.name = item.name
                    ann.angle = item.angle
                    ann.type = item.type
            else:
                ann = SceneMapAnnotation(
                    map_id=map_id,
                    x=item.x,
                    y=item.y,
                    name=item.name,
                    angle=item.angle,
                    type=item.type,
                )
                db.add(ann)

        # 新建/更新路径
        for item in save_request.paths:
            if item.id:
                stmt = select(SceneMapPath).where(
                    SceneMapPath.id == item.id,
                    SceneMapPath.map_id == map_id,
                )
                result = await db.execute(stmt)
                path = result.scalar_one_or_none()
                if path:
                    path.start_annotation_id = item.start_annotation_id
                    path.end_annotation_id = item.end_annotation_id
                    path.name = item.name
                    path.points = item.points
            else:
                path = SceneMapPath(
                    map_id=map_id,
                    start_annotation_id=item.start_annotation_id,
                    end_annotation_id=item.end_annotation_id,
                    name=item.name,
                    points=item.points,
                )
                db.add(path)

        # 新建/更新物体
        for item in save_request.objects:
            if item.id:
                stmt = select(SceneMapObject).where(
                    SceneMapObject.id == item.id,
                    SceneMapObject.map_id == map_id,
                )
                result = await db.execute(stmt)
                obj = result.scalar_one_or_none()
                if obj:
                    obj.type = item.type
                    obj.x = item.x
                    obj.y = item.y
                    obj.width = item.width
                    obj.height = item.height
                    obj.points = item.points
            else:
                obj = SceneMapObject(
                    map_id=map_id,
                    type=item.type,
                    x=item.x,
                    y=item.y,
                    width=item.width,
                    height=item.height,
                    points=item.points,
                )
                db.add(obj)

        await db.flush()
