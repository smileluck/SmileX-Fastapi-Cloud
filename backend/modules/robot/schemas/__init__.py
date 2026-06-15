#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .robot_model import (
    RobotModelQueryParams,
    RobotModelCreate,
    RobotModelUpdate,
    RobotModelResponseData,
)
from .robot import (
    RobotQueryParams,
    RobotCreate,
    RobotUpdate,
    RobotResponseData,
)
from .robot_status_record import (
    RobotStatusRecordQueryParams,
    RobotStatusRecordResponseData,
)
from .robot_event_log import (
    RobotEventLogQueryParams,
    RobotEventLogResponse,
    RobotEventLogDetailResponse,
)

__all__ = [
    # 机器人型号相关
    "RobotModelQueryParams",
    "RobotModelCreate",
    "RobotModelUpdate",
    "RobotModelResponseData",
    # 机器人相关
    "RobotQueryParams",
    "RobotCreate",
    "RobotUpdate",
    "RobotResponseData",
    # 机器人状态记录相关
    "RobotStatusRecordQueryParams",
    "RobotStatusRecordResponseData",
    # 机器人事件日志相关
    "RobotEventLogQueryParams",
    "RobotEventLogResponse",
    "RobotEventLogDetailResponse",
]
