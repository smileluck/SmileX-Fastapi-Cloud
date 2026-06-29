"""initial schema (squashed from init.sql)

Revision ID: 0001
Revises:
Create Date: 2026-06-04

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
        sa.PrimaryKeyConstraint('id'),
        comment='系统用户表\n存储系统管理用户的基本信息和认证凭证',
    )
    op.create_index(op.f('ix_sys_user_id'), 'sys_user', ['id'], unique=True)
    op.create_index(op.f('ix_sys_user_username'), 'sys_user', ['username'], unique=True)

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
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        comment='系统角色表\n存储角色信息及其关联的权限配置',
    )
    op.create_index(op.f('ix_sys_role_id'), 'sys_role', ['id'], unique=True)

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

    # ================================================================
    # Seed data
    # ================================================================

    # Admin user
    op.execute("""
        INSERT INTO sys_user (id, username, password, nickname, email, phone, avatar, last_login_at, last_login_ip, status, is_superuser, deleted_at, created_at, updated_at, last_tenant_id)
        VALUES (2250298479026176, 'admin', '$2b$12$MPXWjrezSywnujoarubtJuKUJKBXugHEEqobTbIWtbJRXAp2aaTUy', '超级管理员', 'admin@example.com', '13800138000', '', NULL, NULL, TRUE, TRUE, NULL, '2026-02-02 10:00:29.81271+08', NULL, NULL)
    """)

    # System configs (rate limit)
    op.execute("""
        INSERT INTO sys_config (id, key, value, default_value, validation_rule, description, type, "group", is_system, deleted_at, created_at, updated_at) VALUES
        (2,  'rate_limit.enabled',               'true',    'true',  NULL, '限流总开关',                     'BOOLEAN', 'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (3,  'rate_limit.ip_per_minute',          '120',     '120',   NULL, 'IP 全局限流（次/分钟）',           'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (4,  'rate_limit.user_per_minute',        '300',     '300',   NULL, '用户限流（次/分钟）',             'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (5,  'rate_limit.login_fail_max',         '5',       '5',     NULL, '登录失败上限次数',                 'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (6,  'rate_limit.login_fail_window',      '600',     '600',   NULL, '登录失败统计窗口（秒）',           'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (7,  'rate_limit.login_fail_block_ttl',   '1800',    '1800',  NULL, '登录失败自动拉黑时长（秒）',       'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (8,  'rate_limit.blacklist_redis_ttl',    '86400',   '86400', NULL, '永久黑名单 Redis 兜底 TTL（秒）', 'NUMBER',  'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (9,  'rate_limit.whitelist_path_prefixes','["/docs","/redoc","/openapi.json","/admin/health"]', '["/docs","/redoc","/openapi.json","/admin/health"]', NULL, '路径白名单前缀',     'JSON',    'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (10, 'rate_limit.whitelist_ips',          '[]',      '[]',    NULL, 'IP 白名单',                      'JSON',    'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL),
        (11, 'rate_limit.path_rules',             '[]',      '[]',    NULL, '路径细粒度限流规则',              'JSON',    'SECURITY', TRUE, NULL, '2026-05-24 17:05:48.363922+08', NULL)
    """)

    # System menus (sorted by id to satisfy parent_id FK)
    op.execute("""
        INSERT INTO sys_menu (id, parent_id, name, path, component, redirect, permission, meta_icon, meta_hidden, meta_affix, meta_breadcrumb, status, type, sort, deleted_at, created_at, updated_at, is_system, meta_href, meta_keep_alive) VALUES
        (2874692539129856, NULL, 'home',                    '/home',                'layout.base$view.home',    NULL,                        NULL,                    'mdi:monitor-dashboard',                FALSE, FALSE, TRUE, TRUE, 'MENU',     1,  NULL, '2026-05-23 16:32:07.074678+08', '2026-05-23 21:29:36.710187+08', TRUE,  NULL, FALSE),
        (2874692539129857, NULL, 'manage',                  '/manage',              'layout.base',              NULL,                        NULL,                    'mdi:cog',                              FALSE, FALSE, TRUE, TRUE, 'CATALOG',  3,  NULL, '2026-05-23 16:32:07.074678+08', '2026-05-29 18:23:19.933746+08', TRUE,  NULL, FALSE),
        (2874692539129858, NULL, 'log',                      '/log',                'layout.base',              NULL,                        NULL,                    'mdi:file-document-outline',            FALSE, FALSE, TRUE, TRUE, 'CATALOG',  4,  NULL, '2026-05-23 16:32:07.074678+08', '2026-05-29 18:23:23.435562+08', TRUE,  NULL, FALSE),
        (2874692539129859, 2874692539129857, 'manage_config', '/manage/config', 'view.manage_config', NULL, 'sys:config:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 1, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129860, 2874692539129857, 'manage_dict',   '/manage/dict',   'view.manage_dict',   NULL, 'sys:dict:list',   NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 2, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129861, 2874692539129857, 'manage_menu',   '/manage/menu',   'view.manage_menu',   NULL, 'sys:menu:list',   NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 3, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129862, 2874692539129857, 'manage_role',   '/manage/role',   'view.manage_role',   NULL, 'sys:role:list',   NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 4, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129863, 2874692539129857, 'manage_user',   '/manage/user',   'view.manage_user',   NULL, 'sys:user:list',   NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 5, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129864, 2874692539129858, 'log_login-log',  '/log/login-log', 'view.log_login-log',  NULL, 'sys:login-log:list',  NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 1, NULL, '2026-05-23 16:32:07.074678+08', NULL, TRUE, NULL, FALSE),
        (2874692539129865, 2874692539129858, 'log_operation-log', '/log/operation-log', 'view.log_operation-log', NULL, 'sys:operation-log:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 2, NULL, '2026-05-23 16:32:07.074678+08', '2026-05-24 14:06:24.504114+08', TRUE, NULL, FALSE),
        (2879249581154304, 2874692539129857, 'log_online-user', '/log/online-user', 'view.log_online-user', NULL, 'sys:online-user:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 9, NULL, '2026-05-24 11:51:01.998205+08', '2026-05-24 14:06:39.545192+08', TRUE, NULL, FALSE),
        (2880160334618624, 2874692539129861, 'manage_menu_list',    NULL, NULL, NULL, 'sys:menu:list',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334618625, 2874692539129861, 'manage_menu_add',     NULL, NULL, NULL, 'sys:menu:add',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334684160, 2874692539129861, 'manage_menu_edit',    NULL, NULL, NULL, 'sys:menu:edit',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334684161, 2874692539129861, 'manage_menu_delete',  NULL, NULL, NULL, 'sys:menu:delete',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334684162, 2874692539129862, 'manage_role_list',    NULL, NULL, NULL, 'sys:role:list',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749696, 2874692539129862, 'manage_role_add',     NULL, NULL, NULL, 'sys:role:add',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749697, 2874692539129862, 'manage_role_edit',    NULL, NULL, NULL, 'sys:role:edit',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749698, 2874692539129862, 'manage_role_delete',  NULL, NULL, NULL, 'sys:role:delete',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749699, 2874692539129863, 'manage_user_list',    NULL, NULL, NULL, 'sys:user:list',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749700, 2874692539129863, 'manage_user_add',     NULL, NULL, NULL, 'sys:user:add',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749701, 2874692539129863, 'manage_user_edit',    NULL, NULL, NULL, 'sys:user:edit',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334749702, 2874692539129863, 'manage_user_delete',  NULL, NULL, NULL, 'sys:user:delete',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334815232, 2874692539129860, 'manage_dict_list',    NULL, NULL, NULL, 'sys:dict:list',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334815233, 2874692539129860, 'manage_dict_add',     NULL, NULL, NULL, 'sys:dict:add',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334815234, 2874692539129860, 'manage_dict_edit',    NULL, NULL, NULL, 'sys:dict:edit',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334815235, 2874692539129860, 'manage_dict_delete',  NULL, NULL, NULL, 'sys:dict:delete',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334815236, 2874692539129859, 'manage_config_list',  NULL, NULL, NULL, 'sys:config:list',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880768, 2874692539129859, 'manage_config_add',   NULL, NULL, NULL, 'sys:config:add',   NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880769, 2874692539129859, 'manage_config_edit',  NULL, NULL, NULL, 'sys:config:edit',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880770, 2874692539129859, 'manage_config_delete',NULL, NULL, NULL, 'sys:config:delete',NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880771, 2874692539129864, 'log_login-log_list',    NULL, NULL, NULL, 'sys:log:list',   NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880772, 2874692539129864, 'log_login-log_delete',  NULL, NULL, NULL, 'sys:log:delete', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334880773, 2874692539129865, 'log_operation-log_list', NULL, NULL, NULL, 'sys:oplog:list', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334946304, 2874692539129865, 'log_operation-log_delete',NULL,NULL, NULL, 'sys:oplog:delete',NULL,TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334946305, 2879249581154304, 'log_online-user_list', NULL, NULL, NULL, 'sys:online:list',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880160334946306, 2879249581154304, 'log_online-user_kick', NULL, NULL, NULL, 'sys:online:kick',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 15:42:39.00864+08',  NULL, TRUE, NULL, FALSE),
        (2880487316791296, 2874692539129857, 'manage_ip-blacklist', '/manage/ip-blacklist', 'view.manage_ip-blacklist', NULL, 'sys:blacklist:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 10, NULL, '2026-05-24 17:05:48.363922+08', NULL, TRUE, NULL, FALSE),
        (2880487316987904, 2880487316791296, 'manage_ip-blacklist_list',   NULL, NULL, NULL, 'sys:blacklist:list',   NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-24 17:05:48.363922+08', NULL, TRUE, NULL, FALSE),
        (2880487317118976, 2880487316791296, 'manage_ip-blacklist_add',    NULL, NULL, NULL, 'sys:blacklist:add',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-24 17:05:48.363922+08', NULL, TRUE, NULL, FALSE),
        (2880487317118977, 2880487316791296, 'manage_ip-blacklist_remove', NULL, NULL, NULL, 'sys:blacklist:remove', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-24 17:05:48.363922+08', NULL, TRUE, NULL, FALSE),
        (2886339278741504, 2874692539129857, 'manage_announcement', '/manage/announcement', 'view.manage_announcement', NULL, 'sys:notice:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 11, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2886339279134720, 2886339278741504, 'manage_announcement_list',    NULL, NULL, NULL, 'sys:notice:list',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2886339279134721, 2886339278741504, 'manage_announcement_add',     NULL, NULL, NULL, 'sys:notice:add',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2886339279134722, 2886339278741504, 'manage_announcement_edit',    NULL, NULL, NULL, 'sys:notice:edit',    NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2886339279134723, 2886339278741504, 'manage_announcement_delete',  NULL, NULL, NULL, 'sys:notice:delete',  NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2886339279134724, 2886339278741504, 'manage_announcement_publish', NULL, NULL, NULL, 'sys:notice:publish', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 5, NULL, '2026-05-25 17:54:02.170377+08', NULL, TRUE, NULL, FALSE),
        (2907499345027072, NULL, 'demo',                        '/demo',                'layout.base',              NULL,                        NULL, 'arcticons:example',                    FALSE, FALSE, TRUE, TRUE, 'CATALOG',  5,  NULL, '2026-05-29 11:35:19.200988+08', '2026-05-29 15:14:30.990737+08', TRUE,  NULL, FALSE),
        (2907499345027073, NULL, 'monitor',                     '/monitor',             'layout.base$view.monitor',  NULL,                        'sys:monitor:list', 'mdi:chart-areaspline-variant',    FALSE, FALSE, TRUE, TRUE, 'MENU',     2,  NULL, '2026-05-28 20:18:46.884071+08', '2026-05-29 18:23:07.213857+08', TRUE,  NULL, FALSE),
        (2907499345027074, 2907499345027073, 'monitor_view',    NULL, NULL, NULL, 'sys:monitor:view', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-28 20:18:46.884071+08', NULL, TRUE, NULL, FALSE),
        (2907499345027075, 2907499345027072, 'demo_upload',     '/demo/upload', 'view.demo_upload', NULL, NULL, 'mdi:upload', FALSE, FALSE, TRUE, TRUE, 'MENU', 5, NULL, '2026-05-28 23:08:07.48867+08', '2026-05-29 15:13:41.448095+08', TRUE, NULL, FALSE),
        (2907499345027076, 2874692539129857, 'manage_file',     '/manage/file', 'view.manage_file', NULL, 'sys:file:list', NULL, FALSE, FALSE, TRUE, TRUE, 'MENU', 8, NULL, '2026-05-28 23:08:07.48867+08', NULL, TRUE, NULL, FALSE),
        (2907499345027077, 2907499345027076, 'manage_file_list',     NULL, NULL, NULL, 'sys:file:list',     NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 1, NULL, '2026-05-28 23:08:07.48867+08', NULL, TRUE, NULL, FALSE),
        (2907499345027078, 2907499345027076, 'manage_file_upload',   NULL, NULL, NULL, 'sys:file:upload',   NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 2, NULL, '2026-05-28 23:08:07.48867+08', NULL, TRUE, NULL, FALSE),
        (2907499345027079, 2907499345027076, 'manage_file_download', NULL, NULL, NULL, 'sys:file:download', NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 3, NULL, '2026-05-28 23:08:07.48867+08', NULL, TRUE, NULL, FALSE),
        (2907499345027080, 2907499345027076, 'manage_file_delete',   NULL, NULL, NULL, 'sys:file:delete',   NULL, TRUE, FALSE, FALSE, TRUE, 'BUTTON', 4, NULL, '2026-05-28 23:08:07.48867+08', NULL, TRUE, NULL, FALSE),
        (2907499345027081, 2907499345027072, 'demo_dict',       '/demo/dict', 'view.demo_dict', NULL, NULL, 'mdi:book-alphabet', FALSE, FALSE, TRUE, TRUE, 'MENU', 4, NULL, '2026-06-04 16:00:00+08', NULL, TRUE, NULL, FALSE),
        (2942406613671936, NULL, 'scheduler', '/scheduler', 'layout.base', '/scheduler/task', NULL, 'material-symbols:schedule-outline', FALSE, FALSE, TRUE, TRUE, 'CATALOG', 95, NULL, '2026-06-04 15:32:41.846173+08', NULL, FALSE, NULL, FALSE),
        (2942406615113728, 2942406613671936, 'scheduler_task', '/scheduler/task', 'view.scheduler_task', NULL, 'sys:scheduler:list', 'material-symbols:task-alt-outline', FALSE, FALSE, TRUE, TRUE, 'MENU', 1, NULL, '2026-06-04 15:32:41.875798+08', NULL, FALSE, NULL, FALSE),
        (2942406615965696, 2942406615113728, '新增任务',  NULL, NULL, NULL, 'sys:scheduler:add',     NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.884895+08', NULL, FALSE, NULL, FALSE),
        (2942406615965697, 2942406615113728, '编辑任务',  NULL, NULL, NULL, 'sys:scheduler:edit',    NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.884895+08', NULL, FALSE, NULL, FALSE),
        (2942406615965698, 2942406615113728, '删除任务',  NULL, NULL, NULL, 'sys:scheduler:delete',  NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.884895+08', NULL, FALSE, NULL, FALSE),
        (2942406615965699, 2942406615113728, '任务详情',  NULL, NULL, NULL, 'sys:scheduler:detail',  NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.88592+08',  NULL, FALSE, NULL, FALSE),
        (2942406615965700, 2942406615113728, '启停任务',  NULL, NULL, NULL, 'sys:scheduler:status',  NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.88592+08',  NULL, FALSE, NULL, FALSE),
        (2942406615965701, 2942406615113728, '手动执行',  NULL, NULL, NULL, 'sys:scheduler:trigger', NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.88592+08',  NULL, FALSE, NULL, FALSE),
        (2942406615965702, 2942406613671936, 'scheduler_log', '/scheduler/log', 'view.scheduler_log', NULL, 'sys:scheduler:log:list', 'material-symbols:history', FALSE, FALSE, TRUE, TRUE, 'MENU', 2, NULL, '2026-06-04 15:32:41.886454+08', NULL, FALSE, NULL, FALSE),
        (2942406617800704, 2942406615965702, '日志详情',  NULL, NULL, NULL, 'sys:scheduler:log:detail',  NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.899353+08', NULL, FALSE, NULL, FALSE),
        (2942406617800705, 2942406615965702, '删除日志',  NULL, NULL, NULL, 'sys:scheduler:log:delete',  NULL, FALSE, FALSE, TRUE, TRUE, 'BUTTON', 0, NULL, '2026-06-04 15:32:41.899767+08', NULL, FALSE, NULL, FALSE)
    """)

    # Gender dict
    op.execute("""
        INSERT INTO sys_dict (id, name, code, description, status, is_system, sort, deleted_at, created_at, updated_at) VALUES
        (8, '性别', 'gender', '性别字典：男、女、未知', TRUE, TRUE, 1, NULL, '2026-06-03 21:52:40.052698+08', '2026-06-03 21:52:40.052698+08')
    """)

    op.execute("""
        INSERT INTO sys_dict_item (id, dict_id, value, label, description, ext_info, status, sort, deleted_at, created_at, updated_at) VALUES
        (7, 8, '1', '男',   NULL, NULL, TRUE, 1, NULL, '2026-06-03 21:52:40.052698+08', '2026-06-03 21:52:40.052698+08'),
        (8, 8, '2', '女',   NULL, NULL, TRUE, 2, NULL, '2026-06-03 21:52:40.052698+08', '2026-06-03 21:52:40.052698+08'),
        (9, 8, '0', '未知', NULL, NULL, TRUE, 3, NULL, '2026-06-03 21:52:40.052698+08', '2026-06-03 21:52:40.052698+08')
    """)

    # System scheduled tasks
    op.execute("""
        INSERT INTO sys_scheduled_task (id, name, task_key, cron_expression, description, trigger_type, trigger_params, status, module, function_path, is_system, last_run_at, next_run_at, last_status, timeout, max_retries, concurrent_policy, deleted_at, created_at, updated_at) VALUES
        (2938394705010688, '清理过期操作日志', 'system.cleanup_operation_logs', '0 3 * * *', '自动清理30天前的操作日志', 'cron', NULL, TRUE, 'modules.scheduler.tasks.builtin', 'modules.scheduler.tasks.builtin.cleanup_operation_logs', TRUE, NULL, NULL, NULL, 300, 0, 'skip', NULL, '2026-06-03 22:32:24.969304+08', NULL),
        (2938394705010689, '清理过期登录日志', 'system.cleanup_login_logs',     '0 4 * * *', '自动清理30天前的登录日志', 'cron', '',    TRUE, 'modules.scheduler.tasks.builtin', 'modules.scheduler.tasks.builtin.cleanup_login_logs',     TRUE, NULL, NULL, NULL, 300, 0, 'skip', NULL, '2026-06-03 22:32:24.97958+08',  NULL),
        (2942449943060480, '刷新限流配置缓存', 'system.refresh_rate_limit_config', '25', '定时从数据库刷新限流参数到内存缓存，避免请求路径上回源', 'interval', '{"seconds": 25}', TRUE, 'modules.scheduler.tasks.rate_limit_config', 'modules.scheduler.tasks.rate_limit_config.refresh_rate_limit_config', TRUE, NULL, NULL, NULL, 300, 0, 'skip', NULL, '2026-06-04 15:43:43.002522+08', NULL)
    """)


def downgrade() -> None:
    op.drop_table('sys_user_role')
    op.drop_table('sys_role_menu')
    op.drop_table('sys_dict_item')
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
    op.drop_table('sys_dict')
    op.drop_table('sys_config')
    op.drop_table('plugin_registry')
    op.drop_table('app_user')
    op.execute('DROP TYPE IF EXISTS menutype')
    op.execute('DROP TYPE IF EXISTS configgroup')
    op.execute('DROP TYPE IF EXISTS configtype')
