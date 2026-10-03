#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BeforeValidator, ConfigDict, Field

from modules.common.schemas.base import BaseEntity, BaseReqEntity, BaseRespEntity, BoolField
from modules.common.schemas.page import PageRequest


def _format_datetime(v):
    if isinstance(v, datetime):
        from zoneinfo import ZoneInfo

        return v.astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    return v


class KnowledgeQueryParams(PageRequest):
    """知识库查询参数"""

    name: Optional[str] = Field(None, description="知识库名称，支持模糊查询")
    code: Optional[str] = Field(None, description="知识库编码，支持模糊查询")
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class KnowledgeCreate(BaseReqEntity):
    """知识库创建请求"""

    name: str = Field(..., description="知识库名称", min_length=1, max_length=20)
    code: str = Field(..., description="知识库编码", min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
    description: Optional[str] = Field(None, description="知识库描述", max_length=200)
    embedding_model_id: int = Field(..., description="向量化模型 ID（须为 embedding 类型，创建后锁定）", gt=0)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: bool = Field(True, description="状态：True-启用，False-禁用")


class KnowledgeUpdate(BaseReqEntity):
    """知识库更新请求（编码与向量化模型不可改；全部字段留空=保持原值）"""

    name: Optional[str] = Field(None, description="知识库名称", min_length=1, max_length=20)
    description: Optional[str] = Field(None, description="知识库描述", max_length=200)
    remark: Optional[str] = Field(None, description="备注", max_length=200)
    status: BoolField = Field(None, description="状态：True-启用，False-禁用")


class KnowledgeResponseData(BaseRespEntity):
    """知识库响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="知识库 ID")
    name: str = Field(..., description="知识库名称")
    code: str = Field(..., description="知识库编码")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model_id: int = Field(..., description="向量化模型 ID")
    embedding_model_name: Optional[str] = Field(None, description="向量化模型名称（联查填充）")
    doc_count: int = Field(0, description="文档数量")
    chunk_count: int = Field(0, description="切片数量")
    remark: Optional[str] = Field(None, description="备注")
    status: bool = Field(..., description="状态")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="创建时间")
    updated_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="更新时间")


class KnowledgeBrief(BaseEntity):
    """知识库简要信息（Agent 表单下拉）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="知识库 ID")
    name: str = Field(..., description="知识库名称")
    code: str = Field(..., description="知识库编码")
    status: bool = Field(..., description="状态")


class KnowledgeDocQueryParams(PageRequest):
    """知识库文档查询参数"""

    file_name: Optional[str] = Field(None, description="文件名，支持模糊查询")
    status: Optional[int] = Field(None, description="处理状态：0-待处理 1-处理中 2-完成 3-失败", ge=0, le=3)


class KnowledgeDocResponseData(BaseEntity):
    """知识库文档响应（处理状态为状态机整数，非启用/禁用布尔）"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="文档 ID")
    knowledge_id: int = Field(..., description="所属知识库 ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件扩展名")
    file_size: int = Field(..., description="原始文件大小（字节）")
    char_count: int = Field(..., description="提取文本长度（字符）")
    chunk_count: int = Field(..., description="切片数量")
    status: int = Field(..., description="处理状态：0-待处理 1-处理中 2-完成 3-失败")
    error_msg: Optional[str] = Field(None, description="失败原因")
    created_at: Annotated[Optional[str], BeforeValidator(_format_datetime)] = Field(None, description="上传时间")


class KnowledgeSearchRequest(BaseReqEntity):
    """检索测试请求"""

    query: str = Field(..., description="检索文本", min_length=1, max_length=2000)
    top_k: int = Field(5, description="返回切片数", ge=1, le=20)


class KnowledgeSearchHit(BaseReqEntity):
    """检索测试命中项"""

    kb_id: int = Field(..., description="知识库 ID")
    kb_name: str = Field(..., description="知识库名称")
    doc_id: int = Field(..., description="文档 ID")
    chunk_index: int = Field(..., description="切片序号")
    content: str = Field(..., description="切片内容")
    score: float = Field(..., description="相似度")
