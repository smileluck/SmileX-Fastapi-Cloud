"""fix robot_status_record location_info stored as JSON string scalar

Revision ID: 0014_fix_location_info_string
Revises: 0013_robot_status_backfill
Create Date: 2026-06-13

修正历史数据中 location_info 被错误写入为 JSON 字符串标量（json_typeof = 'string'）的情况，
将其置为 NULL，避免响应序列化时 Pydantic 校验失败（期望 dict）。
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0014_fix_location_info_string"
down_revision: Union[str, Sequence[str], None] = "0013_robot_status_backfill"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE robot_status_record
            SET location_info = NULL
            WHERE json_typeof(location_info) = 'string'
            """
        )
    )


def downgrade() -> None:
    # 数据修复不可逆，避免误恢复成损坏的值
    pass
