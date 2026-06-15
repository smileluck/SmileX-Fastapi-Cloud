---
name: scene-map-enhancements
description: 场景地图新增/编辑功能增强：图片上传 + 分组选择/输入
metadata:
  type: business
---

## 需求：场景地图新增功能增强

### 时间
2026-06-08

### 内容
1. **图片上传**：新增场景地图时支持上传图片文件，替代原来的手动输入图片ID
2. **所属分组选择/输入**：分组支持两种模式——选择已有分组 或 输入新分组名称，输入的新分组名称如果不存在则自动创建

### 实现方式
- **后端**：`SceneMapCreate` schema 新增 `group_name` 字段，service 层 `_resolve_group_id` 方法按名称查找已有分组，不存在时自动创建
- **前端**：operate drawer 使用 `NUpload` 组件上传图片，分组使用选择/输入切换按钮，分别用 `NSelect` 和 `NInput` 实现

### 涉及文件
- `backend/modules/scene/schemas/scene_map.py`
- `backend/modules/scene/services/scene_map_service.py`
- `frontend/src/views/scene/map/modules/scene-map-operate-drawer.vue`
- `frontend/src/typings/api/scene.d.ts`
