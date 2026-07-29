#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""租户选择/切换接口"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response.response_schema import ResponseModel
from core.exception.errors import ForbiddenError
from core.i18n import t
from core.security.oauth.user_manager import base_user_manager
from plugins.multi_tenant.services.tenant_service import TenantService
from plugins.multi_tenant.schemas.tenant import SelectTenantRequest
from modules.admin.deps.auth.user_manager import current_user
from database.models.sys.user import SysUser

logger = logging.getLogger(__name__)

tenant_auth_router = APIRouter(prefix="/auth", tags=["租户认证"])


@tenant_auth_router.post(
    "/select-tenant",
    response_model=ResponseModel,
    summary="选择/切换租户",
    description="用户选择一个租户后，返回包含 tenant_id 的新 JWT token",
)
async def select_tenant(
    req: SelectTenantRequest,
    user: SysUser = Depends(current_user),
    db: AsyncSession = Depends(get_session),
):
    """选择或切换租户，返回新 token"""
    # 验证用户属于该租户
    tenants = await TenantService.get_user_tenants(db, user.id)
    target = None
    for t in tenants:
        if t.id == req.tenant_id:
            target = t
            break

    if not target:
        raise ForbiddenError(msg=t("tenant.not_belong"))

    if not target.status:
        raise ForbiddenError(msg=t("tenant.disabled"))

    # 查找租户 JWT 配置
    jwt_config = await TenantService.get_tenant_jwt_config_cached(target.id)
    secret_key = jwt_config.secret_key if jwt_config else None
    algorithm = jwt_config.algorithm if jwt_config else None
    access_lifetime = jwt_config.access_lifetime if jwt_config else None

    # 创建包含 tenant_id 的新 token
    tokens = await base_user_manager.create_token(
        user_id=user.id,
        user_role="admin",
        username=user.username,
        tenant_id=target.id,
        secret_key=secret_key,
        algorithm=algorithm,
        access_lifetime=access_lifetime,
    )

    # 保存最后选择的租户
    await TenantService.save_last_tenant(db, user.id, target.id)
    await db.commit()

    tenant_list = [
        {"id": t.id, "name": t.name, "code": t.code}
        for t in tenants
    ]

    return ResponseModel(
        data={
            **tokens.model_dump(),
            "tenant_id": target.id,
            "tenants": tenant_list,
        },
        msg=t("tenant.switched", name=target.name),
    )
