#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
操作日志管理接口
"""
import io
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.i18n import t
from core.response import ResponseModel, ResponsePageModel, response_base
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.utils.excel_export import build_excel_bytes, SYNC_EXPORT_MAX_ROWS
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from modules.admin.exports import get_export_config
from database.models.sys.user import SysUser
from modules.admin.services.sys.operation_log_service import OperationLogService
from modules.admin.schemas.sys.operation_log import (
    OperationLogQueryParams,
    OperationLogResponse,
    OperationLogDetailResponse,
)

logger = logging.getLogger(__name__)

operation_log_router = APIRouter(prefix="/operation-log", tags=["系统管理/操作日志"])


@operation_log_router.get(
    "/list",
    response_model=ResponsePageModel[OperationLogResponse],
    summary="获取操作日志列表",
    dependencies=[Depends(require_permission("sys:oplog:list"))],
)
async def get_log_list(
    query_params: OperationLogQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询操作日志列表"""
    query = OperationLogService.build_operation_log_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=OperationLogResponse,
    )
    return response_base.page(data=page_data)


@operation_log_router.get("/export", summary="导出操作日志 Excel")
async def export_operation_logs(
    module: str | None = Query(None, description="操作模块"),
    action: str | None = Query(None, description="操作类型"),
    user_id: int | None = Query(None, description="操作人ID"),
    username: str | None = Query(None, description="操作人用户名"),
    start_time: str | None = Query(None, description="开始时间"),
    end_time: str | None = Query(None, description="结束时间"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """导出操作日志为 Excel 文件"""
    query_params = OperationLogQueryParams(
        module=module,
        action=action,
        user_id=user_id,
        username=username,
        start_time=start_time,
        end_time=end_time,
    )
    config = get_export_config("operation_log")
    query = config.build_query_fn(query_params).limit(SYNC_EXPORT_MAX_ROWS)
    result = await db.execute(query)
    rows = result.scalars().all()

    excel_bytes = build_excel_bytes(config.columns, rows, sheet_name=config.name)
    filename = f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@operation_log_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量删除操作日志",
    dependencies=[Depends(require_permission("sys:oplog:delete"))],
)
async def batch_delete_logs(
    log_ids: List[int] = Body(..., description="日志ID列表"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量删除操作日志"""
    count = await OperationLogService.batch_delete_logs(db, log_ids)
    return response_base.success(data={"deleted": count}, msg=t("common.batch_delete_plain"))


@operation_log_router.delete(
    "/clear",
    response_model=ResponseModel,
    summary="清理过期操作日志",
    dependencies=[Depends(require_permission("sys:oplog:delete"))],
)
async def clear_logs(
    days: int = Query(30, description="清理多少天前的日志"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """清理指定天数前的操作日志"""
    count = await OperationLogService.clear_logs(db, days)
    return response_base.success(
        data={"deleted": count}, msg=t("operation_log.cleaned_before_days", days=days)
    )


@operation_log_router.get(
    "/{log_id}",
    response_model=ResponseModel[OperationLogDetailResponse],
    summary="获取操作日志详情",
)
async def get_log_detail(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """获取单条操作日志详情"""
    log = await OperationLogService.get_log(db, log_id)
    return response_base.success(
        data=OperationLogDetailResponse.model_validate(log),
        msg=t("operation_log.detail_success"),
    )


@operation_log_router.delete(
    "/{log_id}",
    response_model=ResponseModel,
    summary="删除单条操作日志",
    dependencies=[Depends(require_permission("sys:oplog:delete"))],
)
async def delete_log(
    log_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """删除单条操作日志"""
    ids = [log_id]
    count = await OperationLogService.batch_delete_logs(db, ids)
    return response_base.success(data={"deleted": count}, msg=t("common.delete_success"))
