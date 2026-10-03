#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库管理接口
"""
import logging

from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.exception.errors import RequestError
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeDocQueryParams,
    KnowledgeDocResponseData,
    KnowledgeQueryParams,
    KnowledgeResponseData,
    KnowledgeSearchHit,
    KnowledgeSearchRequest,
    KnowledgeUpdate,
)
from modules.agent.services import KnowledgeService
from modules.agent.utils import paginate_joined
from modules.common.schemas.page import PageRequest, get_page_params, get_paginated_results

logger = logging.getLogger(__name__)

knowledge_router = APIRouter(
    prefix="/knowledge", tags=["知识库管理"], dependencies=[Depends(current_user)]
)


@knowledge_router.get(
    "/list",
    response_model=ResponsePageModel[KnowledgeResponseData],
    dependencies=[Depends(require_permission("knowledge:list"))],
)
async def get_knowledge_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: KnowledgeQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取知识库分页列表（联查向量化模型名称）"""
    logger.info("获取知识库列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = KnowledgeService.build_knowledge_query(query_params)
    page_data = await paginate_joined(
        db=db,
        page_params=page_params,
        query=query,
        schema=KnowledgeResponseData,
        extra_fields=["embedding_model_name"],
    )
    logger.info("获取知识库列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[KnowledgeResponseData](data=page_data)


@knowledge_router.get(
    "/all",
    response_model=ResponseModel[list[KnowledgeResponseData]],
    dependencies=[Depends(require_permission("knowledge:list"))],
)
async def get_all_enabled_knowledge(db: AsyncSession = Depends(get_session)):
    """全部启用知识库（Agent 表单下拉）"""
    from sqlalchemy import select

    from database.models.sys.agent import SysAgentKnowledge

    result = await db.execute(
        select(SysAgentKnowledge)
        .where(SysAgentKnowledge.status.is_(True), SysAgentKnowledge.deleted_at.is_(None))
        .order_by(SysAgentKnowledge.id.asc())
    )
    kbs = result.scalars().all()
    return ResponseModel(data=[KnowledgeResponseData.model_validate(kb) for kb in kbs])


@knowledge_router.get(
    "/{knowledge_id}",
    response_model=ResponseModel[KnowledgeResponseData],
    dependencies=[Depends(require_permission("knowledge:list"))],
)
async def get_knowledge(
    knowledge_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个知识库"""
    logger.info("获取知识库请求，ID: %s", knowledge_id)
    kb = await KnowledgeService.get_knowledge(db, knowledge_id)
    return ResponseModel(data=KnowledgeResponseData.model_validate(kb))


@knowledge_router.post(
    "/add",
    response_model=ResponseModel[KnowledgeResponseData],
    dependencies=[Depends(require_permission("knowledge:add"))],
)
@log_operation(module="knowledge", action="create", description="创建知识库")
async def create_knowledge(
    request: Request,
    payload: KnowledgeCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建知识库（向量化模型创建后锁定）"""
    logger.info("创建知识库请求，编码: %s", payload.code)
    kb = await KnowledgeService.create_knowledge(db, payload)
    return ResponseModel(data=KnowledgeResponseData.model_validate(kb), msg=t("agent.knowledge.create_success"))


@knowledge_router.put(
    "/{knowledge_id}",
    response_model=ResponseModel[KnowledgeResponseData],
    dependencies=[Depends(require_permission("knowledge:edit"))],
)
@log_operation(module="knowledge", action="update", description="更新知识库")
async def update_knowledge(
    knowledge_id: int,
    request: Request,
    payload: KnowledgeUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新知识库（编码与向量化模型不可改）"""
    logger.info("更新知识库请求，ID: %s", knowledge_id)
    kb = await KnowledgeService.update_knowledge(db, knowledge_id, payload)
    return ResponseModel(data=KnowledgeResponseData.model_validate(kb), msg=t("agent.knowledge.update_success"))


@knowledge_router.delete(
    "/{knowledge_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("knowledge:delete"))],
)
@log_operation(module="knowledge", action="delete", description="删除知识库")
async def delete_knowledge(
    knowledge_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除知识库（被智能体绑定时拒绝；Qdrant collection 一并删除）"""
    logger.info("删除知识库请求，ID: %s", knowledge_id)
    await KnowledgeService.delete_knowledge(db, knowledge_id)
    return ResponseModel(msg=t("agent.knowledge.delete_success"))


@knowledge_router.post(
    "/{knowledge_id}/documents",
    response_model=ResponseModel[list[KnowledgeDocResponseData]],
    dependencies=[Depends(require_permission("knowledge:edit"))],
)
@log_operation(module="knowledge", action="upload", description="上传知识库文档")
async def upload_documents(
    knowledge_id: int,
    request: Request,
    files: list[UploadFile] = File(..., description="文档文件（txt/md/pdf/docx，支持多选）"),
    db: AsyncSession = Depends(get_session),
):
    """上传文档（同步提取文本校验，向量化转后台处理）"""
    logger.info("上传知识库文档请求，kb: %s，文件数: %s", knowledge_id, len(files))
    if not files:
        raise RequestError(msg=t("error.knowledge.file_type_unsupported", name=""))

    contents: list[tuple[str, bytes]] = []
    for file in files:
        content = await file.read()
        contents.append((file.filename or "untitled", content))
    docs = await KnowledgeService.upload_documents(db, knowledge_id, contents)
    return ResponseModel(
        data=[KnowledgeDocResponseData.model_validate(doc) for doc in docs],
        msg=t("agent.knowledge.upload_success"),
    )


@knowledge_router.get(
    "/{knowledge_id}/documents/list",
    response_model=ResponsePageModel[KnowledgeDocResponseData],
    dependencies=[Depends(require_permission("knowledge:list"))],
)
async def get_document_list(
    knowledge_id: int,
    page_params: PageRequest = Depends(get_page_params),
    query_params: KnowledgeDocQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取知识库文档分页列表（含处理状态，前端轮询用）"""
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = await KnowledgeService.build_doc_query(db, knowledge_id, query_params)
    page_data = await get_paginated_results(
        db=db, page_params=page_params, query=query, schema=KnowledgeDocResponseData
    )
    return ResponsePageModel[KnowledgeDocResponseData](data=page_data)


@knowledge_router.delete(
    "/{knowledge_id}/documents/{doc_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("knowledge:edit"))],
)
@log_operation(module="knowledge", action="delete", description="删除知识库文档")
async def delete_document(
    knowledge_id: int,
    doc_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除文档（Qdrant 向量点与 PG 账目一并删除）"""
    logger.info("删除知识库文档请求，kb: %s doc: %s", knowledge_id, doc_id)
    await KnowledgeService.delete_document(db, knowledge_id, doc_id)
    return ResponseModel(msg=t("agent.knowledge.doc_delete_success"))


@knowledge_router.post(
    "/{knowledge_id}/documents/{doc_id}/reprocess",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("knowledge:edit"))],
)
@log_operation(module="knowledge", action="reprocess", description="重新处理知识库文档")
async def reprocess_document(
    knowledge_id: int,
    doc_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """重新处理文档（失败重试 / 换切片策略重切）"""
    logger.info("重新处理知识库文档请求，kb: %s doc: %s", knowledge_id, doc_id)
    await KnowledgeService.reprocess_document(db, knowledge_id, doc_id)
    return ResponseModel(msg=t("agent.knowledge.reprocess_success"))


@knowledge_router.post(
    "/{knowledge_id}/rebuild",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("knowledge:edit"))],
)
@log_operation(module="knowledge", action="rebuild", description="重建知识库")
async def rebuild_knowledge(
    knowledge_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """全量重建知识库（全部文档重新切片与向量化）"""
    logger.info("重建知识库请求，ID: %s", knowledge_id)
    count = await KnowledgeService.rebuild_knowledge(db, knowledge_id)
    return ResponseModel(data={"doc_count": count}, msg=t("agent.knowledge.rebuild_success"))


@knowledge_router.post(
    "/{knowledge_id}/search",
    response_model=ResponseModel[list[KnowledgeSearchHit]],
    dependencies=[Depends(require_permission("knowledge:list"))],
)
async def search_knowledge(
    knowledge_id: int,
    payload: KnowledgeSearchRequest,
    db: AsyncSession = Depends(get_session),
):
    """检索测试（返回切片与相似度，调参用）"""
    hits = await KnowledgeService.search_knowledge(db, knowledge_id, payload.query, payload.top_k)
    return ResponseModel(data=hits)
