"""add sys_merchant table and manage_merchant menu seed

Revision ID: 0008
Revises: 0007
Create Date: 2026-07-04

新增「商户管理」模块，用于开放API接口的 HMAC 签名授权鉴证：
1. 建表 sys_merchant（含加密存储的 app_secret）
2. 播种后台菜单 manage_merchant 及其按钮权限，并关联管理员角色
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0008'
down_revision: Union[str, Sequence[str], None] = '0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 与 0002/0006 保持一致的菜单 ID 段
MANAGE_DIR_ID = 2874692539129857
MERCHANT_MENU_ID = 2942406616000010
MERCHANT_BUTTON_IDS = [
    2942406616000011,  # list
    2942406616000012,  # add
    2942406616000013,  # edit
    2942406616000014,  # delete
    2942406616000015,  # reset-secret
]
ALL_MERCHANT_MENU_IDS = [MERCHANT_MENU_ID] + MERCHANT_BUTTON_IDS

ADMIN_ROLE_ID = 2874692539129900


def _merchant_menu_rows() -> list[dict]:
    now = datetime(2026, 7, 4, 10, 0, 0)
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
        {
            **base,
            'id': MERCHANT_MENU_ID,
            'parent_id': MANAGE_DIR_ID,
            'name': 'manage_merchant',
            'path': '/manage/merchant',
            'component': 'view.manage_merchant',
            'permission': 'sys:merchant:list',
            'meta_icon': 'mdi:store',
            'meta_hidden': False,
            'type': 'MENU',
            'sort': 7,
            'created_at': now,
        },
    ]
    buttons = [
        ('manage_merchant_list', 'sys:merchant:list', 1),
        ('manage_merchant_add', 'sys:merchant:add', 2),
        ('manage_merchant_edit', 'sys:merchant:edit', 3),
        ('manage_merchant_delete', 'sys:merchant:delete', 4),
        ('manage_merchant_reset_secret', 'sys:merchant:reset-secret', 5),
    ]
    for bid, (name, perm, sort) in zip(MERCHANT_BUTTON_IDS, buttons):
        rows.append({
            **base,
            'id': bid,
            'parent_id': MERCHANT_MENU_ID,
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

    # 1. 建表 sys_merchant
    op.create_table(
        'sys_merchant',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='商户名称'),
        sa.Column('code', sa.String(length=100), nullable=True, comment='商户编码'),
        sa.Column('contact_name', sa.String(length=50), nullable=True, comment='联系人姓名'),
        sa.Column('contact_phone', sa.String(length=30), nullable=True, comment='联系电话'),
        sa.Column('contact_email', sa.String(length=100), nullable=True, comment='联系邮箱'),
        sa.Column('app_id', sa.String(length=50), nullable=False, comment='商户AppId（公开标识）'),
        sa.Column('app_secret_encrypted', sa.String(length=500), nullable=False,
                  comment='app_secret（Fernet 加密后的 token，验签时解密）'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('secret_updated_at', sa.DateTime(timezone=True), nullable=True,
                  comment='密钥最近一次重置时间'),
        sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('app_id', name='uk_sys_merchant_app_id'),
        comment='系统商户表',
    )
    op.create_index(op.f('ix_sys_merchant_id'), 'sys_merchant', ['id'], unique=True)
    op.create_index(op.f('ix_sys_merchant_code'), 'sys_merchant', ['code'])
    op.create_index(op.f('ix_sys_merchant_app_id'), 'sys_merchant', ['app_id'])

    # 2. 播种 manage_merchant 菜单（幂等：已存在则跳过）
    existing = bind.execute(
        sa.text("SELECT id FROM sys_menu WHERE id = :id"),
        {"id": MERCHANT_MENU_ID},
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
        bind.execute(sys_menu.insert(), _merchant_menu_rows())

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
                    for mid in ALL_MERCHANT_MENU_IDS
                ],
            )


def downgrade() -> None:
    bind = op.get_bind()
    # 先删菜单关联，再删菜单
    bind.execute(
        sa.text(
            "DELETE FROM sys_role_menu WHERE menu_id IN :ids"
        ).bindparams(sa.bindparam('ids', expanding=True)),
        {"ids": ALL_MERCHANT_MENU_IDS},
    )
    bind.execute(
        sa.text(
            "DELETE FROM sys_menu WHERE id IN :ids"
        ).bindparams(sa.bindparam('ids', expanding=True)),
        {"ids": ALL_MERCHANT_MENU_IDS},
    )

    op.drop_index(op.f('ix_sys_merchant_app_id'), table_name='sys_merchant')
    op.drop_index(op.f('ix_sys_merchant_code'), table_name='sys_merchant')
    op.drop_index(op.f('ix_sys_merchant_id'), table_name='sys_merchant')
    op.drop_table('sys_merchant')
