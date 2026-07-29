# 数据库模块迁移到 database 包

- **日期**: 2026-06-03
- **状态**: 已完成
- **类型**: 重构

## 需求描述

将数据库相关代码从分散的位置统一迁移到 `backend/database/` 包中，使数据库层成为独立模块。

## 迁移内容

### ORM 模型层
- `app/models/sys/` → `database/models/sys/`
- `app/models/business/` → `database/models/business/`
- ORM 基类（`Base`、`LogicMixin`、`DateTimeMixin`、`UserMixin`）→ `database/models/base.py`

### 数据库基础设施
- 连接管理 → `database/db_manager.py`、`database/manager/`
- 数据库配置 → `database/config.py`
- 数据库插件（软删除过滤）→ `database/plugins/setup_database.py`

### 工具函数
- 雪花 ID → `database/utils/snowflake.py`
- 字符串工具 → `database/utils/str_utils.py`
- 时区工具 → `database/utils/timezone.py`
- URL 构建器 → `database/utils/url_builder.py`

## 保留在 app/ 的内容

- `modules/common/schemas/base.py` — Pydantic Schema 基类（`BaseEntity`、`BaseReqEntity`、`BaseRespEntity`、`BoolField`）
- `modules/common/schemas/page.py` — 分页基类（`PageRequest`、`get_paginated_results`）
- `modules/common/schemas/mixin.py` — Schema Mixin

## 关键决策

- ORM 层和 Pydantic Schema 层分离：ORM 在 `database/`，Pydantic 在 `modules/common/schemas/`
- `database/__init__.py` 提供统一导出接口
- 导入路径变更：`app.models.sys.*` → `database.models.sys.*`、`app.models.base` → `database.models.base`

## 相关提交

- `d056cc5d refactor(multi_tenant): update model path prefix from app to database`
- `2f13b04a refactor: 调整数据库模型导入路径并重构模型结构`
- `804d95ff refactor: 调整项目目录结构，迁移核心模块到database包`

## 记录日期

2026-06-03
