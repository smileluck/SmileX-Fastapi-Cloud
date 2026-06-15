"""add task_point.annotation_id referencing scene_map_annotation.id

Revision ID: 0015_task_point_annotation_id
Revises: 0014_fix_location_info_string
Create Date: 2026-06-13

为 task_point 表新增 annotation_id 列，关联 scene_map_annotation.id。
保留 point_name 作为冗余显示字段，避免后续点位改名导致历史任务显示丢失。
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0015_task_point_annotation_id"
down_revision: Union[str, Sequence[str], None] = "0014_fix_location_info_string"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "task_point",
        sa.Column("annotation_id", sa.BigInteger(), nullable=True, comment="关联场景标注ID"),
    )
    op.create_foreign_key(
        "fk_task_point_annotation_id_scene_map_annotation",
        "task_point",
        "scene_map_annotation",
        ["annotation_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_task_point_annotation_id_scene_map_annotation",
        "task_point",
        type_="foreignkey",
    )
    op.drop_column("task_point", "annotation_id")
