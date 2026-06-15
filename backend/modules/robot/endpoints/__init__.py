#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .robot_model import robot_model_router
from .robot import robot_router
from .robot_status_record import robot_status_record_router
from .robot_config import robot_config_router
from .robot_event_log import robot_event_log_router

__all__ = ["robot_model_router", "robot_router", "robot_status_record_router", "robot_config_router", "robot_event_log_router"]
