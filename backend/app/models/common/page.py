#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Session,
)
from sqlalchemy import select, and_, or_, ColumnElement, Select
from dataclasses import dataclass
from typing import TypeVar, List, Optional, Tuple, Callable, Type, Any, Union, Dict
from pydantic import Field, BaseModel
from sqlalchemy.sql import func
from core.response import ResponsePageModel, response_base, ResponsePageDataModel
from sqlalchemy.sql.elements import BinaryExpression
from fastapi import Query
from database.models.base import Base

T = TypeVar("SchemaT")


class PageRequest(BaseModel):
    """分页请求的基类模型"""

    page: int = Field(1, description="当前页码，默认第 1 页", gt=0)
    page_size: int = Field(100, description="每页条数，默认 100 条", gt=0, le=2000)

    @field_validator("page")
    def page_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("页码必须为正整数")
        return v

    @field_validator("page_size")
    def page_size_must_be_positive(cls, v):
        if v < 1:
            raise ValueError("每页条数必须为正整数")
        if v > 2000:
            raise ValueError("每页条数最多为 2000 条")
        return v


async def get_paginated_results(
    db: AsyncSession,
    page_params: PageRequest,
    query: Select,
    schema: Optional[BaseModel] = None,
) -> ResponsePageModel:
    """
    获取分页查询结果
    参数:
        db: 数据库异步会话
        page_params: 分页参数对象
        query: SQLAlchemy查询对象
        schema: 数据模型类，用于转换查询结果
    返回:
        分页查询结果对象
    """
    # 保留未分页的 query 用于 count
    base_query = query
    # 分页
    offset = (page_params.page - 1) * page_params.page_size
    data_query = query.offset(offset).limit(page_params.page_size)
    count_query = base_query.with_only_columns(func.count()).order_by(None)

    # 顺序执行：AsyncSession 不支持同一连接上的并发操作
    data_result = await db.execute(data_query)
    count_result = await db.execute(count_query)
    items = data_result.unique().scalars().all()
    total = count_result.scalar() or 0

    records = [schema.model_validate(item) for item in items] if schema else items
    pages = (total + page_params.page_size - 1) // page_params.page_size
    # 返回分页结果
    return ResponsePageDataModel(
        records=records,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
        total_pages=pages,
    )


# FastAPI依赖项：获取分页参数
def get_page_params(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, ge=1, le=2000, description="每页条数，最大2000"),
) -> PageRequest:
    """获取分页查询参数的依赖项"""
    return PageRequest(page=page, page_size=page_size)
