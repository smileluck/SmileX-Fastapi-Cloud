# 人脸识别删除修复

## 需求描述

修复人脸识别 TTS 删除配置时报错的问题，并补齐人像上传控件移除图片时清空表单字段的行为。

## 状态

已完成

## 涉及范围

### 后端

- 人脸识别配置删除服务按项目现有模式同步调用 `soft_delete()`
- 删除配置后提交事务，确保软删除生效

### 前端

- 人像上传控件移除图片时同步清空 `photo_url`

## 约束与备注

- `Base.soft_delete()` 是同步无参方法，不应传入数据库会话或使用 `await`
- 删除已配置人员是软删除业务记录，不直接删除文件管理中的上传文件

## 相关文件

- `backend/modules/robot/services/robot_config_service.py`
- `frontend/src/views/settings/modules/face-recognition-tab.vue`

## 记录日期

2026-06-11
