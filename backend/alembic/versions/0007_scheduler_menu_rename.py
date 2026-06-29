"""rename scheduler menus: drop manage_ prefix

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-27

把 scheduler 子菜单的 name 从 manage_scheduler / manage_scheduler-log
统一改为 scheduler-task / scheduler-log，path 同步归一到 /scheduler 前缀下。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0007'
down_revision: Union[str, Sequence[str], None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# 旧 → 新 映射 (id, new_name, new_path, new_component)
RENAMES = [
    # 任务管理：manage_scheduler → scheduler_task
    (2942406615113728, 'scheduler_task', '/scheduler/task', 'view.scheduler_task'),
    # 执行日志：manage_scheduler-log → scheduler_log
    (2942406615965702, 'scheduler_log', '/scheduler/log', 'view.scheduler_log'),
]

# 旧值用于 downgrade
OLD_VALUES = {
    2942406615113728: ('manage_scheduler', '/scheduler', 'view.manage_scheduler'),
    2942406615965702: ('manage_scheduler-log', '/scheduler/scheduler-log', 'view.manage_scheduler-log'),
}


def upgrade() -> None:
    bind = op.get_bind()
    for menu_id, new_name, new_path, new_component in RENAMES:
        bind.execute(
            sa.text(
                "UPDATE sys_menu SET name = :name, path = :path, component = :comp "
                "WHERE id = :id"
            ),
            {"name": new_name, "path": new_path, "comp": new_component, "id": menu_id},
        )


def downgrade() -> None:
    bind = op.get_bind()
    for menu_id, old_name, old_path, old_component in [
        (mid, *OLD_VALUES[mid]) for mid in [r[0] for r in RENAMES]
    ]:
        bind.execute(
            sa.text(
                "UPDATE sys_menu SET name = :name, path = :path, component = :comp "
                "WHERE id = :id"
            ),
            {"name": old_name, "path": old_path, "comp": old_component, "id": menu_id},
        )
