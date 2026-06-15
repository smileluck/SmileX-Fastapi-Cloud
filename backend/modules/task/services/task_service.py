#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务管理服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, Select
from sqlalchemy.orm import noload, selectinload
from typing import List

from database.models.business.task import Task, task_robot_association
from database.models.business.task_point import TaskPoint
from database.models.business.robot import Robot
from core.exception.errors import NotFoundError
from modules.task.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskQueryParams,
)

logger = logging.getLogger(__name__)


class TaskService:
    """任务管理服务类"""

    @staticmethod
    def build_query(query_params: TaskQueryParams) -> Select:
        """构建任务查询"""
        base_query = select(Task).options(
            noload(Task.points),
            noload(Task.executions),
            noload(Task.robots),
        )

        conditions = [Task.deleted_at.is_(None)]
        if query_params.name:
            conditions.append(Task.name.contains(query_params.name))
        if query_params.task_type:
            conditions.append(Task.task_type == query_params.task_type)
        if query_params.enabled is not None:
            conditions.append(Task.enabled == query_params.enabled)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(Task.id.desc())
        return base_query

    @staticmethod
    async def get(db: AsyncSession, task_id: int) -> Task:
        """获取单个任务"""
        result = await db.execute(
            select(Task)
            .options(noload(Task.executions))
            .where(Task.id == task_id)
            .where(Task.deleted_at.is_(None))
        )
        task_obj = result.scalar_one_or_none()
        if not task_obj:
            raise NotFoundError(msg=f"任务 {task_id} 不存在")
        return task_obj

    @staticmethod
    async def get_with_relations(db: AsyncSession, task_id: int) -> Task:
        """获取任务（含点位和机器人）"""
        result = await db.execute(
            select(Task)
            .options(
                selectinload(Task.points),
                selectinload(Task.robots),
            )
            .where(Task.id == task_id)
            .where(Task.deleted_at.is_(None))
        )
        task_obj = result.unique().scalar_one_or_none()
        if not task_obj:
            raise NotFoundError(msg=f"任务 {task_id} 不存在")
        return task_obj

    @staticmethod
    async def create(db: AsyncSession, task_in: TaskCreate) -> Task:
        """创建任务"""
        try:
            # 验证机器人存在
            robot_result = await db.execute(
                select(Robot).where(
                    Robot.id.in_(task_in.robot_ids),
                    Robot.deleted_at.is_(None),
                )
            )
            robots = robot_result.scalars().all()
            if len(robots) != len(task_in.robot_ids):
                raise NotFoundError(msg="部分机器人不存在")

            # 巡逻任务校验机器人场景约束
            if task_in.task_type == 'patrol':
                robot_map_ids = set(r.map_id for r in robots)
                if None in robot_map_ids:
                    raise NotFoundError(msg="巡逻任务的机器人必须已分配场景")
                if len(robot_map_ids) > 1:
                    raise NotFoundError(msg="巡逻任务不能选择不同场景的机器人")

            # 创建任务主记录
            task_obj = Task(
                name=task_in.name,
                task_type=task_in.task_type,
                broadcast_text=task_in.broadcast_text,
                broadcast_count=task_in.broadcast_count,
                schedule_enabled=task_in.schedule_enabled,
                schedule_date=task_in.schedule_date,
                schedule_start_time=task_in.schedule_start_time,
                schedule_repeat_cycle=task_in.schedule_repeat_cycle,
            )
            db.add(task_obj)
            await db.flush()

            # 创建巡逻点位
            if task_in.points:
                for pt in task_in.points:
                    point_obj = TaskPoint(
                        task_id=task_obj.id,
                        sort_order=pt.sort_order,
                        point_name=pt.point_name,
                        annotation_id=pt.annotation_id,
                        action=pt.action,
                        voice_text=pt.voice_text,
                    )
                    db.add(point_obj)

            # 创建机器人关联
            for robot_id in task_in.robot_ids:
                await db.execute(
                    task_robot_association.insert().values(
                        task_id=task_obj.id, robot_id=robot_id
                    )
                )

            await db.commit()
            await db.refresh(task_obj)
            return task_obj

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("创建任务失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update(db: AsyncSession, task_id: int, task_in: TaskUpdate) -> Task:
        """更新任务"""
        try:
            task_obj = await TaskService.get(db, task_id)

            # 更新基础字段
            update_data = task_in.model_dump(exclude_unset=True, exclude={"points", "robot_ids"})
            for field, value in update_data.items():
                setattr(task_obj, field, value)

            # 更新巡逻点位（全量替换）
            if task_in.points is not None:
                await db.execute(
                    TaskPoint.__table__.delete().where(TaskPoint.task_id == task_id)
                )
                for pt in task_in.points:
                    point_obj = TaskPoint(
                        task_id=task_id,
                        sort_order=pt.sort_order,
                        point_name=pt.point_name,
                        annotation_id=pt.annotation_id,
                        action=pt.action,
                        voice_text=pt.voice_text,
                    )
                    db.add(point_obj)

            # 更新机器人关联（全量替换）
            if task_in.robot_ids is not None:
                # 验证机器人存在
                robot_result = await db.execute(
                    select(Robot).where(
                        Robot.id.in_(task_in.robot_ids),
                        Robot.deleted_at.is_(None),
                    )
                )
                robots = robot_result.scalars().all()
                if len(robots) != len(task_in.robot_ids):
                    raise NotFoundError(msg="部分机器人不存在")

                # 巡逻任务校验机器人场景约束
                effective_type = task_in.task_type or task_obj.task_type
                if effective_type == 'patrol':
                    robot_map_ids = set(r.map_id for r in robots)
                    if None in robot_map_ids:
                        raise NotFoundError(msg="巡逻任务的机器人必须已分配场景")
                    if len(robot_map_ids) > 1:
                        raise NotFoundError(msg="巡逻任务不能选择不同场景的机器人")

                await db.execute(
                    task_robot_association.delete().where(
                        task_robot_association.c.task_id == task_id
                    )
                )
                for robot_id in task_in.robot_ids:
                    await db.execute(
                        task_robot_association.insert().values(
                            task_id=task_id, robot_id=robot_id
                        )
                    )

            await db.commit()
            await db.refresh(task_obj)
            return task_obj

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新任务失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete(db: AsyncSession, task_id: int) -> bool:
        """删除任务（软删除）"""
        try:
            task_obj = await TaskService.get(db, task_id)
            task_obj.soft_delete()
            await db.commit()
            return True
        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除任务失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def toggle_enabled(db: AsyncSession, task_id: int, enabled: bool) -> Task:
        """切换启用/禁用"""
        try:
            task_obj = await TaskService.get(db, task_id)
            task_obj.enabled = enabled
            await db.commit()
            await db.refresh(task_obj)
            return task_obj
        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("切换任务启用状态失败: %s", str(e), exc_info=True)
            raise
