#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导出模板管理接口
"""
import json
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.i18n import t
from core.response import ResponseModel, response_base
from core.decorators.operation_log import log_operation
from core.exception.errors import NotFoundError
from modules.admin.deps.auth.user_manager import current_user
from database.models.sys.user import SysUser
from database.models.sys.export_template import SysExportTemplate
from modules.admin.schemas.sys.export_template import (
    ExportTemplateCreate,
    ExportTemplateUpdate,
    ExportTemplateResponse,
    ModuleFieldResponse,
    ModuleInfoResponse,
)
from modules.admin.exports import EXPORT_REGISTRY

logger = logging.getLogger(__name__)

export_template_router = APIRouter(prefix="/export-template", tags=["导出模板"])


@export_template_router.get(
    "/modules",
    response_model=ResponseModel[list[ModuleInfoResponse]],
    summary="获取可用的导出模块及其字段",
)
async def get_export_modules(
    user: SysUser = Depends(current_user),
):
    """返回所有已注册的导出模块，每个模块包含可选字段列表"""
    modules = []
    for key, config in EXPORT_REGISTRY.items():
        fields = [
            ModuleFieldResponse(field=col.field, header=col.header, width=col.width)
            for col in config.columns
        ]
        modules.append(ModuleInfoResponse(
            module_key=key,
            name=config.name,
            fields=fields,
        ))
    return response_base.success(data=modules)


@export_template_router.get(
    "/list",
    response_model=ResponseModel,
    summary="获取导出模板列表",
)
async def get_template_list(
    page: int = 1,
    page_size: int = 20,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    base_query = select(SysExportTemplate).where(
        SysExportTemplate.created_by == user.id
    ).order_by(SysExportTemplate.created_at.desc())

    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(base_query.offset(offset).limit(page_size))
    templates = result.scalars().all()

    items = [ExportTemplateResponse.from_orm_with_format(t) for t in templates]
    return response_base.success(
        data={"items": items, "total": total, "page": page, "page_size": page_size},
    )


@export_template_router.get(
    "/{template_id}",
    response_model=ResponseModel[ExportTemplateResponse],
    summary="获取模板详情",
)
async def get_template(
    template_id: int,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(SysExportTemplate).where(SysExportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundError(msg=t("export_template.not_found", id=template_id))
    return response_base.success(data=ExportTemplateResponse.from_orm_with_format(template))


@export_template_router.post(
    "/add",
    response_model=ResponseModel[ExportTemplateResponse],
    summary="创建导出模板",
)
@log_operation(module="export_template", action="create", description="创建导出模板")
async def create_template(
    request: Request,
    template_in: ExportTemplateCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    columns_json = json.dumps(
        [c.model_dump() for c in template_in.columns],
        ensure_ascii=False,
    )
    joins_json = None
    if template_in.joins_config:
        joins_json = json.dumps(
            [j.model_dump() for j in template_in.joins_config],
            ensure_ascii=False,
        )
    template = SysExportTemplate(
        name=template_in.name,
        module_key=template_in.module_key,
        columns=columns_json,
        joins_config=joins_json,
        description=template_in.description,
        created_by=user.id,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return response_base.success(
        data=ExportTemplateResponse.from_orm_with_format(template),
        msg=t("common.create_success"),
    )


@export_template_router.put(
    "/{template_id}",
    response_model=ResponseModel[ExportTemplateResponse],
    summary="更新导出模板",
)
@log_operation(module="export_template", action="update", description="更新导出模板")
async def update_template(
    template_id: int,
    request: Request,
    template_in: ExportTemplateUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    result = await db.execute(
        select(SysExportTemplate).where(SysExportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundError(msg=t("export_template.not_found", id=template_id))

    if template_in.name is not None:
        template.name = template_in.name
    if template_in.columns is not None:
        template.columns = json.dumps(
            [c.model_dump() for c in template_in.columns],
            ensure_ascii=False,
        )
    if template_in.joins_config is not None:
        template.joins_config = json.dumps(
            [j.model_dump() for j in template_in.joins_config],
            ensure_ascii=False,
        ) if template_in.joins_config else None
    if template_in.description is not None:
        template.description = template_in.description

    await db.commit()
    await db.refresh(template)
    return response_base.success(
        data=ExportTemplateResponse.from_orm_with_format(template),
        msg=t("common.update_success"),
    )


@export_template_router.delete(
    "/{template_id}",
    response_model=ResponseModel,
    summary="删除导出模板",
)
@log_operation(module="export_template", action="delete", description="删除导出模板")
async def delete_template(
    template_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    result = await db.execute(
        select(SysExportTemplate).where(SysExportTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise NotFoundError(msg=t("export_template.not_found", id=template_id))

    await db.delete(template)
    await db.commit()
    return response_base.success(msg=t("common.delete_success"))
