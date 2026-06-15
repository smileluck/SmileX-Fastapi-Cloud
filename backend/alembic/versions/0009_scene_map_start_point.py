"""add scene_map start_point_x and start_point_y

Revision ID: 0009_scene_map_start_point
Revises: 0008_robot_map_binding
Create Date: 2026-06-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0009_scene_map_start_point"
down_revision: Union[str, Sequence[str], None] = "0008_robot_map_binding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("scene_map"):
        return

    column_names = {column["name"] for column in inspector.get_columns("scene_map")}

    if "start_point_x" not in column_names:
        op.add_column(
            "scene_map",
            sa.Column("start_point_x", sa.Float(), nullable=False, server_default="0", comment="起始点位X坐标"),
        )

    if "start_point_y" not in column_names:
        op.add_column(
            "scene_map",
            sa.Column("start_point_y", sa.Float(), nullable=False, server_default="0", comment="起始点位Y坐标"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("scene_map"):
        return

    column_names = {column["name"] for column in inspector.get_columns("scene_map")}

    if "start_point_y" in column_names:
        op.drop_column("scene_map", "start_point_y")

    if "start_point_x" in column_names:
        op.drop_column("scene_map", "start_point_x")
