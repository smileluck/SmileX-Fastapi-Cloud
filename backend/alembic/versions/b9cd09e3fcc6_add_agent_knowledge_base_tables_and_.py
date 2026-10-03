"""add agent knowledge base tables and model_type

Revision ID: b9cd09e3fcc6
Revises: 0006
Create Date: 2026-10-02

Agent RAG 知识库：
- 新表 sys_agent_knowledge / sys_agent_knowledge_doc / sys_agent_knowledge_chunk
- sys_agent_model 加 model_type（chat/embedding/rerank，存量默认 chat）
- sys_agent 加 knowledge_ids（JSON 文本列）
- 种子："智能体"目录下新增知识库菜单与按钮权限点（不分配角色，运维勾选）
"""
from typing import Sequence, Union
from datetime import datetime as _dt

from alembic import op
import sqlalchemy as sa


revision: str = 'b9cd09e3fcc6'
down_revision: Union[str, Sequence[str], None] = '0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 菜单 ID：延续 0006 的 29424066160041xx 序列（0006 用至 ...134）
_KB_MENU_ID = 2942406616004135
_KB_MENU_IDS = [
    _KB_MENU_ID,                    # 知识库 MENU
    _KB_MENU_ID + 1,                # list 按钮
    _KB_MENU_ID + 2,                # add 按钮
    _KB_MENU_ID + 3,                # edit 按钮
    _KB_MENU_ID + 4,                # delete 按钮
]

# "智能体"顶级目录 ID（0006 种子）
_AGENT_CATALOG_ID = 2942406616004101


def _menu_row(menu_id, parent_id, name, permission, menu_type, sort, path=None, component=None, icon=None, hidden=False):
    return {
        'id': menu_id,
        'parent_id': parent_id,
        'name': name,
        'path': path,
        'component': component,
        'redirect': None,
        'permission': permission,
        'meta_icon': icon,
        'meta_hidden': hidden,
        'meta_affix': False,
        'meta_breadcrumb': True,
        'status': True,
        'type': menu_type,
        'sort': sort,
        'is_system': True,
        'meta_href': None,
        'meta_keep_alive': False,
        'deleted_at': None,
        'created_at': _dt(2026, 10, 2, 23, 0),
        'updated_at': None,
    }


_MENU_ROWS = [
    _menu_row(_KB_MENU_ID, _AGENT_CATALOG_ID, 'agent_knowledge', 'knowledge:list', 'MENU', 7,
              path='/agent/knowledge', component='view.agent_knowledge', icon='mdi:book-multiple-outline'),
    _menu_row(_KB_MENU_ID + 1, _KB_MENU_ID, 'agent_knowledge_list', 'knowledge:list', 'BUTTON', 1, hidden=True),
    _menu_row(_KB_MENU_ID + 2, _KB_MENU_ID, 'agent_knowledge_add', 'knowledge:add', 'BUTTON', 2, hidden=True),
    _menu_row(_KB_MENU_ID + 3, _KB_MENU_ID, 'agent_knowledge_edit', 'knowledge:edit', 'BUTTON', 3, hidden=True),
    _menu_row(_KB_MENU_ID + 4, _KB_MENU_ID, 'agent_knowledge_delete', 'knowledge:delete', 'BUTTON', 4, hidden=True),
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('sys_agent_knowledge',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
    sa.Column('name', sa.String(length=20), nullable=False, comment='知识库名称'),
    sa.Column('code', sa.String(length=64), nullable=False, comment='知识库编码'),
    sa.Column('embedding_model_id', sa.Integer(), nullable=False, comment='向量化模型 ID（sys_agent_model.id，须为 model_type=embedding）'),
    sa.Column('description', sa.String(length=200), nullable=True, comment='知识库描述'),
    sa.Column('doc_count', sa.Integer(), nullable=False, comment='文档数量（冗余计数）'),
    sa.Column('chunk_count', sa.Integer(), nullable=False, comment='切片数量（冗余计数）'),
    sa.Column('remark', sa.String(length=200), nullable=True, comment='备注'),
    sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code', name='uk_sys_agent_knowledge_code')
    )
    op.create_index(op.f('ix_sys_agent_knowledge_id'), 'sys_agent_knowledge', ['id'], unique=True)
    op.create_index(op.f('ix_sys_agent_knowledge_code'), 'sys_agent_knowledge', ['code'], unique=False)

    op.create_table('sys_agent_knowledge_doc',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
    sa.Column('knowledge_id', sa.Integer(), nullable=False, comment='所属知识库 ID（sys_agent_knowledge.id）'),
    sa.Column('file_name', sa.String(length=255), nullable=False, comment='文件名'),
    sa.Column('file_type', sa.String(length=16), nullable=False, comment='文件扩展名（小写，无点）'),
    sa.Column('file_size', sa.Integer(), nullable=False, comment='原始文件大小（字节）'),
    sa.Column('content_hash', sa.String(length=64), nullable=False, comment='内容 SHA-256（同库去重）'),
    sa.Column('content', sa.Text(), nullable=True, comment='提取后的全文文本'),
    sa.Column('char_count', sa.Integer(), nullable=False, comment='全文长度（字符）'),
    sa.Column('chunk_count', sa.Integer(), nullable=False, comment='切片数量'),
    sa.Column('status', sa.Integer(), nullable=False, comment='处理状态：0-待处理 1-处理中 2-完成 3-失败'),
    sa.Column('error_msg', sa.String(length=500), nullable=True, comment='失败原因'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sys_agent_knowledge_doc_id'), 'sys_agent_knowledge_doc', ['id'], unique=True)
    op.create_index('ix_sys_agent_knowledge_doc_kb_hash', 'sys_agent_knowledge_doc', ['knowledge_id', 'content_hash'], unique=False)
    op.create_index(op.f('ix_sys_agent_knowledge_doc_knowledge_id'), 'sys_agent_knowledge_doc', ['knowledge_id'], unique=False)

    op.create_table('sys_agent_knowledge_chunk',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
    sa.Column('knowledge_id', sa.Integer(), nullable=False, comment='所属知识库 ID'),
    sa.Column('doc_id', sa.Integer(), nullable=False, comment='所属文档 ID（sys_agent_knowledge_doc.id）'),
    sa.Column('chunk_index', sa.Integer(), nullable=False, comment='切片序号（文档内从 0 递增）'),
    sa.Column('char_count', sa.Integer(), nullable=False, comment='切片长度（字符）'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sys_agent_knowledge_chunk_id'), 'sys_agent_knowledge_chunk', ['id'], unique=True)
    op.create_index(op.f('ix_sys_agent_knowledge_chunk_doc_id'), 'sys_agent_knowledge_chunk', ['doc_id'], unique=False)
    op.create_index(op.f('ix_sys_agent_knowledge_chunk_knowledge_id'), 'sys_agent_knowledge_chunk', ['knowledge_id'], unique=False)

    op.add_column('sys_agent', sa.Column('knowledge_ids', sa.String(length=512), nullable=True, comment='绑定的知识库 ID JSON 数组文本'))
    op.add_column('sys_agent_model', sa.Column('model_type', sa.String(length=32), nullable=False, server_default='chat', comment='模型类型：chat-对话/embedding-向量化/rerank-重排'))

    op.bulk_insert(
        sa.table(
            'sys_menu',
            sa.column('id', sa.BigInteger),
            sa.column('parent_id', sa.BigInteger),
            sa.column('name', sa.String),
            sa.column('path', sa.String),
            sa.column('component', sa.String),
            sa.column('redirect', sa.String),
            sa.column('permission', sa.String),
            sa.column('meta_icon', sa.String),
            sa.column('meta_hidden', sa.Boolean),
            sa.column('meta_affix', sa.Boolean),
            sa.column('meta_breadcrumb', sa.Boolean),
            sa.column('status', sa.Boolean),
            sa.column('type', sa.String),
            sa.column('sort', sa.Integer),
            sa.column('is_system', sa.Boolean),
            sa.column('meta_href', sa.String),
            sa.column('meta_keep_alive', sa.Boolean),
            sa.column('deleted_at', sa.DateTime),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        _MENU_ROWS,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM sys_menu WHERE id = ANY(ARRAY[%s])" % ", ".join(str(i) for i in _KB_MENU_IDS))
    op.drop_column('sys_agent_model', 'model_type')
    op.drop_column('sys_agent', 'knowledge_ids')
    op.drop_index(op.f('ix_sys_agent_knowledge_chunk_knowledge_id'), table_name='sys_agent_knowledge_chunk')
    op.drop_index(op.f('ix_sys_agent_knowledge_chunk_doc_id'), table_name='sys_agent_knowledge_chunk')
    op.drop_index(op.f('ix_sys_agent_knowledge_chunk_id'), table_name='sys_agent_knowledge_chunk')
    op.drop_table('sys_agent_knowledge_chunk')
    op.drop_index(op.f('ix_sys_agent_knowledge_doc_knowledge_id'), table_name='sys_agent_knowledge_doc')
    op.drop_index('ix_sys_agent_knowledge_doc_kb_hash', table_name='sys_agent_knowledge_doc')
    op.drop_index(op.f('ix_sys_agent_knowledge_doc_id'), table_name='sys_agent_knowledge_doc')
    op.drop_table('sys_agent_knowledge_doc')
    op.drop_index(op.f('ix_sys_agent_knowledge_code'), table_name='sys_agent_knowledge')
    op.drop_index(op.f('ix_sys_agent_knowledge_id'), table_name='sys_agent_knowledge')
    op.drop_table('sys_agent_knowledge')
