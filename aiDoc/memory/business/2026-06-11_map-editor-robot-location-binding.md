# 2026-06-11 地图编辑器机器人定位与绑定场景

## 需求描述

地图编辑器右侧“机器人总览”tab 的机器人列表条目增加定位功能和切换绑定场景功能。定位时根据机器人绑定的场景地图与最新状态位置切换地图并移动画布视口。

## 状态

已完成

## 涉及范围

### 后端

- 机器人表新增可空 `map_id` 字段，关联场景地图
- 机器人创建、更新、列表、详情响应支持 `map_id` / `map_name`
- 新增数据库迁移维护字段与外键

### 前端

- 地图编辑器右侧机器人列表条目增加“定位”按钮
- 地图编辑器右侧机器人列表条目增加绑定场景下拉选择
- 地图编辑器画布暴露按米坐标定位视口的方法
- 机器人 API 类型补齐 `map_id` / `map_name`

## 约束与备注

定位依赖机器人已绑定场景且最新状态记录包含可解析的 `location` 坐标。`location` 优先按 JSON `{ "x": number, "y": number }` 解析，失败时尝试提取字符串中的前两个数字。

## 相关文件

- `backend/database/models/business/robot.py`
- `backend/modules/robot/schemas/robot.py`
- `backend/modules/robot/services/robot_service.py`
- `backend/modules/robot/endpoints/robot.py`
- `backend/alembic/versions/0008_robot_map_binding.py`
- `frontend/src/typings/api/robot.d.ts`
- `frontend/src/views/scene/map-editor/index.vue`
- `frontend/src/views/scene/map-editor/modules/canvas-editor.vue`
- `frontend/src/views/scene/map-editor/modules/property-panel.vue`

## 记录日期

2026-06-11
