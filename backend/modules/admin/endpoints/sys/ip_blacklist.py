#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP 黑名单管理接口
"""
import logging

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from database.models.sys.user import SysUser
from core.i18n import t
from core.response import ResponseModel, ResponsePageModel, response_base
from database.db_manager import get_session
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.schemas.sys.ip_blacklist import (
    IpBlacklistBatchDeleteRequest,
    IpBlacklistCreateRequest,
    IpBlacklistQueryParams,
    IpBlacklistResponse,
)
from modules.admin.services.sys.ip_blacklist_service import IpBlacklistService

logger = logging.getLogger(__name__)

ip_blacklist_router = APIRouter(prefix="/ip-blacklist", tags=["系统管理/IP黑名单"])


@ip_blacklist_router.get(
    "/list",
    response_model=ResponsePageModel[IpBlacklistResponse],
    summary="获取 IP 黑名单列表",
    dependencies=[Depends(require_permission("sys:blacklist:list"))],
)
async def list_blacklist(
    query_params: IpBlacklistQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """分页查询 IP 黑名单"""
    query = IpBlacklistService.build_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=IpBlacklistResponse,
    )
    return response_base.page(data=page_data)


@ip_blacklist_router.post(
    "/add",
    response_model=ResponseModel[IpBlacklistResponse],
    summary="新增 IP 黑名单",
    dependencies=[Depends(require_permission("sys:blacklist:add"))],
)
async def add_blacklist(
    req: IpBlacklistCreateRequest = Body(..., description="新增请求"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """新增一条 IP 黑名单（同步写入 Redis）"""
    entry = await IpBlacklistService.create(db=db, req=req, creator_id=user.id)
    return response_base.success(
        data=IpBlacklistResponse.model_validate(entry),
        msg=t("ip_blacklist.added"),
    )


@ip_blacklist_router.delete(
    "/batch/delete",
    response_model=ResponseModel,
    summary="批量移除 IP 黑名单",
    dependencies=[Depends(require_permission("sys:blacklist:remove"))],
)
async def batch_remove(
    req: IpBlacklistBatchDeleteRequest = Body(..., description="ID 列表"),
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """批量软删除并同步移除 Redis"""
    count = await IpBlacklistService.delete_by_ids(db, req.ids)
    return response_base.success(data={"deleted": count}, msg=t("ip_blacklist.removed"))


@ip_blacklist_router.delete(
    "/{entry_id}",
    response_model=ResponseModel,
    summary="移除单条 IP 黑名单",
    dependencies=[Depends(require_permission("sys:blacklist:remove"))],
)
async def remove_one(
    entry_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    count = await IpBlacklistService.delete_by_ids(db, [entry_id])
    return response_base.success(data={"deleted": count}, msg=t("ip_blacklist.removed"))
