#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from .endpoints.task import task_router
from .endpoints.task_execution import task_execution_router

router = APIRouter(prefix="/task")

router.include_router(task_router)
router.include_router(task_execution_router)
