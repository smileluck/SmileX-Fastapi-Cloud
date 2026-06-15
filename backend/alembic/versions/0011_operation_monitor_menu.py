"""add operation-monitor menu

Revision ID: 0011_operation_monitor_menu
Revises: 0010_robot_event_log
Create Date: 2026-06-12

"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision: str = "0011_operation_monitor_menu"
down_revision: Union[str, Sequence[str], None] = "0010_robot_event_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = datetime(2026, 6, 12, 12, 0, 0, tzinfo=timezone.utc)

MENU_DATA = [
    # 运行监控（顶级菜单）
    {
        "id": 3000000000000050,
        "parent_id": None,
        "name": "operation-monitor",
        "path": "/operation-monitor",
        "component": "layout.base$view.operation-monitor",
        "redirect": None,
        "permission": "robot:monitor:list",
        "meta_icon": "mdi:monitor-eye",
        "meta_hidden": False,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "MENU",
        "sort": 5,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
    # 运行监控按钮权限
    {
        "id": 3000000000000051,
        "parent_id": 3000000000000050,
        "name": "operation_monitor_list",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "robot:monitor:list",
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
    op.bulk_insert(sa.table("sys_menu", *MENU_COLUMNS), MENU_DATA)


def downgrade() -> None:
    op.execute(
        "DELETE FROM sys_menu WHERE id IN ("
        + ",".join(str(mid) for mid in _ALL_NEW_MENU_IDS)
        + ")"
    )
