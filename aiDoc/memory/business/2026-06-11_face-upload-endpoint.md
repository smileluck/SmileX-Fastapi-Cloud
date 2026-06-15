# 人脸识别人像上传接口修复

## 需求描述

修复人脸识别 TTS 上传人像时提示 404 的问题。

## 状态

已完成

## 涉及范围

### 后端

- 在机器人参数配置模块新增专用人像上传接口 `/robot/config/face/upload`
- 复用系统文件存储服务写入 `sys_file`
- 使用 `robot:config:edit` 权限，不再要求页面额外具备系统文件管理上传权限
- 请求体大小限制中加入机器人配置人像上传路径豁免

### 前端

- 人脸识别页面上传人像改调 `/robot/config/face/upload`
- 上传成功后继续保存短预览路径 `/admin/sys/file/{id}/preview`

## 约束与备注

- 人脸识别配置页属于机器人参数配置模块，上传人像应使用该模块权限边界
- 文件预览仍复用系统文件预览接口，业务表只持久化不带 token 的短路径

## 相关文件

- `backend/modules/robot/endpoints/robot_config.py`
- `backend/core/middleware/security_middleware.py`
- `frontend/src/service/api/robot-config.ts`
- `frontend/src/views/settings/modules/face-recognition-tab.vue`

## 记录日期

2026-06-11
