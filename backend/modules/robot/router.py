#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter

from .endpoints import robot_model_router, robot_router, robot_status_record_router, robot_config_router, robot_event_log_router

router = APIRouter(prefix="/robot")

router.include_router(robot_model_router)
router.include_router(robot_router)
router.include_router(robot_status_record_router)
router.include_router(robot_config_router)
router.include_router(robot_event_log_router)
