# 后端分层规则

## 总原则

严格遵循 `Endpoint -> Service -> Model` 依赖方向，禁止跨层调用。

- **Endpoint 层**：处理 HTTP 相关逻辑（参数提取、校验、响应格式化），不含业务逻辑
- **Service 层**：纯业务逻辑，不依赖 FastAPI 请求/响应对象
- **Model 层**：ORM 数据映射，不包含业务逻辑

---

## Model 层

### 基类继承

所有模型继承 `Base`（定义于 `database/models/base.py`）：

```
Base = DataClassBase + LogicMixin + DateTimeMixin
```

- `LogicMixin`：雪花 ID 主键（`snowflake_id_key`）、软删除（`deleted_at`）
- `DateTimeMixin`：`created_at`（自动填充）、`updated_at`（自动更新）
- `UserMixin`（可选）：`created_by`、`updated_by` 审计字段

### 字段声明

- 使用 `Mapped[type]` 类型注解 + `mapped_column()` 定义列
- 表名自动生成：`camel_to_snake(cls.__name__)`（如 `SysUser` → `sys_user`）
- 多对多关系使用 `relationship()` + 显式 `secondary` 中间表

### 模型存放位置

| 目录 | 用途 |
|------|------|
| `database/models/sys/` | 系统模型（用户、角色、权限、菜单、字典、配置） |
| `database/models/business/` | 业务模型 |
| `database/models/base.py` | ORM 公共基类（`Base`、`DataClassBase`、`LogicMixin`、`DateTimeMixin`） |
| `modules/common/schemas/` | Pydantic Schema 基类（`BaseEntity`、`PageRequest` 等） |

---

## Schema 层（Pydantic）

### 基类选择

| 场景 | 基类 | 定义位置 |
|------|------|----------|
| 通用实体 | `BaseEntity` | `modules/common/schemas/base.py` |
| 请求实体 | `BaseReqEntity` | `modules/common/schemas/base.py` |
| 响应实体 | `BaseRespEntity` | `modules/common/schemas/base.py` |

### 响应 Schema 规则

- 有启用/禁用语义的 `status` 字段时，继承 `BaseRespEntity`（自动序列化 `True → "1"`，`False → "2"`）
- 无此类字段时（如日志的 success/failure 状态），继承 `BaseEntity`（保持 bool 原样输出）
- `BaseRespEntity` 同时处理 `is_system` 字段序列化：`True → "1"`，`False → "2"`
- `BaseEntity` 已内含 `from_attributes=True` 和 `datetime → "YYYY-MM-DD HH:mm:ss"` 序列化，无需重复配置
- ORM 对象转换为 Schema 时，必须调用 `SchemaClass.model_validate(orm_instance)`
- **禁止**手写 `_to_response()` / `_to_dict()` 等辅助函数手动转换 ORM 字段

### 布尔字段

使用 `BoolField = Annotated[Optional[bool], BeforeValidator(parse_bool)]` 处理前端传入的 `"1"`/`"2"` 字符串：

- 接受值：`"1"`、`"true"`、`"yes"` → `True`
- 接受值：`"2"`、`"false"`、`"no"` → `False`
- 空值（`""`、`"null"`、`"undefined"`、`None`）→ `None`

### 分页查询 Schema

继承 `PageRequest`（`modules/common/schemas/page.py`）：

- `page`：从 1 开始，默认 1，必须 > 0
- `page_size`：默认 100，最大 200

---

## Service 层

### 规则

- 方法使用 `@staticmethod` 装饰
- 接受 `AsyncSession` 作为第一个参数
- 返回 ORM 模型实例（由 Endpoint 层做 Schema 转换）
- 不依赖 FastAPI 请求/响应对象
- 复杂查询使用 `joinedload()` 预加载关联，避免 N+1 问题
- 使用 `unique()` 处理 joined eager load 结果

### 异常处理

使用 `core/exception/errors.py` 中定义的领域异常：

| 异常类 | HTTP 状态码 | 用途 |
|--------|------------|------|
| `CustomError` | 自定义 | 业务错误，配合 `CustomErrorCode` |
| `RequestError` | 400 | 请求参数错误 |
| `TokenError` | 401 | 认证失败 |
| `ForbiddenError` | 403 | 禁止访问 |
| `AuthorizationError` | 403 | 权限不足 |
| `NotFoundError` | 404 | 资源不存在 |
| `ConflictError` | 409 | 资源冲突（如唯一约束） |
| `ValidationError` | 422 | 数据验证失败 |
| `ServerError` | 500 | 服务器内部错误 |

### 错误码分配

定义于 `core/response/response_code.py:CustomErrorCode`：

| 范围 | 领域 |
|------|------|
| 10001-10100 | 用户 |
| 10101-10200 | 设备 |
| 10201-10300 | 聊天 |
| 10301-10400 | 机器人 |
| 10401-10500 | 紧急联系人 |
| 10501-10600 | 机器人任务 |

新增业务领域时，在此文件末尾追加新范围段。

---

## Endpoint 层

### 规则

- 负责参数提取（`Depends`）、校验、调用 Service、格式化响应
- 必须声明 `response_model=ResponseModel[SchemaT]` 或 `ResponsePageModel[SchemaT]`
- 列表接口必须包含 `page_params: PageRequest = Depends(get_page_params)` 参数
- 分页查询使用 `get_paginated_results()`（`modules/common/schemas/page.py`），返回 `response_base.page(data=page_data)`
- **禁止**在 Endpoint 或 Service 层手动构造分页响应字典（如 `{"items": ..., "total": ...}`）
- ORM 结果转换为 Schema 使用 `SchemaClass.model_validate(instance)`
- 所有端点必须有 docstring 说明用途

### 典型签名

```python
@router.get("/list", response_model=ResponsePageModel[SomeRespSchema])
async def get_list(
    query_params: QuerySchema = Depends(),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(current_user_dep),
):
```

### 响应构建

使用 `response_base`（`core/response/response_schema.py`）：

- 成功：`response_base.success(data=result)`
- 失败：`response_base.fail(res=CustomResponseCode.HTTP_400, msg="错误信息")`
- 分页：`response_base.page(data=page_data)`

---

## Router 层

- 每个模块一个 `router.py`，用 `APIRouter` 创建并聚合子路由
- 子路由使用 `APIRouter(prefix="/...", tags=["..."])`
- 模块路由在 `main.py` 中通过 `app.include_router()` 注册
