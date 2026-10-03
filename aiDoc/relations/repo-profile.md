<!-- last-updated: 2026-05-18 -->
# 项目定位与技术栈

## 项目定位

SmileX-Fastapi-Cloud 是一个云原生智能机器人管理平台，核心能力包括：

- 设备管理与绑定
- 机器人任务编排与状态监控
- 紧急联系人管理
- 系统管理（用户、角色、权限、菜单、字典、配置）
- MCP 工具平台集成

## 后端技术栈

- **语言**: Python 3.11+
- **框架**: FastAPI（async）
- **ORM**: SQLAlchemy 2.0（async，基于 `AsyncSession`）
- **数据库**: PostgreSQL（asyncpg 驱动）
- **缓存**: Redis
- **迁移**: Alembic
- **认证**: JWT + Redis 会话管理
- **密码**: passlib + bcrypt
- **安全**: bleach（输入消毒）、IP 限流
- **ID 生成**: 雪花算法（`database/utils/snowflake.py`）
- **时区**: `Asia/Shanghai`，存储使用带时区的 `datetime`
- **包管理**: uv

## 前端技术栈

- **框架**: Vue 3.5 + TypeScript
- **构建**: Vite 7
- **UI 库**: NaiveUI 2.43
- **状态管理**: Pinia 3.0
- **路由**: Vue Router 4
- **样式**: UnoCSS + SCSS
- **国际化**: vue-i18n 11
- **HTTP**: `@sa/axios`（Axios 封装）
- **工作区**: pnpm workspaces，`@sa/*` 作用域包
  - `@sa/axios`、`@sa/hooks`、`@sa/materials`、`@sa/utils`、`@sa/color`、`@sa/uno-preset`、`@sa/alova`、`@sa/scripts`
- **包管理**: pnpm >= 10.5.0
- **Node**: >= 20.19.0

## 核心特性

| 特性 | 说明 |
|------|------|
| 统一响应 | `ResponseModel[SchemaT]`，含 `code`/`msg`/`data`/`request_id`/`err_code` |
| 统一分页 | `ResponsePageModel[SchemaT]`，含 `records`/`page`/`page_size`/`total`/`total_pages` |
| 雪花 ID | `LogicMixin` 提供全局唯一 `snowflake_id_key` 主键 |
| 软删除 | `LogicMixin` 提供 `deleted_at` 字段 |
| 审计字段 | `DateTimeMixin` 提供 `created_at`/`updated_at`，`UserMixin` 提供 `created_by`/`updated_by` |
| JWT 会话 | Token + Redis 存储，支持刷新令牌 |
| RBAC | 用户-角色-权限-菜单四级权限控制 |
| MCP | 可选挂载 Model Context Protocol 服务端 |
| Status 桥接 | 后端 `bool` ↔ 前端 `"1"`/`"2"` 字符串，详见 `aiDoc/frontend-backend/boundary.md` |
