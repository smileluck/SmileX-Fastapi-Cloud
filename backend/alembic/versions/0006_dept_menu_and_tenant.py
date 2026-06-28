"""add manage_dept menu seed and sys_dept.tenant_id column

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-27

补全部门管理菜单种子（2026-06-25 部门模块上线时遗漏），并给 sys_dept 表
追加 tenant_id 列，让多租户插件启用后可以按租户隔离部门数据。
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0006'
down_revision: Union[str, Sequence[str], None] = '0005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 菜单 ID 与 0002_seed_data.py 中保持一致
MANAGE_DIR_ID = 2874692539129857
DEPT_MENU_ID = 2942406616000001
DEPT_BUTTON_IDS = [
    2942406616000002,
    2942406616000003,
    2942406616000004,
    2942406616000005,
]
ALL_DEPT_MENU_IDS = [DEPT_MENU_ID] + DEPT_BUTTON_IDS

ADMIN_ROLE_ID = 2874692539129900


def _dept_menu_rows() -> list[dict]:
    now = datetime(2026, 6, 27, 10, 0, 0)
    base = {
        'parent_id': MANAGE_DIR_ID,
        'redirect': None,
        'meta_icon': 'ic:outline-account-tree',
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'updated_at': None,
    }
    rows = [
        {
            **base,
            'id': DEPT_MENU_ID,
            'name': 'manage_dept',
            'path': '/manage/dept',
            'component': 'view.manage_dept',
            'permission': 'sys:dept:list',
            'meta_hidden': False,
            'type': 'MENU',
            'sort': 6,
            'created_at': now,
        },
    ]
    buttons = [
        ('manage_dept_list', 'sys:dept:list', 1),
        ('manage_dept_add', 'sys:dept:add', 2),
        ('manage_dept_edit', 'sys:dept:edit', 3),
        ('manage_dept_delete', 'sys:dept:delete', 4),
    ]
    for bid, (name, perm, sort) in zip(DEPT_BUTTON_IDS, buttons):
        rows.append({
            **base,
            'id': bid,
            'name': name,
            'path': None,
            'component': None,
            'permission': perm,
            'meta_icon': None,
            'meta_hidden': True,
            'type': 'BUTTON',
            'sort': sort,
            'created_at': now,
        })
    return rows


def upgrade() -> None:
    bind = op.get_bind()

    # 1. 给 sys_dept 加 tenant_id 列（无条件加；非多租户场景下保持 NULL 无副作用）
    op.add_column(
        'sys_dept',
        sa.Column('tenant_id', sa.BigInteger(), nullable=True, comment='租户ID'),
    )
    op.create_index('ix_sys_dept_tenant_id', 'sys_dept', ['tenant_id'])

    # 2. 补插 manage_dept 菜单（idempotent：已存在则跳过）
    existing = bind.execute(
        sa.text("SELECT id FROM sys_menu WHERE id = :id"),
        {"id": DEPT_MENU_ID},
    ).scalar_one_or_none()
    if existing is None:
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
        bind.execute(sys_menu.insert(), _dept_menu_rows())

        # 关联给管理员角色
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
                    for mid in ALL_DEPT_MENU_IDS
                ],
            )


def downgrade() -> None:
    bind = op.get_bind()
    # 先删关联，再删菜单
    bind.execute(
        sa.text(
            "DELETE FROM sys_role_menu WHERE menu_id IN :ids"
        ).bindparams(sa.bindparam('ids', expanding=True)),
        {"ids": ALL_DEPT_MENU_IDS},
    )
    bind.execute(
        sa.text(
            "DELETE FROM sys_menu WHERE id IN :ids"
        ).bindparams(sa.bindparam('ids', expanding=True)),
        {"ids": ALL_DEPT_MENU_IDS},
    )

    op.drop_index('ix_sys_dept_tenant_id', table_name='sys_dept')
    op.drop_column('sys_dept', 'tenant_id')
