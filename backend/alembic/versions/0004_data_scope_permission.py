"""add sys_dept table, sys_role.data_scope, sys_user.dept_id

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'sys_dept',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True, comment='父部门ID，顶级部门为NULL'),
        sa.Column('name', sa.String(100), nullable=False, comment='部门名称'),
        sa.Column('code', sa.String(100), nullable=True, comment='部门编码'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['sys_dept.id'], ondelete='SET NULL'),
        comment='系统部门表\n树形结构，用于行级数据权限的范围计算',
    )
    op.create_index(op.f('ix_sys_dept_id'), 'sys_dept', ['id'], unique=True)
    op.create_index(op.f('ix_sys_dept_parent_id'), 'sys_dept', ['parent_id'], unique=False)
    op.create_index(op.f('ix_sys_dept_code'), 'sys_dept', ['code'], unique=False)
    op.create_index(
        '_ux_sys_dept_parent_name',
        'sys_dept',
        ['parent_id', 'name'],
        unique=True,
    )

    data_scope_enum = sa.Enum(
        'ALL', 'DEPT_AND_SUB', 'DEPT_ONLY', 'SELF',
        name='sys_role_data_scope',
    )
    data_scope_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'sys_role',
        sa.Column(
            'data_scope',
            data_scope_enum,
            nullable=False,
            server_default='SELF',
            comment='数据范围：ALL/DEPT_AND_SUB/DEPT_ONLY/SELF',
        ),
    )

    op.add_column(
        'sys_user',
        sa.Column(
            'dept_id',
            sa.BigInteger(),
            nullable=True,
            comment='所属部门ID',
        ),
    )
    op.create_index(op.f('ix_sys_user_dept_id'), 'sys_user', ['dept_id'], unique=False)
    op.create_foreign_key(
        'fk_sys_user_dept_id_sys_dept',
        'sys_user',
        'sys_dept',
        ['dept_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_sys_user_dept_id_sys_dept', 'sys_user', type_='foreignkey')
    op.drop_index(op.f('ix_sys_user_dept_id'), table_name='sys_user')
    op.drop_column('sys_user', 'dept_id')

    op.drop_column('sys_role', 'data_scope')

    sa.Enum(name='sys_role_data_scope').drop(op.get_bind(), checkfirst=True)

    op.drop_index('_ux_sys_dept_parent_name', table_name='sys_dept')
    op.drop_index(op.f('ix_sys_dept_code'), table_name='sys_dept')
    op.drop_index(op.f('ix_sys_dept_parent_id'), table_name='sys_dept')
    op.drop_index(op.f('ix_sys_dept_id'), table_name='sys_dept')
    op.drop_table('sys_dept')
