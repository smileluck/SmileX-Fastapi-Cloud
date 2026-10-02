#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
智能体管理接口
"""
import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.decorators.operation_log import log_operation
from core.i18n import t
from core.response.response_schema import ResponseModel, ResponsePageModel
from database.db_manager import get_session
from modules.admin.deps.auth.permission import require_permission
from modules.admin.deps.auth.user_manager import current_user
from modules.agent.schemas.agent import (
    AgentCreate,
    AgentQueryParams,
    AgentResponseData,
    AgentUpdate,
    ToolGroup,
    ToolGroupItem,
)
from modules.agent.services import AgentService, McpServerService
from modules.agent.utils import paginate_joined
from modules.common.schemas.page import PageRequest, get_page_params

logger = logging.getLogger(__name__)

agent_router = APIRouter(
    prefix="/agents", tags=["智能体管理"], dependencies=[Depends(current_user)]
)


def _to_response(agent, model_name=None, provider_name=None) -> AgentResponseData:
    """ORM → 响应（tools/skills 由 schema validator 解析 JSON 文本列）"""
    data = AgentResponseData.model_validate(agent)
    data.model_name = model_name
    data.provider_name = provider_name
    return data


@agent_router.get(
    "/list",
    response_model=ResponsePageModel[AgentResponseData],
    dependencies=[Depends(require_permission("agent:list"))],
)
async def get_agent_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: AgentQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """获取智能体分页列表（含绑定模型与供应商名称）"""
    logger.info("获取智能体列表请求")

    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = AgentService.build_agent_query(query_params)
    page_data = await paginate_joined(
        db, page_params, query, AgentResponseData, ("model_name", "provider_name")
    )
    logger.info("获取智能体列表成功，共 %s 条记录", page_data.total)
    return ResponsePageModel[AgentResponseData](data=page_data)


@agent_router.get(
    "/all",
    response_model=ResponseModel[list[AgentResponseData]],
    dependencies=[Depends(require_permission("agent:chat"))],
)
async def get_all_enabled_agents(db: AsyncSession = Depends(get_session)):
    """全部启用智能体（聊天页下拉）"""
    from sqlalchemy import select

    from database.models.sys.agent import SysAgent

    result = await db.execute(
        select(SysAgent)
        .where(SysAgent.status.is_(True), SysAgent.deleted_at.is_(None))
        .order_by(SysAgent.id.asc())
    )
    agents = result.scalars().all()
    return ResponseModel(data=[_to_response(a) for a in agents])


@agent_router.get(
    "/tools/groups",
    response_model=ResponseModel[list[ToolGroup]],
    dependencies=[Depends(require_permission("agent:list"))],
)
async def get_tool_groups(db: AsyncSession = Depends(get_session)):
    """
    可绑定工具分组（Agent 表单数据源）：内置工具 + 各启用 MCP 服务的工具。
    单个 MCP 服务拉取失败跳过，不阻断整体。
    """
    import asyncio

    from modules.agent.core.mcp_manager import get_mcp_manager
    from modules.agent.core.tool_registry import get_tool_registry

    groups: list[ToolGroup] = [
        ToolGroup(
            group="builtin",
            label=t("agent.tools.builtin_group"),
            tools=[
                ToolGroupItem(name=func.name, description=func.description)
                for func in (
                    get_tool_registry().find(name).def_()
                    for name in get_tool_registry().names()
                )
            ],
        )
    ]

    manager = get_mcp_manager()
    servers = await McpServerService.list_enabled(db)
    for server in servers:
        try:
            tools, _info = await asyncio.wait_for(
                manager.get_tools(db, server.code), timeout=10.0
            )
        except Exception as exc:
            logger.warning("拉取 MCP 服务 %s 工具失败，已跳过: %s", server.code, exc)
            continue
        groups.append(
            ToolGroup(
                group=f"mcp:{server.code}",
                label=f"MCP · {server.name}",
                tools=[
                    ToolGroupItem(name=f"mcp:{server.code}:{info.name}", description=info.description)
                    for info in tools
                ],
            )
        )
    return ResponseModel(data=groups)


@agent_router.get(
    "/{agent_id}",
    response_model=ResponseModel[AgentResponseData],
    dependencies=[Depends(require_permission("agent:list"))],
)
async def get_agent(
    agent_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个智能体"""
    logger.info("获取智能体请求，ID: %s", agent_id)
    agent = await AgentService.get_agent(db, agent_id)
    return ResponseModel(data=_to_response(agent))


@agent_router.post(
    "/add",
    response_model=ResponseModel[AgentResponseData],
    dependencies=[Depends(require_permission("agent:add"))],
)
@log_operation(module="agent", action="create", description="创建智能体")
async def create_agent(
    request: Request,
    agent_create: AgentCreate,
    db: AsyncSession = Depends(get_session),
):
    """创建智能体（绑定模型；工具/技能绑定校验）"""
    logger.info("创建智能体请求，编码: %s", agent_create.code)
    agent = await AgentService.create_agent(db, agent_create)
    return ResponseModel(data=_to_response(agent), msg=t("agent.create_success"))


@agent_router.put(
    "/{agent_id}",
    response_model=ResponseModel[AgentResponseData],
    dependencies=[Depends(require_permission("agent:edit"))],
)
@log_operation(module="agent", action="update", description="更新智能体")
async def update_agent(
    agent_id: int,
    request: Request,
    agent_update: AgentUpdate,
    db: AsyncSession = Depends(get_session),
):
    """更新智能体（编码不可改；tools/skills 留空=不变、空数组=清空）"""
    logger.info("更新智能体请求，ID: %s", agent_id)
    agent = await AgentService.update_agent(db, agent_id, agent_update)
    return ResponseModel(data=_to_response(agent), msg=t("agent.update_success"))


@agent_router.delete(
    "/{agent_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("agent:delete"))],
)
@log_operation(module="agent", action="delete", description="删除智能体")
async def delete_agent(
    agent_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
):
    """删除智能体（会话与用量历史保留，靠冗余名可读）"""
    logger.info("删除智能体请求，ID: %s", agent_id)
    await AgentService.delete_agent(db, agent_id)
    return ResponseModel(msg=t("agent.delete_success"))
