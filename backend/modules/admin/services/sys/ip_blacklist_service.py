#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
IP 黑名单服务：数据库为源，Redis 作为命中查询缓存。
"""
import ipaddress
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.sys.ip_blacklist import SysIpBlacklist
from core.exception.errors import ConflictError, NotFoundError, RequestError
from core.i18n import t
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from core.security.rate_limit import (
    add_ip_to_redis_blacklist,
    remove_ip_from_redis_blacklist,
)
from modules.admin.schemas.sys.ip_blacklist import (
    IpBlacklistCreateRequest,
    IpBlacklistQueryParams,
)

logger = logging.getLogger(__name__)


def _validate_ip(ip: str) -> str:
    try:
        return str(ipaddress.ip_address(ip.strip()))
    except (ValueError, AttributeError) as exc:
        raise RequestError(msg=t("ip_blacklist.invalid_ip", ip=ip)) from exc


def _calc_remaining_ttl(expire_at: Optional[datetime]) -> Optional[int]:
    if not expire_at:
        return None
    now = datetime.now(timezone.utc)
    if expire_at.tzinfo is None:
        expire_at = expire_at.replace(tzinfo=timezone.utc)
    remaining = int((expire_at - now).total_seconds())
    return remaining if remaining > 0 else 0


class IpBlacklistService:
    """IP 黑名单业务服务"""

    @staticmethod
    def build_query(params: IpBlacklistQueryParams):
        conditions = [SysIpBlacklist.deleted_at.is_(None)]
        if params.ip:
            conditions.append(SysIpBlacklist.ip.like(f"%{params.ip}%"))
        if params.type:
            conditions.append(SysIpBlacklist.type == params.type)
        return select(SysIpBlacklist).where(and_(*conditions)).order_by(
            SysIpBlacklist.created_at.desc()
        )

    @staticmethod
    async def create(
        db: AsyncSession,
        req: IpBlacklistCreateRequest,
        creator_id: Optional[int],
    ) -> SysIpBlacklist:
        ip = _validate_ip(req.ip)

        existing = (
            await db.execute(select(SysIpBlacklist).where(SysIpBlacklist.ip == ip))
        ).scalar_one_or_none()
        if existing and existing.deleted_at is None:
            raise ConflictError(msg=t("ip_blacklist.already_in", ip=ip))

        expire_at: Optional[datetime] = None
        ttl_seconds: Optional[int] = None
        if req.type == "temporary":
            now = datetime.now(timezone.utc)
            if req.expire_at:
                expire_at = req.expire_at
                if expire_at.tzinfo is None:
                    expire_at = expire_at.replace(tzinfo=timezone.utc)
                ttl_seconds = int((expire_at - now).total_seconds())
                if ttl_seconds < 0:
                    ttl_seconds = 0
            else:
                ttl_seconds = req.ttl_seconds or 3600
                expire_at = now + timedelta(seconds=ttl_seconds)

        if existing:
            existing.type = req.type
            existing.reason = req.reason
            existing.expire_at = expire_at
            existing.deleted_at = None
            existing.creator_id = creator_id
            entry = existing
        else:
            entry = SysIpBlacklist(
                ip=ip,
                type=req.type,
                reason=req.reason,
                expire_at=expire_at,
                creator_id=creator_id,
            )
            db.add(entry)
        await db.commit()
        await db.refresh(entry)

        try:
            await add_ip_to_redis_blacklist(ip, ttl_seconds=ttl_seconds, reason=req.reason or "")
        except Exception as exc:
            logger.error("写入 Redis 黑名单失败 ip=%s err=%s", ip, exc)

        get_memory_cache().delete(CacheNamespace.IP_BLACKLIST, ip)
        return entry

    @staticmethod
    async def get(db: AsyncSession, entry_id: int) -> SysIpBlacklist:
        result = await db.execute(
            select(SysIpBlacklist).where(SysIpBlacklist.id == entry_id)
        )
        entry = result.scalar_one_or_none()
        if not entry or entry.deleted_at is not None:
            raise NotFoundError(msg=t("ip_blacklist.entry_not_found", id=entry_id))
        return entry

    @staticmethod
    async def delete_by_ids(db: AsyncSession, ids: List[int]) -> int:
        if not ids:
            return 0
        result = await db.execute(
            select(SysIpBlacklist).where(SysIpBlacklist.id.in_(ids))
        )
        entries = result.scalars().all()
        for entry in entries:
            entry.soft_delete()
        await db.commit()

        for entry in entries:
            try:
                await remove_ip_from_redis_blacklist(entry.ip)
                get_memory_cache().delete(CacheNamespace.IP_BLACKLIST, entry.ip)
            except Exception as exc:
                logger.error("移除 Redis 黑名单失败 ip=%s err=%s", entry.ip, exc)
        return len(entries)

    @staticmethod
    async def warmup_to_redis(db: AsyncSession) -> int:
        """从 DB 拉取所有未过期的黑名单写入 Redis。"""
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(SysIpBlacklist).where(SysIpBlacklist.deleted_at.is_(None))
        )
        entries = result.scalars().all()
        count = 0
        for entry in entries:
            if entry.type == "temporary":
                remaining = _calc_remaining_ttl(entry.expire_at)
                if remaining is None or remaining <= 0:
                    continue
                try:
                    await add_ip_to_redis_blacklist(entry.ip, ttl_seconds=remaining, reason=entry.reason or "")
                    count += 1
                except Exception as exc:
                    logger.error("warmup Redis 黑名单失败 ip=%s err=%s", entry.ip, exc)
            else:
                try:
                    await add_ip_to_redis_blacklist(entry.ip, ttl_seconds=None, reason=entry.reason or "")
                    count += 1
                except Exception as exc:
                    logger.error("warmup Redis 黑名单失败 ip=%s err=%s", entry.ip, exc)
        return count

    @staticmethod
    async def auto_block(
        db: AsyncSession,
        ip: str,
        reason: str,
        ttl_seconds: int,
    ) -> Optional[SysIpBlacklist]:
        """系统自动拉黑（如登录失败超限）。

        ip 字段在 DB 层有 UNIQUE 约束，所以无论该 IP 是否已被软删除，都复用同一行：
        - 未过期 / permanent：保持原样
        - temporary 已过期：原地更新 expire_at / reason，复活记录
        - 之前被软删除：清空 deleted_at 并按 temporary 重新写入
        """
        ip = _validate_ip(ip)
        now = datetime.now(timezone.utc)
        existing = (
            await db.execute(select(SysIpBlacklist).where(SysIpBlacklist.ip == ip))
        ).scalar_one_or_none()

        if existing and existing.deleted_at is None and existing.type == "permanent":
            try:
                await add_ip_to_redis_blacklist(
                    ip, ttl_seconds=None, reason=existing.reason or reason
                )
            except Exception as exc:
                logger.error("auto_block 刷新 Redis 失败 ip=%s err=%s", ip, exc)
            return existing

        if existing and existing.deleted_at is None:
            existing_expire = existing.expire_at
            if existing_expire and existing_expire.tzinfo is None:
                existing_expire = existing_expire.replace(tzinfo=timezone.utc)
            if existing_expire and existing_expire > now:
                return existing

        expire_at = now + timedelta(seconds=ttl_seconds)
        if existing:
            existing.type = "temporary"
            existing.reason = reason
            existing.expire_at = expire_at
            existing.deleted_at = None
            existing.creator_id = None
            entry = existing
        else:
            entry = SysIpBlacklist(
                ip=ip,
                type="temporary",
                reason=reason,
                expire_at=expire_at,
                creator_id=None,
            )
            db.add(entry)
        await db.commit()
        await db.refresh(entry)
        try:
            await add_ip_to_redis_blacklist(ip, ttl_seconds=ttl_seconds, reason=reason)
        except Exception as exc:
            logger.error("auto_block 写入 Redis 失败 ip=%s err=%s", ip, exc)
        get_memory_cache().delete(CacheNamespace.IP_BLACKLIST, ip)
        return entry
