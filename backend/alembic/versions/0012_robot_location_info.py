"""add location_info to robot_status_record, make robot_id unique (one-to-one)

Revision ID: 0012_robot_location_info
Revises: 0011_operation_monitor_menu
Create Date: 2026-06-13

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0012_robot_location_info"
down_revision: Union[str, Sequence[str], None] = "0011_operation_monitor_menu"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "robot_status_record",
        sa.Column(
            "location_info",
            sa.JSON(),
            nullable=True,
            server_default='{}',
            comment="位置信息",
        ),
    )
    op.create_unique_constraint("uq_robot_status_record_robot_id", "robot_status_record", ["robot_id"])


def downgrade() -> None:
    op.drop_constraint("uq_robot_status_record_robot_id", "robot_status_record", type_="unique")
    op.drop_column("robot_status_record", "location_info")
