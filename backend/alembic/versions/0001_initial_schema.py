"""initial schema (structure only)

Revision ID: 0001
Revises:
Create Date: 2026-06-04

合并自历史 0001~0011 的全部结构变更（建表 / 加列 / 加索引 / 枚举），
仅含 DDL，不含任何种子数据。种子数据见 0002_seed_data。
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ================================================================
    # Independent tables (no FK dependencies)
    # ================================================================

    op.create_table(
        'app_user',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(255), nullable=False, comment='用户名'),
        sa.Column('phone_code', sa.String(10), nullable=False, comment='手机号区号，如：+86、+1 等'),
        sa.Column('phone', sa.String(13), nullable=False, comment='手机号'),
        sa.Column('password', sa.String(255), nullable=True, comment='密码哈希值'),
        sa.Column('email', sa.String(255), nullable=True, comment='邮箱'),
        sa.Column('wx_openid', sa.String(255), nullable=True, comment='微信 openid'),
        sa.Column('wx_unionid', sa.String(255), nullable=True, comment='微信 unionid'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='用户表 - 存储用户信息',
    )
    op.create_index(op.f('ix_app_user_id'), 'app_user', ['id'], unique=True)

    op.create_table(
        'plugin_registry',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='插件名称'),
        sa.Column('version', sa.String(50), nullable=False, comment='插件版本'),
        sa.Column('is_installed', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='是否已安装'),
        sa.Column('installed_at', sa.DateTime(timezone=True), nullable=False, comment='安装时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='插件注册表\n记录已安装的插件及其版本',
    )
    op.create_index(op.f('ix_plugin_registry_id'), 'plugin_registry', ['id'], unique=True)
    op.create_index(op.f('ix_plugin_registry_name'), 'plugin_registry', ['name'], unique=True)

    op.create_table(
        'sys_config',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('key', sa.String(100), nullable=False, comment='配置键名'),
        sa.Column('value', sa.String(255), nullable=False, comment='配置值'),
        sa.Column('default_value', sa.String(255), nullable=True, comment='默认值'),
        sa.Column('validation_rule', sa.String(255), nullable=True, comment='校验规则'),
        sa.Column('description', sa.String(255), nullable=True, comment='配置描述'),
        sa.Column('type', sa.Enum('STRING', 'NUMBER', 'BOOLEAN', 'JSON', 'ARRAY', name='configtype'), nullable=False, comment='配置类型'),
        sa.Column('group', sa.Enum('SYSTEM', 'SECURITY', 'LOG', 'NETWORK', 'STORAGE', 'CUSTOM', name='configgroup'), nullable=False, comment='配置分组'),
        sa.Column('is_system', sa.Boolean(), nullable=False, comment='是否为系统内置配置'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统配置表\n存储系统全局配置参数',
    )
    op.create_index(op.f('ix_sys_config_id'), 'sys_config', ['id'], unique=True)
    op.create_index(op.f('ix_sys_config_key'), 'sys_config', ['key'], unique=True)

    op.create_table(
        'sys_dict',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='字典名称'),
        sa.Column('code', sa.String(100), nullable=False, comment='字典编码'),
        sa.Column('description', sa.Text(), nullable=True, comment='字典描述'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('is_system', sa.Boolean(), nullable=False, comment='是否为系统内置字典'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统字典表\n存储字典分类信息',
    )
    op.create_index(op.f('ix_sys_dict_id'), 'sys_dict', ['id'], unique=True)
    op.create_index(op.f('ix_sys_dict_code'), 'sys_dict', ['code'], unique=True)

    # sys_dept 必须先于 sys_user 创建，供 sys_user.dept_id 外键引用
    op.create_table(
        'sys_dept',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True, comment='父部门ID，顶级部门为NULL'),
        sa.Column('name', sa.String(100), nullable=False, comment='部门名称'),
        sa.Column('code', sa.String(100), nullable=True, comment='部门编码'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('tenant_id', sa.BigInteger(), nullable=True, comment='租户ID'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['sys_dept.id'], ondelete='SET NULL'),
        comment='系统部门表\n树形结构，用于行级数据权限的范围计算',
    )
    op.create_index(op.f('ix_sys_dept_id'), 'sys_dept', ['id'], unique=True)
    op.create_index(op.f('ix_sys_dept_parent_id'), 'sys_dept', ['parent_id'], unique=False)
    op.create_index(op.f('ix_sys_dept_code'), 'sys_dept', ['code'], unique=False)
    op.create_index('ix_sys_dept_tenant_id', 'sys_dept', ['tenant_id'], unique=False)
    op.create_index('_ux_sys_dept_parent_name', 'sys_dept', ['parent_id', 'name'], unique=True)

    op.create_table(
        'sys_user',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('username', sa.String(50), nullable=False, comment='用户名'),
        sa.Column('password', sa.String(255), nullable=False, comment='密码（加密存储）'),
        sa.Column('nickname', sa.String(100), nullable=True, comment='用户昵称'),
        sa.Column('email', sa.String(100), nullable=True, comment='邮箱'),
        sa.Column('phone', sa.String(20), nullable=True, comment='手机号'),
        sa.Column('avatar', sa.Text(), nullable=True, comment='头像URL'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True, comment='最后登录时间'),
        sa.Column('last_login_ip', sa.String(50), nullable=True, comment='最后登录IP'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, comment='是否为超级管理员'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('last_tenant_id', sa.BigInteger(), nullable=True, comment='最后租户ID'),
        sa.Column('dept_id', sa.BigInteger(), nullable=True, comment='所属部门ID'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dept_id'], ['sys_dept.id'], ondelete='SET NULL'),
        comment='系统用户表\n存储系统管理用户的基本信息和认证凭证',
    )
    op.create_index(op.f('ix_sys_user_id'), 'sys_user', ['id'], unique=True)
    op.create_index(op.f('ix_sys_user_username'), 'sys_user', ['username'], unique=False)
    op.create_index(op.f('ix_sys_user_dept_id'), 'sys_user', ['dept_id'], unique=False)

    op.create_table(
        'sys_role',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='角色名称'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('is_default', sa.Boolean(), nullable=False, comment='是否为默认角色'),
        sa.Column('is_system', sa.Boolean(), nullable=False, comment='是否为系统内置角色'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('desc', sa.Text(), nullable=True, comment='角色描述'),
        sa.Column('data_scope', sa.Enum('ALL', 'DEPT_AND_SUB', 'DEPT_ONLY', 'SELF', name='sys_role_data_scope'), nullable=False, server_default='SELF', comment='数据范围：ALL/DEPT_AND_SUB/DEPT_ONLY/SELF'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        comment='系统角色表\n存储角色信息及其关联的权限配置',
    )
    op.create_index(op.f('ix_sys_role_id'), 'sys_role', ['id'], unique=True)
    op.create_index('ix_sys_role_name', 'sys_role', ['name'], unique=True)

    op.create_table(
        'sys_menu',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True, comment='父菜单ID，顶级菜单为0或NULL'),
        sa.Column('name', sa.String(100), nullable=False, comment='菜单名称'),
        sa.Column('path', sa.String(255), nullable=True, comment='路由路径'),
        sa.Column('component', sa.String(255), nullable=True, comment='组件路径'),
        sa.Column('redirect', sa.String(255), nullable=True, comment='重定向路径'),
        sa.Column('permission', sa.String(100), nullable=True, comment='权限标识，如 sys:user:list'),
        sa.Column('meta_icon', sa.String(50), nullable=True, comment='路由图标'),
        sa.Column('meta_hidden', sa.Boolean(), nullable=False, comment='是否隐藏菜单'),
        sa.Column('meta_affix', sa.Boolean(), nullable=False, comment='是否固定标签'),
        sa.Column('meta_breadcrumb', sa.Boolean(), nullable=False, comment='是否显示面包屑'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('type', sa.Enum('CATALOG', 'MENU', 'BUTTON', 'EXTERNAL', name='menutype'), nullable=False, comment='菜单类型'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('is_system', sa.Boolean(), nullable=False, comment='是否为系统内置菜单'),
        sa.Column('meta_href', sa.String(500), nullable=True, comment='外部链接地址'),
        sa.Column('meta_keep_alive', sa.Boolean(), nullable=False, comment='是否缓存路由'),
        sa.Column('meta_icon_type', sa.SmallInteger(), nullable=False, server_default='1', comment='图标类型：1-iconify，2-本地'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['sys_menu.id'], ondelete='CASCADE'),
        comment='系统菜单表\n存储系统菜单、目录和按钮等权限点',
    )
    op.create_index(op.f('ix_sys_menu_id'), 'sys_menu', ['id'], unique=True)

    op.create_table(
        'sys_login_log',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('username', sa.String(50), nullable=False, comment='登录用户名'),
        sa.Column('ip', sa.String(50), nullable=True, comment='客户端IP'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='登录状态：True-成功，False-失败'),
        sa.Column('detail', sa.String(255), nullable=True, comment='详情'),
        sa.Column('user_agent', sa.String(500), nullable=True, comment='登录设备(User-Agent)'),
        sa.Column('login_time', sa.DateTime(timezone=True), nullable=False, comment='登录时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统登录日志表\n记录用户登录尝试',
    )
    op.create_index(op.f('ix_sys_login_log_id'), 'sys_login_log', ['id'], unique=True)
    op.create_index(op.f('ix_sys_login_log_username'), 'sys_login_log', ['username'], unique=False)

    op.create_table(
        'sys_operation_log',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='操作人ID'),
        sa.Column('username', sa.String(50), nullable=False, comment='操作人用户名'),
        sa.Column('module', sa.String(50), nullable=False, comment='操作模块'),
        sa.Column('action', sa.String(50), nullable=False, comment='操作类型'),
        sa.Column('description', sa.String(255), nullable=True, comment='操作描述'),
        sa.Column('method', sa.String(10), nullable=True, comment='HTTP方法'),
        sa.Column('path', sa.String(255), nullable=True, comment='请求路径'),
        sa.Column('ip', sa.String(50), nullable=True, comment='客户端IP'),
        sa.Column('request_params', sa.Text(), nullable=True, comment='请求参数'),
        sa.Column('response_code', sa.Integer(), nullable=True, comment='响应状态码'),
        sa.Column('elapsed_ms', sa.Float(), nullable=True, comment='耗时(毫秒)'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.Column('response_result', sa.Text(), nullable=True, comment='响应结果'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统操作日志表\n记录用户的关键业务操作',
    )
    op.create_index(op.f('ix_sys_operation_log_id'), 'sys_operation_log', ['id'], unique=True)
    op.create_index(op.f('ix_sys_operation_log_user_id'), 'sys_operation_log', ['user_id'], unique=False)

    op.create_table(
        'sys_export_task',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('task_name', sa.String(200), nullable=False, comment='任务名称'),
        sa.Column('module_key', sa.String(50), nullable=False, comment='模块标识'),
        sa.Column('template_id', sa.BigInteger(), nullable=True, comment='导出模板ID'),
        sa.Column('query_params_json', sa.Text(), nullable=False, comment='查询参数JSON'),
        sa.Column('created_by', sa.BigInteger(), nullable=False, comment='创建者ID'),
        sa.Column('status', sa.String(20), nullable=False, comment='状态: pending/processing/completed/failed'),
        sa.Column('total_rows', sa.Integer(), nullable=True, comment='导出总行数'),
        sa.Column('file_path', sa.String(500), nullable=True, comment='文件存储路径'),
        sa.Column('file_size', sa.Integer(), nullable=True, comment='文件大小(字节)'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True, comment='开始执行时间'),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True, comment='执行完成时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='异步导出任务表',
    )
    op.create_index(op.f('ix_sys_export_task_id'), 'sys_export_task', ['id'], unique=True)
    op.create_index(op.f('ix_sys_export_task_module_key'), 'sys_export_task', ['module_key'], unique=False)

    op.create_table(
        'sys_export_template',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(200), nullable=False, comment='模板名称'),
        sa.Column('module_key', sa.String(50), nullable=False, comment='关联模块标识'),
        sa.Column('columns', sa.Text(), nullable=False, comment='列配置JSON'),
        sa.Column('joins_config', sa.Text(), nullable=True, comment='JOIN配置JSON'),
        sa.Column('description', sa.String(500), nullable=True, comment='模板描述'),
        sa.Column('created_by', sa.BigInteger(), nullable=False, comment='创建者ID'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='导出模板表',
    )
    op.create_index(op.f('ix_sys_export_template_id'), 'sys_export_template', ['id'], unique=True)
    op.create_index(op.f('ix_sys_export_template_module_key'), 'sys_export_template', ['module_key'], unique=False)

    op.create_table(
        'sys_file',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('original_name', sa.String(500), nullable=False, comment='原始文件名'),
        sa.Column('stored_name', sa.String(500), nullable=False, comment='存储文件名'),
        sa.Column('file_path', sa.String(1000), nullable=False, comment='存储路径'),
        sa.Column('file_size', sa.BigInteger(), nullable=False, comment='文件大小(字节)'),
        sa.Column('mime_type', sa.String(200), nullable=False, comment='MIME类型'),
        sa.Column('extension', sa.String(20), nullable=False, comment='扩展名'),
        sa.Column('created_by', sa.BigInteger(), nullable=False, comment='上传者用户ID'),
        sa.Column('storage_platform', sa.String(50), nullable=False, comment='存储平台标识'),
        sa.Column('hash', sa.String(64), nullable=True, comment='SHA-256哈希'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统文件存储表',
    )
    op.create_index(op.f('ix_sys_file_id'), 'sys_file', ['id'], unique=True)

    op.create_table(
        'sys_ip_blacklist',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('ip', sa.String(64), nullable=False, comment='IP 地址'),
        sa.Column('type', sa.String(16), nullable=False, comment='类型：permanent / temporary'),
        sa.Column('reason', sa.String(255), nullable=True, comment='加入原因'),
        sa.Column('expire_at', sa.DateTime(timezone=True), nullable=True, comment='过期时间'),
        sa.Column('creator_id', sa.BigInteger(), nullable=True, comment='创建人ID'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='IP 黑名单表',
    )
    op.create_index(op.f('ix_sys_ip_blacklist_id'), 'sys_ip_blacklist', ['id'], unique=True)
    op.create_index(op.f('ix_sys_ip_blacklist_ip'), 'sys_ip_blacklist', ['ip'], unique=True)

    op.create_table(
        'sys_notice',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('title', sa.String(200), nullable=False, comment='通知标题'),
        sa.Column('content', sa.Text(), nullable=False, comment='通知内容（支持HTML）'),
        sa.Column('sender_id', sa.BigInteger(), nullable=False, comment='发送者用户ID'),
        sa.Column('sender_name', sa.String(100), nullable=False, comment='发送者名称'),
        sa.Column('type', sa.String(50), nullable=False, comment='通知类型'),
        sa.Column('target_type', sa.String(50), nullable=False, comment='推送范围'),
        sa.Column('target_role_ids', sa.ARRAY(sa.BigInteger()), nullable=True, comment='目标角色ID列表'),
        sa.Column('target_user_ids', sa.ARRAY(sa.BigInteger()), nullable=True, comment='目标用户ID列表'),
        sa.Column('priority', sa.String(20), nullable=False, comment='优先级'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-已发布, False-草稿'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True, comment='发布时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='系统通知表',
    )
    op.create_index(op.f('ix_sys_notice_id'), 'sys_notice', ['id'], unique=True)

    op.create_table(
        'sys_notice_read',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('notice_id', sa.BigInteger(), nullable=False, comment='通知ID'),
        sa.Column('is_read', sa.Boolean(), nullable=False, comment='是否已读'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True, comment='阅读时间'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'notice_id', name='uix_user_notice'),
        comment='用户通知阅读记录表',
    )
    op.create_index(op.f('ix_sys_notice_read_id'), 'sys_notice_read', ['id'], unique=True)
    op.create_index(op.f('ix_sys_notice_read_notice_id'), 'sys_notice_read', ['notice_id'], unique=False)
    op.create_index(op.f('ix_sys_notice_read_user_id'), 'sys_notice_read', ['user_id'], unique=False)

    op.create_table(
        'sys_scheduled_task',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(100), nullable=False, comment='任务名称'),
        sa.Column('task_key', sa.String(200), nullable=False, comment='任务唯一标识'),
        sa.Column('cron_expression', sa.String(100), nullable=False, comment='Cron 表达式'),
        sa.Column('description', sa.String(500), nullable=True, comment='任务描述'),
        sa.Column('trigger_type', sa.String(20), nullable=False, comment='触发类型: cron/interval/date'),
        sa.Column('trigger_params', sa.Text(), nullable=True, comment='触发参数 JSON'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态: True启用/False禁用'),
        sa.Column('module', sa.String(100), nullable=True, comment='来源模块'),
        sa.Column('function_path', sa.String(200), nullable=True, comment='函数路径'),
        sa.Column('is_system', sa.Boolean(), nullable=False, comment='系统任务不可删除'),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True, comment='上次执行时间'),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True, comment='下次执行时间'),
        sa.Column('last_status', sa.String(20), nullable=True, comment='上次执行状态'),
        sa.Column('timeout', sa.Integer(), nullable=False, comment='超时时间(秒)'),
        sa.Column('max_retries', sa.Integer(), nullable=False, comment='最大重试次数'),
        sa.Column('concurrent_policy', sa.String(20), nullable=False, comment='并发策略: skip/replace/run'),
        sa.Column('params', sa.JSON(), nullable=True, comment='通用任务参数 JSON'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='定时任务表',
    )
    op.create_index(op.f('ix_sys_scheduled_task_id'), 'sys_scheduled_task', ['id'], unique=True)
    op.create_index(op.f('ix_sys_scheduled_task_task_key'), 'sys_scheduled_task', ['task_key'], unique=True)

    op.create_table(
        'sys_scheduled_task_log',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('task_id', sa.BigInteger(), nullable=False, comment='任务ID'),
        sa.Column('task_name', sa.String(100), nullable=False, comment='任务名称(冗余)'),
        sa.Column('task_key', sa.String(200), nullable=False, comment='任务标识(冗余)'),
        sa.Column('status', sa.String(20), nullable=False, comment='状态'),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=True, comment='开始时间'),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True, comment='结束时间'),
        sa.Column('duration_ms', sa.Float(), nullable=True, comment='耗时(毫秒)'),
        sa.Column('result', sa.Text(), nullable=True, comment='执行结果'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('retry_count', sa.Integer(), nullable=False, comment='重试次数'),
        sa.Column('triggered_by', sa.String(20), nullable=False, comment='触发方式'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='定时任务执行日志表',
    )
    op.create_index(op.f('ix_sys_scheduled_task_log_id'), 'sys_scheduled_task_log', ['id'], unique=True)
    op.create_index(op.f('ix_sys_scheduled_task_log_task_id'), 'sys_scheduled_task_log', ['task_id'], unique=False)

    op.create_table(
        'sys_merchant',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('name', sa.String(length=100), nullable=False, comment='商户名称'),
        sa.Column('code', sa.String(length=100), nullable=True, comment='商户编码'),
        sa.Column('contact_name', sa.String(length=50), nullable=True, comment='联系人姓名'),
        sa.Column('contact_phone', sa.String(length=30), nullable=True, comment='联系电话'),
        sa.Column('contact_email', sa.String(length=100), nullable=True, comment='联系邮箱'),
        sa.Column('app_id', sa.String(length=50), nullable=False, comment='商户AppId（公开标识）'),
        sa.Column('app_secret_encrypted', sa.String(length=500), nullable=False, comment='app_secret（Fernet 加密后的 token，验签时解密）'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态：True-启用，False-禁用'),
        sa.Column('secret_updated_at', sa.DateTime(timezone=True), nullable=True, comment='密钥最近一次重置时间'),
        sa.Column('remark', sa.String(length=500), nullable=True, comment='备注'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('app_id', name='uk_sys_merchant_app_id'),
        comment='系统商户表',
    )
    op.create_index(op.f('ix_sys_merchant_id'), 'sys_merchant', ['id'], unique=True)
    op.create_index(op.f('ix_sys_merchant_code'), 'sys_merchant', ['code'], unique=False)
    op.create_index(op.f('ix_sys_merchant_app_id'), 'sys_merchant', ['app_id'], unique=False)

    op.create_table(
        'sys_openapi_log',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('app_id', sa.String(length=50), nullable=False, comment='调用方 AppId（来自请求头，可能不存在）'),
        sa.Column('method', sa.String(length=10), nullable=False, comment='HTTP方法'),
        sa.Column('path', sa.String(length=255), nullable=False, comment='请求路径'),
        sa.Column('merchant_name', sa.String(length=100), nullable=True, comment='商户名称（冗余，便于展示；可能为空）'),
        sa.Column('status_code', sa.Integer(), nullable=True, comment='HTTP响应状态码'),
        sa.Column('err_code', sa.Integer(), nullable=True, comment='业务错误码（成功为空）'),
        sa.Column('msg', sa.String(length=255), nullable=True, comment='响应消息'),
        sa.Column('client_ip', sa.String(length=50), nullable=True, comment='客户端IP'),
        sa.Column('request_id', sa.String(length=64), nullable=True, comment='请求追踪ID'),
        sa.Column('latency_ms', sa.Integer(), nullable=True, comment='请求耗时(毫秒)'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        comment='开放API调用日志表',
    )
    op.create_index(op.f('ix_sys_openapi_log_id'), 'sys_openapi_log', ['id'], unique=True)
    op.create_index(op.f('ix_sys_openapi_log_app_id'), 'sys_openapi_log', ['app_id'], unique=False)
    op.create_index(op.f('ix_sys_openapi_log_path'), 'sys_openapi_log', ['path'], unique=False)
    op.create_index(op.f('ix_sys_openapi_log_err_code'), 'sys_openapi_log', ['err_code'], unique=False)
    op.create_index(op.f('ix_sys_openapi_log_request_id'), 'sys_openapi_log', ['request_id'], unique=False)

    # ================================================================
    # Tables with FK dependencies
    # ================================================================

    op.create_table(
        'sys_dict_item',
        sa.Column('id', sa.BigInteger(), nullable=False, comment='雪花算法主键 ID'),
        sa.Column('dict_id', sa.BigInteger(), nullable=False, comment='关联字典ID'),
        sa.Column('value', sa.String(100), nullable=False, comment='字典项值'),
        sa.Column('label', sa.String(100), nullable=False, comment='字典项文本'),
        sa.Column('description', sa.Text(), nullable=True, comment='字典项描述'),
        sa.Column('ext_info', sa.Text(), nullable=True, comment='扩展信息(JSON格式)'),
        sa.Column('status', sa.Boolean(), nullable=False, comment='状态'),
        sa.Column('sort', sa.Integer(), nullable=False, comment='排序号'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间，为空则未删除'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dict_id'], ['sys_dict.id'], ondelete='CASCADE'),
        comment='系统字典数据表\n存储字典的具体数据项',
    )
    op.create_index(op.f('ix_sys_dict_item_id'), 'sys_dict_item', ['id'], unique=True)

    op.create_table(
        'sys_role_menu',
        sa.Column('role_id', sa.BigInteger(), nullable=False, comment='角色ID'),
        sa.Column('menu_id', sa.BigInteger(), nullable=False, comment='菜单ID'),
        sa.Column('permission', sa.String(255), nullable=False, comment='权限类型'),
        sa.PrimaryKeyConstraint('role_id', 'menu_id'),
        sa.ForeignKeyConstraint(['menu_id'], ['sys_menu.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['sys_role.id'], ondelete='CASCADE'),
        comment='角色菜单关联表',
    )

    op.create_table(
        'sys_user_role',
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('role_id', sa.BigInteger(), nullable=False, comment='角色ID'),
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        sa.ForeignKeyConstraint(['role_id'], ['sys_role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['sys_user.id'], ondelete='CASCADE'),
        comment='用户角色关联表',
    )


def downgrade() -> None:
    op.drop_table('sys_user_role')
    op.drop_table('sys_role_menu')
    op.drop_table('sys_dict_item')
    op.drop_table('sys_openapi_log')
    op.drop_table('sys_merchant')
    op.drop_table('sys_scheduled_task_log')
    op.drop_table('sys_scheduled_task')
    op.drop_table('sys_notice_read')
    op.drop_table('sys_notice')
    op.drop_table('sys_operation_log')
    op.drop_table('sys_login_log')
    op.drop_table('sys_ip_blacklist')
    op.drop_table('sys_file')
    op.drop_table('sys_export_template')
    op.drop_table('sys_export_task')
    op.drop_table('sys_menu')
    op.drop_table('sys_role')
    op.drop_table('sys_user')
    op.drop_table('sys_dept')
    op.drop_table('sys_dict')
    op.drop_table('sys_config')
    op.drop_table('plugin_registry')
    op.drop_table('app_user')
    op.execute('DROP TYPE IF EXISTS menutype')
    op.execute('DROP TYPE IF EXISTS configgroup')
    op.execute('DROP TYPE IF EXISTS configtype')
    op.execute('DROP TYPE IF EXISTS sys_role_data_scope')
