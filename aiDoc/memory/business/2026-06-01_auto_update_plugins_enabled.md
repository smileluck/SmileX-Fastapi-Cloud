<!-- last-updated: 2026-06-01 -->
# 插件安装自动更新 PLUGINS__ENABLED

## 需求描述

安装插件后，自动将插件名添加到 `.env` 文件中的 `PLUGINS__ENABLED` 列表；卸载插件时自动移除。

## 状态

已完成

## 涉及范围

### 后端

- `backend/plugins/__init__.py` — 新增 `_get_env_files()`、`_update_plugins_env()` 辅助函数，在 `install_plugin` 末尾添加，在 `uninstall_plugin` 末尾移除

### 前端

- `frontend/.env` — PLUGINS__ENABLED 值会被自动更新

## 约束与备注

- 更新范围：`backend/.env`、`backend/.env.dev`、`frontend/.env`（仅更新存在的文件）
- 使用 JSON 解析/序列化处理 `PLUGINS__ENABLED` 的值，保持 `.env` 中格式一致
- 已安装的插件不会重复添加（幂等）

## 相关文件

- `backend/plugins/__init__.py`

## 记录日期

2026-06-01
