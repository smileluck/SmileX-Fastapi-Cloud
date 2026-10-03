#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qdrant 向量存储（httpx 直调 REST，零 SDK）

- 每知识库一个 collection（kb_{id}），创建时锁定该库 embedding 维度
- point 设计：id = 切片雪花 ID；payload = {doc_id, kb_id, chunk_index, content}
- 全部写操作 wait=true，返回即生效；非 2xx 统一抛 KNOWLEDGE_QDRANT_ERROR
- 将来切换其他向量库时实现同名接口的业务约定（ensure/upsert/search/delete*）即可
"""
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from core.config import settings
from core.exception.errors import CustomError
from core.i18n import t
from core.response.response_code import CustomErrorCode

logger = logging.getLogger(__name__)

# 单次 REST 请求超时（秒）：embed 批量入库可能较大，给足余量
QDRANT_TIMEOUT = 60.0
QDRANT_CONNECT_TIMEOUT = 5.0


@dataclass
class VectorPoint:
    """待写入向量点"""

    id: int
    vector: list[float]
    doc_id: int = 0
    kb_id: int = 0
    chunk_index: int = 0
    content: str = ""


@dataclass
class SearchHit:
    """检索命中项"""

    point_id: int
    score: float
    doc_id: int = 0
    chunk_index: int = 0
    content: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


def collection_name(kb_id: int) -> str:
    """知识库对应的 collection 名"""
    return f"kb_{kb_id}"


class QdrantStore:
    """Qdrant REST 客户端（collection 粒度操作）"""

    def __init__(self, base_url: str = "", api_key: str = ""):
        self.base_url = (base_url or settings.AGENT.KB_QDRANT_URL).rstrip("/")
        self.api_key = api_key or settings.AGENT.KB_QDRANT_API_KEY
        self._timeout = httpx.Timeout(QDRANT_TIMEOUT, connect=QDRANT_CONNECT_TIMEOUT)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    async def _request(
        self, method: str, path: str, body: Optional[dict[str, Any]] = None, *, ignore_404: bool = False
    ) -> Optional[dict[str, Any]]:
        """统一请求入口：404 可选忽略（存在性探测），其余非 2xx 抛业务错误"""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.request(method, url, json=body, headers=self._headers())
        except httpx.TimeoutException:
            raise self._error("响应超时")
        except httpx.ConnectError:
            raise self._error("无法连接，请检查 KB_QDRANT_URL")
        except Exception as exc:
            raise self._error(str(exc)[:200])
        if resp.status_code == 404 and ignore_404:
            return None
        if resp.status_code >= 400:
            raise self._error(f"HTTP {resp.status_code}: {resp.text[:200]}")
        if not resp.content:
            return {}
        return resp.json()

    @staticmethod
    def _error(detail: str) -> CustomError:
        return CustomError(
            error=CustomErrorCode.KNOWLEDGE_QDRANT_ERROR,
            msg=t("error.knowledge.qdrant_error", detail=detail),
        )

    async def collection_exists(self, kb_id: int) -> bool:
        """collection 是否存在"""
        result = await self._request(
            "GET", f"/collections/{collection_name(kb_id)}", ignore_404=True
        )
        return result is not None

    async def ensure_collection(self, kb_id: int, dim: int) -> None:
        """不存在则按余弦距离创建 collection（幂等）"""
        if await self.collection_exists(kb_id):
            return
        await self._request(
            "PUT",
            f"/collections/{collection_name(kb_id)}",
            {"vectors": {"size": int(dim), "distance": "Cosine"}},
        )
        logger.info("已创建 Qdrant collection %s（dim=%s）", collection_name(kb_id), dim)

    async def delete_collection(self, kb_id: int) -> None:
        """删除整个 collection（知识库删除；不存在视为成功）"""
        await self._request(
            "DELETE", f"/collections/{collection_name(kb_id)}", ignore_404=True
        )

    async def upsert_points(self, kb_id: int, points: list[VectorPoint]) -> None:
        """批量写入向量点（wait=true）"""
        if not points:
            return
        body = {
            "points": [
                {
                    "id": p.id,
                    "vector": p.vector,
                    "payload": {
                        "doc_id": p.doc_id,
                        "kb_id": p.kb_id,
                        "chunk_index": p.chunk_index,
                        "content": p.content,
                    },
                }
                for p in points
            ]
        }
        await self._request(
            "PUT", f"/collections/{collection_name(kb_id)}/points?wait=true", body
        )

    async def search(
        self, kb_id: int, vector: list[float], top_k: int, score_threshold: float = 0.0
    ) -> list[SearchHit]:
        """向量检索（余弦相似度，Qdrant query API）"""
        body: dict[str, Any] = {
            "query": vector,
            "limit": int(top_k),
            "with_payload": True,
        }
        if score_threshold > 0:
            body["score_threshold"] = float(score_threshold)
        data = await self._request(
            "POST", f"/collections/{collection_name(kb_id)}/points/query", body
        )
        hits: list[SearchHit] = []
        for item in (data or {}).get("result") or []:
            payload = item.get("payload") or {}
            hits.append(
                SearchHit(
                    point_id=item.get("id", 0),
                    score=float(item.get("score", 0.0)),
                    doc_id=int(payload.get("doc_id", 0)),
                    chunk_index=int(payload.get("chunk_index", 0)),
                    content=str(payload.get("content", "")),
                )
            )
        return hits

    async def delete_by_doc(self, kb_id: int, doc_id: int) -> None:
        """按文档删除向量点（重处理前清理残留；collection 不存在忽略）"""
        body = {
            "filter": {"must": [{"key": "doc_id", "match": {"value": int(doc_id)}}]}
        }
        await self._request(
            "POST",
            f"/collections/{collection_name(kb_id)}/points/delete?wait=true",
            body,
            ignore_404=True,
        )

    async def count(self, kb_id: int, doc_id: Optional[int] = None) -> int:
        """统计点数（可按文档过滤；collection 不存在返回 0）"""
        body: dict[str, Any] = {"exact": True}
        if doc_id is not None:
            body["filter"] = {"must": [{"key": "doc_id", "match": {"value": int(doc_id)}}]}
        data = await self._request(
            "POST",
            f"/collections/{collection_name(kb_id)}/points/count",
            body,
            ignore_404=True,
        )
        if not data:
            return 0
        return int((data.get("result") or {}).get("count", 0))


_store: Optional[QdrantStore] = None


def get_vector_store() -> QdrantStore:
    """进程级单例（配置启动时读取，运行期不变）"""
    global _store
    if _store is None:
        _store = QdrantStore()
    return _store
