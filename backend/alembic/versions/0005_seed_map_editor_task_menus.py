"""seed scene_map-editor and task menus

Revision ID: 0005_menus
Revises: 0004_task
Create Date: 2026-06-09

"""

from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision: str = "0005_menus"
down_revision: Union[str, Sequence[str], None] = "0004_task"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = datetime(2026, 6, 9, 12, 0, 0, tzinfo=timezone.utc)

# scene catalog id from 0003
SCENE_CATALOG_ID = 3000000000000004

MENU_DATA = [
    # scene_map-editor (child of scene)
    {
        "id": 3000000000000007,
        "parent_id": SCENE_CATALOG_ID,
        "name": "scene_map-editor",
        "path": "/scene/map-editor",
        "component": "view.scene_map-editor",
        "redirect": None,
        "permission": "scene:map-editor:list",
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
    # task (top-level)
    {
        "id": 3000000000000008,
        "parent_id": None,
        "name": "task",
        "path": "/task",
        "component": "layout.base$view.task",
        "redirect": None,
        "permission": "task:list",
        "meta_icon": "mdi:clipboard-check-outline",
        "meta_hidden": False,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "MENU",
        "sort": 8,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
    # task buttons
    {
        "id": 3000000000000030,
        "parent_id": 3000000000000008,
        "name": "task_list",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "task:list",
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
        "id": 3000000000000031,
        "parent_id": 3000000000000008,
        "name": "task_add",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "task:add",
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
    {
        "id": 3000000000000032,
        "parent_id": 3000000000000008,
        "name": "task_edit",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "task:edit",
        "meta_icon": None,
        "meta_hidden": True,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "BUTTON",
        "sort": 3,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
    {
        "id": 3000000000000033,
        "parent_id": 3000000000000008,
        "name": "task_delete",
        "path": None,
        "component": None,
        "redirect": None,
        "permission": "task:delete",
        "meta_icon": None,
        "meta_hidden": True,
        "meta_affix": False,
        "meta_breadcrumb": True,
        "status": True,
        "type": "BUTTON",
        "sort": 4,
        "is_system": False,
        "meta_href": None,
        "meta_keep_alive": False,
        "deleted_at": None,
        "created_at": NOW,
        "updated_at": NOW,
    },
]

ADMIN_ROLE_ID = 2874692539129900
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

    # op.bulk_insert(
    #     sa.table(
    #         'sys_role_menu',
    #         sa.column('role_id', sa.BigInteger),
    #         sa.column('menu_id', sa.BigInteger),
    #         sa.column('permission', sa.String),
    #     ),
    #     [
    #         {'role_id': ADMIN_ROLE_ID, 'menu_id': mid, 'permission': 'read'}
    #         for mid in _ALL_NEW_MENU_IDS
    #     ],
    # )


def downgrade() -> None:
    # op.execute(
    #     "DELETE FROM sys_role_menu WHERE menu_id IN ("
    #     + ",".join(str(mid) for mid in _ALL_NEW_MENU_IDS)
    #     + ")"
    # )
    op.execute(
        "DELETE FROM sys_menu WHERE id IN ("
        + ",".join(str(mid) for mid in _ALL_NEW_MENU_IDS)
        + ")"
    )
