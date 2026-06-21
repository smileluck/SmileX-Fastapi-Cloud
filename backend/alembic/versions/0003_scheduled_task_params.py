"""add params column to sys_scheduled_task

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-21

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
        'sys_scheduled_task',
        sa.Column('params', sa.JSON(), nullable=True, comment='通用任务参数 JSON'),
    )


def downgrade() -> None:
    op.drop_column('sys_scheduled_task', 'params')
