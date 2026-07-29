#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional
from datetime import datetime

from pydantic import Field
from modules.common.schemas.base import BaseReqEntity, BaseRespEntity, OptionalIntField


class ExportTaskSubmit(BaseReqEntity):
    """提交异步导出任务"""
    module_key: str | None = Field(None, description="模块标识（与 template_id 二选一）")
    template_id: OptionalIntField = Field(None, description="导出模板ID（与 module_key 二选一）")
    query_params: dict = Field(default_factory=dict, description="查询参数，同列表接口筛选条件")


class ExportTaskResponse(BaseRespEntity):
    """导出任务响应"""
    id: int
    task_name: str
    module_key: str
    template_id: int | None = None
    status: str
    total_rows: int | None = None
    file_size: int | None = None
    error_message: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_format(cls, obj) -> "ExportTaskResponse":
        def fmt(dt):
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None

        return cls(
            id=obj.id,
            task_name=obj.task_name,
            module_key=obj.module_key,
            template_id=obj.template_id if hasattr(obj, "template_id") else None,
            status=obj.status,
            total_rows=obj.total_rows,
            file_size=obj.file_size,
            error_message=obj.error_message,
            created_at=fmt(obj.created_at),
            started_at=fmt(obj.started_at),
            finished_at=fmt(obj.finished_at),
        )
