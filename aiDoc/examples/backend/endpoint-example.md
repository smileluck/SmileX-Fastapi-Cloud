# Endpoint 层示例

## 用途

展示如何实现一个标准的 API 端点。

## 核心原则

- 负责参数提取、校验、调用 Service、格式化响应
- 声明 `response_model=ResponseModel[SchemaT]` 或 `ResponsePageModel[SchemaT]`
- 列表接口使用 `get_paginated_results()`
- ORM → Schema 使用 `model_validate()`
- 使用 `response_base` 构建响应

## 示例

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results
from core.response.response_schema import ResponseModel, ResponsePageModel, response_base
from modules.admin.schemas.sys.user import GetUserListQuery, CreateUserReq, GetUserResp
from modules.admin.services.sys.user_service import UserService
from database.db_manager import get_session

router = APIRouter()


@router.get("/list", response_model=ResponsePageModel[GetUserResp], summary="获取用户列表")
async def get_user_list(
    username: str = Query(None, description="用户名"),
    phone: str = Query(None, description="手机号"),
    status: str = Query(None, description="状态（1启用/2禁用）"),
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """分页查询用户列表"""
    # 构建查询
    query = await UserService.get_user_list(db, username=username, status=parse_status(status))
    # 分页查询
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=GetUserResp,
    )
    return response_base.page(data=page_data)


@router.get("/{user_id}", response_model=ResponseModel[GetUserResp], summary="获取用户详情")
async def get_user_detail(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取用户详情"""
    user = await UserService.get_user_by_id(db, user_id)
    user_resp = GetUserResp.model_validate(user)
    return response_base.success(data=user_resp)


@router.post("", response_model=ResponseModel, summary="创建用户")
async def create_user(
    user_data: CreateUserReq,
    db: AsyncSession = Depends(get_session),
):
    """创建用户"""
    user = await UserService.create_user(db, user_data.model_dump())
    await db.commit()
    return response_base.success(msg="创建成功")


@router.delete("/{user_id}", response_model=ResponseModel, summary="删除用户")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
):
    """软删除用户"""
    await UserService.delete_user(db, user_id)
    await db.commit()
    return response_base.success(msg="删除成功")
```

## 关键点

- `Depends(get_page_params)` 从查询参数中提取分页参数
- `Depends(get_session)` 获取异步数据库会话
- `get_paginated_results()` 自动处理分页逻辑，返回 `ResponsePageDataModel`
- `response_base.page()` 包装分页响应
- `response_base.success()` 包装成功响应
- `model_validate()` 将 ORM 实例转为 Schema
- `await db.commit()` 在 Endpoint 层统一提交事务
- 所有端点必须有 docstring

## 真实参考文件

- `backend/modules/admin/endpoints/sys/user.py`
