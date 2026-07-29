#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
通知管理服务
处理通知的创建、发布、查询和已读状态管理
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Select, update
from sqlalchemy.orm import joinedload

from database.models.sys.notice import SysNotice, NoticeType, NoticeTargetType, NoticePriority
from database.models.sys.notice_read import SysNoticeRead
from database.models.sys.user import SysUser
from core.exception.errors import NotFoundError, ForbiddenError, ConflictError
from core.i18n import t
from core.websocket.manager import ConnectionManager
from database.utils.timezone import timezone
from modules.admin.schemas.sys.notice import (
    SysNoticeCreate,
    SysNoticeUpdate,
    SysNoticeQueryParams,
    MyNoticeQueryParams,
)

logger = logging.getLogger(__name__)


class NoticeService:
    """
    通知管理服务类
    """

    @staticmethod
    def _apply_notice_filters(
        base_query: Select, query_params: SysNoticeQueryParams
    ) -> Select:
        """应用通知列表查询条件"""
        conditions = []
        if query_params.title:
            conditions.append(SysNotice.title.like(f"%{query_params.title}%"))
        if query_params.type:
            conditions.append(SysNotice.type == query_params.type)
        if query_params.target_type:
            conditions.append(SysNotice.target_type == query_params.target_type)
        if query_params.status is not None:
            conditions.append(SysNotice.status == query_params.status)
        if query_params.priority:
            conditions.append(SysNotice.priority == query_params.priority)
        if query_params.sender_id is not None:
            conditions.append(SysNotice.sender_id == query_params.sender_id)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.where(SysNotice.deleted_at.is_(None)).order_by(SysNotice.created_at.desc())

    @staticmethod
    def build_notice_list_query(query_params: SysNoticeQueryParams) -> Select:
        """构建通知列表查询对象"""
        base_query = select(SysNotice)
        return NoticeService._apply_notice_filters(base_query, query_params)

    @staticmethod
    async def get_notice_list(
        db: AsyncSession, query_params: SysNoticeQueryParams
    ) -> Tuple[List[SysNotice], int]:
        """
        获取通知列表（管理端）

        Returns:
            Tuple[通知列表, 总记录数]
        """
        logger.info(f"获取通知列表，查询参数: {query_params}")

        base_query = NoticeService.build_notice_list_query(query_params)

        # 统计总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (query_params.page - 1) * query_params.page_size
        paginated_query = base_query.offset(offset).limit(query_params.page_size)

        result = await db.execute(paginated_query)
        notices = result.scalars().all()

        logger.info(f"获取通知列表成功，共 {total} 条记录")
        return list(notices), total

    @staticmethod
    async def get_notice(db: AsyncSession, notice_id: int) -> SysNotice:
        """
        获取单个通知详情

        Raises:
            NotFoundError: 通知不存在
        """
        result = await db.execute(
            select(SysNotice).where(
                SysNotice.id == notice_id,
                SysNotice.deleted_at.is_(None),
            )
        )
        notice = result.scalar_one_or_none()
        if not notice:
            raise NotFoundError(msg=t("notice.not_found", id=notice_id))
        return notice

    @staticmethod
    async def create_notice(
        db: AsyncSession, create_data: SysNoticeCreate, sender: SysUser
    ) -> SysNotice:
        """
        创建通知（默认草稿状态）
        """
        logger.info(f"创建通知，标题: {create_data.title}, 发送者: {sender.username}")

        notice = SysNotice(
            title=create_data.title,
            content=create_data.content,
            type=create_data.type,
            target_type=create_data.target_type,
            target_role_ids=create_data.target_role_ids,
            target_user_ids=create_data.target_user_ids,
            sender_id=sender.id,
            sender_name=sender.nickname or sender.username,
            priority=create_data.priority,
            status=False,
            published_at=None,
        )

        db.add(notice)
        await db.commit()
        await db.refresh(notice)

        logger.info(f"创建通知成功，通知ID: {notice.id}")
        return notice

    @staticmethod
    async def update_notice(
        db: AsyncSession, notice_id: int, update_data: SysNoticeUpdate
    ) -> SysNotice:
        """
        更新通知（仅草稿可编辑）

        Raises:
            NotFoundError: 通知不存在
            ForbiddenError: 通知已发布，不可编辑
        """
        logger.info(f"更新通知，通知ID: {notice_id}")

        notice = await NoticeService.get_notice(db, notice_id)

        if notice.status:
            raise ForbiddenError(msg=t("notice.already_published"))

        update_dict = update_data.model_dump(exclude_unset=True)

        # 校验 target_type 与 target_ids 的对应关系
        target_type = update_dict.get("target_type", notice.target_type)
        role_ids = update_dict.get("target_role_ids", notice.target_role_ids)
        user_ids = update_dict.get("target_user_ids", notice.target_user_ids)

        if target_type == NoticeTargetType.ROLE and not role_ids:
            raise ConflictError(msg=t("notice.role_target_required"))
        if target_type == NoticeTargetType.USER and not user_ids:
            raise ConflictError(msg=t("notice.user_target_required"))

        for key, value in update_dict.items():
            if hasattr(notice, key) and value is not None:
                setattr(notice, key, value)

        await db.commit()
        await db.refresh(notice)

        logger.info(f"更新通知成功，通知ID: {notice_id}")
        return notice

    @staticmethod
    async def delete_notice(db: AsyncSession, notice_id: int) -> bool:
        """
        删除通知（软删除）

        Raises:
            NotFoundError: 通知不存在
        """
        logger.info(f"删除通知，通知ID: {notice_id}")

        notice = await NoticeService.get_notice(db, notice_id)
        notice.soft_delete()
        await db.commit()

        logger.info(f"删除通知成功，通知ID: {notice_id}")
        return True

    @staticmethod
    async def batch_delete_notices(db: AsyncSession, notice_ids: List[int]) -> int:
        """
        批量删除通知
        """
        logger.info(f"批量删除通知，通知ID列表: {notice_ids}")

        delete_count = 0
        for notice_id in notice_ids:
            try:
                await NoticeService.delete_notice(db, notice_id)
                delete_count += 1
            except Exception as e:
                logger.error(f"删除通知失败，通知ID: {notice_id}, 错误: {str(e)}")
                raise e

        logger.info(f"批量删除通知成功，共删除 {delete_count} 条")
        return delete_count

    @staticmethod
    async def publish_notice(
        db: AsyncSession,
        notice_id: int,
        connection_manager: ConnectionManager,
    ) -> SysNotice:
        """
        发布通知并触发 WebSocket 推送

        流程：
        1. 将通知状态设为已发布
        2. 根据 target_type 向在线用户推送 WebSocket 消息
        3. 为所有目标用户创建 SysNoticeRead 记录

        Raises:
            NotFoundError: 通知不存在
            ConflictError: 通知已是发布状态
        """
        logger.info(f"发布通知，通知ID: {notice_id}")

        notice = await NoticeService.get_notice(db, notice_id)

        if notice.status:
            raise ConflictError(msg=t("notice.already_published_status"))

        notice.status = True
        notice.published_at = timezone.now()
        await db.commit()
        await db.refresh(notice)

        # 构建推送消息
        push_message = {
            "type": "notification",
            "data": {
                "id": notice.id,
                "title": notice.title,
                "type": notice.type,
                "priority": notice.priority,
                "sender_name": notice.sender_name,
                "published_at": notice.published_at.isoformat() if notice.published_at else None,
            },
        }

        # 确定目标用户并推送
        target_user_ids: set = set()

        if notice.target_type == NoticeTargetType.ALL:
            # 全员广播
            await connection_manager.broadcast(push_message)
            # 获取所有用户ID用于创建阅读记录
            result = await db.execute(select(SysUser.id).where(SysUser.deleted_at.is_(None), SysUser.status == True))
            target_user_ids = {row[0] for row in result.all()}

        elif notice.target_type == NoticeTargetType.ROLE and notice.target_role_ids:
            # 按角色推送
            for role_id in notice.target_role_ids:
                await connection_manager.send_to_role(role_id, push_message)
            # 获取具有目标角色的用户ID
            from database.models.sys.role import SysRole
            from database.models.sys.association_tables import sys_user_role_association
            result = await db.execute(
                select(sys_user_role_association.c.user_id)
                .where(sys_user_role_association.c.role_id.in_(notice.target_role_ids))
                .distinct()
            )
            target_user_ids = {row[0] for row in result.all()}

        elif notice.target_type == NoticeTargetType.USER and notice.target_user_ids:
            # 按指定用户推送
            await connection_manager.send_to_users(notice.target_user_ids, push_message)
            target_user_ids = set(notice.target_user_ids)

        # 为所有目标用户创建阅读记录（排除已存在的）
        if target_user_ids:
            # 查询已存在的记录，避免重复插入
            existing_result = await db.execute(
                select(SysNoticeRead.user_id).where(
                    SysNoticeRead.notice_id == notice_id,
                    SysNoticeRead.user_id.in_(list(target_user_ids)),
                )
            )
            existing_user_ids = {row[0] for row in existing_result.all()}
            new_user_ids = target_user_ids - existing_user_ids

            if new_user_ids:
                notice_reads = [
                    SysNoticeRead(
                        user_id=user_id,
                        notice_id=notice_id,
                        is_read=False,
                        read_at=None,
                    )
                    for user_id in new_user_ids
                ]
                db.add_all(notice_reads)
                await db.commit()

        logger.info(f"发布通知成功，通知ID: {notice_id}, 目标用户数: {len(target_user_ids)}")
        return notice

    @staticmethod
    async def get_my_notices(
        db: AsyncSession, user_id: int, query_params: MyNoticeQueryParams
    ) -> Tuple[List[dict], int]:
        """
        获取当前用户的通知列表（含已读状态）

        Returns:
            Tuple[通知列表(含已读状态), 总记录数]
        """
        # 联合查询 SysNotice 和 SysNoticeRead
        stmt = (
            select(
                SysNotice,
                SysNoticeRead.is_read,
                SysNoticeRead.read_at,
            )
            .join(
                SysNoticeRead,
                and_(
                    SysNoticeRead.notice_id == SysNotice.id,
                    SysNoticeRead.user_id == user_id,
                ),
                isouter=False,
            )
            .where(
                SysNotice.deleted_at.is_(None),
                SysNotice.status == True,
            )
        )

        if query_params.type:
            stmt = stmt.where(SysNotice.type == query_params.type)
        if query_params.is_read is not None:
            stmt = stmt.where(SysNoticeRead.is_read == query_params.is_read)

        # 统计总数
        count_query = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (query_params.page - 1) * query_params.page_size
        stmt = stmt.order_by(SysNotice.published_at.desc()).offset(offset).limit(query_params.page_size)

        result = await db.execute(stmt)
        rows = result.all()

        notices = []
        for row in rows:
            notice = row[0]
            notices.append({
                "id": notice.id,
                "title": notice.title,
                "content": notice.content,
                "type": notice.type,
                "sender_name": notice.sender_name,
                "priority": notice.priority,
                "is_read": row[1] if row[1] is not None else False,
                "read_at": row[2],
                "published_at": notice.published_at,
                "created_at": notice.created_at,
            })

        return notices, total

    @staticmethod
    async def get_unread_count(db: AsyncSession, user_id: int) -> int:
        """
        获取未读通知数量
        """
        result = await db.execute(
            select(func.count())
            .select_from(SysNoticeRead)
            .join(
                SysNotice,
                SysNotice.id == SysNoticeRead.notice_id,
            )
            .where(
                SysNoticeRead.user_id == user_id,
                SysNoticeRead.is_read == False,
                SysNotice.deleted_at.is_(None),
                SysNotice.status == True,
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def mark_as_read(db: AsyncSession, user_id: int, notice_id: int) -> bool:
        """
        标记单条通知为已读
        """
        result = await db.execute(
            select(SysNoticeRead).where(
                SysNoticeRead.user_id == user_id,
                SysNoticeRead.notice_id == notice_id,
            )
        )
        notice_read = result.scalar_one_or_none()

        if notice_read and not notice_read.is_read:
            notice_read.is_read = True
            notice_read.read_at = timezone.now()
            await db.commit()
            return True
        return False

    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: int) -> int:
        """
        标记所有通知为已读

        Returns:
            更新的记录数
        """
        result = await db.execute(
            update(SysNoticeRead)
            .where(
                SysNoticeRead.user_id == user_id,
                SysNoticeRead.is_read == False,
            )
            .values(is_read=True, read_at=timezone.now())
        )
        await db.commit()
        return result.rowcount or 0
