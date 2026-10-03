<!-- last-updated: 2026-05-31 -->
# 多租户插件

- **日期**: 2026-05-31
- **状态**: 开发中
- **类型**: 新功能

## 需求描述

实现多租户功能，但作为**可选插件**，仅在需要时安装。核心系统不受影响。

## 关键决策

- **租户识别**: JWT Token claim（tenant_id 写入 JWT）
- **用户-租户关系**: 多对多，带租户切换器
- **数据隔离**: 行级（tenant_id 列），复用软删除的 `with_loader_criteria` 模式
- **隔离范围**:
  - 严格隔离（strict）：sys_role, sys_config, sys_dict, sys_dict_item, sys_file, app_user, sys_operation_log, sys_login_log
  - 可选隔离（optional）：sys_menu, sys_notice（全局 + 租户级）
  - 纯全局：sys_user, sys_ip_blacklist
- **权限分级**: 详见 `2026-05-31_tenant_table_permissions.md`

## 涉及模块

- `backend/plugins/` — 新增插件框架 + 多租户插件
- `backend/core/config/` — 新增 PluginModel 配置
- `backend/core/registry/setup_registry.py` — 加载插件
- `backend/core/security/oauth/jwt.py` — 支持 extra_claims
- `frontend/src/plugins/multi_tenant/` — 前端租户插件

## 安装方式

1. `.env` 添加 `PLUGINS__ENABLED=["multi_tenant"]`
2. `alembic/env.py` 取消注释租户模型导入
3. 运行 `alembic revision --autogenerate` + `alembic upgrade head`
4. 运行 `python -m plugins.multi_tenant.install`
