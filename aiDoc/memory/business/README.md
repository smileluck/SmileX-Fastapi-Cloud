# 业务需求记忆

存放每次用户提出的业务需求记录。

## 规则

- 用户提出业务需求时，**必须**新增或更新一条记录
- 使用 `TEMPLATE.md` 作为新记录的模板
- 记录完成后在 `project-memory.md` 中更新索引

## 需求索引

- [2026-05-24 API 限流 / IP 黑名单](./2026-05-24_rate_limit_blacklist.md) — Redis 多维度限流 + DB 持久化 IP 黑名单 + 自动拉黑
- [2026-05-31 多租户插件](./2026-05-31_multi_tenant_plugin.md) — 可选多租户插件，行级隔离，JWT 识别租户
- [2026-05-31 租户表隔离与权限设计](./2026-05-31_tenant_table_permissions.md) — strict/optional/全局三级隔离 + 权限分级
- [2026-06-01 租户 JWT 配置 + 登录自动选择租户](./2026-06-01_tenant_jwt_config_and_auto_select.md) — 混合模式 JWT 签名 + 登录自动选租户 + Redis/DB 双写
- [2026-06-01 插件安装自动更新 PLUGINS__ENABLED](./2026-06-01_auto_update_plugins_enabled.md) — 安装/卸载插件时自动更新 .env 中的启用列表
- [2026-06-03 数据库模块迁移](./2026-06-03_database_migration.md) — ORM 模型、连接管理、工具函数统一迁移到 database/ 包
- [2026-06-03 字典通用组件](./2026-06-03_dict_components.md) — useDict composable + DictSelect/DictTag/DictText 通用组件 + gender 种子数据
- [2026-06-17 登录 redirect 不生效修复](./2026-06-17_login_redirect_fix.md) — checkTabClear 在首次登录会吞掉 redirect 参数，登录后误回首页
- [2026-06-25 登录默认页改为权限列表第一项](./2026-06-25_login_home_from_first_permission.md) — 后端按菜单顺序 DFS 取首个有 component 的叶子作为 home
- [2026-06-25 数据权限（行级可见性）](./2026-06-25_data_scope_permission.md) — 角色配置 data_scope（ALL/DEPT_AND_SUB/DEPT_ONLY/SELF）+ 部门树 + Service 层注入过滤；含用户管理示范
- [2026-06-27 登录与菜单三件套修复](./2026-06-27_login_misc_fixes.md) — 菜单 iconType 持久化 + 侧边栏本地 icon 渲染；确认黑名单自动拉黑 IP 来源；记住密码本地缓存回填；在线用户列表去重（同 IP+UA 顶掉旧 session）；补全部门管理菜单种子 + 多租户插件支持 sys_dept 隔离
- [2026-07-04 用户/角色管理缺陷修复 + 提交类型约束加固](./2026-07-04_user_role_manage_hardening.md) — 角色重名查重(create+update)、create_user 加载 roles 修复 422、前端 flat-request 错误处理改 {error} 解构、User/Role 专用请求类型、Dict is_system 对齐、各模块 schema 校验加固
