#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
菜单管理服务
处理菜单相关的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_,Select
from sqlalchemy.orm import noload, joinedload, selectinload
from typing import List, Optional, Tuple

from sqlalchemy import func
from database.models.sys.menu import SysMenu, MenuType
from database.models.sys.user import SysUser
from database.models.sys.role import SysRole
from core.exception.errors import NotFoundError, ConflictError, ForbiddenError
from core.utils.memory_cache import get_memory_cache, CacheNamespace
from modules.admin.schemas.sys.menu import (
    SysMenuCreate,
    SysMenuUpdate,
    SysMenuQueryParams,
    SysMenuTreeResponse,
    SysMenuResponseData,
)

logger = logging.getLogger(__name__)


def _type_to_str(menu_type: MenuType) -> str:
    mapping = {MenuType.CATALOG: "1", MenuType.MENU: "2", MenuType.EXTERNAL: "2", MenuType.BUTTON: "3"}
    return mapping.get(menu_type, "1")


class MenuService:
    """
    菜单管理服务类
    """

    @staticmethod
    async def get_menu_list(
        db: AsyncSession,
        query_params: SysMenuQueryParams,
    ) -> List[SysMenu]:
        """
        获取菜单列表（带查询条件）

        Args:
            db: 数据库会话
            query_params: 查询参数

        Returns:
            菜单列表
        """
        logger.debug("获取菜单列表，查询参数: %s", query_params)

        # 构建基础查询
        base_query = select(SysMenu).options(
            noload(SysMenu.children),
            noload(SysMenu.parent),
            noload(SysMenu.roles),
        )
        conditions = []
        if query_params.status is not None:
            conditions.append(SysMenu.status == query_params.status)
        if query_params.name:
            conditions.append(SysMenu.name.like(f"%{query_params.name}%"))
        if query_params.type:
            conditions.append(SysMenu.type == query_params.type)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 添加排序
        base_query = base_query.order_by(SysMenu.sort, SysMenu.id)

        # 执行查询
        result = await db.execute(base_query)
        menus = result.scalars().all()

        logger.debug("获取菜单列表成功，共 %s 条记录", len(menus))
        return menus

    @staticmethod
    def build_menu_query(
        query_params: SysMenuQueryParams,
    ) -> Select:
        """
        构建菜单查询对象

        Args:
            query_params: 查询参数

        Returns:
            SQLAlchemy查询对象
        """
        # 构建基础查询（抑制模型级 selectin 自动联查）
        base_query = select(SysMenu).options(
            noload(SysMenu.children),
            noload(SysMenu.parent),
            noload(SysMenu.roles),
        )

        # 添加查询条件
        conditions = []
        if query_params.status is not None:
            conditions.append(SysMenu.status == query_params.status)
        if query_params.name:
            conditions.append(SysMenu.name.like(f"%{query_params.name}%"))
        if query_params.type:
            conditions.append(SysMenu.type == query_params.type)
        if query_params.is_system is not None:
            conditions.append(SysMenu.is_system == query_params.is_system)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        # 添加排序
        base_query = base_query.order_by(SysMenu.sort, SysMenu.id)

        return base_query

    @staticmethod
    async def get_menu_list_paginated(
        db: AsyncSession,
        query_params: SysMenuQueryParams,
        page: int = 1,
        page_size: int = 100,
    ) -> Tuple[List[SysMenu], int]:
        """
        获取菜单列表（带分页和查询条件）

        Args:
            db: 数据库会话
            query_params: 查询参数
            page: 页码
            page_size: 每页条数

        Returns:
            Tuple[菜单列表, 总记录数]
        """
        logger.debug(
            "获取菜单列表（分页），查询参数: %s, 页码: %s, 每页条数: %s",
            query_params, page, page_size,
        )

        # 构建查询
        base_query = MenuService.build_menu_query(query_params)

        # 统计总数
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # 分页
        offset = (page - 1) * page_size
        paginated_query = base_query.offset(offset).limit(page_size)

        # 执行查询
        result = await db.execute(paginated_query)
        menus = result.scalars().all()

        logger.debug(
            "获取菜单列表（分页）成功，共 %s 条记录，当前页 %s 条",
            total, len(menus),
        )
        return menus, total

    @staticmethod
    async def get_menu_tree(
        db: AsyncSession,
        status: Optional[bool] = None,
    ) -> List[SysMenuTreeResponse]:
        """
        获取菜单树结构

        Args:
            db: 数据库会话
            status: 状态筛选

        Returns:
            菜单树结构
        """
        logger.debug("获取菜单树结构，状态: %s", status)

        # 先获取所有菜单
        base_query = select(SysMenu).options(
            noload(SysMenu.children),
            noload(SysMenu.parent),
            noload(SysMenu.roles),
        ).order_by(SysMenu.sort, SysMenu.id)
        if status is not None:
            base_query = base_query.where(SysMenu.status == status)

        result = await db.execute(base_query)
        menus = result.scalars().all()

        # 构建菜单字典映射
        menu_map = {}
        root_menus = []

        # 首先创建所有菜单的响应模型实例
        for menu in menus:
            menu_response = SysMenuTreeResponse(
                id=menu.id,
                label=menu.name,
                pId=menu.parent_id,
                menuType=_type_to_str(menu.type),
                children=[],
            )
            menu_map[menu.id] = menu_response

        # 构建树结构
        for menu in menus:
            menu_response = menu_map[menu.id]
            if not menu.parent_id:
                root_menus.append(menu_response)
            else:
                parent = menu_map.get(menu.parent_id)
                if parent:
                    parent.children.append(menu_response)

        logger.debug("获取菜单树结构成功，共 %s 个根菜单", len(root_menus))
        return root_menus

    @staticmethod
    async def get_menu(db: AsyncSession, menu_id: int) -> SysMenu:
        """
        获取单个菜单

        Args:
            db: 数据库会话
            menu_id: 菜单ID

        Returns:
            菜单对象

        Raises:
            NotFoundError: 菜单不存在
        """
        logger.debug("获取菜单信息，菜单ID: %s", menu_id)

        result = await db.execute(
            select(SysMenu)
            .options(
                noload(SysMenu.children),
                noload(SysMenu.parent),
                noload(SysMenu.roles),
            )
            .where(SysMenu.id == menu_id)
        )
        menu = result.scalar_one_or_none()

        if not menu:
            logger.warning("菜单不存在，菜单ID: %s", menu_id)
            raise NotFoundError(msg=f"菜单 {menu_id} 不存在")

        logger.debug("获取菜单信息成功，菜单名称: %s", menu.name)
        return menu

    @staticmethod
    async def create_menu(db: AsyncSession, menu_create: SysMenuCreate, *, is_superuser: bool = False) -> SysMenu:
        """
        创建菜单

        Args:
            db: 数据库会话
            menu_create: 菜单创建请求模型

        Returns:
            创建后的菜单对象

        Raises:
            NotFoundError: 父菜单不存在
            ConflictError: 菜单名称已存在
        """
        logger.info("创建菜单，菜单名称: %s", menu_create.name)

        # 检查父菜单是否存在
        if menu_create.parent_id:
            result = await db.execute(
                select(SysMenu)
                .options(
                    noload(SysMenu.children),
                    noload(SysMenu.parent),
                    noload(SysMenu.roles),
                )
                .where(SysMenu.id == menu_create.parent_id)
            )
            parent_menu = result.scalar_one_or_none()
            if not parent_menu:
                logger.warning("创建菜单失败，父菜单不存在: %s", menu_create.parent_id)
                raise NotFoundError(msg=f"父菜单 {menu_create.parent_id} 不存在")

            # 按钮类型菜单的上级仅允许为菜单类型
            if menu_create.type == MenuType.BUTTON and parent_menu.type != MenuType.MENU:
                logger.warning("创建菜单失败，按钮类型菜单的上级仅允许为菜单类型: parent_type=%s", parent_menu.type)
                raise ConflictError(msg="按钮类型菜单的上级仅允许为菜单类型")

        # 按钮类型菜单必须指定上级菜单
        if menu_create.type == MenuType.BUTTON and not menu_create.parent_id:
            logger.warning("创建菜单失败，按钮类型菜单必须指定上级菜单")
            raise ConflictError(msg="按钮类型菜单必须指定上级菜单")

        # 创建菜单对象
        menu = SysMenu(
            parent_id=menu_create.parent_id,
            name=menu_create.name,
            path=menu_create.path,
            component=menu_create.component,
            redirect=menu_create.redirect,
            permission=menu_create.permission,
            meta_icon=menu_create.meta_icon,
            meta_icon_type=menu_create.meta_icon_type,
            meta_hidden=menu_create.meta_hidden,
            meta_affix=menu_create.meta_affix,
            meta_breadcrumb=menu_create.meta_breadcrumb,
            meta_href=menu_create.meta_href,
            meta_keep_alive=menu_create.meta_keep_alive,
            status=menu_create.status,
            type=menu_create.type,
            sort=menu_create.sort,
            is_system=False if not is_superuser else getattr(menu_create, 'is_system', False),
        )

        db.add(menu)
        await db.commit()
        get_memory_cache().invalidate(CacheNamespace.PERMISSION)
        await db.refresh(menu)

        logger.info("创建菜单成功，菜单ID: %s", menu.id)
        return menu

    @staticmethod
    async def update_menu(
        db: AsyncSession, menu_id: int, menu_update: SysMenuUpdate, *, is_superuser: bool = False
    ) -> SysMenu:
        """
        更新菜单

        Args:
            db: 数据库会话
            menu_id: 菜单ID
            menu_update: 菜单更新请求模型

        Returns:
            更新后的菜单对象

        Raises:
            NotFoundError: 菜单不存在或父菜单不存在
            ConflictError: 不能将自己设置为父菜单
        """
        logger.info("更新菜单信息，菜单ID: %s", menu_id)

        # 获取菜单
        menu = await MenuService.get_menu(db, menu_id)

        # 检查是否为系统内置菜单
        if menu.is_system and not is_superuser:
            logger.warning("更新菜单失败，不能修改系统内置菜单，菜单ID: %s", menu_id)
            raise ForbiddenError(msg="不能修改系统内置菜单")

        # 检查父菜单
        # 确定最终的菜单类型和父ID（优先使用更新值，否则用原值）
        final_type = menu_update.type if menu_update.type is not None else menu.type
        final_parent_id = menu_update.parent_id if menu_update.parent_id is not None else menu.parent_id

        # 按钮类型菜单必须指定上级菜单
        if final_type == MenuType.BUTTON and not final_parent_id:
            logger.warning("更新菜单失败，按钮类型菜单必须指定上级菜单")
            raise ConflictError(msg="按钮类型菜单必须指定上级菜单")

        if menu_update.parent_id is not None:
            # 不能将自己设置为父菜单
            if menu_update.parent_id == menu_id:
                logger.warning("更新菜单失败，不能将自己设置为父菜单: %s", menu_id)
                raise ConflictError(msg="不能将自己设置为父菜单")

            # 检查父菜单是否存在
            if menu_update.parent_id:
                result = await db.execute(
                    select(SysMenu)
                    .options(
                        noload(SysMenu.children),
                        noload(SysMenu.parent),
                        noload(SysMenu.roles),
                    )
                    .where(SysMenu.id == menu_update.parent_id)
                )
                parent_menu = result.scalar_one_or_none()
                if not parent_menu:
                    logger.warning(
                        "更新菜单失败，父菜单不存在: %s", menu_update.parent_id,
                    )
                    raise NotFoundError(msg=f"父菜单 {menu_update.parent_id} 不存在")

                # 按钮类型菜单的上级仅允许为菜单类型
                if final_type == MenuType.BUTTON and parent_menu.type != MenuType.MENU:
                    logger.warning("更新菜单失败，按钮类型菜单的上级仅允许为菜单类型: parent_type=%s", parent_menu.type)
                    raise ConflictError(msg="按钮类型菜单的上级仅允许为菜单类型")

                # 检查循环引用：向上遍历目标父菜单的祖先链，确保当前菜单不在其中
                ancestor_id = menu_update.parent_id
                checked = set()
                while ancestor_id and ancestor_id not in checked:
                    if ancestor_id == menu_id:
                        logger.warning("更新菜单失败，循环引用: 菜单 %s 的后代不能作为父菜单", menu_id)
                        raise ConflictError(msg="不能将自己的子菜单设置为父菜单")
                    checked.add(ancestor_id)
                    anc_result = await db.execute(
                        select(SysMenu.parent_id).where(SysMenu.id == ancestor_id)
                    )
                    ancestor_id = anc_result.scalar_one_or_none()

        # 更新菜单信息
        update_data = menu_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(menu, key):
                setattr(menu, key, value)

        await db.commit()
        get_memory_cache().invalidate(CacheNamespace.PERMISSION)
        await db.refresh(menu)

        logger.info("更新菜单信息成功，菜单ID: %s", menu_id)
        return menu

    @staticmethod
    async def delete_menu(db: AsyncSession, menu_id: int, *, is_superuser: bool = False) -> bool:
        """
        删除菜单

        Args:
            db: 数据库会话
            menu_id: 菜单ID

        Returns:
            是否删除成功

        Raises:
            NotFoundError: 菜单不存在
        """
        logger.info("删除菜单，菜单ID: %s", menu_id)

        # 获取菜单
        menu = await MenuService.get_menu(db, menu_id)

        # 检查是否为系统内置菜单
        if menu.is_system and not is_superuser:
            logger.warning("删除菜单失败，不能删除系统内置菜单，菜单ID: %s", menu_id)
            raise ForbiddenError(msg="不能删除系统内置菜单")

        await db.delete(menu)
        await db.commit()
        get_memory_cache().invalidate(CacheNamespace.PERMISSION)

        logger.info("删除菜单成功，菜单ID: %s", menu_id)
        return True

    @staticmethod
    async def batch_update_menus_status(
        db: AsyncSession, menu_ids: List[int], status: bool, *, is_superuser: bool = False
    ) -> int:
        """
        批量更新菜单状态

        Args:
            db: 数据库会话
            menu_ids: 菜单ID列表
            status: 要设置的状态

        Returns:
            更新的菜单数量
        """
        logger.info("批量更新菜单状态，菜单ID列表: %s, 状态: %s", menu_ids, status)

        # 获取菜单
        result = await db.execute(
            select(SysMenu)
            .options(
                noload(SysMenu.children),
                noload(SysMenu.parent),
                noload(SysMenu.roles),
            )
            .where(SysMenu.id.in_(menu_ids))
        )
        menus = result.scalars().all()

        # 更新状态
        update_count = 0
        for menu in menus:
            if not menu.is_system or is_superuser:
                menu.status = status
                update_count += 1
            else:
                logger.warning("不能修改系统内置菜单状态，菜单ID: %s", menu.id)

        await db.commit()
        get_memory_cache().invalidate(CacheNamespace.PERMISSION)

        logger.info("批量更新菜单状态成功，共更新 %s 个菜单", update_count)
        return update_count

    @staticmethod
    async def batch_delete_menus(db: AsyncSession, menu_ids: List[int], *, is_superuser: bool = False) -> int:
        """
        批量删除菜单

        Args:
            db: 数据库会话
            menu_ids: 菜单ID列表

        Returns:
            删除的菜单数量
        """
        logger.info("批量删除菜单，菜单ID列表: %s", menu_ids)

        delete_count = 0
        for menu_id in menu_ids:
            try:
                await MenuService.delete_menu(db, menu_id, is_superuser=is_superuser)
                delete_count += 1
            except NotFoundError:
                logger.warning("菜单不存在，跳过: %s", menu_id)
            except ForbiddenError as e:
                logger.warning("跳过系统内置菜单: %s", menu_id)
                raise e

        logger.info("批量删除菜单成功，共删除 %s 个菜单", delete_count)
        return delete_count

    @staticmethod
    async def get_user_menu_tree(
        db: AsyncSession, user: SysUser
    ) -> List[SysMenuTreeResponse]:
        """
        获取当前用户的菜单权限树

        Args:
            db: 数据库会话
            user: 当前用户

        Returns:
            菜单权限树
        """
        logger.debug("获取用户菜单权限树，用户ID: %s", user.id)

        if user.is_superuser:
            stmt = (
                select(SysMenu)
                .options(
                    noload(SysMenu.children),
                    noload(SysMenu.parent),
                    noload(SysMenu.roles),
                )
                .where(
                    SysMenu.type != MenuType.BUTTON,
                    SysMenu.status == True,
                )
                .order_by(SysMenu.sort, SysMenu.id)
            )
            result = await db.execute(stmt)
            menus = result.scalars().all()
        else:
            # 预加载 user.roles.menus
            stmt = (
                select(SysUser)
                .options(
                    joinedload(SysUser.roles).options(
                        joinedload(SysRole.menus)
                    )
                )
                .where(SysUser.id == user.id)
            )
            result = await db.execute(stmt)
            user_with_relations = result.unique().scalar_one()

            # 收集所有启用的非 BUTTON 菜单 ID
            menu_ids: set[int] = set()
            for role in user_with_relations.roles:
                if not role.status:
                    continue
                for menu in role.menus:
                    if menu.status and menu.type != MenuType.BUTTON:
                        menu_ids.add(menu.id)

            # 一次性加载 id->parent_id 映射，在内存中解析祖先
            if menu_ids:
                parent_result = await db.execute(
                    select(SysMenu.id, SysMenu.parent_id)
                )
                parent_map = dict(parent_result.all())
                queue = list(menu_ids)
                while queue:
                    current = queue.pop()
                    pid = parent_map.get(current)
                    if pid and pid not in menu_ids:
                        menu_ids.add(pid)
                        queue.append(pid)

            if not menu_ids:
                return []

            stmt = (
                select(SysMenu)
                .options(
                    noload(SysMenu.children),
                    noload(SysMenu.parent),
                    noload(SysMenu.roles),
                )
                .where(
                    SysMenu.id.in_(menu_ids),
                    SysMenu.status == True,
                )
                .order_by(SysMenu.sort, SysMenu.id)
            )
            result = await db.execute(stmt)
            menus = result.scalars().all()

        # 构建菜单树
        menu_map = {}
        root_menus = []

        for menu in menus:
            menu_response = SysMenuTreeResponse(
                id=menu.id,
                label=menu.name,
                pId=menu.parent_id,
                menuType=_type_to_str(menu.type),
                children=[],
            )
            menu_map[menu.id] = menu_response

        for menu in menus:
            menu_response = menu_map[menu.id]
            if not menu.parent_id:
                root_menus.append(menu_response)
            else:
                parent = menu_map.get(menu.parent_id)
                if parent:
                    parent.children.append(menu_response)

        logger.debug("获取用户菜单权限树成功，共 %s 个根菜单", len(root_menus))
        return root_menus

    @staticmethod
    async def get_user_assign_menu_tree(
        db: AsyncSession, user: SysUser
    ) -> List[SysMenuTreeResponse]:
        """
        获取当前用户可分配的菜单权限树（包含按钮类型）。
        超级用户返回全部菜单，普通用户仅返回自身角色拥有的菜单和按钮。

        Args:
            db: 数据库会话
            user: 当前用户

        Returns:
            菜单权限树（含按钮）
        """
        logger.debug("获取用户可分配菜单树，用户ID: %s", user.id)

        if user.is_superuser:
            stmt = (
                select(SysMenu)
                .options(
                    noload(SysMenu.children),
                    noload(SysMenu.parent),
                    noload(SysMenu.roles),
                )
                .where(SysMenu.status == True)
                .order_by(SysMenu.sort, SysMenu.id)
            )
            result = await db.execute(stmt)
            menus = result.scalars().all()
        else:
            # 预加载 user.roles.menus（包含按钮类型）
            stmt = (
                select(SysUser)
                .options(
                    joinedload(SysUser.roles).options(
                        joinedload(SysRole.menus)
                    )
                )
                .where(SysUser.id == user.id)
            )
            result = await db.execute(stmt)
            user_with_relations = result.unique().scalar_one()

            # 收集所有启用的菜单 ID（包含按钮）
            menu_ids: set[int] = set()
            for role in user_with_relations.roles:
                if not role.status:
                    continue
                for menu in role.menus:
                    if menu.status:
                        menu_ids.add(menu.id)

            # 补全祖先节点
            if menu_ids:
                parent_result = await db.execute(
                    select(SysMenu.id, SysMenu.parent_id)
                )
                parent_map = dict(parent_result.all())
                queue = list(menu_ids)
                while queue:
                    current = queue.pop()
                    pid = parent_map.get(current)
                    if pid and pid not in menu_ids:
                        menu_ids.add(pid)
                        queue.append(pid)

            if not menu_ids:
                return []

            stmt = (
                select(SysMenu)
                .options(
                    noload(SysMenu.children),
                    noload(SysMenu.parent),
                    noload(SysMenu.roles),
                )
                .where(
                    SysMenu.id.in_(menu_ids),
                    SysMenu.status == True,
                )
                .order_by(SysMenu.sort, SysMenu.id)
            )
            result = await db.execute(stmt)
            menus = result.scalars().all()

        # 构建菜单树
        menu_map = {}
        root_menus = []

        for menu in menus:
            menu_response = SysMenuTreeResponse(
                id=menu.id,
                label=menu.name,
                pId=menu.parent_id,
                menuType=_type_to_str(menu.type),
                children=[],
            )
            menu_map[menu.id] = menu_response

        for menu in menus:
            menu_response = menu_map[menu.id]
            if not menu.parent_id:
                root_menus.append(menu_response)
            else:
                parent = menu_map.get(menu.parent_id)
                if parent:
                    parent.children.append(menu_response)

        logger.debug("获取用户可分配菜单树成功，共 %s 个根菜单", len(root_menus))
        return root_menus

    @staticmethod
    async def get_user_permitted_menu_ids(
        db: AsyncSession, user: SysUser
    ) -> set[int]:
        """
        获取用户有权限的菜单 ID 集合（含按钮）。超管返回 None 表示全部允许。

        Args:
            db: 数据库会话
            user: 当前用户

        Returns:
            菜单 ID 集合，超管返回 None
        """
        if user.is_superuser:
            return None

        stmt = (
            select(SysUser)
            .options(
                joinedload(SysUser.roles).options(
                    joinedload(SysRole.menus)
                )
            )
            .where(SysUser.id == user.id)
        )
        result = await db.execute(stmt)
        user_with_relations = result.unique().scalar_one()

        menu_ids: set[int] = set()
        for role in user_with_relations.roles:
            if not role.status:
                continue
            for menu in role.menus:
                if menu.status:
                    menu_ids.add(menu.id)

        # 补全祖先节点
        if menu_ids:
            parent_result = await db.execute(
                select(SysMenu.id, SysMenu.parent_id)
            )
            parent_map = dict(parent_result.all())
            queue = list(menu_ids)
            while queue:
                current = queue.pop()
                pid = parent_map.get(current)
                if pid and pid not in menu_ids:
                    menu_ids.add(pid)
                    queue.append(pid)

        return menu_ids

    @staticmethod
    async def build_menu_tree_list(db: AsyncSession) -> List[SysMenuResponseData]:
        """
        获取菜单树形列表（包含完整菜单信息）

        Args:
            db: 数据库会话

        Returns:
            树形菜单列表
        """
        base_query = select(SysMenu).options(
            noload(SysMenu.children),
            noload(SysMenu.parent),
            noload(SysMenu.roles),
        ).order_by(SysMenu.sort, SysMenu.id)

        result = await db.execute(base_query)
        menus = result.scalars().all()

        # 转换为响应模型
        menu_map: dict[int, SysMenuResponseData] = {}
        for menu in menus:
            menu_map[menu.id] = SysMenuResponseData.model_validate(menu)

        # 构建树结构
        root_menus: List[SysMenuResponseData] = []
        for menu in menus:
            resp = menu_map[menu.id]
            if not menu.parent_id:
                root_menus.append(resp)
            else:
                parent = menu_map.get(menu.parent_id)
                if parent:
                    parent.children.append(resp)

        logger.debug("获取菜单树形列表成功，共 %s 个根菜单", len(root_menus))
        return root_menus
