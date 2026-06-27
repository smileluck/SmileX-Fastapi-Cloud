"""add sys_menu.meta_icon_type

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'sys_menu',
        sa.Column(
            'meta_icon_type',
            sa.SmallInteger(),
            nullable=False,
            server_default='1',
            comment='图标类型：1-iconify，2-本地',
        ),
    )


def downgrade() -> None:
    op.drop_column('sys_menu', 'meta_icon_type')
