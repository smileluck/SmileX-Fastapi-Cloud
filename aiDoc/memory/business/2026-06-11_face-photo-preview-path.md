# 人脸识别人像预览路径修复

## 需求描述

修复人脸识别 TTS 创建接口 `/robot/config/face` 因前端提交带 token 的完整人像预览 URL，超过后端 `photo_url` 255 字符限制导致 422 的问题。

## 状态

已完成

## 涉及范围

### 后端

- 人脸识别配置请求模型对 `photo_url` 做兼容清洗：完整预览 URL 转为不带 query token 的预览路径
- 保持 `photo_url` 数据库存储为短路径，避免持久化认证 token

### 前端

- 上传人像后保存 `/admin/sys/file/{id}/preview` 短路径
- 展示人像时根据当前 token 动态生成可访问预览 URL

## 约束与备注

- 文件预览接口通过 query token 鉴权，业务表不得持久化 token
- 旧数据若已保存完整预览 URL，前端展示时会剥离旧 token 并追加当前 token

## 相关文件

- `backend/modules/robot/schemas/robot_config.py`
- `frontend/src/service/api/file.ts`
- `frontend/src/views/settings/modules/face-recognition-tab.vue`

## 记录日期

2026-06-11
