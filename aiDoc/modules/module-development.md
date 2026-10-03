<!-- last-updated: 2026-10-02 -->
# 模块开发指南

## 新建后端模块

按以下步骤创建 `backend/modules/<name>/` 模块：

### 1. 创建目录结构

```
backend/modules/<name>/
├── __init__.py
├── router.py          # 路由注册
├── deps/              # 依赖注入
│   └── __init__.py
├── endpoints/         # API 端点
│   └── __init__.py
├── schemas/           # Pydantic Schema
│   └── __init__.py
└── services/          # 业务服务
    └── __init__.py
```

### 2. 定义 ORM 模型

在 `database/models/` 对应目录（`sys/` 或 `business/`）中创建模型文件。

继承 `Base`（来自 `database/models/base.py`），使用 `Mapped[]` + `mapped_column()`。

参考：`database/models/sys/user.py`

### 3. 定义 Pydantic Schema

在 `modules/<name>/schemas/` 中创建请求和响应 Schema。

- 请求 Schema 继承 `BaseReqEntity` 或 `BaseEntity`
- 响应 Schema 继承 `BaseRespEntity`
- 配置 `model_config = ConfigDict(from_attributes=True)`
- 查询参数继承 `PageRequest`

参考：`modules/admin/schemas/sys/user.py`

### 4. 实现 Service 层

在 `modules/<name>/services/` 中创建服务类。

- 方法使用 `@staticmethod`
- 接受 `AsyncSession` 作为第一个参数
- 返回 ORM 实例
- 抛出领域异常

参考：`modules/admin/services/sys/user_service.py`

### 5. 创建 Endpoint

在 `modules/<name>/endpoints/` 中创建端点文件。

- 声明 `response_model=ResponseModel[SchemaT]`
- 列表接口使用 `get_paginated_results()`
- ORM → Schema 使用 `model_validate()`

参考：`modules/admin/endpoints/sys/user.py`

### 6. 创建 Router

在 `modules/<name>/router.py` 中创建 `APIRouter` 并包含子路由。

参考：`modules/admin/router.py`

### 7. 注册模块

在 `main.py` 中添加 `app.include_router(<name>_router)`。

### 8. 数据库迁移

```bash
uv run alembic revision --autogenerate -m "add <name> module"
uv run alembic upgrade head
```

---

## 新建前端功能

### 1. 定义 TypeScript 类型

在 `frontend/src/typings/api/<feature>.d.ts` 中定义接口类型，放在 `Api` 命名空间下。

参考：`frontend/src/typings/api/`

### 2. 创建 API 函数

在 `frontend/src/service/api/<feature>.ts` 中创建 API 调用函数。

- 函数名使用 `fetch` 前缀（如 `fetchGetUserList`、`fetchCreateUser`）
- 使用 `@sa/axios` 封装的请求方法
- Status 字段转换使用 `enableStatusToBoolean()` / `booleanToEnableStatus()`

参考：`frontend/src/service/api/system-manage.ts`

### 3. 添加国际化

在以下文件中添加对应的翻译键：

- `frontend/src/locales/langs/zh-cn.ts`
- `frontend/src/locales/langs/en-us.ts`
- 更新 `frontend/src/typings/app.d.ts` 中的 `App.I18n.Schema` 类型约束

### 4. 创建页面组件

在 `frontend/src/views/<feature>/` 下创建页面文件夹：

```
src/views/<feature>/
├── index.vue          # 主页面
└── modules/           # 子组件
    └── SomeModule.vue
```

参考：`frontend/src/views/manage/`

### 5. 生成路由

```bash
pnpm gen-route
```

---

## 设计原则

- 模块保持自包含，减少跨模块直接依赖
- 遵循现有模块的命名和组织模式
- 新增模块前，先查阅 `aiDoc/examples/` 中的示例
- 参考现有模块（`admin/`）作为模板
