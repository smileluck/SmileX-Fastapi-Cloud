#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from fastapi import FastAPI

from plugins.base import PluginBase
from plugins.multi_tenant.models.tenant import Tenant, sys_user_tenant_association
from plugins.multi_tenant.database.tenant_filter import setup_tenant_filter_plug
from plugins.multi_tenant.middleware.tenant_middleware import TenantContextMiddleware

logger = logging.getLogger(__name__)

# 严格租户隔离的表（查询只返回当前租户数据）
TENANT_STRICT_TABLES = [
    "sys_role",
    "sys_file",
    "app_user",
    "sys_operation_log",
    "sys_login_log",
    "sys_dept",
]

# 可选租户隔离的表（查询返回当前租户 + 全局数据，tenant_id IS NULL 为全局）
TENANT_OPTIONAL_TABLES = [
    "sys_menu",
    "sys_notice",
]

# 所有需要添加 tenant_id 列的表
TENANT_SCOPED_TABLES = TENANT_STRICT_TABLES + TENANT_OPTIONAL_TABLES

# 模型路径映射
MODEL_MAP = {
    "sys_role": "database.models.sys.role:SysRole",
    "sys_file": "database.models.sys.file:SysFile",
    "app_user": "database.models.business.user:AppUser",
    "sys_operation_log": "database.models.sys.operation_log:SysOperationLog",
    "sys_login_log": "database.models.sys.login_log:SysLoginLog",
    "sys_menu": "database.models.sys.menu:SysMenu",
    "sys_notice": "database.models.sys.notice:SysNotice",
    "sys_dept": "database.models.sys.dept:SysDept",
}


def _import_model(model_path: str):
    """动态导入模型类"""
    import importlib

    module_path, class_name = model_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class MultiTenantPlugin(PluginBase):
    """多租户插件"""

    name = "multi_tenant"
    version = "1.1.0"
    description = "多租户隔离插件，支持行级数据隔离和租户管理"

    # ---- Alembic 模型注册 ----

    def register_alembic_models(self) -> None:
        """
        在 alembic autogenerate 前调用。
        导入插件模型 → 注册到 Base.metadata。
        给已有模型的表追加 tenant_id 列 → autogenerate 检测到差异生成 ADD COLUMN。
        """
        from plugins.models import PluginRegistry
        from plugins.multi_tenant.models.tenant import Tenant, sys_user_tenant_association
        from sqlalchemy import BigInteger, Column

        # 给目标模型动态追加 tenant_id 列
        for table_name, model_path in MODEL_MAP.items():
            model_cls = _import_model(model_path)

            if "tenant_id" not in model_cls.__table__.columns:
                model_cls.__table__.append_column(
                    Column(
                        "tenant_id",
                        BigInteger,
                        nullable=True,
                        comment="租户ID",
                    )
                )
                logger.info("  alembic: 为 %s 追加 tenant_id 列", table_name)

    # ---- 安装 / 卸载 ----

    async def on_install(self) -> None:
        """
        安装：创建默认租户，迁移现有数据，分配超级管理员，种子菜单。
        要求 alembic 迁移已执行（表和列已存在）。
        """
        from database.db_manager import get_session
        from sqlalchemy import text
        from database.utils.snowflake import snowflake
        from database.utils.timezone import timezone

        async for db in get_session():
            # 1. 创建默认租户
            result = await db.execute(
                text("SELECT id FROM sys_tenant WHERE code = 'default' LIMIT 1")
            )
            existing = result.scalar_one_or_none()
            if existing:
                tenant_id = existing
                print(f"  默认租户已存在 (ID: {tenant_id})")
            else:
                tenant_id = snowflake.generate()
                now = timezone.now()
                await db.execute(
                    text(
                        "INSERT INTO sys_tenant (id, name, code, status, max_users, created_at) "
                        "VALUES (:id, '默认租户', 'default', true, 9999, :now)"
                    ),
                    {"id": tenant_id, "now": now},
                )
                print(f"  默认租户创建成功 (ID: {tenant_id})")

            # 2. 迁移严格隔离的表数据到默认租户
            for table in TENANT_STRICT_TABLES:
                await self._migrate_strict_table(db, table, tenant_id)

            # 3. optional 表保持 tenant_id = NULL（全局数据不变）
            for table in TENANT_OPTIONAL_TABLES:
                print(f"  {table}: 全局表，保持 tenant_id = NULL")

            # 4. 分配超级管理员到默认租户
            await self._assign_superuser(db, tenant_id)

            # 5. 种子菜单
            await self._seed_menus(db)

            await db.commit()
            print("  多租户插件安装完成")

        # 6. 安装前端文件
        self._install_frontend()

    async def _migrate_strict_table(self, db, table: str, tenant_id: int) -> None:
        """迁移严格隔离表的数据到默认租户"""
        from sqlalchemy import text

        try:
            col_check = await db.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = :table AND column_name = 'tenant_id'"
                ),
                {"table": table},
            )
            if col_check.scalar_one_or_none():
                result = await db.execute(
                    text(
                        f"UPDATE {table} SET tenant_id = :tid "
                        f"WHERE tenant_id = 0 OR tenant_id IS NULL"
                    ),
                    {"tid": tenant_id},
                )
                if result.rowcount > 0:
                    print(f"  {table}: 迁移 {result.rowcount} 条记录")
            else:
                print(f"  {table}: tenant_id 列不存在，跳过")
        except Exception as e:
            print(f"  {table}: 迁移失败 - {e}")

    async def _assign_superuser(self, db, tenant_id: int) -> None:
        """分配超级管理员到默认租户"""
        from sqlalchemy import text

        result = await db.execute(
            text("SELECT id FROM sys_user WHERE is_superuser = true LIMIT 1")
        )
        superuser_id = result.scalar_one_or_none()
        if superuser_id:
            check = await db.execute(
                text(
                    "SELECT 1 FROM sys_user_tenant "
                    "WHERE user_id = :uid AND tenant_id = :tid"
                ),
                {"uid": superuser_id, "tid": tenant_id},
            )
            if not check.scalar_one_or_none():
                await db.execute(
                    text(
                        "INSERT INTO sys_user_tenant (user_id, tenant_id, role) "
                        "VALUES (:uid, :tid, 'owner')"
                    ),
                    {"uid": superuser_id, "tid": tenant_id},
                )
                print(f"  超级管理员 (ID: {superuser_id}) 已分配到默认租户")

    async def on_uninstall(self) -> None:
        """卸载：清理种子菜单数据，删除前端文件"""
        from database.db_manager import get_session
        from sqlalchemy import text

        async for db in get_session():
            await db.execute(
                text("DELETE FROM sys_menu WHERE permission LIKE 'tenant:%'")
            )
            await db.execute(
                text("DELETE FROM sys_menu WHERE path = '/manage/tenant' OR name = 'manage_tenant'")
            )
            await db.execute(
                text("DELETE FROM sys_menu WHERE path = '/manage/tenant-config' OR name = 'tenant_config'")
            )
            await db.commit()
            print("  已清理租户管理菜单数据")

        # 删除前端文件
        self._uninstall_frontend()

    async def _seed_menus(self, db) -> None:
        """插入租户管理菜单种子数据"""
        from database.models.sys.menu import SysMenu, MenuType
        from sqlalchemy import select

        # 检查是否已存在
        result = await db.execute(
            select(SysMenu.id).where(SysMenu.name == "tenant").limit(1)
        )
        if result.scalar_one_or_none():
            return

        # 目录：租户管理（tenant_id=NULL 表示全局菜单，所有租户可见）
        catalog = SysMenu(
            parent_id=None,
            name="tenant",
            path="/manage/tenant",
            component="layout.base",
            redirect="/manage/tenant/list",
            permission=None,
            meta_icon="ic-outline-business",
            type=MenuType.CATALOG,
            sort=90,
        )
        db.add(catalog)
        await db.flush()

        # 菜单：租户列表
        menu = SysMenu(
            parent_id=catalog.id,
            name="tenant_list",
            path="/manage/tenant/list",
            component="view.manage_tenant",
            redirect=None,
            permission="tenant:tenant:list",
            meta_icon="ic-outline-business",
            type=MenuType.MENU,
            sort=1,
        )
        db.add(menu)
        await db.flush()

        # 按钮
        buttons = [
            ("tenant:tenant:add", "新增租户"),
            ("tenant:tenant:edit", "编辑租户"),
            ("tenant:tenant:delete", "删除租户"),
            ("tenant:tenant:detail", "租户详情"),
            ("tenant:tenant:status", "租户状态"),
            ("tenant:tenant:assign", "分配用户"),
            ("tenant:tenant:users", "租户用户"),
            ("tenant:tenant:remove", "移除用户"),
        ]
        for perm, label in buttons:
            btn = SysMenu(
                parent_id=menu.id,
                name=label,
                path="",
                component=None,
                redirect=None,
                permission=perm,
                meta_icon=None,
                type=MenuType.BUTTON,
                sort=0,
            )
            db.add(btn)

        # 菜单：租户配置
        config_menu = SysMenu(
            parent_id=catalog.id,
            name="tenant_config",
            path="/manage/tenant-config",
            component="view.manage_tenant-config",
            redirect=None,
            permission="tenant:tenant:config",
            meta_icon="ic-outline-settings",
            type=MenuType.MENU,
            sort=2,
        )
        db.add(config_menu)

    # ---- 激活 ----

    def on_activate(self, app: FastAPI) -> None:
        from database.models.sys.user import SysUser
        from plugins.multi_tenant.models.tenant import Tenant
        from plugins.multi_tenant.database.tenant_filter import (
            register_tenant_strict,
            register_tenant_optional,
        )
        from sqlalchemy.orm import relationship

        # 双向设置 Tenant.users 和 SysUser.tenants
        if not hasattr(SysUser, "tenants"):
            SysUser.tenants = relationship(
                "Tenant",
                secondary=sys_user_tenant_association,
                back_populates="users",
                lazy="noload",
                default_factory=list,
            )
        if not hasattr(Tenant, "users") or not isinstance(
            getattr(Tenant, "users", None), property
        ):
            Tenant.users = relationship(
                "SysUser",
                secondary=sys_user_tenant_association,
                back_populates="tenants",
                lazy="noload",
                default_factory=list,
            )

        # 为所有需要租户隔离的模型动态追加 tenant_id Mapped 属性
        from sqlalchemy import BigInteger
        from sqlalchemy.orm import column_property

        for table_name in TENANT_SCOPED_TABLES:
            model_cls = _import_model(MODEL_MAP[table_name])
            if "tenant_id" not in model_cls.__mapper__.columns:
                # 确保表也有该列
                if "tenant_id" not in model_cls.__table__.columns:
                    from sqlalchemy import Column
                    model_cls.__table__.append_column(
                        Column("tenant_id", BigInteger, nullable=True, comment="租户ID"),
                    )
                # 通过 mapper.add_property 将已有列注册为 ORM 属性
                model_cls.__mapper__.add_property(
                    "tenant_id",
                    model_cls.__table__.c.tenant_id,
                )

        # 注册严格隔离模型
        for table_name in TENANT_STRICT_TABLES:
            model_cls = _import_model(MODEL_MAP[table_name])
            register_tenant_strict(model_cls)

        # 注册可选隔离模型
        for table_name in TENANT_OPTIONAL_TABLES:
            model_cls = _import_model(MODEL_MAP[table_name])
            register_tenant_optional(model_cls)

        logger.info(
            "多租户插件已激活 (strict: %d, optional: %d)",
            len(TENANT_STRICT_TABLES),
            len(TENANT_OPTIONAL_TABLES),
        )

    # ---- 注册 ----

    def register_routes(self, app: FastAPI) -> None:
        from plugins.multi_tenant.router import router
        app.include_router(router)

    def register_middleware(self, app: FastAPI) -> None:
        app.add_middleware(TenantContextMiddleware)

    def register_database_plugins(self) -> None:
        setup_tenant_filter_plug()
        logger.info("租户数据过滤插件已注册")

    # ---- 前端文件管理 ----

    def _frontend_plugin_dir(self) -> str:
        """后端插件目录中的前端文件存储路径"""
        import os
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "frontend"
        )

    def _frontend_src_dir(self) -> str:
        """前端源码树根路径"""
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(os.path.dirname(backend_dir), "frontend", "src")

    def _install_frontend(self) -> None:
        """复制前端插件文件到前端源码树"""
        import shutil
        import os

        src = self._frontend_plugin_dir()
        dst = self._frontend_src_dir()

        if not os.path.exists(src):
            print("  前端文件目录不存在，跳过")
            return

        # 复制 views
        src_views = os.path.join(src, "views")
        dst_views = os.path.join(dst, "views")
        if os.path.exists(src_views):
            # 复制 manage/tenant
            src_tenant = os.path.join(src_views, "manage", "tenant")
            dst_tenant = os.path.join(dst_views, "manage", "tenant")
            if os.path.exists(src_tenant):
                os.makedirs(os.path.dirname(dst_tenant), exist_ok=True)
                shutil.copytree(src_tenant, dst_tenant, dirs_exist_ok=True)
                print(f"  前端视图已复制: views/manage/tenant/")

            # 复制 manage/tenant-config
            src_tenant_config = os.path.join(src_views, "manage", "tenant-config")
            dst_tenant_config = os.path.join(dst_views, "manage", "tenant-config")
            if os.path.exists(src_tenant_config):
                os.makedirs(os.path.dirname(dst_tenant_config), exist_ok=True)
                shutil.copytree(src_tenant_config, dst_tenant_config, dirs_exist_ok=True)
                print(f"  前端视图已复制: views/manage/tenant-config/")

        # 复制 plugins (API, store, components, index.ts)
        src_plugins = os.path.join(src, "plugins", "multi_tenant")
        dst_plugins = os.path.join(dst, "plugins", "multi_tenant")
        if os.path.exists(src_plugins):
            os.makedirs(os.path.dirname(dst_plugins), exist_ok=True)
            shutil.copytree(src_plugins, dst_plugins, dirs_exist_ok=True)
            print(f"  前端插件已复制: plugins/multi_tenant/")

        print("  前端文件安装完成（需重新构建前端）")

    def _uninstall_frontend(self) -> None:
        """删除前端源码树中的插件文件"""
        import shutil
        import os

        dst = self._frontend_src_dir()

        # 删除 views/manage/tenant
        tenant_views = os.path.join(dst, "views", "manage", "tenant")
        if os.path.exists(tenant_views):
            shutil.rmtree(tenant_views)
            print("  已删除 views/manage/tenant/")

        # 删除 views/manage/tenant-config
        tenant_config_views = os.path.join(dst, "views", "manage", "tenant-config")
        if os.path.exists(tenant_config_views):
            shutil.rmtree(tenant_config_views)
            print("  已删除 views/manage/tenant-config/")

        # 删除 plugins/multi_tenant
        tenant_plugins = os.path.join(dst, "plugins", "multi_tenant")
        if os.path.exists(tenant_plugins):
            shutil.rmtree(tenant_plugins)
            print("  已删除 plugins/multi_tenant/")

        print("  前端文件已清理（需重新构建前端）")
