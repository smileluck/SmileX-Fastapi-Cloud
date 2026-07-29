#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知管理相关接口
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.i18n import t
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    ResponsePageDataModel,
)
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.admin.services.sys import NoticeService
from modules.admin.schemas.sys.notice import (
    SysNoticeResponse,
    SysNoticeListResponse,
    SysNoticeCreate,
    SysNoticeUpdate,
    SysNoticeQueryParams,
    MyNoticeQueryParams,
    MyNoticeResponse,
    BatchReadRequest,
)

logger = logging.getLogger(__name__)

# 创建通知管理路由
notice_router = APIRouter(
    prefix="/notice", tags=["通知管理"], dependencies=[Depends(current_user)]
)


@notice_router.get(
    "/list",
    response_model=ResponsePageModel[SysNoticeListResponse],
    dependencies=[Depends(require_permission("sys:notice:list"))],
)
async def get_notice_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysNoticeQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    获取通知列表（管理端）
    """
    logger.info("获取通知列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = NoticeService.build_notice_list_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SysNoticeListResponse,
    )

    logger.info(f"获取通知列表成功，共 {page_data.total} 条记录")
    return ResponsePageModel[SysNoticeListResponse](data=page_data)


@notice_router.get(
    "/{notice_id}",
    response_model=ResponseModel[SysNoticeResponse],
    dependencies=[Depends(require_permission("sys:notice:list"))],
)
async def get_notice(
    notice_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取通知详情
    """
    logger.info(f"获取通知详情，通知ID: {notice_id}")

    notice = await NoticeService.get_notice(db, notice_id)
    notice_response = SysNoticeResponse.model_validate(notice)

    logger.info(f"获取通知详情成功，通知ID: {notice_id}")
    return ResponseModel(data=notice_response)


@notice_router.post(
    "/add",
    response_model=ResponseModel[SysNoticeResponse],
    dependencies=[Depends(require_permission("sys:notice:add"))],
)
@log_operation(module="notice", action="create", description="创建通知")
async def create_notice(
    request: Request,
    notice_create: SysNoticeCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建通知（默认草稿状态）
    """
    logger.info(f"创建通知请求，标题: {notice_create.title}")

    notice = await NoticeService.create_notice(db, notice_create, user)
    notice_response = SysNoticeResponse.model_validate(notice)

    logger.info(f"创建通知成功，通知ID: {notice.id}")
    return ResponseModel(data=notice_response, msg=t("notice.create_success"))


@notice_router.put(
    "/{notice_id}",
    response_model=ResponseModel[SysNoticeResponse],
    dependencies=[Depends(require_permission("sys:notice:edit"))],
)
@log_operation(module="notice", action="update", description="更新通知")
async def update_notice(
    notice_id: int,
    request: Request,
    notice_update: SysNoticeUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新通知（仅草稿可编辑）
    """
    logger.info(f"更新通知请求，通知ID: {notice_id}")

    notice = await NoticeService.update_notice(db, notice_id, notice_update)
    notice_response = SysNoticeResponse.model_validate(notice)

    logger.info(f"更新通知成功，通知ID: {notice_id}")
    return ResponseModel(data=notice_response, msg=t("notice.update_success"))


@notice_router.delete(
    "/batch",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:notice:delete"))],
)
@log_operation(module="notice", action="batch_delete", description="批量删除通知")
async def batch_delete_notices(
    request: Request,
    notice_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除通知
    """
    logger.info(f"批量删除通知请求，通知ID: {notice_ids}")

    delete_count = await NoticeService.batch_delete_notices(db, notice_ids)

    logger.info(f"批量删除通知成功，共删除 {delete_count} 条")
    return ResponseModel(
        msg=t("notice.batch_delete_success", count=delete_count),
        data={"delete_count": delete_count},
    )


@notice_router.delete(
    "/{notice_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:notice:delete"))],
)
@log_operation(module="notice", action="delete", description="删除通知")
async def delete_notice(
    notice_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除通知
    """
    logger.info(f"删除通知请求，通知ID: {notice_id}")

    await NoticeService.delete_notice(db, notice_id)

    logger.info(f"删除通知成功，通知ID: {notice_id}")
    return ResponseModel(msg=t("notice.delete_success"))


@notice_router.post(
    "/{notice_id}/publish",
    response_model=ResponseModel[SysNoticeResponse],
    dependencies=[Depends(require_permission("sys:notice:publish"))],
)
@log_operation(module="notice", action="publish", description="发布通知")
async def publish_notice(
    notice_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    发布通知并触发 WebSocket 实时推送
    """
    logger.info(f"发布通知请求，通知ID: {notice_id}")

    connection_manager = getattr(request.app.state, "connection_manager", None)
    if connection_manager is None:
        logger.error("发布通知失败: connection_manager 未初始化")
        return ResponseModel(msg=t("notice.server_error_no_manager"), code=500)

    notice = await NoticeService.publish_notice(db, notice_id, connection_manager)
    notice_response = SysNoticeResponse.model_validate(notice)

    logger.info(f"发布通知成功，通知ID: {notice_id}")
    return ResponseModel(data=notice_response, msg=t("notice.publish_success"))


# ==================== 我的通知（接收端） ====================

@notice_router.get(
    "/my/list",
    response_model=ResponsePageModel[MyNoticeResponse],
)
async def get_my_notices(
    page_params: PageRequest = Depends(get_page_params),
    query_params: MyNoticeQueryParams = Depends(),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    获取我的通知列表
    """
    logger.info(f"获取我的通知列表，用户ID: {user.id}")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    notices, total = await NoticeService.get_my_notices(db, user.id, query_params)

    page_data = ResponsePageDataModel[MyNoticeResponse](
        records=[MyNoticeResponse.model_validate(n) for n in notices],
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
        total_pages=(total + page_params.page_size - 1) // page_params.page_size,
    )

    logger.info(f"获取我的通知列表成功，共 {total} 条")
    return ResponsePageModel[MyNoticeResponse](data=page_data)


@notice_router.get(
    "/my/unread-count",
    response_model=ResponseModel[int],
)
async def get_unread_count(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    获取未读通知数量
    """
    count = await NoticeService.get_unread_count(db, user.id)
    return ResponseModel(data=count)


@notice_router.put(
    "/my/{notice_id}/read",
    response_model=ResponseModel,
)
async def mark_as_read(
    notice_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    标记单条通知为已读
    """
    success = await NoticeService.mark_as_read(db, user.id, notice_id)
    if success:
        return ResponseModel(msg=t("notice.mark_read_success"))
    return ResponseModel(msg=t("notice.already_read_or_not_found"))


@notice_router.put(
    "/my/read-all",
    response_model=ResponseModel,
)
async def mark_all_as_read(
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """
    标记所有通知为已读
    """
    count = await NoticeService.mark_all_as_read(db, user.id)
    return ResponseModel(msg=t("notice.marked_read_count", count=count), data={"count": count})
