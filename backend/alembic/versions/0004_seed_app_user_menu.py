"""seed app_user admin menu

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28

为"应用用户管理"后台模块插入菜单 + 4 个权限按钮种子。
仅插菜单记录，不向 sys_role_menu_association 分配任何角色 ——
上线后由运维在角色管理页为目标角色勾选。
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 系统管理目录 id（与 0002 种子保持一致）
_SYS_MANAGE_PARENT_ID = 2874692539129857

_APP_USER_MENU_ROWS = [
    {
        'id': 2942406616003001,
        'parent_id': _SYS_MANAGE_PARENT_ID,
        'name': 'manage_app_user',
        'path': '/manage/app-user',
        'component': 'view.manage_app-user',
        'redirect': None,
        'permission': 'sys:app_user:list',
        'meta_icon': 'ic:outline-people-alt',
        'meta_hidden': False,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'MENU',
        'sort': 12,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': datetime(2026, 7, 28, 10, 0, 0),
        'updated_at': None,
    },
    {
        'id': 2942406616003002,
        'parent_id': 2942406616003001,
        'name': 'manage_app_user_list',
        'path': None,
        'component': None,
        'redirect': None,
        'permission': 'sys:app_user:list',
        'meta_icon': None,
        'meta_hidden': True,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'BUTTON',
        'sort': 1,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': datetime(2026, 7, 28, 10, 0, 0),
        'updated_at': None,
    },
    {
        'id': 2942406616003003,
        'parent_id': 2942406616003001,
        'name': 'manage_app_user_add',
        'path': None,
        'component': None,
        'redirect': None,
        'permission': 'sys:app_user:add',
        'meta_icon': None,
        'meta_hidden': True,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'BUTTON',
        'sort': 2,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': datetime(2026, 7, 28, 10, 0, 0),
        'updated_at': None,
    },
    {
        'id': 2942406616003004,
        'parent_id': 2942406616003001,
        'name': 'manage_app_user_edit',
        'path': None,
        'component': None,
        'redirect': None,
        'permission': 'sys:app_user:edit',
        'meta_icon': None,
        'meta_hidden': True,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'BUTTON',
        'sort': 3,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': datetime(2026, 7, 28, 10, 0, 0),
        'updated_at': None,
    },
    {
        'id': 2942406616003005,
        'parent_id': 2942406616003001,
        'name': 'manage_app_user_delete',
        'path': None,
        'component': None,
        'redirect': None,
        'permission': 'sys:app_user:delete',
        'meta_icon': None,
        'meta_hidden': True,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'BUTTON',
        'sort': 4,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': datetime(2026, 7, 28, 10, 0, 0),
        'updated_at': None,
    },
]

_APP_USER_MENU_IDS = [row['id'] for row in _APP_USER_MENU_ROWS]


def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            'sys_menu',
            sa.column('id', sa.BigInteger),
            sa.column('parent_id', sa.BigInteger),
            sa.column('name', sa.String),
            sa.column('path', sa.String),
            sa.column('component', sa.String),
            sa.column('redirect', sa.String),
            sa.column('permission', sa.String),
            sa.column('meta_icon', sa.String),
            sa.column('meta_hidden', sa.Boolean),
            sa.column('meta_affix', sa.Boolean),
            sa.column('meta_breadcrumb', sa.Boolean),
            sa.column('status', sa.Boolean),
            sa.column('type', sa.String),
            sa.column('sort', sa.Integer),
            sa.column('is_system', sa.Boolean),
            sa.column('meta_href', sa.String),
            sa.column('meta_keep_alive', sa.Boolean),
            sa.column('deleted_at', sa.DateTime),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        _APP_USER_MENU_ROWS,
    )


def downgrade() -> None:
    op.execute(
        f"DELETE FROM sys_menu WHERE id IN ({', '.join(str(i) for i in _APP_USER_MENU_IDS)})"
    )
