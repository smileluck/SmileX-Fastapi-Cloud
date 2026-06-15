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
- [2026-06-09 任务管理](./2026-06-09_task-management.md) — 机器人巡逻/播报任务管理，含任务配置、执行控制、历史记录
- [2026-06-11 机器人配置迁移修复](./2026-06-11_robot-config-migration-fix.md) — 修复 robot_voice_config 存量表缺少 robot_id 导致语音配置接口 500
- [2026-06-11 人脸识别人像预览路径修复](./2026-06-11_face-photo-preview-path.md) — 避免持久化带 token 的完整预览 URL 导致 photo_url 超长 422
- [2026-06-11 人脸识别删除修复](./2026-06-11_face-delete-fix.md) — 修复删除配置时错误调用 soft_delete，并补齐移除人像清空字段
- [2026-06-11 人脸识别人像上传接口修复](./2026-06-11_face-upload-endpoint.md) — 新增机器人配置专用上传接口，避免上传人像 404
- [2026-06-11 机器人参数配置选择机器人布局调整](./2026-06-11_robot-config-select-layout.md) — 行走速度和电量报警阈值改为下拉选择机器人后读取配置
- [2026-06-11 地图编辑器右侧卡片与机器人总览](./2026-06-11_map-editor-right-panel-robot-overview.md) — 修复右侧卡片遮盖并新增机器人总览 tab
- [2026-06-11 地图编辑器机器人定位与绑定场景](./2026-06-11_map-editor-robot-location-binding.md) — 机器人总览列表支持定位与切换绑定场景
- [2026-06-11 场景地图 JSON 点位导入](./2026-06-11_scene-map-json-import.md) — 地图编辑器支持将 label/position JSON 导入为标注点
- [2026-06-11 机器人场景绑定可空与存量库缺列修复](./2026-06-11_robot-map-binding-nullable-fix.md) — robot.map_id 缺列自动补齐，未绑定场景不支持定位
- [2026-06-11 地图编辑器新增场景图片与起始点位](./2026-06-11_map-editor-create-scene-image-start-point.md) — 新增场景上传图片并按原图/网页显示尺寸缩放保存起始点位
