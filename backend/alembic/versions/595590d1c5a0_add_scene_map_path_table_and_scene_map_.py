"""add scene_map_path table and scene_map resolution field

Revision ID: 595590d1c5a0
Revises: 0003
Create Date: 2026-06-09 11:58:10.001068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '595590d1c5a0'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('scene_map_path',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('map_id', sa.BigInteger(), nullable=False, comment='地图ID'),
        sa.Column('start_annotation_id', sa.BigInteger(), nullable=False, comment='起始标注ID'),
        sa.Column('end_annotation_id', sa.BigInteger(), nullable=False, comment='结束标注ID'),
        sa.Column('name', sa.String(length=100), nullable=True, comment='路径名称'),
        sa.Column('points', sa.Text(), nullable=True, comment='中间路径点(JSON数组)'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['end_annotation_id'], ['scene_map_annotation.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['map_id'], ['scene_map.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['start_annotation_id'], ['scene_map_annotation.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='\n    场景地图路径表\n    '
    )
    op.create_index(op.f('ix_scene_map_path_id'), 'scene_map_path', ['id'], unique=True)
    op.add_column('scene_map', sa.Column('resolution', sa.Float(), server_default='0.2', nullable=False, comment='分辨率(米/像素)，如0.2表示1像素=20厘米'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('scene_map', 'resolution')
    op.drop_index(op.f('ix_scene_map_path_id'), table_name='scene_map_path')
    op.drop_table('scene_map_path')
