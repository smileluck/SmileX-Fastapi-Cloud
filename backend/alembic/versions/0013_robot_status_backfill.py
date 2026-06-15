"""backfill robot_status_record for existing robots

Revision ID: 0013_robot_status_backfill
Revises: 0012_robot_location_info
Create Date: 2026-06-13

为已有但缺少状态记录的机器人补充一条默认的 robot_status_record（一对一）。
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0013_robot_status_backfill"
down_revision: Union[str, Sequence[str], None] = "0012_robot_location_info"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    missing_rows = bind.execute(sa.text(
        """
        SELECT r.id FROM robot r
        LEFT JOIN robot_status_record s ON s.robot_id = r.id AND s.deleted_at IS NULL
        WHERE r.deleted_at IS NULL AND s.id IS NULL
        """
    )).fetchall()

    if not missing_rows:
        return

    from database.utils.snowflake import snowflake
    from database.utils.timezone import timezone

    now = timezone.now()
    records = [
        {
            "id": snowflake.generate(),
            "robot_id": row[0],
            "battery": 0,
            "signal": 0,
            "speed": 0,
            "location_info": {},
            "deleted_at": None,
            "created_at": now,
            "updated_at": None,
        }
        for row in missing_rows
    ]

    op.bulk_insert(
        sa.table(
            "robot_status_record",
            sa.column("id", sa.BigInteger),
            sa.column("robot_id", sa.BigInteger),
            sa.column("battery", sa.Float),
            sa.column("signal", sa.Integer),
            sa.column("speed", sa.Float),
            sa.column("location_info", sa.JSON),
            sa.column("deleted_at", sa.DateTime),
            sa.column("created_at", sa.DateTime),
            sa.column("updated_at", sa.DateTime),
        ),
        records,
    )


def downgrade() -> None:
    # 不回滚数据，避免误删业务数据
    pass
