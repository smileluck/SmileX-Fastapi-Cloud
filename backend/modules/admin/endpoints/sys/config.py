#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统配置相关接口
"""
import logging
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.db_manager import get_session
from core.i18n import t
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    ResponsePageDataModel,
    response_base,
)
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.admin.services.sys import ConfigService
from modules.admin.schemas.sys.config import (
    SysConfigCreate,
    SysConfigUpdate,
    SysConfigQueryParams,
    SysConfigResponseData,
    SysConfigSimpleResponse,
    SysConfigBatchUpdate,
    SysConfigReset,
    SysConfigByGroupQuery,
)
from database.models.sys.config import ConfigType, ConfigGroup

# 获取logger
logger = logging.getLogger(__name__)

# 创建配置管理路由
config_router = APIRouter(
    prefix="/config", tags=["系统配置"], dependencies=[Depends(current_user)]
)


@config_router.get("/list", response_model=ResponsePageModel[SysConfigResponseData], dependencies=[Depends(require_permission("sys:config:list"))])
async def get_config_list(
    query_params: SysConfigQueryParams = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取配置列表（分页）
    """
    try:
        logger.info("获取配置列表接口被调用")

        # 合并分页参数
        query_params.page = page_params.page
        query_params.page_size = page_params.page_size

        # 构建查询对象
        query = ConfigService.build_config_query(query_params)

        # 使用通用分页方法
        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=SysConfigResponseData,
        )

        logger.info("获取配置列表接口成功，共 %d 条记录", page_data.total)
        return response_base.page(data=page_data)

    except Exception as e:
        logger.error("获取配置列表接口失败: %s", str(e), exc_info=True)
        raise


@config_router.get("/all", response_model=ResponseModel[List[SysConfigSimpleResponse]])
async def get_all_configs(
    group: ConfigGroup = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """
    获取所有配置（不分页）
    """
    try:
        logger.info("获取所有配置接口被调用")

        # 构建查询参数
        query_params = SysConfigQueryParams(
            group=group,
            page=1,
            page_size=1000,
        )

        # 调用服务层
        configs, _ = await ConfigService.get_config_list(db, query_params)

        # 转换为响应模型
        records = [SysConfigSimpleResponse.model_validate(c) for c in configs]

        logger.info("获取所有配置接口成功，共 %d 条记录", len(records))
        return response_base.success(data=records)

    except Exception as e:
        logger.error("获取所有配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.get(
    "/group/{group}", response_model=ResponseModel[List[SysConfigSimpleResponse]]
)
async def get_configs_by_group(
    group: ConfigGroup,
    db: AsyncSession = Depends(get_session),
):
    """
    按分组获取配置列表
    """
    try:
        logger.info("按分组获取配置接口被调用，分组: %s", group)

        # 构建查询参数
        query = SysConfigByGroupQuery(
            group=group,
        )

        # 调用服务层
        configs = await ConfigService.get_configs_by_group(db, query)

        # 转换为响应模型
        records = [SysConfigSimpleResponse.model_validate(c) for c in configs]

        logger.info("按分组获取配置接口成功，共 %d 条记录", len(records))
        return response_base.success(data=records)

    except Exception as e:
        logger.error("按分组获取配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.get(
    "/id/{config_id}", response_model=ResponseModel[SysConfigResponseData]
)
async def get_config_by_id(
    config_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    通过ID获取单个配置
    """
    try:
        logger.info("获取配置详情接口被调用，配置ID: %d", config_id)

        config = await ConfigService.get_config_by_id(db, config_id)
        response_data = SysConfigResponseData.model_validate(config)

        logger.info("获取配置详情接口成功，配置ID: %d", config_id)
        return response_base.success(data=response_data)

    except Exception as e:
        logger.error("获取配置详情接口失败: %s", str(e), exc_info=True)
        raise


@config_router.get(
    "/key/{config_key}", response_model=ResponseModel[SysConfigResponseData]
)
async def get_config_by_key(
    config_key: str,
    db: AsyncSession = Depends(get_session),
):
    """
    通过键名获取单个配置
    """
    try:
        logger.info("获取配置详情接口被调用，配置键名: %s", config_key)

        config = await ConfigService.get_config_by_key(db, config_key)
        response_data = SysConfigResponseData.model_validate(config)

        logger.info("获取配置详情接口成功，配置键名: %s", config_key)
        return response_base.success(data=response_data)

    except Exception as e:
        logger.error("获取配置详情接口失败: %s", str(e), exc_info=True)
        raise


@config_router.get("/value/{config_key}", response_model=ResponseModel)
async def get_config_value(
    config_key: str,
    default: Optional[str] = Query(None, description="默认值"),
    db: AsyncSession = Depends(get_session),
):
    """
    获取配置值（已根据类型转换）
    """
    try:
        logger.info("获取配置值接口被调用，配置键名: %s", config_key)

        value = await ConfigService.get_config_value(db, config_key, default)

        logger.info("获取配置值接口成功，配置键名: %s", config_key)
        return response_base.success(data=value)

    except Exception as e:
        logger.error("获取配置值接口失败: %s", str(e), exc_info=True)
        raise


@config_router.post("/add", response_model=ResponseModel[SysConfigResponseData], dependencies=[Depends(require_permission("sys:config:add"))])
@log_operation(module="config", action="create", description="创建配置")
async def create_config(
    request: Request,
    config_in: SysConfigCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建配置
    """
    try:
        logger.info("创建配置接口被调用")

        config = await ConfigService.create_config(
            db, config_in, is_superuser=user.is_superuser
        )
        response_data = SysConfigResponseData.model_validate(config)

        logger.info("创建配置接口成功，配置ID: %d", config.id)
        return response_base.success(data=response_data, msg=t("common.create_success"))

    except Exception as e:
        logger.error("创建配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.put("/{config_id}", response_model=ResponseModel[SysConfigResponseData], dependencies=[Depends(require_permission("sys:config:edit"))])
@log_operation(module="config", action="update", description="更新配置")
async def update_config(
    config_id: int,
    request: Request,
    config_in: SysConfigUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新配置
    """
    try:
        logger.info("更新配置接口被调用，配置ID: %d", config_id)

        config = await ConfigService.update_config(
            db, config_id, config_in, is_superuser=user.is_superuser
        )
        response_data = SysConfigResponseData.model_validate(config)

        logger.info("更新配置接口成功，配置ID: %d", config_id)
        return response_base.success(data=response_data, msg=t("common.update_success"))

    except Exception as e:
        logger.error("更新配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.put("/batch/update", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:config:edit"))])
@log_operation(module="config", action="batch_update", description="批量更新配置")
async def batch_update_configs(
    request: Request,
    batch_in: SysConfigBatchUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量更新配置
    """
    try:
        logger.info("批量更新配置接口被调用")

        updated_count = await ConfigService.batch_update_configs(
            db, batch_in, is_superuser=user.is_superuser
        )

        logger.info("批量更新配置接口成功，更新数量: %d", updated_count)
        return response_base.success(msg=t("common.batch_update_count", count=updated_count))

    except Exception as e:
        logger.error("批量更新配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.put("/batch/reset", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:config:edit"))])
@log_operation(module="config", action="batch_reset", description="批量重置配置")
async def reset_configs(
    request: Request,
    reset_in: SysConfigReset,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量重置配置为默认值
    """
    try:
        logger.info("重置配置接口被调用")

        reset_count = await ConfigService.reset_configs(
            db, reset_in, is_superuser=user.is_superuser
        )

        logger.info("重置配置接口成功，重置数量: %d", reset_count)
        return response_base.success(msg=t("config.reset_count", count=reset_count))

    except Exception as e:
        logger.error("重置配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.delete("/batch", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:config:delete"))])
@log_operation(module="config", action="batch_delete", description="批量删除配置")
async def batch_delete_configs(
    request: Request,
    config_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    批量删除配置
    """
    try:
        logger.info("批量删除配置接口被调用，配置ID列表: %s", config_ids)

        delete_count = await ConfigService.batch_delete_configs(
            db, config_ids, is_superuser=user.is_superuser
        )

        logger.info("批量删除配置接口成功，共删除 %d 个配置", delete_count)
        return response_base.success(msg=t("config.batch_delete_success", count=delete_count))

    except Exception as e:
        logger.error("批量删除配置接口失败: %s", str(e), exc_info=True)
        raise


@config_router.delete("/{config_id}", response_model=ResponseModel, dependencies=[Depends(require_permission("sys:config:delete"))])
@log_operation(module="config", action="delete", description="删除配置")
async def delete_config(
    config_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除配置
    """
    try:
        logger.info("删除配置接口被调用，配置ID: %d", config_id)

        await ConfigService.delete_config(
            db, config_id, is_superuser=user.is_superuser
        )

        logger.info("删除配置接口成功，配置ID: %d", config_id)
        return response_base.success(msg=t("common.delete_success"))

    except Exception as e:
        logger.error("删除配置接口失败: %s", str(e), exc_info=True)
        raise
