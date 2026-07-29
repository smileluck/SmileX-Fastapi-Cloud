"""seed business menu + app_user

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-28

新增"业务管理"顶级目录(CATALOG)，应用用户管理菜单挂其下。
仅插菜单记录，不向 sys_role_menu_association 分配任何角色 ——
上线后由运维在角色管理页为目标角色勾选。

注意：菜单 name 与前端 elegant-router 路由名保持一致（含连字符），
否则前端按菜单 name 找不到组件与 i18n（参照 manage_ip-blacklist 先例）。
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 业务管理顶级目录 id（parent_id=None）
_SYS_BUSINESS_DIR_ID = 2942406616004001
# 应用用户管理菜单 id（挂在业务管理下）
_APP_USER_MENU_ID = 2942406616004002

_DT = datetime(2026, 7, 28, 10, 0, 0)

_APP_USER_MENU_ROWS = [
    # 业务管理目录（CATALOG）
    {
        'id': _SYS_BUSINESS_DIR_ID,
        'parent_id': None,
        'name': 'business',
        'path': '/business',
        'component': 'layout.base',
        'redirect': None,
        'permission': None,
        'meta_icon': 'mdi:briefcase-outline',
        'meta_hidden': False,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'CATALOG',
        'sort': 3,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': _DT,
        'updated_at': None,
    },
    # 应用用户管理（MENU，挂在业务管理目录下）
    {
        'id': _APP_USER_MENU_ID,
        'parent_id': _SYS_BUSINESS_DIR_ID,
        'name': 'business_app-user',
        'path': '/business/app-user',
        'component': 'view.business_app-user',
        'redirect': None,
        'permission': 'sys:app_user:list',
        'meta_icon': 'mdi:account-group-outline',
        'meta_hidden': False,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': 'MENU',
        'sort': 1,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': _DT,
        'updated_at': None,
    },
    # 4 个权限按钮（BUTTON），挂在应用用户管理菜单下
    {
        'id': 2942406616004003,
        'parent_id': _APP_USER_MENU_ID,
        'name': 'business_app-user_list',
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
        'created_at': _DT,
        'updated_at': None,
    },
    {
        'id': 2942406616004004,
        'parent_id': _APP_USER_MENU_ID,
        'name': 'business_app-user_add',
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
        'created_at': _DT,
        'updated_at': None,
    },
    {
        'id': 2942406616004005,
        'parent_id': _APP_USER_MENU_ID,
        'name': 'business_app-user_edit',
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
        'created_at': _DT,
        'updated_at': None,
    },
    {
        'id': 2942406616004006,
        'parent_id': _APP_USER_MENU_ID,
        'name': 'business_app-user_delete',
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
        'created_at': _DT,
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
