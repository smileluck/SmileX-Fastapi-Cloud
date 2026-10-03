#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库管理服务

存储分工：chunk 元数据与状态机在 PG；向量与切片正文在 Qdrant（每库一 collection）。
一致性规则：处理前按 doc 清理两侧残留（幂等重跑）；删除先 Qdrant 后 PG；
对账定时任务以 PG 账目为准自动重跑偏差文档。
"""
import asyncio
import hashlib
import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence

from sqlalchemy import and_, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import (
    DOC_STATUS_COMPLETED,
    DOC_STATUS_FAILED,
    DOC_STATUS_PENDING,
    DOC_STATUS_PROCESSING,
    SysAgentKnowledge,
    SysAgentKnowledgeChunk,
    SysAgentKnowledgeDoc,
    SysAgentModel,
    SysAgentProvider,
)
from modules.agent.core.knowledge_chunker import chunk_text
from modules.agent.core.knowledge_parser import extract_file_type, parse_document
from modules.agent.core.knowledge_retriever import KnowledgeRetriever
from modules.agent.core.qdrant_store import VectorPoint, get_vector_store
from modules.agent.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeDocQueryParams,
    KnowledgeQueryParams,
    KnowledgeSearchHit,
    KnowledgeUpdate,
)
from modules.agent.services.provider_service import ProviderService
from modules.agent.utils import archive_and_soft_delete

logger = logging.getLogger(__name__)

# Agent 可绑定知识库数量上限
MAX_KNOWLEDGE_BINDINGS = 5


class KnowledgeService:
    """知识库管理服务类"""

    # ---------- 查询 ----------

    @staticmethod
    def build_knowledge_query(query_params: KnowledgeQueryParams):
        """构建知识库分页查询条件（联查向量化模型名称）"""
        base_query = (
            select(SysAgentKnowledge, SysAgentModel.name)
            .join(SysAgentModel, SysAgentKnowledge.embedding_model_id == SysAgentModel.id, isouter=True)
        )
        conditions = [SysAgentKnowledge.deleted_at.is_(None)]
        if query_params.status is not None:
            conditions.append(SysAgentKnowledge.status == query_params.status)
        if query_params.name:
            conditions.append(SysAgentKnowledge.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysAgentKnowledge.code.like(f"%{query_params.code}%"))
        return base_query.where(and_(*conditions)).order_by(SysAgentKnowledge.id.desc())

    @staticmethod
    async def get_knowledge(db: AsyncSession, kb_id: int) -> SysAgentKnowledge:
        """获取单个知识库，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysAgentKnowledge).where(
                SysAgentKnowledge.id == kb_id, SysAgentKnowledge.deleted_at.is_(None)
            )
        )
        kb = result.scalar_one_or_none()
        if not kb:
            raise NotFoundError(msg=t("error.knowledge.not_found", id=kb_id))
        return kb

    @staticmethod
    async def _ensure_code_unique(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> None:
        """校验知识库编码唯一（排除自身）"""
        conditions = [SysAgentKnowledge.code == code, SysAgentKnowledge.deleted_at.is_(None)]
        if exclude_id is not None:
            conditions.append(SysAgentKnowledge.id != exclude_id)
        result = await db.execute(select(SysAgentKnowledge.id).where(and_(*conditions)))
        if result.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_CODE_EXIST,
                msg=t("error.knowledge.code_exist", code=code),
            )

    @staticmethod
    async def check_enabled(db: AsyncSession, kb_id: int) -> SysAgentKnowledge:
        """校验知识库存在且启用（供智能体绑定校验）"""
        result = await db.execute(
            select(SysAgentKnowledge).where(
                SysAgentKnowledge.id == kb_id, SysAgentKnowledge.deleted_at.is_(None)
            )
        )
        kb = result.scalar_one_or_none()
        if kb is None or not kb.status:
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_NOT_FOUND,
                msg=t("error.knowledge.not_found_or_disabled", id=kb_id),
            )
        return kb

    @staticmethod
    async def validate_knowledge_ids(db: AsyncSession, kb_ids: list[int]) -> None:
        """校验 Agent 绑定的知识库：去重、上限、存在且启用"""
        if len(kb_ids) > MAX_KNOWLEDGE_BINDINGS:
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_TOO_MANY,
                msg=t("error.knowledge.too_many", max=MAX_KNOWLEDGE_BINDINGS),
            )
        for kb_id in dict.fromkeys(kb_ids):
            await KnowledgeService.check_enabled(db, kb_id)

    # ---------- 基础 CRUD ----------

    @staticmethod
    async def _validate_embedding_model(db: AsyncSession, model_id: int) -> SysAgentModel:
        """校验向量化模型：存在、启用且为 embedding 类型"""
        result = await db.execute(
            select(SysAgentModel).where(
                SysAgentModel.id == model_id, SysAgentModel.deleted_at.is_(None)
            )
        )
        model = result.scalar_one_or_none()
        if model is None or not model.status or model.model_type != "embedding":
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_EMBEDDING_MODEL_INVALID,
                msg=t("error.knowledge.embedding_model_invalid", id=model_id),
            )
        return model

    @staticmethod
    async def create_knowledge(db: AsyncSession, payload: KnowledgeCreate) -> SysAgentKnowledge:
        """创建知识库（向量化模型锁定）"""
        logger.info("创建知识库，编码: %s", payload.code)
        await KnowledgeService._ensure_code_unique(db, payload.code)
        await KnowledgeService._validate_embedding_model(db, payload.embedding_model_id)

        kb = SysAgentKnowledge(
            name=payload.name,
            code=payload.code,
            description=payload.description,
            embedding_model_id=payload.embedding_model_id,
            remark=payload.remark,
            status=payload.status,
        )
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
        logger.info("创建知识库成功，ID: %s", kb.id)
        return kb

    @staticmethod
    async def update_knowledge(db: AsyncSession, kb_id: int, payload: KnowledgeUpdate) -> SysAgentKnowledge:
        """更新知识库（编码与向量化模型不可改）"""
        logger.info("更新知识库，ID: %s", kb_id)
        kb = await KnowledgeService.get_knowledge(db, kb_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("code", None)
        update_data.pop("embedding_model_id", None)
        for key, value in update_data.items():
            if hasattr(kb, key) and value is not None:
                setattr(kb, key, value)

        await db.commit()
        await db.refresh(kb)
        logger.info("更新知识库成功，ID: %s", kb_id)
        return kb

    @staticmethod
    async def delete_knowledge(db: AsyncSession, kb_id: int) -> bool:
        """删除知识库；被智能体绑定时拒绝；先删 Qdrant collection 再物理删子表"""
        from modules.agent.services.agent_service import AgentService

        logger.info("删除知识库，ID: %s", kb_id)
        kb = await KnowledgeService.get_knowledge(db, kb_id)

        used = await AgentService.count_agents_using_knowledge(db, kb_id)
        if used > 0:
            raise CustomError(error=CustomErrorCode.KNOWLEDGE_IN_USE, msg=t("error.knowledge.in_use"))

        # 先删向量侧（失败抛错阻断，避免 Qdrant 残留可检索内容）
        await get_vector_store().delete_collection(kb_id)
        await db.execute(
            delete(SysAgentKnowledgeChunk).where(SysAgentKnowledgeChunk.knowledge_id == kb_id)
        )
        await db.execute(
            delete(SysAgentKnowledgeDoc).where(SysAgentKnowledgeDoc.knowledge_id == kb_id)
        )
        await archive_and_soft_delete(db, kb, "code")
        logger.info("删除知识库成功，ID: %s", kb_id)
        return True

    # ---------- 文档：查询 ----------

    @staticmethod
    async def build_doc_query(db: AsyncSession, kb_id: int, query_params: KnowledgeDocQueryParams):
        """构建文档分页查询（前置校验知识库归属）"""
        await KnowledgeService.get_knowledge(db, kb_id)
        conditions = [
            SysAgentKnowledgeDoc.knowledge_id == kb_id,
            SysAgentKnowledgeDoc.deleted_at.is_(None),
        ]
        if query_params.file_name:
            conditions.append(SysAgentKnowledgeDoc.file_name.like(f"%{query_params.file_name}%"))
        if query_params.status is not None:
            conditions.append(SysAgentKnowledgeDoc.status == query_params.status)
        return (
            select(SysAgentKnowledgeDoc)
            .where(and_(*conditions))
            .order_by(SysAgentKnowledgeDoc.id.desc())
        )

    @staticmethod
    async def get_doc(db: AsyncSession, doc_id: int) -> SysAgentKnowledgeDoc:
        """获取单个文档，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysAgentKnowledgeDoc).where(
                SysAgentKnowledgeDoc.id == doc_id, SysAgentKnowledgeDoc.deleted_at.is_(None)
            )
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise NotFoundError(msg=t("error.knowledge.doc_not_found", id=doc_id))
        return doc

    # ---------- 文档：上传与处理管线 ----------

    @staticmethod
    async def upload_documents(
        db: AsyncSession, kb_id: int, files: Sequence[tuple[str, bytes]]
    ) -> list[SysAgentKnowledgeDoc]:
        """
        上传文档：同步提取文本与校验（格式/大小/去重/上限），入库后异步向量化。

        files 为 (file_name, content) 列表；单个文件校验失败立即抛出（整体不入库）。
        """
        kb = await KnowledgeService.get_knowledge(db, kb_id)
        max_bytes = settings.AGENT.KB_MAX_FILE_SIZE_MB * 1024 * 1024

        existing = await db.execute(
            select(func.count()).select_from(SysAgentKnowledgeDoc).where(
                SysAgentKnowledgeDoc.knowledge_id == kb_id,
                SysAgentKnowledgeDoc.deleted_at.is_(None),
            )
        )
        if (existing.scalar() or 0) + len(files) > settings.AGENT.KB_MAX_DOCS:
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_TOO_MANY_DOCS,
                msg=t("error.knowledge.too_many_docs", max=settings.AGENT.KB_MAX_DOCS),
            )

        docs: list[SysAgentKnowledgeDoc] = []
        for file_name, content in files:
            if len(content) > max_bytes:
                raise CustomError(
                    error=CustomErrorCode.KNOWLEDGE_FILE_TOO_LARGE,
                    msg=t(
                        "error.knowledge.file_too_large",
                        name=file_name,
                        max=settings.AGENT.KB_MAX_FILE_SIZE_MB,
                    ),
                )
            text = parse_document(file_name, content)  # 类型/空内容校验在内
            content_hash = hashlib.sha256(content).hexdigest()
            dup = await db.execute(
                select(SysAgentKnowledgeDoc.id).where(
                    SysAgentKnowledgeDoc.knowledge_id == kb_id,
                    SysAgentKnowledgeDoc.content_hash == content_hash,
                    SysAgentKnowledgeDoc.deleted_at.is_(None),
                )
            )
            if dup.scalar_one_or_none() is not None:
                raise CustomError(
                    error=CustomErrorCode.KNOWLEDGE_DOC_DUPLICATED,
                    msg=t("error.knowledge.doc_duplicated", name=file_name),
                )
            doc = SysAgentKnowledgeDoc(
                knowledge_id=kb_id,
                file_name=file_name,
                file_type=extract_file_type(file_name),
                file_size=len(content),
                content_hash=content_hash,
                content=text,
                char_count=len(text),
                status=DOC_STATUS_PENDING,
            )
            db.add(doc)
            docs.append(doc)

        await db.flush()
        await KnowledgeService._refresh_counts(db, kb)
        await db.commit()
        for doc in docs:
            await db.refresh(doc)

        spawn_doc_processing([doc.id for doc in docs])
        logger.info("知识库 %s（%s）上传 %s 个文档，已转后台处理", kb_id, kb.name, len(docs))
        return docs

    @staticmethod
    async def process_document(db: AsyncSession, doc_id: int) -> None:
        """
        文档处理管线（后台任务 / 对账重跑共用）：
        抢占状态机 → 双侧清残留 → 切片 → 批量向量化 → PG 账目 + Qdrant 双写 → 完成。
        任一步失败标 FAILED 记录原因；重跑入口保证幂等。
        """
        doc = await KnowledgeService.get_doc(db, doc_id)

        # 条件更新抢占状态机，并发重入直接拒绝
        claim = await db.execute(
            update(SysAgentKnowledgeDoc)
            .where(
                SysAgentKnowledgeDoc.id == doc_id,
                SysAgentKnowledgeDoc.status != DOC_STATUS_PROCESSING,
            )
            .values(status=DOC_STATUS_PROCESSING, error_msg=None)
        )
        if claim.rowcount == 0:
            raise CustomError(error=CustomErrorCode.KNOWLEDGE_DOC_PROCESSING, msg=t("error.knowledge.doc_processing"))
        await db.commit()

        try:
            content = doc.content or ""
            texts = chunk_text(content, settings.AGENT.KB_CHUNK_SIZE, settings.AGENT.KB_CHUNK_OVERLAP)
            if not texts:
                raise ValueError("文档内容为空或切片结果为空")

            # 幂等：清两侧残留（失败/中断重跑场景）
            store = get_vector_store()
            await store.delete_by_doc(doc.knowledge_id, doc_id)
            await db.execute(
                delete(SysAgentKnowledgeChunk).where(SysAgentKnowledgeChunk.doc_id == doc_id)
            )

            # PG 账目先行（拿雪花 ID 作为 Qdrant point id）
            chunks: list[SysAgentKnowledgeChunk] = []
            for index, text in enumerate(texts):
                chunk = SysAgentKnowledgeChunk(
                    knowledge_id=doc.knowledge_id,
                    doc_id=doc_id,
                    chunk_index=index,
                    char_count=len(text),
                )
                db.add(chunk)
                chunks.append(chunk)
            await db.flush()

            # 向量化（批量化 + 首批时建 collection）
            client, model_name = await KnowledgeService._embedding_client(db, doc.knowledge_id)
            dim = 0
            batch_size = settings.AGENT.KB_EMBED_BATCH
            for start in range(0, len(texts), batch_size):
                batch_texts = texts[start : start + batch_size]
                batch_chunks = chunks[start : start + batch_size]
                vectors = await client.embeddings(model_name, batch_texts)
                if dim == 0:
                    dim = len(vectors[0])
                    await store.ensure_collection(doc.knowledge_id, dim)
                await store.upsert_points(
                    doc.knowledge_id,
                    [
                        VectorPoint(
                            id=chunk.id,
                            vector=vector,
                            doc_id=doc_id,
                            kb_id=doc.knowledge_id,
                            chunk_index=chunk.chunk_index,
                            content=text,
                        )
                        for chunk, vector, text in zip(batch_chunks, vectors, batch_texts)
                    ],
                )

            doc.status = DOC_STATUS_COMPLETED
            doc.chunk_count = len(chunks)
            doc.error_msg = None
            await db.commit()
            logger.info("文档 %s 处理完成，切片 %s 个", doc_id, len(chunks))
        except Exception as exc:
            await db.rollback()
            doc = await KnowledgeService.get_doc(db, doc_id)
            doc.status = DOC_STATUS_FAILED
            doc.error_msg = str(exc)[:500]
            await db.commit()
            logger.warning("文档 %s 处理失败: %s", doc_id, exc)
            raise

        kb = await KnowledgeService.get_knowledge(db, doc.knowledge_id)
        await KnowledgeService._refresh_counts(db, kb)

    @staticmethod
    async def _embedding_client(db: AsyncSession, kb_id: int) -> tuple[object, str]:
        """按知识库配置构造向量化客户端，返回 (LLMClient, model_name)"""
        result = await db.execute(
            select(SysAgentModel, SysAgentProvider)
            .join(SysAgentKnowledge, SysAgentModel.id == SysAgentKnowledge.embedding_model_id)
            .join(SysAgentProvider, SysAgentModel.provider_id == SysAgentProvider.id)
            .where(SysAgentKnowledge.id == kb_id)
        )
        row = result.first()
        if row is None:
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_EMBEDDING_MODEL_INVALID,
                msg=t("error.knowledge.embedding_model_invalid", id=0),
            )
        model, provider = row[0], row[1]
        return ProviderService.build_client(provider), model.name

    @staticmethod
    async def _refresh_counts(db: AsyncSession, kb: SysAgentKnowledge) -> None:
        """刷新知识库冗余计数（文档数 / 切片数）"""
        doc_count = await db.execute(
            select(func.count()).select_from(SysAgentKnowledgeDoc).where(
                SysAgentKnowledgeDoc.knowledge_id == kb.id,
                SysAgentKnowledgeDoc.deleted_at.is_(None),
            )
        )
        chunk_count = await db.execute(
            select(func.count()).select_from(SysAgentKnowledgeChunk).where(
                SysAgentKnowledgeChunk.knowledge_id == kb.id
            )
        )
        kb.doc_count = doc_count.scalar() or 0
        kb.chunk_count = chunk_count.scalar() or 0
        await db.commit()

    # ---------- 文档：删除 / 重处理 / 重建 ----------

    @staticmethod
    async def delete_document(db: AsyncSession, kb_id: int, doc_id: int) -> bool:
        """删除文档：先删 Qdrant 点（失败阻断），再物理删 PG 账目"""
        logger.info("删除知识库文档，kb=%s doc=%s", kb_id, doc_id)
        kb = await KnowledgeService.get_knowledge(db, kb_id)
        doc = await KnowledgeService.get_doc(db, doc_id)
        if doc.knowledge_id != kb_id:
            raise NotFoundError(msg=t("error.knowledge.doc_not_found", id=doc_id))

        await get_vector_store().delete_by_doc(kb_id, doc_id)
        await db.execute(
            delete(SysAgentKnowledgeChunk).where(SysAgentKnowledgeChunk.doc_id == doc_id)
        )
        await db.delete(doc)
        await KnowledgeService._refresh_counts(db, kb)
        logger.info("删除知识库文档成功，kb=%s doc=%s", kb_id, doc_id)
        return True

    @staticmethod
    async def reprocess_document(db: AsyncSession, kb_id: int, doc_id: int) -> bool:
        """重新处理文档（失败重试 / 换切片策略重切；基于已提取全文）"""
        kb = await KnowledgeService.get_knowledge(db, kb_id)
        doc = await KnowledgeService.get_doc(db, doc_id)
        if doc.knowledge_id != kb_id:
            raise NotFoundError(msg=t("error.knowledge.doc_not_found", id=doc_id))
        if not (doc.content or "").strip():
            raise CustomError(
                error=CustomErrorCode.KNOWLEDGE_EMPTY_CONTENT,
                msg=t("error.knowledge.empty_content", name=doc.file_name),
            )

        doc.status = DOC_STATUS_PENDING
        doc.error_msg = None
        await db.commit()
        spawn_doc_processing([doc_id])
        return True

    @staticmethod
    async def rebuild_knowledge(db: AsyncSession, kb_id: int) -> int:
        """全量重建：所有文档复位待处理并重跑（换向量化模型/切片策略后使用）"""
        kb = await KnowledgeService.get_knowledge(db, kb_id)
        result = await db.execute(
            select(SysAgentKnowledgeDoc.id).where(
                SysAgentKnowledgeDoc.knowledge_id == kb_id,
                SysAgentKnowledgeDoc.deleted_at.is_(None),
            )
        )
        doc_ids = [row[0] for row in result.all()]
        if not doc_ids:
            return 0

        await db.execute(
            update(SysAgentKnowledgeDoc)
            .where(SysAgentKnowledgeDoc.id.in_(doc_ids))
            .values(status=DOC_STATUS_PENDING, error_msg=None)
        )
        await db.commit()
        spawn_doc_processing(doc_ids)
        logger.info("知识库 %s（%s）发起全量重建，文档 %s 个", kb_id, kb.name, len(doc_ids))
        return len(doc_ids)

    # ---------- 对账（定时任务） ----------

    @staticmethod
    async def reset_stuck_docs(db: AsyncSession) -> int:
        """复位处理中超时文档（重启丢任务等场景）：processing 超时 → failed 待重试"""
        deadline = datetime.now(timezone.utc) - timedelta(
            minutes=settings.AGENT.KB_DOC_PROCESS_TIMEOUT_MIN
        )
        result = await db.execute(
            update(SysAgentKnowledgeDoc)
            .where(
                SysAgentKnowledgeDoc.status == DOC_STATUS_PROCESSING,
                SysAgentKnowledgeDoc.updated_at < deadline,
            )
            .values(status=DOC_STATUS_FAILED, error_msg="处理超时已复位，可重新处理")
        )
        await db.commit()
        count = result.rowcount or 0
        if count:
            logger.warning("复位超时处理中文档 %s 个", count)
        return count

    @staticmethod
    async def reconcile(db: AsyncSession) -> dict:
        """
        向量对账：PG 切片账目 vs Qdrant 点数；偏差文档自动重跑（幂等管线自愈）。
        Qdrant 不可用时记 WARNING 跳过本轮（不阻断调度）。
        """
        await KnowledgeService.reset_stuck_docs(db)

        result = await db.execute(
            select(SysAgentKnowledge).where(SysAgentKnowledge.deleted_at.is_(None))
        )
        store = get_vector_store()
        mismatches: list[int] = []
        for kb in result.scalars().all():
            try:
                doc_rows = await db.execute(
                    select(SysAgentKnowledgeDoc.id, SysAgentKnowledgeDoc.chunk_count).where(
                        SysAgentKnowledgeDoc.knowledge_id == kb.id,
                        SysAgentKnowledgeDoc.deleted_at.is_(None),
                    )
                )
                for doc_id, pg_count in doc_rows.all():
                    qdrant_count = await store.count(kb.id, doc_id)
                    if pg_count != qdrant_count:
                        mismatches.append(doc_id)
            except Exception as exc:
                logger.warning("知识库 %s 对账失败（Qdrant 异常？）: %s", kb.id, exc)

        for doc_id in mismatches:
            spawn_doc_processing([doc_id])
        if mismatches:
            logger.warning("知识库对账发现 %s 个偏差文档，已自动重跑", len(mismatches))
        return {"reprocessed": len(mismatches)}

    # ---------- 检索 ----------

    @staticmethod
    async def search_knowledge(
        db: AsyncSession, kb_id: int, query: str, top_k: int
    ) -> list[KnowledgeSearchHit]:
        """检索测试（管理端调参用；不要求知识库启用）"""
        await KnowledgeService.get_knowledge(db, kb_id)
        results = await KnowledgeRetriever.retrieve(db, query, [kb_id], top_k=top_k)
        return [
            KnowledgeSearchHit(
                kb_id=r.kb_id,
                kb_name=r.kb_name,
                doc_id=r.doc_id,
                chunk_index=r.chunk_index,
                content=r.content,
                score=round(r.score, 4),
            )
            for r in results
        ]


# ---------- 后台任务 ----------

# 运行中的后台处理任务集合（强引用防 GC，完成自动移除）
_BACKGROUND_TASKS: set[asyncio.Task] = set()


def spawn_doc_processing(doc_ids: list[int]) -> None:
    """为每个文档派发独立后台处理任务（各自管理 DB 会话）"""
    for doc_id in doc_ids:
        task = asyncio.create_task(_process_doc_task(doc_id))
        _BACKGROUND_TASKS.add(task)
        task.add_done_callback(_BACKGROUND_TASKS.discard)


async def _process_doc_task(doc_id: int) -> None:
    """单文档后台处理入口（异常兜底记日志；业务失败已落文档状态机）"""
    from database.db_manager import get_session

    started = time.monotonic()
    try:
        async for db in get_session():
            await KnowledgeService.process_document(db, doc_id)
            break
    except CustomError:
        pass  # 并发抢占等业务拒绝，状态机已表达
    except Exception:
        logger.exception("文档 %s 后台处理异常", doc_id)
    finally:
        logger.debug("文档 %s 后台任务结束，耗时 %.1fs", doc_id, time.monotonic() - started)
