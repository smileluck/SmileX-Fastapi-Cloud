"""robot config tables + menus

Revision ID: 0006
Revises: 0005_menus
Create Date: 2026-06-10

"""

from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005_menus"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = datetime(2026, 6, 10, 12, 0, 0, tzinfo=timezone.utc)

MENU_DATA = [
    # settings menu
    {
        "id": 3000000000000034,
        "parent_id": None,
        "name": "settings",
        "path": "/settings",
        "component": "view.settings",
        "redirect": None,
        "permission": "robot:config:list",
        "meta_icon": None,
        "meta_hidden": False,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "MENU",
        "sort": 3,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
    # settings buttons
    {
        "id": 3000000000000035,
        "parent_id": 3000000000000034,
        "name": "settings_list",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "robot:config:list",
        "meta_icon": None,
        "meta_hidden": True,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "BUTTON",
        "sort": 1,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "id": 3000000000000036,
        "parent_id": 3000000000000034,
        "name": "settings_edit",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "robot:config:edit",
        "meta_icon": None,
        "meta_hidden": True,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "BUTTON",
        "sort": 2,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
]

_ALL_NEW_MENU_IDS = [row["id"] for row in MENU_DATA]

MENU_COLUMNS = [
    sa.column("id", sa.BigInteger),
    sa.column("parent_id", sa.BigInteger),
    sa.column("name", sa.String),
    sa.column("path", sa.String),
    sa.column("component", sa.String),
    sa.column("redirect", sa.String),
    sa.column("permission", sa.String),
    sa.column("meta_icon", sa.String),
    sa.column("meta_hidden", sa.Boolean),
    sa.column("meta_affix", sa.Boolean),
    sa.column("meta_breadcrumb", sa.Boolean),
    sa.column("status", sa.Boolean),
    sa.column("type", sa.String),
    sa.column("sort", sa.Integer),
    sa.column("is_system", sa.Boolean),
    sa.column("meta_href", sa.String),
    sa.column("meta_keep_alive", sa.Boolean),
    sa.column("deleted_at", sa.DateTime),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
]


def upgrade() -> None:
    # Add columns to robot table
    op.add_column(
        "robot",
        sa.Column(
            "speed_level",
            sa.String(20),
            nullable=True,
            comment="速度等级：normal-正常速度,slow-慢速,low-低速",
        ),
    )
    op.add_column(
        "robot",
        sa.Column(
            "battery_threshold",
            sa.Integer(),
            nullable=True,
            comment="电量报警阈值(%)",
        ),
    )

    # Create robot_voice_config table
    op.create_table(
        "robot_voice_config",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "robot_id",
            sa.BigInteger(),
            nullable=False,
            comment="机器人ID",
        ),
        sa.Column("wake_word", sa.String(20), nullable=True, comment="唤醒词"),
        sa.Column("tts_voice", sa.String(50), nullable=True, comment="音色"),
        sa.Column("tts_speed", sa.Integer(), nullable=True, comment="语速"),
        sa.Column("tts_volume", sa.Integer(), nullable=True, comment="音量"),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="删除时间，为空则未删除",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("robot_id"),
        sa.ForeignKeyConstraint(["robot_id"], ["robot.id"]),
        comment="机器人语音配置表",
    )

    # Create robot_face_recognition table
    op.create_table(
        "robot_face_recognition",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("person_name", sa.String(100), nullable=False, comment="人员名称"),
        sa.Column("photo_url", sa.String(255), nullable=False, comment="人像图片URL"),
        sa.Column("broadcast_text", sa.Text(), nullable=False, comment="语音播报内容"),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="删除时间，为空则未删除",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        comment="机器人人脸识别TTS配置表",
    )

    # Insert menu data
    op.bulk_insert(sa.table("sys_menu", *MENU_COLUMNS), MENU_DATA)


def downgrade() -> None:
    op.execute(
        "DELETE FROM sys_menu WHERE id IN ("
        + ",".join(str(mid) for mid in _ALL_NEW_MENU_IDS)
        + ")"
    )

    op.drop_table("robot_face_recognition")
    op.drop_table("robot_voice_config")
    op.drop_column("robot", "battery_threshold")
    op.drop_column("robot", "speed_level")
