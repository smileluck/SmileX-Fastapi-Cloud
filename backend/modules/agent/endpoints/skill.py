#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技能管理接口
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.schemas.skill import (
    SkillCreate,
    SkillQueryParams,
    SkillResponseData,
    SkillUpdate,
)
from modules.agent.services import SkillService
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results

logger = logging.getLogger(__name__)

skill_router = APIRouter(
    prefix="/skills", tags=["技能管理"], dependencies=[Depends(current_user)]
)


async def _attach_files(db: AsyncSession, data: SkillResponseData, skill_id: int) -> SkillResponseData:
    """装载附属文件到响应"""
    files = await SkillService.load_files(db, skill_id)
    from modules.agent.schemas.skill import SkillFileResponseData

    data.files = [SkillFileResponseData.model_validate(f) for f in files]
    data.file_count = len(data.files)
    return data


@skill_router.get(
    "/list",
    response_model=ResponsePageModel[SkillResponseData],
    dependencies=[Depends(require_permission("skill:list"))],
)
async def get_skill_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SkillQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取技能分页列表（不含附属文件内容，仅计数）"""
    logger.info("获取技能列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = SkillService.build_skill_query(query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=SkillResponseData
    )
    logger.info("获取技能列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[SkillResponseData](data=page_data)


@skill_router.get(
    "/all",
    response_model=ResponseModel[list[SkillResponseData]],
    dependencies=[Depends(require_permission("skill:list"))],
)
async def get_all_enabled_skills(db: AsyncSession = Depends(get_session)):
    """全部启用技能（Agent 表单下拉）"""
    from sqlalchemy import select

    from database.models.sys.skill import SysSkill

    result = await db.execute(
        select(SysSkill)
        .where(SysSkill.status.is_(True), SysSkill.deleted_at.is_(None))
        .order_by(SysSkill.id.asc())
    )
    skills = result.scalars().all()
    return ResponseModel(data=[SkillResponseData.model_validate(s) for s in skills])


@skill_router.get(
    "/{skill_id}",
    response_model=ResponseModel[SkillResponseData],
    dependencies=[Depends(require_permission("skill:list"))],
)
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个技能（含附属文件内容）"""
    logger.info("获取技能请求，ID: %s", skill_id)
    skill = await SkillService.get_skill(db, skill_id)
    data = SkillResponseData.model_validate(skill)
    data = await _attach_files(db, data, skill_id)
    return ResponseModel(data=data)


@skill_router.post(
    "/add",
    response_model=ResponseModel[SkillResponseData],
    dependencies=[Depends(require_permission("skill:add"))],
)
@log_operation(module="skill", action="create", description="创建技能")
async def create_skill(
    request: Request,
    skill_create: SkillCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建技能（主指令 + 附属文件整体提交）"""
    logger.info("创建技能请求，编码: %s", skill_create.code)
    skill = await SkillService.create_skill(db, skill_create)
    data = SkillResponseData.model_validate(skill)
    data = await _attach_files(db, data, skill.id)
    return ResponseModel(data=data, msg=t("agent.skill.create_success"))


@skill_router.put(
    "/{skill_id}",
    response_model=ResponseModel[SkillResponseData],
    dependencies=[Depends(require_permission("skill:edit"))],
)
@log_operation(module="skill", action="update", description="更新技能")
async def update_skill(
    skill_id: int,
    request: Request,
    skill_update: SkillUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新技能（编码不可改；files 留空=不变、空数组=清空）"""
    logger.info("更新技能请求，ID: %s", skill_id)
    skill = await SkillService.update_skill(db, skill_id, skill_update)
    data = SkillResponseData.model_validate(skill)
    data = await _attach_files(db, data, skill_id)
    return ResponseModel(data=data, msg=t("agent.skill.update_success"))


@skill_router.delete(
    "/{skill_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("skill:delete"))],
)
@log_operation(module="skill", action="delete", description="删除技能")
async def delete_skill(
    skill_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除技能（被智能体绑定时拒绝）"""
    logger.info("删除技能请求，ID: %s", skill_id)
    await SkillService.delete_skill(db, skill_id)
    return ResponseModel(msg=t("agent.skill.delete_success"))
