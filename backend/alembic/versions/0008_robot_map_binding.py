"""add robot map binding

Revision ID: 0008_robot_map_binding
Revises: 0007_robot_voice_config_robot_id
Create Date: 2026-06-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_robot_map_binding"
down_revision: Union[str, Sequence[str], None] = "0007_robot_voice_config_robot_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("robot"):
        return

    column_names = {column["name"] for column in inspector.get_columns("robot")}
    if "map_id" in column_names:
        return

    op.add_column(
        "robot",
        sa.Column("map_id", sa.BigInteger(), nullable=True, comment="绑定场景地图ID"),
    )
    op.create_foreign_key(
        "fk_robot_map_id_scene_map",
        "robot",
        "scene_map",
        ["map_id"],
        ["id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("robot"):
        return

    column_names = {column["name"] for column in inspector.get_columns("robot")}
    if "map_id" not in column_names:
        return

    foreign_key_names = {
        foreign_key["name"] for foreign_key in inspector.get_foreign_keys("robot")
    }
    if "fk_robot_map_id_scene_map" in foreign_key_names:
        op.drop_constraint("fk_robot_map_id_scene_map", "robot", type_="foreignkey")

    op.drop_column("robot", "map_id")
