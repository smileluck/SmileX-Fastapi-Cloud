"""app_user admin fields

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-28

为 app_user 增加后台管理所需字段：
- status      启用/禁用状态（NOT NULL，默认 true）
- avatar      头像 URL
- last_login_at  最后登录时间
- last_login_ip  最后登录 IP
并补 (phone_code, phone) 唯一索引，作为业务层查重的 DB 级兜底。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'app_user',
        sa.Column(
            'status',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
            comment='状态：True-启用，False-禁用',
        ),
    )
    op.add_column(
        'app_user',
        sa.Column('avatar', sa.Text(), nullable=True, comment='头像URL'),
    )
    op.add_column(
        'app_user',
        sa.Column(
            'last_login_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='最后登录时间',
        ),
    )
    op.add_column(
        'app_user',
        sa.Column(
            'last_login_ip',
            sa.String(50),
            nullable=True,
            comment='最后登录IP',
        ),
    )
    op.create_index(
        'ux_app_user_phone_code_phone',
        'app_user',
        ['phone_code', 'phone'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ux_app_user_phone_code_phone', table_name='app_user')
    op.drop_column('app_user', 'last_login_ip')
    op.drop_column('app_user', 'last_login_at')
    op.drop_column('app_user', 'avatar')
    op.drop_column('app_user', 'status')
