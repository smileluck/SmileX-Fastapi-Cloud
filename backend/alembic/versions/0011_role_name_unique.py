"""unique index on sys_role.name

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-13

为 sys_role.name 补建唯一索引。SysRole 模型中早已声明 name 的 unique=True，
但初始迁移 (0001) 只建了 ix_sys_role_id，name 的唯一约束从未落到 DB，
导致可以通过非正规途径（历史数据/并发）产生重名角色——这正是用户表单中
「选一个角色却勾选两个」bug 的根因。本迁移先重命名存量重名角色（每组保留
最小 id 的原名，其余追加 _dup_<id> 后缀），再创建唯一索引。

注：role_service 的 create_role/update_role 已有按 name 查重的应用层校验
（且不过滤 deleted_at），DB 唯一索引作为最终兜底，与现有应用层行为一致。
"""
from typing import Sequence, Union

from alembic import op


revision: str = '0011'
down_revision: Union[str, Sequence[str], None] = '0010'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLE = 'sys_role'
INDEX_NAME = 'ix_sys_role_name'


def upgrade() -> None:
    # 1) 清理存量重名角色：仅在重名分组里，保留最小 id 的原名，其余追加唯一后缀。
    #    后缀含主键 id（全局唯一）→ 结果唯一；SUBSTR(...,1,74) 控制总长不超过 name 的 String(100)。
    #    若无重名数据，该 UPDATE 命中 0 行，是安全的空操作。
    op.execute(
        f"""
        UPDATE {TABLE} r
        SET name = SUBSTR(r.name, 1, 74) || '_dup_' || r.id::text
        WHERE r.name IN (
            SELECT name FROM {TABLE} GROUP BY name HAVING COUNT(*) > 1
        )
        AND r.id <> (
            SELECT MIN(id) FROM {TABLE} r2 WHERE r2.name = r.name
        )
        """
    )

    # 2) 创建唯一索引（与 ix_sys_user_username 同样使用 create_index + unique=True）
    op.create_index(INDEX_NAME, TABLE, ['name'], unique=True)


def downgrade() -> None:
    op.drop_index(INDEX_NAME, table_name=TABLE)
