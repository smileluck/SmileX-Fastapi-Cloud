#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
部门管理服务
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, Select
from sqlalchemy.orm import noload
from typing import List, Optional, Tuple

from database.models.sys.dept import SysDept
from core.exception.errors import NotFoundError, ConflictError, ValidationError
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from modules.admin.schemas.sys.dept import (
    SysDeptCreate,
    SysDeptUpdate,
    SysDeptQueryParams,
    SysDeptResponseData,
    SysDeptTreeResponse,
)

logger = logging.getLogger(__name__)


def _invalidate_data_scope_cache() -> None:
    """角色/部门变更可能影响数据权限计算，失效权限缓存"""
    get_memory_cache().invalidate(CacheNamespace.PERMISSION)


class DeptService:
    """
    部门管理服务类
    """

    @staticmethod
    def build_dept_query(query_params: SysDeptQueryParams) -> Select:
        base_query = select(SysDept).options(noload(SysDept.children), noload(SysDept.parent))

        conditions = []
        if query_params.status is not None:
            conditions.append(SysDept.status == query_params.status)
        if query_params.name:
            conditions.append(SysDept.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysDept.code.like(f"%{query_params.code}%"))

        if conditions:
            base_query = base_query.where(and_(*conditions))

        return base_query.order_by(SysDept.sort.asc(), SysDept.id.asc())

    @staticmethod
    async def get_dept_list(
        db: AsyncSession, query_params: SysDeptQueryParams
    ) -> Tuple[List[SysDept], int]:
        logger.debug("获取部门列表，查询参数: %s", query_params)

        base_query = DeptService.build_dept_query(query_params)

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        offset = (query_params.page - 1) * query_params.page_size
        paginated_query = base_query.offset(offset).limit(query_params.page_size)

        result = await db.execute(paginated_query)
        depts = result.scalars().all()

        logger.debug("获取部门列表成功，共 %s 条记录", total)
        return depts, total

    @staticmethod
    async def get_all_depts(db: AsyncSession, *, only_active: bool = False) -> List[SysDept]:
        query = select(SysDept).options(noload(SysDept.children), noload(SysDept.parent))
        if only_active:
            query = query.where(SysDept.status == True)
        query = query.order_by(SysDept.sort.asc(), SysDept.id.asc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def _build_response_tree(flat_depts: List[SysDept]) -> List[SysDeptResponseData]:
        """根据扁平 ORM 列表构建 Pydantic 响应树（不查 DB）"""
        resp_map: dict[int, SysDeptResponseData] = {
            dept.id: SysDeptResponseData.model_validate(dept) for dept in flat_depts
        }
        roots: List[SysDeptResponseData] = []
        for dept in flat_depts:
            resp = resp_map[dept.id]
            if dept.parent_id and dept.parent_id in resp_map:
                resp_map[dept.parent_id].children.append(resp)
            else:
                roots.append(resp)
        return roots

    @staticmethod
    def _build_simple_tree(flat_depts: List[SysDept]) -> List[SysDeptTreeResponse]:
        """根据扁平 ORM 列表构建简化树（仅 id/label/pId/children），用于下拉"""
        tree_map: dict[int, SysDeptTreeResponse] = {
            dept.id: SysDeptTreeResponse(
                id=dept.id, label=dept.name, pId=dept.parent_id, status=dept.status
            )
            for dept in flat_depts
        }
        roots: List[SysDeptTreeResponse] = []
        for dept in flat_depts:
            node = tree_map[dept.id]
            if dept.parent_id and dept.parent_id in tree_map:
                tree_map[dept.parent_id].children.append(node)
            else:
                roots.append(node)
        return roots

    @staticmethod
    async def get_dept_tree(
        db: AsyncSession, *, only_active: bool = False
    ) -> List[SysDeptResponseData]:
        flat = await DeptService.get_all_depts(db, only_active=only_active)
        return DeptService._build_response_tree(flat)

    @staticmethod
    async def get_dept_tree_simple(
        db: AsyncSession, *, only_active: bool = False
    ) -> List[SysDeptTreeResponse]:
        flat = await DeptService.get_all_depts(db, only_active=only_active)
        return DeptService._build_simple_tree(flat)

    @staticmethod
    async def get_dept(db: AsyncSession, dept_id: int) -> SysDept:
        logger.debug("获取部门信息，部门ID: %s", dept_id)

        result = await db.execute(select(SysDept).where(SysDept.id == dept_id))
        dept = result.scalar_one_or_none()
        if not dept:
            logger.warning("部门不存在，部门ID: %s", dept_id)
            raise NotFoundError(msg=f"部门 {dept_id} 不存在")
        return dept

    @staticmethod
    async def create_dept(db: AsyncSession, dept_create: SysDeptCreate) -> SysDept:
        logger.info("创建部门，部门名: %s", dept_create.name)

        if dept_create.code:
            existing = await db.execute(
                select(SysDept).where(SysDept.code == dept_create.code)
            )
            if existing.scalar_one_or_none():
                raise ConflictError(msg="部门编码已存在")

        if dept_create.parent_id:
            await DeptService.get_dept(db, dept_create.parent_id)

        dept = SysDept(
            parent_id=dept_create.parent_id,
            name=dept_create.name,
            code=dept_create.code,
            status=dept_create.status,
            sort=dept_create.sort,
        )
        db.add(dept)
        await db.commit()
        await db.refresh(dept)

        _invalidate_data_scope_cache()
        logger.info("创建部门成功，部门ID: %s", dept.id)
        return dept

    @staticmethod
    async def update_dept(
        db: AsyncSession, dept_id: int, dept_update: SysDeptUpdate
    ) -> SysDept:
        logger.info("更新部门信息，部门ID: %s", dept_id)

        dept = await DeptService.get_dept(db, dept_id)

        if dept_update.parent_id is not None and dept_update.parent_id == dept_id:
            raise ValidationError(msg="不能将自身的父部门设为自己")

        if dept_update.code is not None and dept_update.code != dept.code:
            existing = await db.execute(
                select(SysDept).where(
                    SysDept.code == dept_update.code, SysDept.id != dept_id
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictError(msg="部门编码已存在")

        update_data = dept_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(dept, key) and value is not None:
                setattr(dept, key, value)

        await db.commit()
        await db.refresh(dept)

        _invalidate_data_scope_cache()
        logger.info("更新部门信息成功，部门ID: %s", dept_id)
        return dept

    @staticmethod
    async def delete_dept(db: AsyncSession, dept_id: int) -> bool:
        logger.info("删除部门，部门ID: %s", dept_id)

        dept = await DeptService.get_dept(db, dept_id)

        children_result = await db.execute(
            select(SysDept.id).where(SysDept.parent_id == dept_id).limit(1)
        )
        if children_result.scalar_one_or_none() is not None:
            raise ValidationError(msg="存在子部门，不能删除")

        from database.models.sys.user import SysUser
        users_result = await db.execute(
            select(SysUser.id).where(SysUser.dept_id == dept_id).limit(1)
        )
        if users_result.scalar_one_or_none() is not None:
            raise ValidationError(msg="部门下存在用户，不能删除")

        await db.delete(dept)
        await db.commit()

        _invalidate_data_scope_cache()
        logger.info("删除部门成功，部门ID: %s", dept_id)
        return True

    @staticmethod
    async def batch_delete_depts(db: AsyncSession, dept_ids: List[int]) -> int:
        logger.info("批量删除部门，部门ID列表: %s", dept_ids)
        delete_count = 0
        for dept_id in dept_ids:
            try:
                await DeptService.delete_dept(db, dept_id)
                delete_count += 1
            except Exception as e:
                logger.error(f"删除部门失败，部门ID: {dept_id}, 错误: {str(e)}")
                raise
        return delete_count

    @staticmethod
    async def batch_update_depts_status(
        db: AsyncSession, dept_ids: List[int], status: bool
    ) -> int:
        logger.info("批量更新部门状态，部门ID列表: %s, 状态: %s", dept_ids, status)

        result = await db.execute(select(SysDept).where(SysDept.id.in_(dept_ids)))
        depts = result.scalars().all()

        update_count = 0
        for dept in depts:
            dept.status = status
            update_count += 1

        await db.commit()
        _invalidate_data_scope_cache()

        return update_count
