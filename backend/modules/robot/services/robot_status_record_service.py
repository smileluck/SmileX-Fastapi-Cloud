#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人状态记录管理服务
处理机器人状态记录相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, Select
from sqlalchemy.orm import noload
from typing import List, Tuple, Optional

from database.models.business.robot_status_record import RobotStatusRecord
from database.models.business.robot import Robot
from core.exception.errors import NotFoundError
from modules.robot.schemas.robot_status_record import RobotStatusRecordQueryParams

logger = logging.getLogger(__name__)


class RobotStatusRecordService:
    """
    机器人状态记录管理服务类
    """

    @staticmethod
    def build_query(query_params: RobotStatusRecordQueryParams) -> Select:
        """
        构建机器人状态记录查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        base_query = select(RobotStatusRecord).options(
            noload(RobotStatusRecord.robot)
        )

        conditions = [RobotStatusRecord.deleted_at.is_(None)]
        if query_params.robot_id:
            conditions.append(RobotStatusRecord.robot_id == query_params.robot_id)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(RobotStatusRecord.id.desc())

        return base_query

    @staticmethod
    async def get_list(
        db: AsyncSession, query_params: RobotStatusRecordQueryParams
    ) -> Tuple[List[RobotStatusRecord], int]:
        """
        获取机器人状态记录列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (状态记录列表, 总数)
        """
        try:
            logger.debug(
                "获取机器人状态记录列表，查询参数: %s",
                query_params.model_dump(exclude_none=True),
            )

            # 先验证机器人是否存在
            robot_result = await db.execute(
                select(Robot)
                .where(Robot.id == query_params.robot_id)
                .where(Robot.deleted_at.is_(None))
            )
            if not robot_result.scalar_one_or_none():
                raise NotFoundError(
                    msg=f"机器人 {query_params.robot_id} 不存在"
                )

            base_query = RobotStatusRecordService.build_query(query_params)

            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            records = result.scalars().all()

            logger.debug("获取机器人状态记录列表成功，共 %d 条记录", total)
            return records, total

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取机器人状态记录列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_latest(
        db: AsyncSession, robot_id: int
    ) -> Optional[RobotStatusRecord]:
        """
        获取机器人最新的状态记录

        Args:
            db: 数据库会话
            robot_id: 机器人ID

        Returns:
            最新的状态记录，不存在则返回 None

        Raises:
            NotFoundError: 机器人不存在
        """
        try:
            logger.debug("获取机器人最新状态记录，机器人ID: %d", robot_id)

            # 先验证机器人是否存在
            robot_result = await db.execute(
                select(Robot)
                .where(Robot.id == robot_id)
                .where(Robot.deleted_at.is_(None))
            )
            if not robot_result.scalar_one_or_none():
                raise NotFoundError(msg=f"机器人 {robot_id} 不存在")

            result = await db.execute(
                select(RobotStatusRecord)
                .options(noload(RobotStatusRecord.robot))
                .where(RobotStatusRecord.robot_id == robot_id)
                .where(RobotStatusRecord.deleted_at.is_(None))
                .order_by(RobotStatusRecord.id.desc())
                .limit(1)
            )
            record = result.scalar_one_or_none()

            logger.debug(
                "获取机器人最新状态记录成功，机器人ID: %d，%s",
                robot_id,
                "有记录" if record else "无记录",
            )
            return record

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "获取机器人最新状态记录失败: %s", str(e), exc_info=True
            )
            raise
