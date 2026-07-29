#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
商户管理服务
"""
import logging
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import and_, select, Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from core.security.openapi import encrypt_secret, generate_app_id, generate_app_secret
from core.utils.memory_cache import CacheNamespace, get_memory_cache
from database.models.sys.merchant import SysMerchant
from database.utils.timezone import timezone
from modules.admin.schemas.sys.merchant import (
    SysMerchantCreate,
    SysMerchantQueryParams,
    SysMerchantUpdate,
)

logger = logging.getLogger(__name__)

# 商户鉴权查询缓存的 TTL（秒）
_MERCHANT_CACHE_TTL = 30


def _invalidate_merchant_cache(app_id: str) -> None:
    """失效指定 app_id 的鉴权缓存"""
    if app_id:
        get_memory_cache().delete(CacheNamespace.MERCHANT, app_id)


class MerchantService:
    """商户管理服务类"""

    @staticmethod
    def build_merchant_query(query_params: SysMerchantQueryParams) -> Select:
        """构建商户分页查询条件"""
        base_query = select(SysMerchant)

        conditions = []
        if query_params.status is not None:
            conditions.append(SysMerchant.status == query_params.status)
        if query_params.name:
            conditions.append(SysMerchant.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysMerchant.code.like(f"%{query_params.code}%"))
        if query_params.app_id:
            conditions.append(SysMerchant.app_id.like(f"%{query_params.app_id}%"))

        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.order_by(SysMerchant.sort.asc(), SysMerchant.id.desc())

    @staticmethod
    async def get_merchant(db: AsyncSession, merchant_id: int) -> SysMerchant:
        """获取单个商户，不存在则抛 NotFoundError"""
        result = await db.execute(select(SysMerchant).where(SysMerchant.id == merchant_id))
        merchant = result.scalar_one_or_none()
        if not merchant:
            raise NotFoundError(msg=t("merchant.not_found", id=merchant_id))
        return merchant

    @staticmethod
    async def get_by_app_id(db: AsyncSession, app_id: str) -> Optional[SysMerchant]:
        """根据 AppId 查询商户（供鉴权使用）"""
        result = await db.execute(select(SysMerchant).where(SysMerchant.app_id == app_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_active_by_app_id_cached(
        db: AsyncSession, app_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        开放API 鉴权场景下按 app_id 获取商户轻量信息（带 30s 内存缓存）。

        只缓存 {id, name, app_id, status, app_secret_encrypted}，
        app_secret 由调用方每次内联解密（不在 worker 内存中保留明文）。
        """
        cache = get_memory_cache()
        cached = cache.get(CacheNamespace.MERCHANT, app_id)
        if cached is not None:
            return cached

        merchant = await MerchantService.get_by_app_id(db, app_id)
        if merchant is None:
            # 缓存“未命中标记”意义不大，直接返回 None
            return None

        payload: Dict[str, Any] = {
            "id": merchant.id,
            "name": merchant.name,
            "app_id": merchant.app_id,
            "status": merchant.status,
            "app_secret_encrypted": merchant.app_secret_encrypted,
        }
        cache.set(CacheNamespace.MERCHANT, app_id, payload, _MERCHANT_CACHE_TTL)
        return payload

    @staticmethod
    async def create_merchant(
        db: AsyncSession, payload: SysMerchantCreate
    ) -> Tuple[SysMerchant, str]:
        """
        创建商户，自动生成 app_id / app_secret。
        返回 (merchant, app_secret 明文) —— 明文仅此次返回，由调用方一次性下发给前端。
        """
        logger.info("创建商户，商户名: %s", payload.name)

        if payload.code:
            existing = await db.execute(select(SysMerchant).where(SysMerchant.code == payload.code))
            if existing.scalar_one_or_none():
                raise CustomError(
                    error=CustomErrorCode.MERCHANT_CODE_EXIST,
                    msg=t("merchant.code_exist", code=payload.code),
                )

        # 生成 app_id（极小概率冲突，冲突则重试）
        for _ in range(3):
            app_id = generate_app_id()
            conflict = await db.execute(select(SysMerchant.id).where(SysMerchant.app_id == app_id))
            if conflict.scalar_one_or_none() is None:
                break
        else:
            raise CustomError(
                error=CustomErrorCode.MERCHANT_APP_ID_CONFLICT,
                msg=t("merchant.app_id_conflict"),
            )

        plaintext_secret = generate_app_secret()
        merchant = SysMerchant(
            name=payload.name,
            code=payload.code,
            contact_name=payload.contact_name,
            contact_phone=payload.contact_phone,
            contact_email=payload.contact_email,
            app_id=app_id,
            app_secret_encrypted=encrypt_secret(plaintext_secret),
            remark=payload.remark,
            status=payload.status,
            sort=payload.sort,
        )
        merchant.touch_secret()
        try:
            db.add(merchant)
            await db.commit()
        except IntegrityError as exc:
            await db.rollback()
            raise CustomError(
                error=CustomErrorCode.MERCHANT_APP_ID_CONFLICT,
                msg=t("merchant.app_id_conflict_short"),
            ) from exc
        await db.refresh(merchant)

        logger.info("创建商户成功，商户ID: %s, AppId: %s", merchant.id, merchant.app_id)
        return merchant, plaintext_secret

    @staticmethod
    async def update_merchant(
        db: AsyncSession, merchant_id: int, payload: SysMerchantUpdate
    ) -> SysMerchant:
        """更新商户基础信息（不涉及 app_secret）"""
        logger.info("更新商户信息，商户ID: %s", merchant_id)
        merchant = await MerchantService.get_merchant(db, merchant_id)

        if payload.code is not None and payload.code != merchant.code:
            existing = await db.execute(
                select(SysMerchant).where(
                    SysMerchant.code == payload.code, SysMerchant.id != merchant_id
                )
            )
            if existing.scalar_one_or_none():
                raise CustomError(
                    error=CustomErrorCode.MERCHANT_CODE_EXIST,
                    msg=t("merchant.code_exist", code=payload.code),
                )

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(merchant, key) and value is not None:
                setattr(merchant, key, value)

        await db.commit()
        await db.refresh(merchant)

        _invalidate_merchant_cache(merchant.app_id)
        logger.info("更新商户信息成功，商户ID: %s", merchant_id)
        return merchant

    @staticmethod
    async def reset_secret(
        db: AsyncSession, merchant_id: int
    ) -> Tuple[SysMerchant, str]:
        """重置商户密钥，返回 (merchant, 新的明文 app_secret)"""
        logger.info("重置商户密钥，商户ID: %s", merchant_id)
        merchant = await MerchantService.get_merchant(db, merchant_id)

        plaintext_secret = generate_app_secret()
        merchant.app_secret_encrypted = encrypt_secret(plaintext_secret)
        merchant.touch_secret()

        await db.commit()
        await db.refresh(merchant)

        _invalidate_merchant_cache(merchant.app_id)
        logger.info("重置商户密钥成功，商户ID: %s", merchant_id)
        return merchant, plaintext_secret

    @staticmethod
    async def delete_merchant(db: AsyncSession, merchant_id: int) -> bool:
        """删除商户（沿用与部门一致的删除语义）"""
        logger.info("删除商户，商户ID: %s", merchant_id)
        merchant = await MerchantService.get_merchant(db, merchant_id)

        app_id = merchant.app_id
        await db.delete(merchant)
        await db.commit()

        _invalidate_merchant_cache(app_id)
        logger.info("删除商户成功，商户ID: %s", merchant_id)
        return True
