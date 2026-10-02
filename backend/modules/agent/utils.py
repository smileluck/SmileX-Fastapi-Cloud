#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体模块公共工具
"""
import json
from typing import Any, Optional, Sequence

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.response.response_schema import ResponsePageDataModel
from modules.common.schemas.page import PageRequest


def dump_str_list(values: Optional[list[str]]) -> str:
    """字符串列表序列化为 JSON 文本列（空列表/None → 空串，等价“未配置”）"""
    if not values:
        return ""
    return json.dumps(values, ensure_ascii=False)


def load_str_list(text: Optional[str]) -> list[str]:
    """JSON 文本列反序列化为字符串列表（空串/解析失败 → 空列表）"""
    if not text:
        return []
    try:
        values = json.loads(text)
    except json.JSONDecodeError:
        return []
    if not isinstance(values, list):
        return []
    return [str(v) for v in values if v]


def archive_unique_columns(obj, *columns: str) -> None:
    """
    软删前归档唯一列：改为 `原值前缀#<id>`，释放唯一索引供同码重建。

    与 SmileX-Admin-Gin 的 ArchiveUniqueColumns 语义一致；仅截取原值前 60 字符避免超长。
    """
    for column in columns:
        value = getattr(obj, column, None)
        if value:
            setattr(obj, column, f"{str(value)[:60]}#{obj.id}")


async def archive_and_soft_delete(db: AsyncSession, obj, *columns: str) -> None:
    """归档唯一列并软删提交"""
    archive_unique_columns(obj, *columns)
    obj.soft_delete()
    await db.commit()


async def paginate_joined(
    db: AsyncSession,
    page_params: PageRequest,
    query,
    schema: type[BaseModel],
    extra_fields: Sequence[str],
) -> ResponsePageDataModel:
    """
    联查分页：query 形如 select(ORM, col1, col2)，extra_fields 为附加列对应的
    响应字段名（按位置对应）。ORM 主实体经 schema.model_validate 转换后按位填充。
    """
    offset = (page_params.page - 1) * page_params.page_size
    data_query = query.offset(offset).limit(page_params.page_size)
    count_query = select(func.count()).select_from(query.subquery())

    data_result = await db.execute(data_query)
    count_result = await db.execute(count_query)
    rows = data_result.unique().all()
    total = count_result.scalar() or 0

    records: list[Any] = []
    for row in rows:
        orm_obj = row[0]
        item = schema.model_validate(orm_obj)
        for field_name, value in zip(extra_fields, row[1:]):
            setattr(item, field_name, value)
        records.append(item)

    pages = (total + page_params.page_size - 1) // page_params.page_size
    return ResponsePageDataModel(
        records=records,
        page=page_params.page,
        page_size=page_params.page_size,
        total=total,
        total_pages=pages,
    )
