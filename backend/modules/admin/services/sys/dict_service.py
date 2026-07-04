#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
字典管理服务
处理字典相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, and_, func, Select
from sqlalchemy.orm import noload
from typing import List, Optional, Tuple

from database.models.sys.dict import SysDict, SysDictItem
from core.exception.errors import NotFoundError, ConflictError, ForbiddenError
from modules.admin.schemas.sys.dict import (
    SysDictCreate,
    SysDictUpdate,
    SysDictQueryParams,
    SysDictItemCreate,
    SysDictItemUpdate,
    SysDictItemQueryParams,
    SysDictBatchUpdateStatus,
    SysDictItemBatchUpdateStatus,
)

# 获取logger
logger = logging.getLogger(__name__)


class DictService:
    """
    字典管理服务类
    """

    @staticmethod
    def build_dict_query(
        query_params: SysDictQueryParams,
    ) -> Select:
        """
        构建字典查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        # 构建基础查询（抑制模型级 selectin 自动联查 dict_items）
        base_query = select(SysDict).options(noload(SysDict.dict_items))

        # 构建筛选条件
        conditions = []
        if query_params.name:
            conditions.append(SysDict.name.contains(query_params.name))
        if query_params.code:
            conditions.append(SysDict.code.contains(query_params.code))
        if query_params.status is not None:
            conditions.append(SysDict.status == query_params.status)
        if query_params.is_system is not None:
            conditions.append(SysDict.is_system == query_params.is_system)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 排序
        base_query = base_query.order_by(SysDict.sort.asc(), SysDict.id.desc())

        return base_query

    @staticmethod
    async def get_dict_list(
        db: AsyncSession, query_params: SysDictQueryParams
    ) -> Tuple[List[SysDict], int]:
        """
        获取字典列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (字典列表, 总数)
        """
        try:
            logger.debug(
                "获取字典列表，查询参数: %s", query_params.model_dump(exclude_none=True)
            )

            # 构建查询
            base_query = DictService.build_dict_query(query_params)

            # 先查询总数 - 使用正确的方式
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            # 分页查询
            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            dicts = result.scalars().all()

            logger.debug("获取字典列表成功，共 %d 条记录", total)
            return dicts, total

        except Exception as e:
            logger.error("获取字典列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_dict(db: AsyncSession, dict_id: int) -> SysDict:
        """
        获取单个字典

        Args:
            db: 数据库会话
            dict_id: 字典ID

        Returns:
            字典对象

        Raises:
            NotFoundError: 字典不存在
        """
        try:
            logger.debug("获取字典详情，字典ID: %d", dict_id)

            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.id == dict_id)
            )
            dict_obj = result.scalar_one_or_none()

            if not dict_obj:
                logger.warning("字典不存在，字典ID: %d", dict_id)
                raise NotFoundError(msg=f"字典 {dict_id} 不存在")

            logger.debug("获取字典详情成功，字典ID: %d", dict_id)
            return dict_obj

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取字典详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_dict_by_code(db: AsyncSession, code: str) -> SysDict:
        """
        通过编码获取字典

        Args:
            db: 数据库会话
            code: 字典编码

        Returns:
            字典对象

        Raises:
            NotFoundError: 字典不存在
        """
        try:
            logger.debug("通过编码获取字典，字典编码: %s", code)

            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.code == code)
            )
            dict_obj = result.scalar_one_or_none()

            if not dict_obj:
                logger.warning("字典不存在，字典编码: %s", code)
                raise NotFoundError(msg=f"字典编码 {code} 不存在")

            logger.debug("通过编码获取字典成功，字典编码: %s", code)
            return dict_obj

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("通过编码获取字典失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_dict_with_items(db: AsyncSession, dict_id: int) -> SysDict:
        """
        获取字典及其所有字典项

        Args:
            db: 数据库会话
            dict_id: 字典ID

        Returns:
            字典对象（包含字典项）

        Raises:
            NotFoundError: 字典不存在
        """
        try:
            logger.debug("获取字典及其字典项，字典ID: %d", dict_id)

            from sqlalchemy.orm import joinedload

            result = await db.execute(
                select(SysDict)
                .options(joinedload(SysDict.dict_items))
                .where(SysDict.id == dict_id)
            )
            dict_obj = result.unique().scalar_one_or_none()

            if not dict_obj:
                logger.warning("字典不存在，字典ID: %d", dict_id)
                raise NotFoundError(msg=f"字典 {dict_id} 不存在")

            logger.debug("获取字典及其字典项成功，字典ID: %d", dict_id)
            return dict_obj

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取字典及其字典项失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def create_dict(
        db: AsyncSession, dict_in: SysDictCreate, *, is_superuser: bool = False
    ) -> SysDict:
        """
        创建字典

        Args:
            db: 数据库会话
            dict_in: 字典创建请求

        Returns:
            创建后的字典对象

        Raises:
            ConflictError: 字典编码已存在
        """
        try:
            logger.info("创建字典，请求数据: %s", dict_in.model_dump(exclude_none=True))

            # 检查字典编码是否已存在
            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.code == dict_in.code)
            )
            if result.scalar_one_or_none():
                logger.warning("字典编码已存在，编码: %s", dict_in.code)
                raise ConflictError(msg="字典编码已存在")

            # 创建字典对象
            dict_obj = SysDict(
                name=dict_in.name,
                code=dict_in.code,
                description=dict_in.description,
                status=dict_in.status,
                sort=dict_in.sort,
                is_system=False if not is_superuser else getattr(dict_in, 'is_system', False),
            )

            db.add(dict_obj)
            await db.commit()
            await db.refresh(dict_obj)

            logger.info("创建字典成功，字典ID: %d", dict_obj.id)
            return dict_obj

        except ConflictError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("创建字典失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update_dict(
        db: AsyncSession,
        dict_id: int,
        dict_in: SysDictUpdate,
        *,
        is_superuser: bool = False,
    ) -> SysDict:
        """
        更新字典

        Args:
            db: 数据库会话
            dict_id: 字典ID
            dict_in: 字典更新请求

        Returns:
            更新后的字典对象

        Raises:
            NotFoundError: 字典不存在
            ForbiddenError: 系统内置字典禁止修改
        """
        try:
            logger.info(
                "更新字典，字典ID: %d，请求数据: %s",
                dict_id,
                dict_in.model_dump(exclude_none=True),
            )

            # 查询字典
            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.id == dict_id)
            )
            existing_dict = result.scalar_one_or_none()

            if not existing_dict:
                logger.warning("字典不存在，字典ID: %d", dict_id)
                raise NotFoundError(msg=f"字典 {dict_id} 不存在")

            # 非超级管理员不能修改系统内置字典
            if existing_dict.is_system and not is_superuser:
                logger.warning("系统内置字典禁止修改，字典ID: %d", dict_id)
                raise ForbiddenError(msg="系统内置字典禁止修改")

            # 更新字段
            update_data = dict_in.model_dump(exclude_unset=True)

            # 非超级管理员不能将字典标记为系统内置（与 create_dict 保持一致）
            if update_data.get("is_system") is True and not is_superuser:
                update_data.pop("is_system", None)

            for field, value in update_data.items():
                setattr(existing_dict, field, value)

            await db.commit()
            await db.refresh(existing_dict)

            logger.info("更新字典成功，字典ID: %d", dict_id)
            return existing_dict

        except (NotFoundError, ForbiddenError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新字典失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def batch_update_dict_status(
        db: AsyncSession,
        batch_in: SysDictBatchUpdateStatus,
        *,
        is_superuser: bool = False,
    ) -> int:
        """
        批量更新字典状态

        Args:
            db: 数据库会话
            batch_in: 批量更新请求

        Returns:
            更新的数量
        """
        try:
            logger.info(
                "批量更新字典状态，字典ID列表: %s，状态: %s",
                batch_in.dict_ids,
                batch_in.status,
            )

            from sqlalchemy import update

            stmt = (
                update(SysDict)
                .where(SysDict.id.in_(batch_in.dict_ids))
            )

            # 非超级管理员跳过系统内置字典
            if not is_superuser:
                stmt = stmt.where(SysDict.is_system == False)

            stmt = stmt.values(status=batch_in.status)
            result = await db.execute(stmt)
            updated_count = result.rowcount

            await db.commit()

            logger.info("批量更新字典状态成功，更新数量: %d", updated_count)
            return updated_count

        except Exception as e:
            await db.rollback()
            logger.error("批量更新字典状态失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete_dict(
        db: AsyncSession, dict_id: int, *, is_superuser: bool = False
    ) -> bool:
        """
        删除字典

        Args:
            db: 数据库会话
            dict_id: 字典ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 字典不存在
            ForbiddenError: 系统内置字典禁止删除
        """
        try:
            logger.info("删除字典，字典ID: %d", dict_id)

            # 查询字典
            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.id == dict_id)
            )
            dict_obj = result.scalar_one_or_none()

            if not dict_obj:
                logger.warning("字典不存在，字典ID: %d", dict_id)
                raise NotFoundError(msg=f"字典 {dict_id} 不存在")

            # 非超级管理员不能删除系统内置字典
            if dict_obj.is_system and not is_superuser:
                logger.warning("系统内置字典禁止删除，字典ID: %d", dict_id)
                raise ForbiddenError(msg="系统内置字典禁止删除")

            await db.delete(dict_obj)
            await db.commit()

            logger.info("删除字典成功，字典ID: %d", dict_id)
            return True

        except (NotFoundError, ForbiddenError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除字典失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    def build_dict_item_query(
        query_params: SysDictItemQueryParams,
    ) -> Select:
        """
        构建字典项查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        # 构建基础查询（抑制模型级 selectin 自动联查 dict）
        base_query = select(SysDictItem).options(noload(SysDictItem.dict))

        # 构建筛选条件
        conditions = []
        if query_params.dict_id:
            conditions.append(SysDictItem.dict_id == query_params.dict_id)
        if query_params.label:
            conditions.append(SysDictItem.label.contains(query_params.label))
        if query_params.value:
            conditions.append(SysDictItem.value.contains(query_params.value))
        if query_params.status is not None:
            conditions.append(SysDictItem.status == query_params.status)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 排序
        base_query = base_query.order_by(SysDictItem.sort.asc(), SysDictItem.id.desc())

        return base_query

    @staticmethod
    async def get_dict_item_list(
        db: AsyncSession, query_params: SysDictItemQueryParams
    ) -> Tuple[List[SysDictItem], int]:
        """
        获取字典项列表（分页）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            (字典项列表, 总数)
        """
        try:
            logger.debug(
                "获取字典项列表，查询参数: %s",
                query_params.model_dump(exclude_none=True),
            )

            # 构建查询
            base_query = DictService.build_dict_item_query(query_params)

            # 先查询总数 - 使用正确的方式
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0

            # 分页查询
            query = base_query
            if query_params.page and query_params.page_size:
                offset = (query_params.page - 1) * query_params.page_size
                query = query.offset(offset).limit(query_params.page_size)

            result = await db.execute(query)
            dict_items = result.scalars().all()

            logger.debug("获取字典项列表成功，共 %d 条记录", total)
            return dict_items, total

        except Exception as e:
            logger.error("获取字典项列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_dict_items_by_dict_code(
        db: AsyncSession, dict_code: str
    ) -> List[SysDictItem]:
        """
        通过字典编码获取字典项列表（只返回启用的）

        Args:
            db: 数据库会话
            dict_code: 字典编码

        Returns:
            字典项列表
        """
        try:
            logger.debug("通过字典编码获取字典项，字典编码: %s", dict_code)

            query = (
                select(SysDictItem)
                .options(noload(SysDictItem.dict))
                .join(SysDict, SysDictItem.dict_id == SysDict.id)
                .where(SysDict.code == dict_code)
                .where(SysDictItem.status == True)
                .where(SysDict.status == True)
                .order_by(SysDictItem.sort.asc(), SysDictItem.id.desc())
            )

            result = await db.execute(query)
            dict_items = result.scalars().all()

            logger.debug(
                "通过字典编码获取字典项成功，字典编码: %s，数量: %d",
                dict_code,
                len(dict_items),
            )
            return dict_items

        except Exception as e:
            logger.error("通过字典编码获取字典项失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_dict_item(db: AsyncSession, item_id: int) -> SysDictItem:
        """
        获取单个字典项

        Args:
            db: 数据库会话
            item_id: 字典项ID

        Returns:
            字典项对象

        Raises:
            NotFoundError: 字典项不存在
        """
        try:
            logger.debug("获取字典项详情，字典项ID: %d", item_id)

            result = await db.execute(
                select(SysDictItem)
                .options(noload(SysDictItem.dict))
                .where(SysDictItem.id == item_id)
            )
            dict_item = result.scalar_one_or_none()

            if not dict_item:
                logger.warning("字典项不存在，字典项ID: %d", item_id)
                raise NotFoundError(msg=f"字典项 {item_id} 不存在")

            logger.debug("获取字典项详情成功，字典项ID: %d", item_id)
            return dict_item

        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取字典项详情失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def create_dict_item(
        db: AsyncSession, item_in: SysDictItemCreate
    ) -> SysDictItem:
        """
        创建字典项

        Args:
            db: 数据库会话
            item_in: 字典项创建请求

        Returns:
            创建后的字典项对象

        Raises:
            NotFoundError: 字典不存在
        """
        try:
            logger.info(
                "创建字典项，请求数据: %s", item_in.model_dump(exclude_none=True)
            )

            # 检查字典是否存在
            result = await db.execute(
                select(SysDict)
                .options(noload(SysDict.dict_items))
                .where(SysDict.id == item_in.dict_id)
            )
            if not result.scalar_one_or_none():
                logger.warning("字典不存在，字典ID: %d", item_in.dict_id)
                raise NotFoundError(msg=f"字典 {item_in.dict_id} 不存在")

            # 创建字典项对象
            dict_item = SysDictItem(
                dict_id=item_in.dict_id,
                value=item_in.value,
                label=item_in.label,
                description=item_in.description,
                ext_info=item_in.ext_info,
                status=item_in.status,
                sort=item_in.sort,
            )

            db.add(dict_item)
            await db.commit()
            await db.refresh(dict_item)

            logger.info("创建字典项成功，字典项ID: %d", dict_item.id)
            return dict_item

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("创建字典项失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update_dict_item(
        db: AsyncSession, item_id: int, item_in: SysDictItemUpdate
    ) -> SysDictItem:
        """
        更新字典项

        Args:
            db: 数据库会话
            item_id: 字典项ID
            item_in: 字典项更新请求

        Returns:
            更新后的字典项对象

        Raises:
            NotFoundError: 字典项不存在
        """
        try:
            logger.info(
                "更新字典项，字典项ID: %d，请求数据: %s",
                item_id,
                item_in.model_dump(exclude_none=True),
            )

            # 查询字典项
            result = await db.execute(
                select(SysDictItem)
                .options(noload(SysDictItem.dict))
                .where(SysDictItem.id == item_id)
            )
            existing_item = result.scalar_one_or_none()

            if not existing_item:
                logger.warning("字典项不存在，字典项ID: %d", item_id)
                raise NotFoundError(msg=f"字典项 {item_id} 不存在")

            # 更新字段
            update_data = item_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_item, field, value)

            await db.commit()
            await db.refresh(existing_item)

            logger.info("更新字典项成功，字典项ID: %d", item_id)
            return existing_item

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新字典项失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def batch_update_dict_item_status(
        db: AsyncSession, batch_in: SysDictItemBatchUpdateStatus
    ) -> int:
        """
        批量更新字典项状态

        Args:
            db: 数据库会话
            batch_in: 批量更新请求

        Returns:
            更新的数量
        """
        try:
            logger.info(
                "批量更新字典项状态，字典项ID列表: %s，状态: %s",
                batch_in.item_ids,
                batch_in.status,
            )

            from sqlalchemy import update

            stmt = (
                update(SysDictItem)
                .where(SysDictItem.id.in_(batch_in.item_ids))
                .values(status=batch_in.status)
            )
            result = await db.execute(stmt)
            updated_count = result.rowcount

            await db.commit()

            logger.info("批量更新字典项状态成功，更新数量: %d", updated_count)
            return updated_count

        except Exception as e:
            await db.rollback()
            logger.error("批量更新字典项状态失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete_dict_item(db: AsyncSession, item_id: int) -> bool:
        """
        删除字典项

        Args:
            db: 数据库会话
            item_id: 字典项ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 字典项不存在
        """
        try:
            logger.info("删除字典项，字典项ID: %d", item_id)

            # 查询字典项
            result = await db.execute(
                select(SysDictItem)
                .options(noload(SysDictItem.dict))
                .where(SysDictItem.id == item_id)
            )
            dict_item = result.scalar_one_or_none()

            if not dict_item:
                logger.warning("字典项不存在，字典项ID: %d", item_id)
                raise NotFoundError(msg=f"字典项 {item_id} 不存在")

            await db.delete(dict_item)
            await db.commit()

            logger.info("删除字典项成功，字典项ID: %d", item_id)
            return True

        except NotFoundError:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除字典项失败: %s", str(e), exc_info=True)
            raise
