# 机器人配置迁移修复

## 需求描述

修复语音合成配置接口访问 `/robot/config/voice` 时，数据库表 `robot_voice_config` 缺少 `robot_id` 字段导致 500 的问题。

## 状态

已完成

## 涉及范围

### 后端

- Alembic 迁移：为已创建但缺少 `robot_id` 的 `robot_voice_config` 表补齐字段、外键和唯一约束
- 机器人参数配置模块：保持语音配置按 `robot_id` 查询与保存

### 前端

无直接变更

## 约束与备注

- 当前 `0006` 迁移已包含 `robot_id`，但已应用旧版本 `0006` 的数据库不会自动重跑，需要后续迁移修复存量库结构
- 修复迁移应保持幂等，避免新库重复创建列或约束

## 相关文件

- `backend/alembic/versions/0007_fix_robot_voice_config_robot_id.py`
- `backend/alembic/versions/0006_robot_config_tables.py`
- `backend/database/models/business/robot_voice_config.py`
- `backend/modules/robot/services/robot_config_service.py`

## 记录日期

2026-06-11
