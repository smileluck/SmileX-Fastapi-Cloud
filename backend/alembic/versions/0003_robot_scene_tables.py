"""robot and scene module tables + seed data

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-08

"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NOW = datetime(2026, 6, 8, 0, 0, 0)


def upgrade() -> None:
    # ================================================================
    # Independent tables
    # ================================================================

    # 1. robot_model
    op.create_table(
        'robot_model',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='机器人型号名称'),
        sa.Column('brand', sa.String(100), nullable=False, comment='品牌'),
        sa.Column('model', sa.String(100), nullable=False, comment='型号'),
        sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='状态：True-启用，False-禁用'),
        sa.Column('sort', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        comment='机器人型号表',
    )

    # 4. scene_group (independent, self-referential FK created together)
    op.create_table(
        'scene_group',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='分组名称'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True, comment='父分组ID'),
        sa.Column('sort', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='排序号'),
        sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='状态：True-启用，False-禁用'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['scene_group.id'], ondelete='CASCADE'),
        comment='场景分组表',
    )

    # ================================================================
    # Tables with FK dependencies
    # ================================================================

    # 2. robot (depends on robot_model)
    op.create_table(
        'robot',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='机器人名称'),
        sa.Column('model_id', sa.BigInteger(), nullable=False, comment='关联机器人型号ID'),
        sa.Column('serial_number', sa.String(100), nullable=False, comment='序列号'),
        sa.Column('status', sa.Enum('online', 'offline', 'inactive', name='robotstatus'), nullable=False, server_default='inactive', comment='状态'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.UniqueConstraint('serial_number'),
        sa.ForeignKeyConstraint(['model_id'], ['robot_model.id']),
        comment='机器人表',
    )

    # 3. robot_status_record (depends on robot)
    op.create_table(
        'robot_status_record',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('robot_id', sa.BigInteger(), nullable=False, comment='关联机器人ID'),
        sa.Column('battery', sa.Float(), nullable=False, server_default=sa.text('0'), comment='电量百分比'),
        sa.Column('signal', sa.Integer(), nullable=False, server_default=sa.text('0'), comment='信号强度'),
        sa.Column('speed', sa.Float(), nullable=False, server_default=sa.text('0'), comment='速度'),
        sa.Column('location', sa.Text(), nullable=True, comment='位置信息'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.ForeignKeyConstraint(['robot_id'], ['robot.id']),
        comment='机器人状态记录表',
    )

    # 5. scene_map (depends on scene_group, sys_file)
    op.create_table(
        'scene_map',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, comment='地图名称'),
        sa.Column('group_id', sa.BigInteger(), nullable=True, comment='关联分组ID'),
        sa.Column('image_id', sa.BigInteger(), nullable=True, comment='关联图片文件ID'),
        sa.Column('width', sa.Integer(), nullable=True, comment='地图宽度'),
        sa.Column('height', sa.Integer(), nullable=True, comment='地图高度'),
        sa.Column('status', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='状态：True-启用，False-禁用'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.ForeignKeyConstraint(['group_id'], ['scene_group.id']),
        sa.ForeignKeyConstraint(['image_id'], ['sys_file.id']),
        comment='场景地图表',
    )

    # 6. scene_map_annotation (depends on scene_map)
    op.create_table(
        'scene_map_annotation',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('map_id', sa.BigInteger(), nullable=False, comment='关联地图ID'),
        sa.Column('x', sa.Float(), nullable=False, comment='X坐标'),
        sa.Column('y', sa.Float(), nullable=False, comment='Y坐标'),
        sa.Column('name', sa.String(100), nullable=False, comment='标注名称'),
        sa.Column('angle', sa.Float(), nullable=False, server_default=sa.text('0'), comment='角度'),
        sa.Column('type', sa.String(50), nullable=False, comment='标注类型'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.ForeignKeyConstraint(['map_id'], ['scene_map.id'], ondelete='CASCADE'),
        comment='场景地图标注表',
    )

    # 7. scene_map_object (depends on scene_map)
    op.create_table(
        'scene_map_object',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('map_id', sa.BigInteger(), nullable=False, comment='关联地图ID'),
        sa.Column('type', sa.String(50), nullable=False, comment='物体类型'),
        sa.Column('x', sa.Float(), nullable=False, comment='X坐标'),
        sa.Column('y', sa.Float(), nullable=False, comment='Y坐标'),
        sa.Column('width', sa.Float(), nullable=False, server_default=sa.text('0'), comment='宽度'),
        sa.Column('height', sa.Float(), nullable=False, server_default=sa.text('0'), comment='高度'),
        sa.Column('points', sa.Text(), nullable=True, comment='多边形顶点数据'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
        sa.ForeignKeyConstraint(['map_id'], ['scene_map.id'], ondelete='CASCADE'),
        comment='场景地图物体表',
    )

    # ================================================================
    # Seed: dictionaries
    # ================================================================

    op.bulk_insert(
        sa.table(
            'sys_dict',
            sa.column('id', sa.BigInteger),
            sa.column('name', sa.String),
            sa.column('code', sa.String),
            sa.column('description', sa.String),
            sa.column('status', sa.Boolean),
            sa.column('is_system', sa.Boolean),
            sa.column('sort', sa.Integer),
            sa.column('deleted_at', sa.DateTime),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        [
            {
                'id': 9, 'name': '地图标注类型', 'code': 'map_annotation_type',
                'description': '场景地图标注点类型', 'status': True, 'is_system': False,
                'sort': 0, 'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
            },
            {
                'id': 10, 'name': '地图物体类型', 'code': 'map_object_type',
                'description': '场景地图物体类型', 'status': True, 'is_system': False,
                'sort': 0, 'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
            },
            {
                'id': 11, 'name': '机器人状态', 'code': 'robot_status',
                'description': '机器人在线状态', 'status': True, 'is_system': False,
                'sort': 0, 'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
            },
        ],
    )

    # ================================================================
    # Seed: dictionary items
    # ================================================================

    op.bulk_insert(
        sa.table(
            'sys_dict_item',
            sa.column('id', sa.BigInteger),
            sa.column('dict_id', sa.BigInteger),
            sa.column('value', sa.String),
            sa.column('label', sa.String),
            sa.column('description', sa.String),
            sa.column('ext_info', sa.String),
            sa.column('status', sa.Boolean),
            sa.column('sort', sa.Integer),
            sa.column('deleted_at', sa.DateTime),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        [
            # map_annotation_type items (dict_id=9)
            {'id': 10, 'dict_id': 9, 'value': 'reception', 'label': '接待点',
             'description': None, 'ext_info': None, 'status': True, 'sort': 1,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
            {'id': 11, 'dict_id': 9, 'value': 'service', 'label': '服务点',
             'description': None, 'ext_info': None, 'status': True, 'sort': 2,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
            # map_object_type items (dict_id=10)
            {'id': 12, 'dict_id': 10, 'value': 'wall', 'label': '墙体',
             'description': None, 'ext_info': None, 'status': True, 'sort': 1,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
            {'id': 13, 'dict_id': 10, 'value': 'virtual_wall', 'label': '虚拟墙',
             'description': None, 'ext_info': None, 'status': True, 'sort': 2,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
            {'id': 14, 'dict_id': 10, 'value': 'restricted', 'label': '禁行区',
             'description': None, 'ext_info': None, 'status': True, 'sort': 3,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
            {'id': 15, 'dict_id': 10, 'value': 'custom', 'label': '自定义',
             'description': None, 'ext_info': None, 'status': True, 'sort': 4,
             'deleted_at': None, 'created_at': NOW, 'updated_at': NOW},
        ],
    )

    # ================================================================
    # Seed: menus
    # ================================================================

    MENU_DATA = [
        # --- Robot catalog ---
        {
            'id': 3000000000000001, 'parent_id': None, 'name': 'robot',
            'path': '/robot', 'component': 'layout.base',
            'redirect': '/robot/model', 'permission': None,
            'meta_icon': 'mdi:robot', 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'CATALOG', 'sort': 6,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # Robot sub-menus
        {
            'id': 3000000000000002, 'parent_id': 3000000000000001, 'name': 'robot_model',
            'path': '/robot/model', 'component': 'view.robot_model',
            'redirect': None, 'permission': 'robot:model:list',
            'meta_icon': None, 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'MENU', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000003, 'parent_id': 3000000000000001, 'name': 'robot_manage',
            'path': '/robot/manage', 'component': 'view.robot_manage',
            'redirect': None, 'permission': 'robot:manage:list',
            'meta_icon': None, 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'MENU', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # --- Scene catalog ---
        {
            'id': 3000000000000004, 'parent_id': None, 'name': 'scene',
            'path': '/scene', 'component': 'layout.base',
            'redirect': '/scene/group', 'permission': None,
            'meta_icon': 'mdi:map-outline', 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'CATALOG', 'sort': 7,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # Scene sub-menus
        {
            'id': 3000000000000005, 'parent_id': 3000000000000004, 'name': 'scene_group',
            'path': '/scene/group', 'component': 'view.scene_group',
            'redirect': None, 'permission': 'scene:group:list',
            'meta_icon': None, 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'MENU', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000006, 'parent_id': 3000000000000004, 'name': 'scene_map',
            'path': '/scene/map', 'component': 'view.scene_map',
            'redirect': None, 'permission': 'scene:map:list',
            'meta_icon': None, 'meta_hidden': False,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'MENU', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # --- BUTTON permissions: robot_model ---
        {
            'id': 3000000000000010, 'parent_id': 3000000000000002, 'name': 'robot_model_list',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:model:list',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000011, 'parent_id': 3000000000000002, 'name': 'robot_model_add',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:model:add',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000012, 'parent_id': 3000000000000002, 'name': 'robot_model_edit',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:model:edit',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 3,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000013, 'parent_id': 3000000000000002, 'name': 'robot_model_delete',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:model:delete',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 4,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # --- BUTTON permissions: robot_manage ---
        {
            'id': 3000000000000014, 'parent_id': 3000000000000003, 'name': 'robot_manage_list',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:manage:list',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000015, 'parent_id': 3000000000000003, 'name': 'robot_manage_add',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:manage:add',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000016, 'parent_id': 3000000000000003, 'name': 'robot_manage_edit',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:manage:edit',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 3,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000017, 'parent_id': 3000000000000003, 'name': 'robot_manage_delete',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'robot:manage:delete',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 4,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # --- BUTTON permissions: scene_group ---
        {
            'id': 3000000000000018, 'parent_id': 3000000000000005, 'name': 'scene_group_list',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:group:list',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000019, 'parent_id': 3000000000000005, 'name': 'scene_group_add',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:group:add',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000020, 'parent_id': 3000000000000005, 'name': 'scene_group_edit',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:group:edit',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 3,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000021, 'parent_id': 3000000000000005, 'name': 'scene_group_delete',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:group:delete',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 4,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        # --- BUTTON permissions: scene_map ---
        {
            'id': 3000000000000022, 'parent_id': 3000000000000006, 'name': 'scene_map_list',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:map:list',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 1,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000023, 'parent_id': 3000000000000006, 'name': 'scene_map_add',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:map:add',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 2,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000024, 'parent_id': 3000000000000006, 'name': 'scene_map_edit',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:map:edit',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 3,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
        {
            'id': 3000000000000025, 'parent_id': 3000000000000006, 'name': 'scene_map_delete',
            'path': None, 'component': None,
            'redirect': None, 'permission': 'scene:map:delete',
            'meta_icon': None, 'meta_hidden': True,
            'meta_affix': False, 'meta_breadcrumb': True,
            'status': True, 'type': 'BUTTON', 'sort': 4,
            'is_system': False, 'meta_href': None, 'meta_keep_alive': False,
            'deleted_at': None, 'created_at': NOW, 'updated_at': NOW,
        },
    ]

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
        MENU_DATA,
    )

    # ================================================================
    # Seed: role-menu associations for admin role
    # ================================================================

    ADMIN_ROLE_ID = 2874692539129900
    _ALL_NEW_MENU_IDS = [row['id'] for row in MENU_DATA]


def downgrade() -> None:
    # Remove role-menu associations for new menus

    # Remove new menus
    op.execute(
        "DELETE FROM sys_menu WHERE id IN ("
        "  3000000000000001, 3000000000000002, 3000000000000003,"
        "  3000000000000004, 3000000000000005, 3000000000000006,"
        "  3000000000000010, 3000000000000011, 3000000000000012, 3000000000000013,"
        "  3000000000000014, 3000000000000015, 3000000000000016, 3000000000000017,"
        "  3000000000000018, 3000000000000019, 3000000000000020, 3000000000000021,"
        "  3000000000000022, 3000000000000023, 3000000000000024, 3000000000000025"
        ")"
    )

    # Remove new dictionary items
    op.execute(
        "DELETE FROM sys_dict_item WHERE id IN (10, 11, 12, 13, 14, 15)"
    )

    # Remove new dictionaries
    op.execute(
        "DELETE FROM sys_dict WHERE id IN (9, 10, 11)"
    )

    # Drop tables in reverse dependency order
    op.drop_table('scene_map_object')
    op.drop_table('scene_map_annotation')
    op.drop_table('scene_map')
    op.drop_table('robot_status_record')
    op.drop_table('robot')
    op.drop_table('scene_group')
    op.drop_table('robot_model')

    # Drop the enum type created for robot.status
    op.execute('DROP TYPE IF EXISTS robotstatus')
