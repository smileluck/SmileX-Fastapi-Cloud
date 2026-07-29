# Pydantic Schema 示例

## 用途

展示如何定义请求、响应和查询参数 Schema。

## 核心原则

- 请求 Schema 继承 `BaseReqEntity`
- 响应 Schema 继承 `BaseRespEntity`（自动处理 `status` 和 `is_system` 序列化）
- 必须配置 `model_config = ConfigDict(from_attributes=True)`
- 布尔字段使用 `BoolField`
- ORM → Schema 使用 `model_validate()`

## 示例

```python
from pydantic import ConfigDict
from modules.common.schemas.base import BaseEntity, BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest
from typing import Optional


# 查询参数 Schema
class GetUserListQuery(BaseEntity):
    """用户列表查询参数"""
    username: Optional[str] = None
    phone: Optional[str] = None
    status: BoolField = None  # 接受 "1"/"2"/true/false，转为 bool 或 None


# 创建用户请求 Schema
class CreateUserReq(BaseReqEntity):
    """创建用户请求"""
    username: str
    password: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role_ids: list[int] = []


# 更新用户请求 Schema
class UpdateUserReq(BaseReqEntity):
    """更新用户请求"""
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: BoolField = None
    role_ids: Optional[list[int]] = None


# 用户响应 Schema
class GetUserResp(BaseRespEntity):
    """用户响应（status 自动序列化为 "1"/"2"）"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None
    status: bool  # BaseRespEntity 自动序列化：True → "1"，False → "2"
    is_system: bool  # BaseRespEntity 自动序列化
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
```

## 关键点

- `BaseRespEntity` 中的 `status` 和 `is_system` 字段**不要**手动处理序列化，`@field_serializer` 已自动处理
- `BoolField` 用于接收前端 `"1"`/`"2"` 输入，会自动转为 `bool`
- `from_attributes=True` 是必须的，用于从 SQLAlchemy 对象转换
- 时间字段在 `BaseEntity` 的 `json_encoders` 中已配置自动格式化

## 真实参考文件

- `backend/modules/common/schemas/base.py`
- `backend/modules/admin/schemas/sys/user.py`
