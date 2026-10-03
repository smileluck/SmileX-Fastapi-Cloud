<!-- last-updated: 2026-06-03 -->
# ORM 模型示例

## 用途

展示如何定义一个标准的 SQLAlchemy ORM 模型。

## 核心原则

- 继承 `Base`（来自 `database.models.base`）
- 使用 `Mapped[type]` + `mapped_column()` 定义字段
- 表名通过 `camel_to_snake(cls.__name__)` 自动生成
- 使用 `relationship()` 定义关联关系

## 示例

```python
"""用户模型"""
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, ForeignKey, Table, Column
from database.models.base import Base, UserMixin

# 多对多中间表
sys_user_role = Table(
    "sys_user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("sys_user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("sys_role.id"), primary_key=True),
    comment="用户角色关联表",
)


class SysUser(Base, UserMixin):
    """系统用户表"""

    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    password: Mapped[str] = mapped_column(String(255), comment="密码")
    nickname: Mapped[str | None] = mapped_column(String(50), default=None, comment="昵称")
    email: Mapped[str | None] = mapped_column(String(100), default=None, comment="邮箱")
    phone: Mapped[str | None] = mapped_column(String(20), default=None, comment="手机号")
    avatar: Mapped[str | None] = mapped_column(String(255), default=None, comment="头像")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态（True启用/False禁用）")
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否系统内置")

    # 关联关系
    roles: Mapped[list["SysRole"]] = relationship(
        secondary=sys_user_role,
        back_populates="users",
        lazy="selectin",
    )
```

## 关键点

- `Base` 自动提供 `id`（雪花 ID）、`created_at`、`updated_at`、`deleted_at`
- 需要审计字段时额外继承 `UserMixin`（添加 `created_by`、`updated_by`）
- `lazy="selectin"` 或在查询时使用 `joinedload()` 控制关联加载策略
- 多对多关系需要显式定义中间表

## 真实参考文件

- `backend/database/models/sys/user.py`
- `backend/database/models/sys/role.py`
- `backend/database/models/base.py`
