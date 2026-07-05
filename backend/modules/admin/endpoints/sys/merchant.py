#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
商户管理相关接口
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from database.models.sys.user import SysUser
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.schemas.sys.merchant import (
    SysMerchantCreate,
    SysMerchantQueryParams,
    SysMerchantResponseData,
    SysMerchantSecretResetResponse,
    SysMerchantUpdate,
    SysMerchantWithSecret,
)
from modules.admin.services.sys import MerchantService

logger = logging.getLogger(__name__)

merchant_router = APIRouter(
    prefix="/merchant", tags=["商户管理"], dependencies=[Depends(current_user)]
)


@merchant_router.get(
    "/list",
    response_model=ResponsePageModel[SysMerchantResponseData],
    dependencies=[Depends(require_permission("sys:merchant:list"))],
)
async def get_merchant_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysMerchantQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取商户分页列表（响应不含 app_secret）"""
    logger.info("获取商户列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = MerchantService.build_merchant_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=SysMerchantResponseData
    )

    logger.info(f"获取商户列表成功，共 {page_data.total} 条记录")
    return ResponsePageModel[SysMerchantResponseData](data=page_data)


@merchant_router.get(
    "/{merchant_id}",
    response_model=ResponseModel[SysMerchantResponseData],
    dependencies=[Depends(require_permission("sys:merchant:list"))],
)
async def get_merchant(
    merchant_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个商户（响应不含 app_secret）"""
    logger.info(f"获取单个商户请求，商户ID: {merchant_id}")
    merchant = await MerchantService.get_merchant(db, merchant_id)
    return ResponseModel(data=SysMerchantResponseData.model_validate(merchant))


@merchant_router.post(
    "/add",
    response_model=ResponseModel[SysMerchantWithSecret],
    dependencies=[Depends(require_permission("sys:merchant:add"))],
)
@log_operation(module="merchant", action="create", description="创建商户")
async def create_merchant(
    request: Request,
    merchant_create: SysMerchantCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建商户。

    响应中 **一次性** 返回明文 app_secret，调用方必须立即妥善保存，
    后续接口不再提供明文查询。需要时请使用「重置密钥」。
    """
    logger.info(f"创建商户请求，商户名: {merchant_create.name}")
    merchant, plaintext_secret = await MerchantService.create_merchant(db, merchant_create)
    logger.info(f"创建商户成功，商户ID: {merchant.id}")
    data = SysMerchantWithSecret.model_validate(merchant)
    data.app_secret = plaintext_secret
    return ResponseModel(data=data, msg="创建商户成功，请立即保存 AppSecret")


@merchant_router.put(
    "/{merchant_id}",
    response_model=ResponseModel[SysMerchantResponseData],
    dependencies=[Depends(require_permission("sys:merchant:edit"))],
)
@log_operation(module="merchant", action="update", description="更新商户")
async def update_merchant(
    merchant_id: int,
    request: Request,
    merchant_update: SysMerchantUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """更新商户基础信息（不可用于修改 app_secret）"""
    logger.info(f"更新商户请求，商户ID: {merchant_id}")
    merchant = await MerchantService.update_merchant(db, merchant_id, merchant_update)
    logger.info(f"更新商户成功，商户ID: {merchant_id}")
    return ResponseModel(data=SysMerchantResponseData.model_validate(merchant), msg="更新商户成功")


@merchant_router.put(
    "/{merchant_id}/reset-secret",
    response_model=ResponseModel[SysMerchantSecretResetResponse],
    dependencies=[Depends(require_permission("sys:merchant:reset-secret"))],
)
@log_operation(module="merchant", action="reset_secret", description="重置商户密钥")
async def reset_merchant_secret(
    merchant_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    重置商户密钥。

    响应中 **一次性** 返回新的明文 app_secret，旧密钥立即失效。
    """
    logger.info(f"重置商户密钥请求，商户ID: {merchant_id}")
    merchant, plaintext_secret = await MerchantService.reset_secret(db, merchant_id)
    logger.info(f"重置商户密钥成功，商户ID: {merchant_id}")
    data = SysMerchantSecretResetResponse(
        app_id=merchant.app_id,
        app_secret=plaintext_secret,
        secret_updated_at=merchant.secret_updated_at,
    )
    return ResponseModel(data=data, msg="重置密钥成功，请立即保存新 AppSecret")


@merchant_router.delete(
    "/{merchant_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:merchant:delete"))],
)
@log_operation(module="merchant", action="delete", description="删除商户")
async def delete_merchant(
    merchant_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """删除商户"""
    logger.info(f"删除商户请求，商户ID: {merchant_id}")
    await MerchantService.delete_merchant(db, merchant_id)
    logger.info(f"删除商户成功，商户ID: {merchant_id}")
    return ResponseModel(msg="删除商户成功")
