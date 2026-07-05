#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开放API调用日志相关接口
"""
import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from database.models.sys.user import SysUser
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.schemas.sys.openapi_log import (
    OpenapiLogQueryParams,
    OpenapiLogResponse,
)
from modules.admin.services.sys import OpenapiLogService

logger = logging.getLogger(__name__)

openapi_log_router = APIRouter(prefix="/openapi-log", tags=["系统管理/调用日志"])


@openapi_log_router.get(
    "/list",
    response_model=ResponsePageModel[OpenapiLogResponse],
    summary="获取开放API调用日志列表",
    dependencies=[Depends(require_permission("sys:openapi-log:list"))],
)
async def get_openapi_log_list(
    query_params: OpenapiLogQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """分页查询开放API调用日志"""
    query = OpenapiLogService.build_openapi_log_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=OpenapiLogResponse,
    )
    return ResponsePageModel[OpenapiLogResponse](data=page_data)


@openapi_log_router.get(
    "/{log_id}",
    response_model=ResponseModel[OpenapiLogResponse],
    summary="获取开放API调用日志详情",
    dependencies=[Depends(require_permission("sys:openapi-log:list"))],
)
async def get_openapi_log(
    log_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单条开放API调用日志"""
    log = await OpenapiLogService.get_log(db, log_id)
    return ResponseModel(data=OpenapiLogResponse.model_validate(log))


@openapi_log_router.delete(
    "/batch",
    response_model=ResponseModel,
    summary="批量删除开放API调用日志",
    dependencies=[Depends(require_permission("sys:openapi-log:delete"))],
)
async def batch_delete_openapi_logs(
    log_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """批量删除开放API调用日志"""
    count = await OpenapiLogService.batch_delete_logs(db, log_ids)
    return ResponseModel(msg=f"批量删除成功，共删除 {count} 条", data={"delete_count": count})


@openapi_log_router.delete(
    "/{log_id}",
    response_model=ResponseModel,
    summary="删除单条开放API调用日志",
    dependencies=[Depends(require_permission("sys:openapi-log:delete"))],
)
async def delete_openapi_log(
    log_id: int,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """删除单条开放API调用日志"""
    await OpenapiLogService.get_log(db, log_id)
    await OpenapiLogService.batch_delete_logs(db, [log_id])
    return ResponseModel(msg="删除成功")
