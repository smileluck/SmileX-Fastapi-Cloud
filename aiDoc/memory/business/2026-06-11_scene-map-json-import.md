# 场景地图 JSON 点位导入

## 需求描述

地图编辑器需要支持将用户提供的点位 JSON 导入为场景地图标注。输入数据包含 `label`、`position`、`node`、`description`，其中 `position` 的前三项分别映射为标注的 `x`、`y`、`angle`。

## 状态

已完成

## 涉及范围

### 后端

无后端模型变更；当前标注模型仅保存 `name`、`x`、`y`、`angle`、`type`。

### 前端

- 地图编辑器工具栏增加 JSON 导入入口
- 地图编辑器将导入数据转换为标注点并加入当前选中地图

## 约束与备注

- `label` 映射为标注名称
- 重复 `label` 使用 `description` 对名称进行消歧
- 当前模型不保存 `node` 和 `description` 原始字段
- 导入点位类型使用接待点 `reception`

## 相关文件

- `frontend/src/views/scene/map-editor/index.vue`
- `frontend/src/views/scene/map-editor/composables/useMapEditor.ts`
- `frontend/src/views/scene/map-editor/modules/editor-toolbar.vue`

## 记录日期

2026-06-11
