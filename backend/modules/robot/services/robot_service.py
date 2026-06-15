#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人管理服务
处理机器人相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, Select
from sqlalchemy.orm import noload
from typing import List, Tuple

from database.models.business.robot import Robot, RobotStatus
from database.models.business.robot_status_record import RobotStatusRecord
from database.models.business.robot_model import RobotModel
from database.models.business.scene_map import SceneMap
from core.exception.errors import NotFoundError, ConflictError
from modules.robot.schemas.robot import (
    RobotCreate,
    RobotUpdate,
    RobotQueryParams,
)
from modules.robot.services.robot_schema_service import RobotSchemaService

logger = logging.getLogger(__name__)


class RobotService:
    """
    机器人管理服务类
    """

    @staticmethod
    def build_query(query_params: RobotQueryParams) -> Select:
        """
        构建机器人查询对象（关联 RobotModel 获取 model_name）

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        base_query = (
            select(Robot)
            .options(noload(Robot.status_record))
        )

        conditions = [Robot.deleted_at.is_(None)]
        if query_params.name:
            conditions.append(Robot.name.contains(query_params.name))
        if query_params.serial_number:
            conditions.append(Robot.serial_number.contains(query_params.serial_number))
        if query_params.status:
            conditions.append(Robot.status == RobotStatus(query_params.status))
        if query_params.model_id:
            conditions.append(Robot.model_id == query_params.model_id)
        if query_params.map_id:
            conditions.append(Robot.map_id == query_params.map_id)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(Robot.id.desc())

        return base_query

    @staticmethod
    async def get_list(
        db: AsyncSession, query_params: RobotQueryParams
    ) -> Tuple[List[Robot], int]:
        """
        获取机器人列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (机器人列表, 总数)
        """
        try:
            await RobotSchemaService.ensure_robot_map_binding(db)
            logger.debug(
                "获取机器人列表，查询参数: %s",
                query_params.model_dump(exclude_none=True),
            )

            base_query = RobotService.build_query(query_params)

            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            records = result.scalars().all()

            logger.debug("获取机器人列表成功，共 %d 条记录", total)
            return records, total

        except Exception as e:
            logger.error("获取机器人列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get(db: AsyncSession, robot_id: int) -> Robot:
        """
        获取单个机器人

        Args:
            db: 数据库会话
            robot_id: 机器人ID

        Returns:
            机器人对象

        Raises:
            NotFoundError: 机器人不存在
        """
        try:
            logger.debug("获取机器人详情，机器人ID: %d", robot_id)

            result = await db.execute(
                select(Robot)
                .options(noload(Robot.status_record))
                .where(Robot.id == robot_id)
                .where(Robot.deleted_at.is_(None))
            )
            robot_obj = result.scalar_one_or_none()

            if not robot_obj:
                logger.warning("机器人不存在，机器人ID: %d", robot_id)
                raise NotFoundError(msg=f"机器人 {robot_id} 不存在")

            logger.debug("获取机器人详情成功，机器人ID: %d", robot_id)
            return robot_obj

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取机器人详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def create(db: AsyncSession, robot_in: RobotCreate) -> Robot:
        """
        创建机器人

        Args:
            db: 数据库会话
            robot_in: 机器人创建请求

        Returns:
            创建后的机器人对象

        Raises:
            NotFoundError: 关联型号不存在
            ConflictError: 序列号已存在
        """
        try:
            logger.info(
                "创建机器人，请求数据: %s",
                robot_in.model_dump(exclude_none=True),
            )

            # 检查关联型号是否存在
            model_result = await db.execute(
                select(RobotModel)
                .where(RobotModel.id == robot_in.model_id)
                .where(RobotModel.deleted_at.is_(None))
            )
            if not model_result.scalar_one_or_none():
                logger.warning("关联型号不存在，型号ID: %d", robot_in.model_id)
                raise NotFoundError(msg=f"机器人型号 {robot_in.model_id} 不存在")

            if robot_in.map_id is not None:
                map_result = await db.execute(
                    select(SceneMap)
                    .where(SceneMap.id == robot_in.map_id)
                    .where(SceneMap.deleted_at.is_(None))
                )
                if not map_result.scalar_one_or_none():
                    raise NotFoundError(msg=f"场景地图 {robot_in.map_id} 不存在")

            # 检查序列号是否已存在
            sn_result = await db.execute(
                select(Robot)
                .where(Robot.serial_number == robot_in.serial_number)
                .where(Robot.deleted_at.is_(None))
            )
            if sn_result.scalar_one_or_none():
                logger.warning("序列号已存在: %s", robot_in.serial_number)
                raise ConflictError(msg=f"序列号 {robot_in.serial_number} 已存在")

            robot_obj = Robot(
                name=robot_in.name,
                model_id=robot_in.model_id,
                serial_number=robot_in.serial_number,
                map_id=robot_in.map_id,
                status=RobotStatus(robot_in.status),
            )

            db.add(robot_obj)
            await db.flush()

            status_record = RobotStatusRecord(robot_id=robot_obj.id)
            db.add(status_record)

            await db.commit()
            await db.refresh(robot_obj)

            logger.info("创建机器人成功，机器人ID: %d", robot_obj.id)
            return robot_obj

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("创建机器人失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update(
        db: AsyncSession, robot_id: int, robot_in: RobotUpdate
    ) -> Robot:
        """
        更新机器人

        Args:
            db: 数据库会话
            robot_id: 机器人ID
            robot_in: 机器人更新请求

        Returns:
            更新后的机器人对象

        Raises:
            NotFoundError: 机器人不存在
            ConflictError: 序列号已被其他机器人占用
        """
        try:
            logger.info(
                "更新机器人，机器人ID: %d，请求数据: %s",
                robot_id,
                robot_in.model_dump(exclude_none=True),
            )

            result = await db.execute(
                select(Robot)
                .options(noload(Robot.status_record))
                .where(Robot.id == robot_id)
                .where(Robot.deleted_at.is_(None))
            )
            existing = result.scalar_one_or_none()

            if not existing:
                logger.warning("机器人不存在，机器人ID: %d", robot_id)
                raise NotFoundError(msg=f"机器人 {robot_id} 不存在")

            # 如果更新序列号，检查唯一性
            update_data = robot_in.model_dump(exclude_unset=True)
            if "serial_number" in update_data and update_data["serial_number"] != existing.serial_number:
                sn_result = await db.execute(
                    select(Robot)
                    .where(Robot.serial_number == update_data["serial_number"])
                    .where(Robot.deleted_at.is_(None))
                )
                if sn_result.scalar_one_or_none():
                    logger.warning(
                        "序列号已被占用: %s", update_data["serial_number"]
                    )
                    raise ConflictError(
                        msg=f"序列号 {update_data['serial_number']} 已存在"
                    )

            # 如果更新型号，检查型号是否存在
            if "model_id" in update_data:
                model_result = await db.execute(
                    select(RobotModel)
                    .where(RobotModel.id == update_data["model_id"])
                    .where(RobotModel.deleted_at.is_(None))
                )
                if not model_result.scalar_one_or_none():
                    raise NotFoundError(
                        msg=f"机器人型号 {update_data['model_id']} 不存在"
                    )

            if "map_id" in update_data and update_data["map_id"] is not None:
                map_result = await db.execute(
                    select(SceneMap)
                    .where(SceneMap.id == update_data["map_id"])
                    .where(SceneMap.deleted_at.is_(None))
                )
                if not map_result.scalar_one_or_none():
                    raise NotFoundError(
                        msg=f"场景地图 {update_data['map_id']} 不存在"
                    )

            # 如果更新状态，转换枚举
            if "status" in update_data and update_data["status"] is not None:
                update_data["status"] = RobotStatus(update_data["status"])

            for field, value in update_data.items():
                setattr(existing, field, value)

            await db.commit()
            await db.refresh(existing)

            logger.info("更新机器人成功，机器人ID: %d", robot_id)
            return existing

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新机器人失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete(db: AsyncSession, robot_id: int) -> bool:
        """
        删除机器人

        Args:
            db: 数据库会话
            robot_id: 机器人ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 机器人不存在
        """
        try:
            logger.info("删除机器人，机器人ID: %d", robot_id)

            result = await db.execute(
                select(Robot)
                .options(noload(Robot.status_record))
                .where(Robot.id == robot_id)
                .where(Robot.deleted_at.is_(None))
            )
            robot_obj = result.scalar_one_or_none()

            if not robot_obj:
                logger.warning("机器人不存在，机器人ID: %d", robot_id)
                raise NotFoundError(msg=f"机器人 {robot_id} 不存在")

            await db.delete(robot_obj)
            await db.commit()

            logger.info("删除机器人成功，机器人ID: %d", robot_id)
            return True

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除机器人失败: %s", str(e), exc_info=True)
            raise
