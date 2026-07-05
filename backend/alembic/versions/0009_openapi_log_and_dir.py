"""add sys_openapi_log table, merchant_open directory, move manage_merchant, seed openapi-log menu

Revision ID: 0009
Revises: 0008
Create Date: 2026-07-05

1. 建表 sys_openapi_log（开放API调用日志）
2. 新增顶级目录菜单 merchant_open（商户开放管理）
3. 将 manage_merchant 从 manage 目录移到 merchant_open 下（更新 parent_id 与 path）
4. 播种 manage_openapi_log 菜单与按钮权限，挂在 merchant_open 下
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0009'
down_revision: Union[str, Sequence[str], None] = '0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 复用与 0006/0008 一致的菜单 ID 段
MERCHANT_MENU_ID = 2942406616000010  # 0008 播种的 manage_merchant
MERCHANT_OPEN_DIR_ID = 2942406616000020
OPENAPI_LOG_MENU_ID = 2942406616000021
OPENAPI_LOG_BUTTON_IDS = [
    2942406616000022,  # list
    2942406616000023,  # delete
]
ALL_NEW_MENU_IDS = [MERCHANT_OPEN_DIR_ID, OPENAPI_LOG_MENU_ID] + OPENAPI_LOG_BUTTON_IDS

ADMIN_ROLE_ID = 2874692539129900


def _new_menu_rows() -> list[dict]:
    now = datetime(2026, 7, 5, 12, 0, 0)
    base = {
        'redirect': None,
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
        # 顶级目录：商户开放管理
        {
            **base,
            'id': MERCHANT_OPEN_DIR_ID,
            'parent_id': None,
            'name': 'merchant-open',
            'path': '/merchant-open',
            'component': 'layout.base',
            'permission': None,
            'meta_icon': 'mdi:connection',
            'meta_hidden': False,
            'type': 'CATALOG',
            'sort': 4,
            'created_at': now,
        },
        # 开放API调用日志 菜单
        {
            **base,
            'id': OPENAPI_LOG_MENU_ID,
            'parent_id': MERCHANT_OPEN_DIR_ID,
            'name': 'merchant-open_openapi-log',
            'path': '/merchant-open/openapi-log',
            'component': 'view.merchant-open_openapi-log',
            'permission': 'sys:openapi-log:list',
            'meta_icon': 'mdi:chart-line-variant',
            'meta_hidden': False,
            'type': 'MENU',
            'sort': 2,
            'created_at': now,
        },
    ]
    buttons = [
        ('merchant-open_openapi-log_list', 'sys:openapi-log:list', 1),
        ('merchant-open_openapi-log_delete', 'sys:openapi-log:delete', 2),
    ]
    for bid, (name, perm, sort) in zip(OPENAPI_LOG_BUTTON_IDS, buttons):
        rows.append({
            **base,
            'id': bid,
            'parent_id': OPENAPI_LOG_MENU_ID,
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

    # 1. 建表 sys_openapi_log
    op.create_table(
        'sys_openapi_log',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('app_id', sa.String(length=50), nullable=False, comment='调用方 AppId（来自请求头，可能不存在）'),
        sa.Column('method', sa.String(length=10), nullable=False, comment='HTTP方法'),
        sa.Column('path', sa.String(length=255), nullable=False, comment='请求路径'),
        sa.Column('merchant_name', sa.String(length=100), nullable=True, comment='商户名称（冗余，便于展示；可能为空）'),
        sa.Column('status_code', sa.Integer(), nullable=True, comment='HTTP响应状态码'),
        sa.Column('err_code', sa.Integer(), nullable=True, comment='业务错误码（成功为空）'),
        sa.Column('msg', sa.String(length=255), nullable=True, comment='响应消息'),
        sa.Column('client_ip', sa.String(length=50), nullable=True, comment='客户端IP'),
        sa.Column('request_id', sa.String(length=64), nullable=True, comment='请求追踪ID'),
        sa.Column('latency_ms', sa.Integer(), nullable=True, comment='请求耗时(毫秒)'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='开放API调用日志表',
    )
    op.create_index(op.f('ix_sys_openapi_log_id'), 'sys_openapi_log', ['id'], unique=True)
    op.create_index(op.f('ix_sys_openapi_log_app_id'), 'sys_openapi_log', ['app_id'])
    op.create_index(op.f('ix_sys_openapi_log_path'), 'sys_openapi_log', ['path'])
    op.create_index(op.f('ix_sys_openapi_log_err_code'), 'sys_openapi_log', ['err_code'])
    op.create_index(op.f('ix_sys_openapi_log_request_id'), 'sys_openapi_log', ['request_id'])

    # 2. 播种新菜单（目录 + openapi-log 菜单 + 按钮），幂等
    existing = bind.execute(
        sa.text("SELECT id FROM sys_menu WHERE id = :id"),
        {"id": MERCHANT_OPEN_DIR_ID},
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
        bind.execute(sys_menu.insert(), _new_menu_rows())

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
                    for mid in ALL_NEW_MENU_IDS
                ],
            )

    # 3. 把 manage_merchant 从 manage 目录移到 merchant_open 目录下（目录已存在，FK 满足）
    #    同步重命名路由 name 与 component，对齐前端 views/merchant-open/merchant/
    bind.execute(
        sa.text(
            "UPDATE sys_menu SET parent_id = :pid, path = :path, name = :name, "
            "component = :comp, sort = 1 WHERE id = :mid"
        ),
        {
            "pid": MERCHANT_OPEN_DIR_ID,
            "path": "/merchant-open/merchant",
            "name": "merchant-open_merchant",
            "comp": "view.merchant-open_merchant",
            "mid": MERCHANT_MENU_ID,
        },
    )


def downgrade() -> None:
    bind = op.get_bind()
    # 还原 manage_merchant 到 manage 目录（含原始 name/component）
    bind.execute(
        sa.text(
            "UPDATE sys_menu SET parent_id = :pid, path = :path, name = :name, "
            "component = :comp, sort = 7 WHERE id = :mid"
        ),
        {
            "pid": 2874692539129857,
            "path": "/manage/merchant",
            "name": "manage_merchant",
            "comp": "view.manage_merchant",
            "mid": MERCHANT_MENU_ID,
        },
    )
    # 删除本次新增的菜单与角色关联
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

    op.drop_index(op.f('ix_sys_openapi_log_request_id'), table_name='sys_openapi_log')
    op.drop_index(op.f('ix_sys_openapi_log_err_code'), table_name='sys_openapi_log')
    op.drop_index(op.f('ix_sys_openapi_log_path'), table_name='sys_openapi_log')
    op.drop_index(op.f('ix_sys_openapi_log_app_id'), table_name='sys_openapi_log')
    op.drop_index(op.f('ix_sys_openapi_log_id'), table_name='sys_openapi_log')
    op.drop_table('sys_openapi_log')
