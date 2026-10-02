#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 服务器接入管理服务
"""
import json
import logging
from typing import Optional

from sqlalchemy import and_, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.mcp_server import SysMcpServer
from modules.agent.core import crypto as agent_crypto
from modules.agent.core.mcp_manager import get_mcp_manager
from modules.agent.schemas.mcp_server import (
    McpHeaderItem,
    McpServerCreate,
    McpServerQueryParams,
    McpServerUpdate,
)
from modules.agent.utils import archive_and_soft_delete

logger = logging.getLogger(__name__)


class McpServerService:
    """MCP 服务器管理服务类"""

    @staticmethod
    def build_server_query(query_params: McpServerQueryParams) -> Select:
        """构建 MCP 服务分页查询条件"""
        base_query = select(SysMcpServer)

        conditions = [SysMcpServer.deleted_at.is_(None)]
        if query_params.status is not None:
            conditions.append(SysMcpServer.status == query_params.status)
        if query_params.name:
            conditions.append(SysMcpServer.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysMcpServer.code.like(f"%{query_params.code}%"))
        if query_params.transport:
            conditions.append(SysMcpServer.transport == query_params.transport)

        return base_query.where(and_(*conditions)).order_by(SysMcpServer.id.desc())

    @staticmethod
    async def get_server(db: AsyncSession, server_id: int) -> SysMcpServer:
        """获取单个 MCP 服务，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysMcpServer).where(
                SysMcpServer.id == server_id, SysMcpServer.deleted_at.is_(None)
            )
        )
        server = result.scalar_one_or_none()
        if not server:
            raise NotFoundError(msg=t("error.mcp_server.not_found", id=server_id))
        return server

    @staticmethod
    async def check_server(db: AsyncSession, code: str) -> SysMcpServer:
        """按编码校验服务存在且启用（供智能体工具绑定校验）"""
        result = await db.execute(
            select(SysMcpServer).where(
                SysMcpServer.code == code, SysMcpServer.deleted_at.is_(None)
            )
        )
        server = result.scalar_one_or_none()
        if server is None:
            raise CustomError(
                error=CustomErrorCode.MCP_SERVER_NOT_FOUND,
                msg=t("error.mcp_server.not_found_by_code", code=code),
            )
        if not server.status:
            raise CustomError(
                error=CustomErrorCode.MCP_SERVER_NOT_FOUND,
                msg=t("error.mcp_server.disabled_by_code", code=code),
            )
        return server

    @staticmethod
    async def _ensure_code_unique(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> None:
        """校验服务编码唯一（排除自身）"""
        conditions = [SysMcpServer.code == code, SysMcpServer.deleted_at.is_(None)]
        if exclude_id is not None:
            conditions.append(SysMcpServer.id != exclude_id)
        result = await db.execute(select(SysMcpServer.id).where(and_(*conditions)))
        if result.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.MCP_SERVER_CODE_EXIST,
                msg=t("error.mcp_server.code_exist", code=code),
            )

    @staticmethod
    def _validate_base_url(base_url: str) -> None:
        """base_url 须为 http(s) 地址"""
        if not base_url.startswith(("http://", "https://")):
            raise CustomError(
                error=CustomErrorCode.MCP_SERVER_NOT_FOUND,
                msg=t("error.mcp_server.bad_url"),
            )

    @staticmethod
    async def create_server(db: AsyncSession, payload: McpServerCreate) -> SysMcpServer:
        """创建 MCP 服务；token 加密落库 + 掩码冗余"""
        logger.info("创建 MCP 服务，编码: %s", payload.code)
        await McpServerService._ensure_code_unique(db, payload.code)
        McpServerService._validate_base_url(payload.base_url)

        headers_json = ""
        if payload.headers:
            headers_json = json.dumps(
                [{"key": h.key, "value": h.value} for h in payload.headers], ensure_ascii=False
            )

        server = SysMcpServer(
            name=payload.name,
            code=payload.code,
            transport=payload.transport,
            base_url=payload.base_url,
            headers=headers_json,
            token_enc=agent_crypto.encrypt_secret(payload.token or "", agent_crypto.MCP_DOMAIN),
            token_mask=agent_crypto.mask_secret(payload.token or ""),
            remark=payload.remark,
            status=payload.status,
        )
        db.add(server)
        await db.commit()
        await db.refresh(server)
        logger.info("创建 MCP 服务成功，ID: %s", server.id)
        return server

    @staticmethod
    async def update_server(
        db: AsyncSession, server_id: int, payload: McpServerUpdate
    ) -> SysMcpServer:
        """更新 MCP 服务（编码不可改；token 留空=保持不变）"""
        logger.info("更新 MCP 服务，ID: %s", server_id)
        server = await McpServerService.get_server(db, server_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("code", None)
        token = update_data.pop("token", None)
        headers = update_data.pop("headers", None)

        for key, value in update_data.items():
            if hasattr(server, key) and value is not None:
                setattr(server, key, value)
        if update_data.get("base_url"):
            McpServerService._validate_base_url(update_data["base_url"])
        if token is not None:
            server.token_enc = agent_crypto.encrypt_secret(token, agent_crypto.MCP_DOMAIN)
            server.token_mask = agent_crypto.mask_secret(token)
        if headers is not None:
            server.headers = json.dumps(
                [{"key": h["key"], "value": h["value"]} for h in headers], ensure_ascii=False
            ) if headers else ""

        await db.commit()
        await db.refresh(server)
        get_mcp_manager().drop(server.code)
        logger.info("更新 MCP 服务成功，ID: %s", server_id)
        return server

    @staticmethod
    async def delete_server(db: AsyncSession, server_id: int) -> bool:
        """删除 MCP 服务；被智能体工具引用时拒绝"""
        from modules.agent.services.agent_service import AgentService

        logger.info("删除 MCP 服务，ID: %s", server_id)
        server = await McpServerService.get_server(db, server_id)

        used = await AgentService.count_agents_using_mcp(db, server.code)
        if used > 0:
            raise CustomError(
                error=CustomErrorCode.MCP_SERVER_IN_USE,
                msg=t("error.mcp_server.in_use"),
            )

        get_mcp_manager().drop(server.code)
        await archive_and_soft_delete(db, server, "code")
        logger.info("删除 MCP 服务成功，ID: %s", server_id)
        return True

    @staticmethod
    async def test_server(db: AsyncSession, server_id: int) -> dict:
        """连通测试（真实握手；失败也是有效结果，不抛错）"""
        server = await McpServerService.get_server(db, server_id)
        manager = get_mcp_manager()
        result = await manager.test_server(server)
        result["server_id"] = server.id
        result["server_code"] = server.code
        return result

    @staticmethod
    async def list_enabled(db: AsyncSession) -> list[SysMcpServer]:
        """全部启用的 MCP 服务（工具分组数据源）"""
        result = await db.execute(
            select(SysMcpServer)
            .where(SysMcpServer.status.is_(True), SysMcpServer.deleted_at.is_(None))
            .order_by(SysMcpServer.id.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    def parse_headers(server: SysMcpServer) -> list[McpHeaderItem]:
        """解析自定义请求头 JSON 文本（存的是 [{"key","value"}] 数组）"""
        try:
            raw = json.loads(server.headers) if server.headers else []
        except json.JSONDecodeError:
            raw = []
        result: list[McpHeaderItem] = []
        if isinstance(raw, list):
            for item in raw:
                if isinstance(item, dict) and item.get("key"):
                    result.append(McpHeaderItem(key=item["key"], value=item.get("value", "")))
        return result
