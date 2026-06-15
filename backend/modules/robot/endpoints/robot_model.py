#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人型号管理相关接口
"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    response_base,
)
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.robot.services.robot_model_service import RobotModelService
from modules.robot.schemas.robot_model import (
    RobotModelCreate,
    RobotModelUpdate,
    RobotModelQueryParams,
    RobotModelResponseData,
)

logger = logging.getLogger(__name__)

robot_model_router = APIRouter(
    prefix="/model", tags=["机器人型号管理"], dependencies=[Depends(current_user)]
)


@robot_model_router.get(
    "/list",
    response_model=ResponsePageModel[RobotModelResponseData],
    dependencies=[Depends(require_permission("robot:model:list"))],
)
async def get_robot_model_list(
    query_params: RobotModelQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取机器人型号列表（分页）
    """
    try:
        logger.info("获取机器人型号列表接口被调用")

        query = RobotModelService.build_query(query_params)

        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=RobotModelResponseData,
        )

        logger.info("获取机器人型号列表接口成功，共 %d 条记录", page_data.total)
        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取机器人型号列表接口失败: %s", str(e), exc_info=True)
        raise


@robot_model_router.get(
    "/all",
    response_model=ResponseModel[List[RobotModelResponseData]],
)
async def get_all_robot_models(
    db: AsyncSession = Depends(get_session),
):
    """
    获取所有已启用的机器人型号（不分页，用于下拉选择）
    """
    try:
        logger.info("获取所有机器人型号接口被调用")

        records = await RobotModelService.get_all(db)
        response_list = [RobotModelResponseData.model_validate(r) for r in records]

        logger.info("获取所有机器人型号接口成功，共 %d 条记录", len(response_list))
        return response_base.success(data=response_list)

    except Exception as e:
        logger.error("获取所有机器人型号接口失败: %s", str(e), exc_info=True)
        raise


@robot_model_router.get(
    "/{model_id}",
    response_model=ResponseModel[RobotModelResponseData],
)
async def get_robot_model(
    model_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取单个机器人型号
    """
    try:
        logger.info("获取机器人型号详情接口被调用，型号ID: %d", model_id)

        model_obj = await RobotModelService.get(db, model_id)
        response_data = RobotModelResponseData.model_validate(model_obj)

        logger.info("获取机器人型号详情接口成功，型号ID: %d", model_id)
        return response_base.success(data=response_data)

    except Exception as e:
        logger.error("获取机器人型号详情接口失败: %s", str(e), exc_info=True)
        raise


@robot_model_router.post(
    "/add",
    response_model=ResponseModel[RobotModelResponseData],
    dependencies=[Depends(require_permission("robot:model:add"))],
)
@log_operation(module="robot_model", action="create", description="创建机器人型号")
async def create_robot_model(
    request: Request,
    model_in: RobotModelCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建机器人型号
    """
    try:
        logger.info("创建机器人型号接口被调用")

        model_obj = await RobotModelService.create(db, model_in)
        response_data = RobotModelResponseData.model_validate(model_obj)

        logger.info("创建机器人型号接口成功，型号ID: %d", model_obj.id)
        return response_base.success(data=response_data, msg="创建成功")

    except Exception as e:
        logger.error("创建机器人型号接口失败: %s", str(e), exc_info=True)
        raise


@robot_model_router.put(
    "/{model_id}",
    response_model=ResponseModel[RobotModelResponseData],
    dependencies=[Depends(require_permission("robot:model:edit"))],
)
@log_operation(module="robot_model", action="update", description="更新机器人型号")
async def update_robot_model(
    model_id: int,
    request: Request,
    model_in: RobotModelUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新机器人型号
    """
    try:
        logger.info("更新机器人型号接口被调用，型号ID: %d", model_id)

        model_obj = await RobotModelService.update(db, model_id, model_in)
        response_data = RobotModelResponseData.model_validate(model_obj)

        logger.info("更新机器人型号接口成功，型号ID: %d", model_id)
        return response_base.success(data=response_data, msg="更新成功")

    except Exception as e:
        logger.error("更新机器人型号接口失败: %s", str(e), exc_info=True)
        raise


@robot_model_router.delete(
    "/{model_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("robot:model:delete"))],
)
@log_operation(module="robot_model", action="delete", description="删除机器人型号")
async def delete_robot_model(
    model_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除机器人型号
    """
    try:
        logger.info("删除机器人型号接口被调用，型号ID: %d", model_id)

        await RobotModelService.delete(db, model_id)

        logger.info("删除机器人型号接口成功，型号ID: %d", model_id)
        return response_base.success(msg="删除成功")

    except Exception as e:
        logger.error("删除机器人型号接口失败: %s", str(e), exc_info=True)
        raise
