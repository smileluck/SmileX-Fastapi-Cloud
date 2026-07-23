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
- [2026-07-11 本地 .log 日志按日期目录滚动](./2026-07-11_rolling_logs_by_date.md) — Python 应用日志与 Gunicorn access/error 日志统一按 `YYYY-MM-DD/` 目录滚动，完善 deploy/deploy.sh 与 systemd 服务
- [2026-07-05 商户管理 + 开放API HMAC 签名鉴权](./2026-07-05_merchant_openapi_auth.md) — sys_merchant 表（app_secret Fernet 加密）+ 后台 CRUD/重置密钥 + /open/* HMAC-SHA256 签名校验（时间戳窗口 + Redis nonce 防重放）+ /open/demo/ping 示例 +（迭代）商户开放管理目录 + sys_openapi_log 调用日志中间件
- [2026-07-07 异步导出、全局校验、角色表单与登录禁用优化](./2026-07-07_export_validation_login_disable.md) — 头部导出记录入口 + 操作日志异步导出 + APScheduler 每分钟执行/超时清理、WebSocket+轮询状态同步、BaseReqEntity 全局 trim + BaseRespEntity 类型安全、PageRequest int 防御 + 中文错误、角色 name/desc 长度前后端校验、禁用用户登录拦截、操作日志 total 修复 + 导出轮询白名单
- [2026-07-13 导出记录弹窗状态标识优化 + 查看全部路由修复](./2026-07-13_export_record_ui_and_constant_route.md) — 弹窗状态由图标改为 NTag（绿成功/红失败/黄生成中/灰排队）+ 下载按钮补 i18n 文本；export-record 路由纳入 constant 列表（dynamic 模式下后端菜单不返回 hideInMenu 路由）
- [2026-07-13 新建商户「数据校验错误」修复](./2026-07-13_merchant_create_validation_fix.md) — SysMerchantWithSecret.app_secret 原必填，model_validate(ORM) 缺字段抛 ValidationError；改 default=""，端点既有逻辑随后赋真实明文
- [2026-07-13 开放API测试页 crypto.subtle 报错修复](./2026-07-13_openapi_test_crypto_subtle_fallback.md) — HTTP/局域网下 crypto.subtle 为 undefined 导致 importKey 崩溃；新增 hmac-sha256 util（原生优先 + 纯 JS 回退，已用标准向量验证）
- [2026-07-13 启动时打印日志文件落地位置](./2026-07-13_print_log_location_on_startup.md) — setup_logging() 在 fileConfig 后动态读取 root logger 的文件 handler，打印日志目录/文件/归档子目录
- [2026-07-13 i18n Schema 补全 + 类型清理](./2026-07-13_i18n_schema_and_type_cleanup.md) — app.d.ts 补 exportTask/notification.tooltip/role.form.maxLength；修 dict Ref 导入、export blob 直传、角色选择 value 改 name（潜在 Bug）、number[] 转换、bordered 布尔；typecheck 38→0
- [2026-07-13 操作日志白名单补充高频轮询接口](./2026-07-13_operation_log_whitelist_polling.md) — 据近 3h 日志 Top，白名单追加 /admin/sys/route、notice/my/unread-count、notice/my/list；写操作与业务列表保留
- [2026-07-13 表格空字段统一显示为 "-"](./2026-07-13_table_empty_cell_placeholder.md) — 在共享 table hook 的 getColumns 注入默认 render（tableCellText），16 表自动生效；menu 内联表 routeName/routePath 手工补
- [2026-07-14 用户编辑保存角色不生效修复](./2026-07-14_user_list_roles_for_edit.md) — 列表响应 `SysUserListResponse` 缺 `roles`，编辑抽屉无法回填 → 保存提交 `role_ids:[]` 清空角色；补 `roles` 字段（selectinload 已有，零额外查询）
- [2026-07-14 密码复杂度策略：6-20 位且至少含字母+数字](./2026-07-14_password_complexity_policy.md) — 收紧 REG_PWD 用于写入侧（新建/修改/注册/重置），登录改仅非空避免拦截旧密码；后端 SysUserCreate/SysUserPasswordUpdate 加 validator（修 new_password max 100→20）
- [2026-07-14 调度器时区修复 + create_superuser naive 时间](./2026-07-14_scheduler_timezone_fix.md) — APScheduler/CronTrigger.from_crontab 默认按服务器本地时区，UTC 服务器 cron 偏移 8h；三处显式固定 Asia/Shanghai；create_superuser 改 aware
- [2026-07-15 关于我们页面（前端常驻路由 + 构建时 Git 历史）](./2026-07-15_about_page.md) — 左右布局「关于」页：左项目介绍（定位/技术栈/特性），右 NTimeline 展示 Git 提交；about 经 `onRouteMetaGen` 标 constant 进侧边栏固定菜单（不走动态菜单）；Git 历史由自研 vite 插件 buildStart 采集、经 virtual module 暴露，无 git 空态；纯前端不动后端
- [2026-05-27 运维 P0 修复：健康探针 + 启动硬终止](./2026-05-27_ops_p0_health_probe.md) — 新增无鉴权顶级探针 `/health`（liveness）与 `/ready`（readiness，检查 DB+Redis）；`deploy.env` 健康检查从 `/openapi.json` 改为 `/ready`（修复生产环境 openapi 被禁用导致健康检查恒 404）；`main.py` lifespan 调度器同步失败改为硬阻止启动，IP 黑名单预热失败加结构化降级日志，种子数据降 WARNING；**采用顶级路由方案（B 方案）**——澄清 `/open/*` 是商户 HMAC 签名接口（探针恒 401），`/admin/sys/*` 需额外维护操作日志白名单，顶级路径天然不受任何业务中间件约束，无需维护白名单
