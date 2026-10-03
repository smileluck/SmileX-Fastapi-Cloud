<!-- last-updated: 2026-05-31 -->
# 插件开发与管理指南

## 概述

插件系统允许以可选方式扩展核心功能。插件安装后通过 Alembic 自动建表/加列，运行时通过配置启用。

核心文件：

- `backend/plugins/base.py` — 插件基类 `PluginBase`
- `backend/plugins/__init__.py` — 插件注册表、加载、安装/卸载
- `backend/plugins/cli.py` — CLI 管理入口
- `backend/plugins/alembic_utils.py` — Alembic 自动化工具
- `backend/plugins/models.py` — `plugin_registry` 表模型

## CLI 命令

```bash
cd backend

# 安装插件（自动注册模型 → 生成迁移 → 执行迁移 → 种子数据）
python -m plugins install <plugin_name>

# 卸载插件（清理种子数据 → 生成删除迁移 → 执行迁移）
python -m plugins uninstall <plugin_name>

# 查看插件状态
python -m plugins list
```

## 启用插件

在 `.env` 中配置：

```env
PLUGINS__ENABLED=["multi_tenant"]
```

应用启动时 `setup_registry.py` → `load_plugins()` 会加载已启用插件。

## 插件生命周期

```
install ─→ on_install()     种子数据
             ↓
activate ─→ register_database_plugins()  数据库事件监听
         ─→ register_middleware()         中间件
         ─→ register_routes()             路由
         ─→ on_activate()                 运行时初始化
             ↓
deactivate  应用停止时自动结束
             ↓
uninstall ─→ on_uninstall()  清理种子数据
           → 生成删除迁移并执行
```

## 创建新插件

### 1. 目录结构

```
backend/plugins/<plugin_name>/
├── __init__.py
├── plugin.py           # 插件主类（继承 PluginBase）
├── router.py           # 路由注册
├── models/             # 插件模型
│   ├── __init__.py
│   └── *.py
├── endpoints/          # API 端点
│   ├── __init__.py
│   └── *.py
├── schemas/            # Pydantic Schema
│   ├── __init__.py
│   └── *.py
├── services/           # 业务服务
│   ├── __init__.py
│   └── *.py
├── middleware/          # 中间件（可选）
│   ├── __init__.py
│   └── *.py
├── database/           # 数据库事件（可选）
│   ├── __init__.py
│   └── *.py
├── deps/               # 依赖注入（可选）
│   ├── __init__.py
│   └── *.py
└── frontend/           # 前端文件（可选，安装时复制到 frontend/src/）
```

### 2. 实现插件主类

```python
# backend/plugins/<plugin_name>/plugin.py
from plugins.base import PluginBase
from fastapi import FastAPI


class MyPlugin(PluginBase):
    name = "my_plugin"
    version = "1.0.0"
    description = "插件说明"

    def register_alembic_models(self) -> None:
        """注册插件模型到 Base.metadata，Alembic 自动检测差异生成迁移"""
        from plugins.my_plugin.models.my_model import MyModel  # noqa: F401

    async def on_install(self) -> None:
        """安装后执行：种子数据、菜单初始化等"""
        pass

    async def on_uninstall(self) -> None:
        """卸载前执行：清理种子数据"""
        pass

    def on_activate(self, app: FastAPI) -> None:
        """每次启动时执行：运行时初始化"""
        pass

    def register_routes(self, app: FastAPI) -> None:
        """注册 FastAPI 路由"""
        from plugins.my_plugin.router import router
        app.include_router(router)

    def register_middleware(self, app: FastAPI) -> None:
        """注册中间件（不需要则 pass）"""
        pass

    def register_database_plugins(self) -> None:
        """注册数据库事件监听（不需要则 pass）"""
        pass
```

### 3. 注册到插件表

在 `backend/plugins/__init__.py` 的 `PLUGIN_MODULES` 中添加：

```python
PLUGIN_MODULES = {
    "multi_tenant": "plugins.multi_tenant.plugin:MultiTenantPlugin",
    "my_plugin": "plugins.my_plugin.plugin:MyPlugin",  # 新增
}
```

### 4. 前端文件管理（可选）

如需前端页面，在插件目录下放 `frontend/` 子目录：

```
backend/plugins/<plugin_name>/frontend/
├── views/              # 复制到 frontend/src/views/
└── plugins/<name>/     # 复制到 frontend/src/plugins/<name>/
```

在插件主类中实现 `_install_frontend()` 和 `_uninstall_frontend()`，参考 `multi_tenant` 插件。

## 安装流程详解

`install_plugin()` 全自动执行：

1. **`register_alembic_models()`** — 导入插件模型到 `Base.metadata`，可动态修改已有模型（加列）
2. **`autogenerate_and_upgrade()`** — Alembic 检测 `Base.metadata` 与数据库差异，自动生成 `ADD TABLE` / `ADD COLUMN` 迁移并执行
3. **写 `plugin_registry` 记录** — 标记已安装
4. **`on_install()`** — 种子数据（默认数据、菜单等）

## 卸载流程详解

`uninstall_plugin()` 全自动执行：

1. **`on_uninstall()`** — 清理种子数据（菜单等）
2. **标记 `plugin_registry` 为未安装**
3. **`generate_removal_and_upgrade()`** — 不导入插件模型，Alembic 检测数据库多出的表/列，自动生成 `DROP TABLE` / `DROP COLUMN` 迁移并执行

## 修改已有模型

插件可以为已有模型动态添加列（如 `tenant_id`），在 `register_alembic_models()` 中：

```python
from sqlalchemy import BigInteger, Column

model_cls.__table__.append_column(
    Column("new_column", BigInteger, nullable=True, comment="说明")
)
```

Alembic autogenerate 会检测到新列并生成 `ADD COLUMN`。

## 数据库事件注册

使用 SQLAlchemy 事件监听实现自动行为（如租户过滤、软删除），在 `register_database_plugins()` 中注册：

```python
from sqlalchemy import event
from sqlalchemy.orm import Session

@event.listens_for(Session, "do_orm_execute")
def _my_filter(execute_state):
    # 自动过滤逻辑
    pass
```

可通过 `execution_options` 控制跳过：`session.execute(stmt, execution_options={"ignore_my_plugin": True})`。

## 多租户插件集成

如需与多租户插件配合：

- **严格隔离**：`register_tenant_strict(model_cls)` — 查询只返回 `tenant_id == current_tenant_id`
- **可选隔离**：`register_tenant_optional(model_cls)` — 查询返回当前租户 + 全局数据（`tenant_id IS NULL`）
- **跳过过滤**：`execution_options={"ignore_tenant": True}`

参考：`aiDoc/memory/business/2026-05-31_tenant_table_permissions.md`

## 注意事项

- 插件之间不应有直接依赖，通过注册表和事件解耦
- `register_alembic_models()` 只在安装/卸载时调用，不在每次启动时调用
- 运行时行为通过 `on_activate()` 和注册钩子实现
- 卸载会删除数据库表和列，确保 `on_uninstall()` 清理了引用这些表/列的种子数据
- 前端文件安装后需重新构建前端
