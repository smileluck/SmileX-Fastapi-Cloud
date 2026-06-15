"""add task management tables

Revision ID: 0004_task
Revises: 595590d1c5a0
Create Date: 2026-06-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0004_task'
down_revision: Union[str, Sequence[str], None] = '595590d1c5a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 任务主表
    op.create_table(
        'task',
        sa.Column('id', sa.BigInteger(), primary_key=True, unique=True, autoincrement=True, comment='主键 ID'),
        sa.Column('name', sa.String(20), nullable=False, comment='任务名称'),
        sa.Column('task_type', sa.String(20), nullable=False, comment='任务类型: patrol-巡逻, broadcast-播报'),
        sa.Column('broadcast_text', sa.Text(), nullable=True, comment='播报文本'),
        sa.Column('broadcast_count', sa.String(10), nullable=True, comment='播报次数: 1/2/3/5/loop'),
        sa.Column('schedule_enabled', sa.Boolean(), server_default=sa.text('false'), comment='是否启用定时调度'),
        sa.Column('schedule_date', sa.Date(), nullable=True, comment='调度日期'),
        sa.Column('schedule_start_time', sa.Time(), nullable=True, comment='调度开始时间'),
        sa.Column('schedule_repeat_cycle', sa.String(20), nullable=True, comment='重复周期: none/daily/weekly/monthly'),
        sa.Column('enabled', sa.Boolean(), server_default=sa.text('true'), comment='启用状态'),
        sa.Column('status', sa.String(20), server_default='idle', comment='执行状态: idle/running/paused'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间'),
        comment='任务表',
    )

    # 任务巡逻点位表
    op.create_table(
        'task_point',
        sa.Column('id', sa.BigInteger(), primary_key=True, unique=True, autoincrement=True, comment='主键 ID'),
        sa.Column('task_id', sa.BigInteger(), sa.ForeignKey('task.id', ondelete='CASCADE'), nullable=False, comment='所属任务ID'),
        sa.Column('sort_order', sa.Integer(), server_default='0', comment='排序'),
        sa.Column('point_name', sa.String(100), nullable=True, comment='点位名称'),
        sa.Column('action', sa.String(20), nullable=False, comment='运控动作: wave/bow/turn/wait/nod'),
        sa.Column('voice_text', sa.Text(), nullable=True, comment='语音播报文本'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间'),
        comment='任务巡逻点位表',
    )

    # 任务-机器人关联表
    op.create_table(
        'task_robot',
        sa.Column('task_id', sa.BigInteger(), sa.ForeignKey('task.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('robot_id', sa.BigInteger(), sa.ForeignKey('robot.id', ondelete='CASCADE'), primary_key=True),
    )

    # 任务执行记录表
    op.create_table(
        'task_execution',
        sa.Column('id', sa.BigInteger(), primary_key=True, unique=True, autoincrement=True, comment='主键 ID'),
        sa.Column('task_id', sa.BigInteger(), sa.ForeignKey('task.id', ondelete='CASCADE'), nullable=False, comment='关联任务ID'),
        sa.Column('task_name', sa.String(20), nullable=False, comment='快照: 任务名称'),
        sa.Column('task_type', sa.String(20), nullable=False, comment='快照: 任务类型'),
        sa.Column('status', sa.String(20), server_default='pending', comment='执行状态'),
        sa.Column('progress', sa.Integer(), server_default='0', comment='进度百分比 0-100'),
        sa.Column('current_position', sa.String(100), nullable=True, comment='当前执行位置'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True, comment='结束时间'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('robot_id', sa.BigInteger(), sa.ForeignKey('robot.id'), nullable=True, comment='执行机器人ID'),
        sa.Column('triggered_by', sa.String(20), server_default='manual', comment='触发方式: manual/schedule'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间'),
        comment='任务执行记录表',
    )


def downgrade() -> None:
    op.drop_table('task_execution')
    op.drop_table('task_robot')
    op.drop_table('task_point')
    op.drop_table('task')
