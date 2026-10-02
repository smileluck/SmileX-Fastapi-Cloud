#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体管理服务
"""
import logging
from typing import Optional

from sqlalchemy import and_, func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.agent import SysAgent, SysAgentModel, SysAgentProvider
from modules.agent.core.tool_registry import get_tool_registry
from modules.agent.schemas.agent import AgentCreate, AgentQueryParams, AgentUpdate
from modules.agent.services.skill_service import SkillService
from modules.agent.utils import archive_and_soft_delete, dump_str_list, load_str_list

logger = logging.getLogger(__name__)

# 工具/技能绑定上限
MAX_TOOLS = 10
MAX_SKILLS = 10


class AgentService:
    """智能体管理服务类"""

    @staticmethod
    def build_agent_query(query_params: AgentQueryParams) -> Select:
        """构建智能体分页查询条件（联查模型与供应商名称）"""
        base_query = (
            select(SysAgent, SysAgentModel.name, SysAgentProvider.name)
            .join(SysAgentModel, SysAgent.model_id == SysAgentModel.id, isouter=True)
            .join(SysAgentProvider, SysAgentModel.provider_id == SysAgentProvider.id, isouter=True)
        )

        conditions = [SysAgent.deleted_at.is_(None)]
        if query_params.status is not None:
            conditions.append(SysAgent.status == query_params.status)
        if query_params.name:
            conditions.append(SysAgent.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysAgent.code.like(f"%{query_params.code}%"))

        return base_query.where(and_(*conditions)).order_by(SysAgent.id.desc())

    @staticmethod
    async def get_agent(db: AsyncSession, agent_id: int) -> SysAgent:
        """获取单个智能体，不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysAgent).where(SysAgent.id == agent_id, SysAgent.deleted_at.is_(None))
        )
        agent = result.scalar_one_or_none()
        if not agent:
            raise NotFoundError(msg=t("error.agent.not_found", id=agent_id))
        return agent

    @staticmethod
    async def _ensure_code_unique(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> None:
        """校验智能体编码唯一（排除自身）"""
        conditions = [SysAgent.code == code, SysAgent.deleted_at.is_(None)]
        if exclude_id is not None:
            conditions.append(SysAgent.id != exclude_id)
        result = await db.execute(select(SysAgent.id).where(and_(*conditions)))
        if result.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.AGENT_CODE_EXIST,
                msg=t("error.agent.code_exist", code=code),
            )

    @staticmethod
    async def validate_tools(db: AsyncSession, tools: list[str]) -> None:
        """
        校验工具绑定：
        - 内置工具须已在注册表注册
        - mcp:<code>:<tool> 仅强校验服务存在且启用（工具存在性动态，不卡配置）
        """
        if len(tools) > MAX_TOOLS:
            raise CustomError(
                error=CustomErrorCode.AGENT_NOT_FOUND,
                msg=t("error.agent.too_many_tools", max=MAX_TOOLS),
            )
        registry = get_tool_registry()
        from modules.agent.services.mcp_server_service import McpServerService

        seen: set[str] = set()
        for name in tools:
            if name in seen:
                continue
            seen.add(name)
            if name.startswith("mcp:"):
                parts = name.split(":", 2)
                if len(parts) != 3 or not parts[1] or not parts[2]:
                    raise CustomError(
                        error=CustomErrorCode.MCP_SERVER_NOT_FOUND,
                        msg=t("error.mcp_server.bad_tool_ref", name=name),
                    )
                await McpServerService.check_server(db, parts[1])
            elif name not in registry.names():
                raise CustomError(
                    error=CustomErrorCode.MCP_SERVER_NOT_FOUND,
                    msg=t("error.agent.unknown_tool", name=name),
                )

    @staticmethod
    async def validate_skills(db: AsyncSession, skills: list[str]) -> None:
        """校验技能绑定：存在且启用；去重；上限保护"""
        if len(skills) > MAX_SKILLS:
            raise CustomError(
                error=CustomErrorCode.SKILL_NOT_FOUND,
                msg=t("error.skill.too_many", max=MAX_SKILLS),
            )
        unique_codes = list(dict.fromkeys(skills))
        for code in unique_codes:
            await SkillService.check_enabled(db, code)

    @staticmethod
    async def create_agent(db: AsyncSession, payload: AgentCreate) -> SysAgent:
        """创建智能体"""
        logger.info("创建智能体，编码: %s", payload.code)
        await AgentService._ensure_code_unique(db, payload.code)

        # 模型存在性校验
        result = await db.execute(
            select(SysAgentModel.id).where(
                SysAgentModel.id == payload.model_id, SysAgentModel.deleted_at.is_(None)
            )
        )
        if result.scalar_one_or_none() is None:
            raise NotFoundError(msg=t("error.agent.model_not_found", id=payload.model_id))

        await AgentService.validate_tools(db, payload.tools)
        await AgentService.validate_skills(db, payload.skills)

        agent = SysAgent(
            name=payload.name,
            code=payload.code,
            model_id=payload.model_id,
            system_prompt=payload.system_prompt,
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
            tools=dump_str_list(list(dict.fromkeys(payload.tools))),
            skills=dump_str_list(list(dict.fromkeys(payload.skills))),
            remark=payload.remark,
            status=payload.status,
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        logger.info("创建智能体成功，ID: %s", agent.id)
        return agent

    @staticmethod
    async def update_agent(db: AsyncSession, agent_id: int, payload: AgentUpdate) -> SysAgent:
        """更新智能体（编码不可改；tools/skills None=不变、空数组=清空）"""
        logger.info("更新智能体，ID: %s", agent_id)
        agent = await AgentService.get_agent(db, agent_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("code", None)

        tools = update_data.pop("tools", None)
        skills = update_data.pop("skills", None)
        if tools is not None:
            await AgentService.validate_tools(db, tools)
            agent.tools = dump_str_list(list(dict.fromkeys(tools)))
        if skills is not None:
            await AgentService.validate_skills(db, skills)
            agent.skills = dump_str_list(list(dict.fromkeys(skills)))

        if "model_id" in update_data and update_data["model_id"] is not None:
            result = await db.execute(
                select(SysAgentModel.id).where(
                    SysAgentModel.id == update_data["model_id"],
                    SysAgentModel.deleted_at.is_(None),
                )
            )
            if result.scalar_one_or_none() is None:
                raise NotFoundError(msg=t("error.agent.model_not_found", id=update_data["model_id"]))

        for key, value in update_data.items():
            if hasattr(agent, key) and value is not None:
                setattr(agent, key, value)

        await db.commit()
        await db.refresh(agent)
        logger.info("更新智能体成功，ID: %s", agent_id)
        return agent

    @staticmethod
    async def delete_agent(db: AsyncSession, agent_id: int) -> bool:
        """删除智能体（软删归档；会话与用量不级联，靠冗余名称保历史可读）"""
        logger.info("删除智能体，ID: %s", agent_id)
        agent = await AgentService.get_agent(db, agent_id)
        await archive_and_soft_delete(db, agent, "code")
        logger.info("删除智能体成功，ID: %s", agent_id)
        return True

    @staticmethod
    def parse_tools(agent: SysAgent) -> list[str]:
        """解析智能体绑定的工具名列表"""
        return load_str_list(agent.tools)

    @staticmethod
    def parse_skills(agent: SysAgent) -> list[str]:
        """解析智能体绑定的技能编码列表"""
        return load_str_list(agent.skills)

    @staticmethod
    async def count_agents_using_skill(db: AsyncSession, skill_code: str) -> int:
        """统计引用指定技能编码的智能体数量（JSON 文本列带引号精确模糊匹配）"""
        result = await db.execute(
            select(func.count()).select_from(SysAgent).where(
                SysAgent.skills.like(f'%"{skill_code}"%'),
                SysAgent.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def count_agents_using_mcp(db: AsyncSession, server_code: str) -> int:
        """统计工具引用指定 MCP 服务（mcp:<code>: 前缀足够特异）的智能体数量"""
        result = await db.execute(
            select(func.count()).select_from(SysAgent).where(
                SysAgent.tools.like(f'%mcp:{server_code}:%'),
                SysAgent.deleted_at.is_(None),
            )
        )
        return result.scalar() or 0
