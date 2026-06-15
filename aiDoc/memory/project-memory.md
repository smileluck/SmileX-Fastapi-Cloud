# 项目记忆索引

本文件是 `aiDoc/memory/` 的总入口。

## 长期记忆

暂无。

## 业务需求记忆

- [2026-06-11 机器人配置迁移修复](./business/2026-06-11_robot-config-migration-fix.md) — 修复 robot_voice_config 存量表缺少 robot_id 导致语音配置接口 500
- [2026-06-11 人脸识别人像预览路径修复](./business/2026-06-11_face-photo-preview-path.md) — 避免持久化带 token 的完整预览 URL 导致 photo_url 超长 422
- [2026-06-11 人脸识别删除修复](./business/2026-06-11_face-delete-fix.md) — 修复删除配置时错误调用 soft_delete，并补齐移除人像清空字段
- [2026-06-11 人脸识别人像上传接口修复](./business/2026-06-11_face-upload-endpoint.md) — 新增机器人配置专用上传接口，避免上传人像 404
- [2026-06-11 机器人参数配置选择机器人布局调整](./business/2026-06-11_robot-config-select-layout.md) — 行走速度和电量报警阈值改为下拉选择机器人后读取配置
- [2026-06-11 地图编辑器右侧卡片与机器人总览](./business/2026-06-11_map-editor-right-panel-robot-overview.md) — 修复右侧卡片遮盖并新增机器人总览 tab
- [2026-06-11 地图编辑器机器人定位与绑定场景](./business/2026-06-11_map-editor-robot-location-binding.md) — 机器人总览列表支持定位与切换绑定场景
- [2026-06-11 场景地图 JSON 点位导入](./business/2026-06-11_scene-map-json-import.md) — 地图编辑器支持将 label/position JSON 导入为标注点
- [2026-06-11 机器人场景绑定可空与存量库缺列修复](./business/2026-06-11_robot-map-binding-nullable-fix.md) — robot.map_id 缺列自动补齐，未绑定场景不支持定位
- [2026-06-11 地图编辑器新增场景图片与起始点位](./business/2026-06-11_map-editor-create-scene-image-start-point.md) — 新增场景上传图片并按原图/网页显示尺寸缩放保存起始点位

## 维护说明

- 新增记忆时，在对应目录创建 Markdown 文件，并在此索引中添加条目
- 过时的记忆应及时清理
- 记忆文件应包含日期标记，便于判断时效性
