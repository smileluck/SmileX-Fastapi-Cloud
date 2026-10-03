#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库检索编排

多知识库检索：按 embedding 模型分组共享一次 query 向量化，逐库向量检索，
合并按分数排序取 top_k。单库失败跳过不阻断（对话链路降级为不注入该库）。
"""
import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from database.models.sys.agent import SysAgentModel, SysAgentProvider, SysAgentKnowledge
from modules.agent.core.llm_client import LLMClient
from modules.agent.core.qdrant_store import get_vector_store
from modules.agent.services.provider_service import ProviderService

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """检索结果切片（含来源信息，供注入与引用展示）"""

    kb_id: int
    kb_name: str
    doc_id: int
    chunk_index: int
    content: str
    score: float


def build_kb_context(chunks: list[RetrievedChunk]) -> str:
    """检索结果拼接为 system prompt 引用材料段（受总 60KB 截断保护）"""
    if not chunks:
        return ""
    lines = ["以下是从知识库检索到的参考资料，回答时请优先依据这些内容（若与问题无关可忽略）："]
    for i, chunk in enumerate(chunks, start=1):
        lines.append(f"\n【参考资料{i} | 知识库: {chunk.kb_name} | 相似度: {chunk.score:.2f}】")
        lines.append(chunk.content)
    return "\n".join(lines)


class KnowledgeRetriever:
    """知识库向量检索（对话注入与检索测试共用）"""

    @staticmethod
    async def retrieve(
        db: AsyncSession,
        query: str,
        kb_ids: list[int],
        top_k: int = 0,
        score_threshold: float = -1.0,
    ) -> list[RetrievedChunk]:
        """
        检索多个知识库。

        - 只检索存在、启用且未软删的知识库；缺失/禁用静默跳过
        - 同一 embedding 模型的库共享一次 query 向量化
        - 任一库检索失败记 WARNING 跳过，不抛出
        """
        if not kb_ids or not query.strip():
            return []
        top_k = top_k or settings.AGENT.KB_TOP_K
        threshold = (
            score_threshold
            if score_threshold >= 0
            else settings.AGENT.KB_SCORE_THRESHOLD
        )

        result = await db.execute(
            select(SysAgentKnowledge, SysAgentModel, SysAgentProvider)
            .join(SysAgentModel, SysAgentKnowledge.embedding_model_id == SysAgentModel.id)
            .join(SysAgentProvider, SysAgentModel.provider_id == SysAgentProvider.id)
            .where(
                SysAgentKnowledge.id.in_(kb_ids),
                SysAgentKnowledge.deleted_at.is_(None),
                SysAgentKnowledge.status.is_(True),
                SysAgentModel.deleted_at.is_(None),
                SysAgentModel.status.is_(True),
                SysAgentProvider.deleted_at.is_(None),
                SysAgentProvider.status.is_(True),
            )
        )
        rows = result.all()
        if not rows:
            return []

        # 按 embedding 模型分组，共享一次 query 向量化
        by_model: dict[int, list[tuple[SysAgentKnowledge, LLMClient, str]]] = {}
        for kb, model, provider in rows:
            by_model.setdefault(model.id, []).append(
                (kb, ProviderService.build_client(provider), model.name)
            )

        store = get_vector_store()
        hits: list[RetrievedChunk] = []
        for entries in by_model.values():
            _, client, model_name = entries[0]
            try:
                vectors = await client.embeddings(model_name, [query])
                query_vector = vectors[0]
            except Exception as exc:
                logger.warning("知识库检索向量化失败（model=%s），跳过 %s 个库: %s", model_name, len(entries), exc)
                continue
            for kb, _, _ in entries:
                try:
                    for hit in await store.search(kb.id, query_vector, top_k, threshold):
                        hits.append(
                            RetrievedChunk(
                                kb_id=kb.id,
                                kb_name=kb.name,
                                doc_id=hit.doc_id,
                                chunk_index=hit.chunk_index,
                                content=hit.content,
                                score=hit.score,
                            )
                        )
                except Exception as exc:
                    logger.warning("知识库 %s（%s）检索失败，已跳过: %s", kb.id, kb.name, exc)

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:top_k]
