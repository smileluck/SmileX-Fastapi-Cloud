"""seed demo_openapi-test menu under demo CATALOG

Revision ID: 0010
Revises: 0009
Create Date: 2026-07-05

在「示例」(demo) 目录下新增「OpenAPI 测试」菜单，提供一个浏览器内构造 HMAC
签名并调用 /open/* 的调试页面。仅菜单播种，无表结构变更。
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0010'
down_revision: Union[str, Sequence[str], None] = '0009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# demo CATALOG 与 0002_seed_data.py 保持一致
DEMO_DIR_ID = 2907499345027072
OPENAPI_TEST_MENU_ID = 2942406616000030
ALL_NEW_MENU_IDS = [OPENAPI_TEST_MENU_ID]

ADMIN_ROLE_ID = 2874692539129900


def _menu_rows() -> list[dict]:
    now = datetime(2026, 7, 5, 14, 0, 0)
    base = {
        'parent_id': DEMO_DIR_ID,
        'redirect': None,
        'permission': None,
        'meta_hidden': False,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'updated_at': None,
    }
    return [
        {
            **base,
            'id': OPENAPI_TEST_MENU_ID,
            'name': 'demo_openapi-test',
            'path': '/demo/openapi-test',
            'component': 'view.demo_openapi-test',
            'meta_icon': 'mdi:link-variant',
            'type': 'MENU',
            'sort': 3,
            'created_at': now,
        },
    ]


def upgrade() -> None:
    bind = op.get_bind()

    existing = bind.execute(
        sa.text("SELECT id FROM sys_menu WHERE id = :id"),
        {"id": OPENAPI_TEST_MENU_ID},
    ).scalar_one_or_none()
    if existing is not None:
        return

    sys_menu = sa.Table(
        'sys_menu',
        sa.MetaData(),
        sa.Column('id', sa.BigInteger),
        sa.Column('parent_id', sa.BigInteger),
        sa.Column('name', sa.String),
        sa.Column('path', sa.String),
        sa.Column('component', sa.String),
        sa.Column('redirect', sa.String),
        sa.Column('permission', sa.String),
        sa.Column('meta_icon', sa.String),
        sa.Column('meta_hidden', sa.Boolean),
        sa.Column('meta_affix', sa.Boolean),
        sa.Column('meta_breadcrumb', sa.Boolean),
        sa.Column('status', sa.Boolean),
        sa.Column('type', sa.String),
        sa.Column('sort', sa.Integer),
        sa.Column('is_system', sa.Boolean),
        sa.Column('meta_href', sa.String),
        sa.Column('meta_keep_alive', sa.Boolean),
        sa.Column('deleted_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )
    bind.execute(sys_menu.insert(), _menu_rows())

    admin_exists = bind.execute(
        sa.text("SELECT id FROM sys_role WHERE id = :rid"),
        {"rid": ADMIN_ROLE_ID},
    ).scalar_one_or_none()
    if admin_exists is not None:
        sys_role_menu = sa.Table(
            'sys_role_menu',
            sa.MetaData(),
            sa.Column('role_id', sa.BigInteger),
            sa.Column('menu_id', sa.BigInteger),
            sa.Column('permission', sa.String),
        )
        bind.execute(
            sys_role_menu.insert(),
            [
                {'role_id': ADMIN_ROLE_ID, 'menu_id': mid, 'permission': 'read'}
                for mid in ALL_NEW_MENU_IDS
            ],
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text("DELETE FROM sys_role_menu WHERE menu_id IN :ids").bindparams(
            sa.bindparam('ids', expanding=True)
        ),
        {"ids": ALL_NEW_MENU_IDS},
    )
    bind.execute(
        sa.text("DELETE FROM sys_menu WHERE id IN :ids").bindparams(
            sa.bindparam('ids', expanding=True)
        ),
        {"ids": ALL_NEW_MENU_IDS},
    )
