#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
部门管理相关接口
"""
import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.db_manager import get_session
from core.response.response_schema import ResponseModel, ResponsePageModel, ResponsePageDataModel
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser

from modules.admin.services.sys import DeptService
from modules.admin.schemas.sys.dept import (
    SysDeptResponseData,
    SysDeptTreeResponse,
    SysDeptCreate,
    SysDeptUpdate,
    SysDeptQueryParams,
    SysDeptBatchUpdateStatus,
)

logger = logging.getLogger(__name__)

dept_router = APIRouter(
    prefix="/dept", tags=["部门管理"], dependencies=[Depends(current_user)]
)


@dept_router.get(
    "/list",
    response_model=ResponsePageModel[SysDeptResponseData],
    dependencies=[Depends(require_permission("sys:dept:list"))],
)
async def get_dept_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysDeptQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取部门分页列表"""
    logger.info("获取部门列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = DeptService.build_dept_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=SysDeptResponseData
    )

    logger.info(f"获取部门列表成功，共 {page_data.total} 条记录")
    return ResponsePageModel[SysDeptResponseData](data=page_data)


@dept_router.get(
    "/tree",
    response_model=ResponseModel[List[SysDeptResponseData]],
    dependencies=[Depends(require_permission("sys:dept:list"))],
)
async def get_dept_tree(
    only_active: bool = False,
    db: AsyncSession = Depends(get_session),
):
    """获取部门树（完整字段）"""
    logger.info("获取部门树请求")
    tree = await DeptService.get_dept_tree(db, only_active=only_active)
    logger.info(f"获取部门树成功，共 {len(tree)} 个根部门")
    return ResponseModel(data=tree)


@dept_router.get(
    "/tree-select",
    response_model=ResponseModel[List[SysDeptTreeResponse]],
)
async def get_dept_tree_select(
    only_active: bool = True,
    db: AsyncSession = Depends(get_session),
):
    """获取部门简化树，用于表单下拉选择"""
    logger.info("获取部门下拉树请求")
    tree = await DeptService.get_dept_tree_simple(db, only_active=only_active)
    return ResponseModel(data=tree)


@dept_router.get(
    "/{dept_id}",
    response_model=ResponseModel[SysDeptResponseData],
    dependencies=[Depends(require_permission("sys:dept:list"))],
)
async def get_dept(
    dept_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个部门"""
    logger.info(f"获取单个部门请求，部门ID: {dept_id}")
    dept = await DeptService.get_dept(db, dept_id)
    return ResponseModel(data=SysDeptResponseData.model_validate(dept))


@dept_router.post(
    "/add",
    response_model=ResponseModel[SysDeptResponseData],
    dependencies=[Depends(require_permission("sys:dept:add"))],
)
@log_operation(module="dept", action="create", description="创建部门")
async def create_dept(
    request: Request,
    dept_create: SysDeptCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """创建部门"""
    logger.info(f"创建部门请求，部门名: {dept_create.name}")
    dept = await DeptService.create_dept(db, dept_create)
    logger.info(f"创建部门成功，部门ID: {dept.id}")
    return ResponseModel(data=SysDeptResponseData.model_validate(dept), msg="创建部门成功")


@dept_router.put(
    "/{dept_id}",
    response_model=ResponseModel[SysDeptResponseData],
    dependencies=[Depends(require_permission("sys:dept:edit"))],
)
@log_operation(module="dept", action="update", description="更新部门")
async def update_dept(
    dept_id: int,
    request: Request,
    dept_update: SysDeptUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """更新部门"""
    logger.info(f"更新部门请求，部门ID: {dept_id}")
    dept = await DeptService.update_dept(db, dept_id, dept_update)
    logger.info(f"更新部门成功，部门ID: {dept_id}")
    return ResponseModel(data=SysDeptResponseData.model_validate(dept), msg="更新部门成功")


@dept_router.delete(
    "/batch",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:dept:delete"))],
)
@log_operation(module="dept", action="batch_delete", description="批量删除部门")
async def batch_delete_depts(
    request: Request,
    dept_ids: List[int],
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """批量删除部门"""
    logger.info(f"批量删除部门请求，部门ID: {dept_ids}")
    delete_count = await DeptService.batch_delete_depts(db, dept_ids)
    logger.info(f"批量删除部门成功，共删除 {delete_count} 个部门")
    return ResponseModel(
        msg=f"批量删除成功，共删除 {delete_count} 个部门",
        data={"delete_count": delete_count},
    )


@dept_router.put(
    "/batch/status",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:dept:edit"))],
)
@log_operation(module="dept", action="batch_update_status", description="批量更新部门状态")
async def batch_update_depts_status(
    request: Request,
    batch_update: SysDeptBatchUpdateStatus,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """批量更新部门状态"""
    logger.info(
        f"批量更新部门状态请求，部门ID: {batch_update.dept_ids}, 状态: {batch_update.status}"
    )
    update_count = await DeptService.batch_update_depts_status(
        db, batch_update.dept_ids, batch_update.status
    )
    status_text = "启用" if batch_update.status else "禁用"
    logger.info(f"批量更新部门状态成功，共 {update_count} 个部门被{status_text}")
    return ResponseModel(
        msg=f"批量{status_text}成功，共 {update_count} 个部门",
        data={"update_count": update_count},
    )


@dept_router.delete(
    "/{dept_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("sys:dept:delete"))],
)
@log_operation(module="dept", action="delete", description="删除部门")
async def delete_dept(
    dept_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """删除部门"""
    logger.info(f"删除部门请求，部门ID: {dept_id}")
    await DeptService.delete_dept(db, dept_id)
    logger.info(f"删除部门成功，部门ID: {dept_id}")
    return ResponseModel(msg="删除部门成功")
