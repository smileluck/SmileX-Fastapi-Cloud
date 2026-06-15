"""fix robot voice config robot_id column

Revision ID: 0007_robot_voice_config_robot_id
Revises: 0006
Create Date: 2026-06-11

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_robot_voice_config_robot_id"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("robot_voice_config"):
        return

    column_names = {
        column["name"] for column in inspector.get_columns("robot_voice_config")
    }
    if "robot_id" in column_names:
        return

    op.add_column(
        "robot_voice_config",
        sa.Column("robot_id", sa.BigInteger(), nullable=True, comment="机器人ID"),
    )
    op.create_foreign_key(
        "fk_robot_voice_config_robot_id_robot",
        "robot_voice_config",
        "robot",
        ["robot_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_robot_voice_config_robot_id",
        "robot_voice_config",
        ["robot_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("robot_voice_config"):
        return

    column_names = {
        column["name"] for column in inspector.get_columns("robot_voice_config")
    }
    if "robot_id" not in column_names:
        return

    constraint_names = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("robot_voice_config")
    }
    if "uq_robot_voice_config_robot_id" in constraint_names:
        op.drop_constraint(
            "uq_robot_voice_config_robot_id",
            "robot_voice_config",
            type_="unique",
        )

    foreign_key_names = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("robot_voice_config")
    }
    if "fk_robot_voice_config_robot_id_robot" in foreign_key_names:
        op.drop_constraint(
            "fk_robot_voice_config_robot_id_robot",
            "robot_voice_config",
            type_="foreignkey",
        )

    op.drop_column("robot_voice_config", "robot_id")
