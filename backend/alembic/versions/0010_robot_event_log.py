"""add robot_event_log table

Revision ID: 0010_robot_event_log
Revises: 0009_scene_map_start_point
Create Date: 2026-06-12

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0010_robot_event_log"
down_revision: Union[str, Sequence[str], None] = "0009_scene_map_start_point"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "robot_event_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("robot_id", sa.BigInteger(), nullable=False, comment="机器人ID"),
        sa.Column("event_type", sa.String(20), nullable=False, comment="事件类型：task-任务，alarm-告警"),
        sa.Column("event_status", sa.String(20), nullable=False, comment="事件状态：normal-正常，abnormal-异常"),
        sa.Column("event_content", sa.Text(), nullable=True, comment="事件内容"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True, comment="删除时间，为空则未删除"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment="创建时间"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True, comment="更新时间"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["robot_id"], ["robot.id"]),
    )
    op.create_index("ix_robot_event_log_robot_id", "robot_event_log", ["robot_id"])


def downgrade() -> None:
    op.drop_index("ix_robot_event_log_robot_id", table_name="robot_event_log")
    op.drop_table("robot_event_log")
