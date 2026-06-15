# 机器人场景绑定可空与存量库缺列修复

## 需求描述

修复机器人列表/定位相关接口在存量数据库缺少 `robot.map_id` 字段时触发 500 的问题。机器人关联场景允许为空，只有绑定场景后才支持定位。

## 状态

已完成

## 涉及范围

### 后端

- 启动时检查并补齐 `robot.map_id` 字段
- 机器人管理接口查询前确保 `robot.map_id` 存在
- `map_id` 保持可空，未绑定时响应为空

### 前端

- 地图编辑器机器人总览已有未绑定场景时提示“请先绑定场景”的定位限制

## 约束与备注

- 存量数据库可能已经应用旧版本迁移但未执行 `0008_robot_map_binding`，因此运行时需要幂等检查补列
- 定位依赖 `map_id` 和最新状态记录中的 `location` 坐标，未绑定场景不执行定位

## 相关文件

- `backend/main.py`
- `backend/modules/robot/endpoints/robot.py`
- `backend/modules/robot/services/robot_schema_service.py`
- `backend/modules/robot/services/robot_service.py`
- `frontend/src/views/scene/map-editor/modules/property-panel.vue`

## 记录日期

2026-06-11
