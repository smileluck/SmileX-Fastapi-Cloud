from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import sys
import io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from database.models.base import Base

# Import all models to ensure they are registered with Base
from database.models.sys.user import SysUser
from database.models.sys.role import SysRole
from database.models.sys.menu import SysMenu
from database.models.sys.merchant import SysMerchant
from database.models.sys.config import SysConfig
from database.models.sys.dict import SysDict, SysDictItem
from database.models.sys.association_tables import (
    sys_user_role_association,
    sys_role_menu_association,
)
from database.models.sys.operation_log import SysOperationLog
from database.models.sys.export_task import SysExportTask
from database.models.sys.export_template import SysExportTemplate
from database.models.sys.ip_blacklist import SysIpBlacklist
from database.models.sys.file import SysFile
from database.models.sys.notice import SysNotice
from database.models.sys.notice_read import SysNoticeRead
from database.models.sys.login_log import SysLoginLog
from database.models.business.user import AppUser
from database.models.sys.scheduled_task import SysScheduledTask
from database.models.sys.task_log import SysScheduledTaskLog

# Set target_metadata to Base.metadata
target_metadata = Base.metadata

# 让 alembic 使用与运行时一致的环境配置（.env.{ENVIR}），而非 alembic.ini 中硬编码的 sqlalchemy.url。
# core.config.settings 由 load_config() 按 ENVIR 加载对应 .env.{env} 文件；
# alembic 迁移走同步驱动，故 build_url(async_mode=False)。
from core.config import settings as app_settings

_db_url = app_settings.DATABASE.build_url(async_mode=False)
config.set_main_option("sqlalchemy.url", _db_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need to DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate it with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
