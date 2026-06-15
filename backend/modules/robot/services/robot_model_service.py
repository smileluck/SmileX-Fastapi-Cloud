#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人型号管理服务
处理机器人型号相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, Select
from sqlalchemy.orm import noload
from typing import List, Tuple

from database.models.business.robot_model import RobotModel
from database.models.business.robot import Robot
from core.exception.errors import NotFoundError, ConflictError
from modules.robot.schemas.robot_model import (
    RobotModelCreate,
    RobotModelUpdate,
    RobotModelQueryParams,
)

logger = logging.getLogger(__name__)


class RobotModelService:
    """
    机器人型号管理服务类
    """

    @staticmethod
    def build_query(query_params: RobotModelQueryParams) -> Select:
        """
        构建机器人型号查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        base_query = select(RobotModel).options(noload(RobotModel.robots))

        conditions = [RobotModel.deleted_at.is_(None)]
        if query_params.name:
            conditions.append(RobotModel.name.contains(query_params.name))
        if query_params.brand:
            conditions.append(RobotModel.brand.contains(query_params.brand))
        if query_params.status is not None:
            conditions.append(RobotModel.status == query_params.status)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(RobotModel.sort.asc(), RobotModel.id.desc())

        return base_query

    @staticmethod
    async def get_list(
        db: AsyncSession, query_params: RobotModelQueryParams
    ) -> Tuple[List[RobotModel], int]:
        """
        获取机器人型号列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (型号列表, 总数)
        """
        try:
            logger.debug(
                "获取机器人型号列表，查询参数: %s",
                query_params.model_dump(exclude_none=True),
            )

            base_query = RobotModelService.build_query(query_params)

            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            records = result.scalars().all()

            logger.debug("获取机器人型号列表成功，共 %d 条记录", total)
            return records, total

        except Exception as e:
            logger.error("获取机器人型号列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_all(db: AsyncSession) -> List[RobotModel]:
        """
        获取所有已启用的机器人型号（不分页，用于下拉选择）

        Args:
            db: 数据库会话

        Returns:
            型号列表
        """
        try:
            logger.debug("获取所有已启用的机器人型号")

            query = (
                select(RobotModel)
                .options(noload(RobotModel.robots))
                .where(RobotModel.deleted_at.is_(None))
                .where(RobotModel.status == True)
                .order_by(RobotModel.sort.asc(), RobotModel.id.desc())
            )

            result = await db.execute(query)
            records = result.scalars().all()

            logger.debug("获取所有已启用的机器人型号成功，共 %d 条记录", len(records))
            return records

        except Exception as e:
            logger.error("获取所有已启用的机器人型号失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get(db: AsyncSession, model_id: int) -> RobotModel:
        """
        获取单个机器人型号

        Args:
            db: 数据库会话
            model_id: 型号ID

        Returns:
            型号对象

        Raises:
            NotFoundError: 型号不存在
        """
        try:
            logger.debug("获取机器人型号详情，型号ID: %d", model_id)

            result = await db.execute(
                select(RobotModel)
                .options(noload(RobotModel.robots))
                .where(RobotModel.id == model_id)
                .where(RobotModel.deleted_at.is_(None))
            )
            model_obj = result.scalar_one_or_none()

            if not model_obj:
                logger.warning("机器人型号不存在，型号ID: %d", model_id)
                raise NotFoundError(msg=f"机器人型号 {model_id} 不存在")

            logger.debug("获取机器人型号详情成功，型号ID: %d", model_id)
            return model_obj

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取机器人型号详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def create(db: AsyncSession, model_in: RobotModelCreate) -> RobotModel:
        """
        创建机器人型号

        Args:
            db: 数据库会话
            model_in: 型号创建请求

        Returns:
            创建后的型号对象
        """
        try:
            logger.info(
                "创建机器人型号，请求数据: %s",
                model_in.model_dump(exclude_none=True),
            )

            model_obj = RobotModel(
                name=model_in.name,
                brand=model_in.brand,
                model=model_in.model,
                status=model_in.status,
                sort=model_in.sort,
            )

            db.add(model_obj)
            await db.commit()
            await db.refresh(model_obj)

            logger.info("创建机器人型号成功，型号ID: %d", model_obj.id)
            return model_obj

        except Exception as e:
            await db.rollback()
            logger.error("创建机器人型号失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update(
        db: AsyncSession, model_id: int, model_in: RobotModelUpdate
    ) -> RobotModel:
        """
        更新机器人型号

        Args:
            db: 数据库会话
            model_id: 型号ID
            model_in: 型号更新请求

        Returns:
            更新后的型号对象

        Raises:
            NotFoundError: 型号不存在
        """
        try:
            logger.info(
                "更新机器人型号，型号ID: %d，请求数据: %s",
                model_id,
                model_in.model_dump(exclude_none=True),
            )

            result = await db.execute(
                select(RobotModel)
                .options(noload(RobotModel.robots))
                .where(RobotModel.id == model_id)
                .where(RobotModel.deleted_at.is_(None))
            )
            existing = result.scalar_one_or_none()

            if not existing:
                logger.warning("机器人型号不存在，型号ID: %d", model_id)
                raise NotFoundError(msg=f"机器人型号 {model_id} 不存在")

            update_data = model_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing, field, value)

            await db.commit()
            await db.refresh(existing)

            logger.info("更新机器人型号成功，型号ID: %d", model_id)
            return existing

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新机器人型号失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete(db: AsyncSession, model_id: int) -> bool:
        """
        删除机器人型号

        Args:
            db: 数据库会话
            model_id: 型号ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 型号不存在
            ConflictError: 型号下存在关联机器人
        """
        try:
            logger.info("删除机器人型号，型号ID: %d", model_id)

            result = await db.execute(
                select(RobotModel)
                .options(noload(RobotModel.robots))
                .where(RobotModel.id == model_id)
                .where(RobotModel.deleted_at.is_(None))
            )
            model_obj = result.scalar_one_or_none()

            if not model_obj:
                logger.warning("机器人型号不存在，型号ID: %d", model_id)
                raise NotFoundError(msg=f"机器人型号 {model_id} 不存在")

            # 检查是否有关联的机器人
            robot_count_result = await db.execute(
                select(func.count()).select_from(Robot).where(
                    and_(
                        Robot.model_id == model_id,
                        Robot.deleted_at.is_(None),
                    )
                )
            )
            robot_count = robot_count_result.scalar() or 0
            if robot_count > 0:
                logger.warning(
                    "机器人型号下存在关联机器人，型号ID: %d，数量: %d",
                    model_id,
                    robot_count,
                )
                raise ConflictError(msg=f"该型号下存在 {robot_count} 个关联机器人，无法删除")

            await db.delete(model_obj)
            await db.commit()

            logger.info("删除机器人型号成功，型号ID: %d", model_id)
            return True

        except (NotFoundError, ConflictError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除机器人型号失败: %s", str(e), exc_info=True)
            raise
