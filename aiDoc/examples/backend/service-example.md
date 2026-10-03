<!-- last-updated: 2026-06-03 -->
# Service 层示例

## 用途

展示如何实现一个标准的业务服务类。

## 核心原则

- 方法使用 `@staticmethod`
- 接受 `AsyncSession` 作为第一个参数
- 返回 ORM 实例（不返回 Schema）
- 抛出领域异常（`CustomError`、`NotFoundError`、`ConflictError` 等）
- 使用 `joinedload()` 预加载关联

## 示例

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from core.exception.errors import NotFoundError, ConflictError, CustomError
from core.response.response_code import CustomErrorCode
from database.models.sys.user import SysUser


class UserService:
    """用户服务"""

    @staticmethod
    async def get_user_list(db: AsyncSession, username: str = None, status: bool = None):
        """获取用户列表"""
        query = select(SysUser).where(SysUser.deleted_at.is_(None))
        if username:
            query = query.where(SysUser.username.ilike(f"%{username}%"))
        if status is not None:
            query = query.where(SysUser.status == status)
        query = query.options(selectinload(SysUser.roles))
        return query

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> SysUser:
        """根据 ID 获取用户"""
        query = select(SysUser).where(
            SysUser.id == user_id,
            SysUser.deleted_at.is_(None),
        ).options(selectinload(SysUser.roles))
        result = await db.execute(query)
        user = result.unique().scalars().first()
        if not user:
            raise NotFoundError(msg="用户不存在")
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> SysUser:
        """创建用户"""
        # 检查唯一约束
        existing = await db.execute(
            select(SysUser).where(SysUser.username == user_data["username"])
        )
        if existing.scalars().first():
            raise ConflictError(msg="用户名已存在")

        user = SysUser(**user_data)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        """软删除用户"""
        user = await UserService.get_user_by_id(db, user_id)
        user.soft_delete()
        await db.flush()
```

## 关键点

- 软删除查询必须加 `deleted_at.is_(None)` 条件
- 软删除操作调用模型的 `soft_delete()` 方法
- `joinedload()` / `selectinload()` 用于预加载关联，避免 N+1
- 使用 `result.unique().scalars()` 处理 joined eager load 的结果
- 所有数据库变更后调用 `await db.flush()`（事务由 Endpoint 层的 `await db.commit()` 统一提交）
- 唯一约束检查在 Service 层完成，抛出 `ConflictError`

## 真实参考文件

- `backend/modules/admin/services/sys/user_service.py`
