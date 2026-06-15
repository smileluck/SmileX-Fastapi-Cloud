---
name: robot-scene-modules
description: 机器人管理和场景地图管理模块需求（2026-06-08）
metadata:
  type: project
  created: 2026-06-08
---

## 需求：机器人与场景管理模块

新增7个业务子模块：

1. **机器人型号管理** — ID, 名称, 品牌, 型号。CRUD。
2. **机器人管理** — ID, 名称, 型号(FK→型号), 序列号, 状态(在线/离线/未激活)。CRUD。
3. **机器人状态记录** — 机器人管理的子入口（只读），电量, 信号, 速度, 位置(JSON)。
4. **场景分组管理** — ID, 名称, 父级(nullable)。树形结构，前端普通表格展示。
5. **场景地图管理** — ID, 名称, 分组(FK), 二维图(文件上传)。
6. **场景地图标注** — 地图子入口，x, y, 名称, 角度, 类型(字典: 接待点/服务点)。
7. **场景地图物体** — 地图子入口，类型(字典: 墙体/虚拟墙/禁行区/自定义), x, y, width, height, 不规则物体(JSON points)。

### 后端
- 两个新模块 `modules/robot/` 和 `modules/scene/`
- 模型在 `database/models/business/`
- 字典: map_annotation_type, map_object_type, robot_status

### 前端
- 4个页面: robot/model, robot/manage, scene/group, scene/map
- 子入口: 状态记录(只读抽屉), 地图详情(抽屉含标注/物体Tab)
- 字典组件用于类型选择
