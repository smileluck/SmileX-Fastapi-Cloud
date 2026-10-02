#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI 智能体模块路由聚合
"""
from fastapi import APIRouter

from modules.agent.endpoints.agent import agent_router
from modules.agent.endpoints.chat import chat_router
from modules.agent.endpoints.mcp import mcp_router
from modules.agent.endpoints.model import model_router
from modules.agent.endpoints.provider import provider_router
from modules.agent.endpoints.skill import skill_router

router = APIRouter(prefix="/admin/agent", tags=["AI 智能体"])

router.include_router(provider_router)
router.include_router(model_router)
router.include_router(agent_router)
router.include_router(chat_router)
router.include_router(mcp_router)
router.include_router(skill_router)
