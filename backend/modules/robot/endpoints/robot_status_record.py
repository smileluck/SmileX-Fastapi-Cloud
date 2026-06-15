#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人状态记录相关接口
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from database.db_manager import get_session
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    response_base,
)
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission

from modules.robot.services.robot_status_record_service import RobotStatusRecordService
from modules.robot.schemas.robot_status_record import (
    RobotStatusRecordQueryParams,
    RobotStatusRecordResponseData,
)

logger = logging.getLogger(__name__)

robot_status_record_router = APIRouter(
    prefix="/manage", tags=["机器人状态记录"], dependencies=[Depends(current_user)]
)


@robot_status_record_router.get(
    "/{robot_id}/status/list",
    response_model=ResponsePageModel[RobotStatusRecordResponseData],
    dependencies=[Depends(require_permission("robot:manage:list"))],
)
async def get_robot_status_record_list(
    robot_id: int,
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取机器人状态记录列表（分页）
    """
    try:
        logger.info("获取机器人状态记录列表接口被调用，机器人ID: %d", robot_id)

        query_params = RobotStatusRecordQueryParams(robot_id=robot_id)
        query = RobotStatusRecordService.build_query(query_params)

        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=RobotStatusRecordResponseData,
        )

        logger.info(
            "获取机器人状态记录列表接口成功，机器人ID: %d，共 %d 条记录",
            robot_id,
            page_data.total,
        )
        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取机器人状态记录列表接口失败: %s", str(e), exc_info=True)
        raise


@robot_status_record_router.get(
    "/{robot_id}/status/latest",
    response_model=ResponseModel[Optional[RobotStatusRecordResponseData]],
)
async def get_robot_status_latest(
    robot_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取机器人最新状态记录
    """
    try:
        logger.info("获取机器人最新状态记录接口被调用，机器人ID: %d", robot_id)

        record = await RobotStatusRecordService.get_latest(db, robot_id)

        if record:
            response_data = RobotStatusRecordResponseData.model_validate(record)
            logger.info("获取机器人最新状态记录接口成功，机器人ID: %d", robot_id)
            return response_base.success(data=response_data)
        else:
            logger.info("机器人无状态记录，机器人ID: %d", robot_id)
            return response_base.success(data=None, msg="暂无状态记录")

    except Exception as e:
        logger.error("获取机器人最新状态记录接口失败: %s", str(e), exc_info=True)
        raise
