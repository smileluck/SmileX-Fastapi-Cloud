#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List, Annotated
from pydantic import Field, ConfigDict, BeforeValidator, field_validator
from datetime import datetime, date, time

from app.models.common.base import BaseEntity, BaseRespEntity, BaseReqEntity, BoolField


def _bool_to_enable_str(v):
    """将 bool 转换为 "1"/"2" 字符串"""
    if isinstance(v, bool):
        return "1" if v else "2"
    return v

EnableStatusField = Annotated[str, BeforeValidator(_bool_to_enable_str)]

VALID_REPEAT_CYCLES = {'none', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'}


def _validate_repeat_cycle(v: Optional[str]) -> Optional[str]:
    """校验逗号分隔的重复周期值"""
    if v is None or v == '':
        return None
    for part in v.split(','):
        part = part.strip()
        if part not in VALID_REPEAT_CYCLES:
            raise ValueError(f"无效的重复周期值: {part}")
    return v


# ==================== 点位 Schema ====================

class TaskPointCreate(BaseReqEntity):
    """巡逻点位创建"""
    sort_order: int = Field(0, description="排序")
    point_name: Optional[str] = Field(None, description="点位名称", max_length=100)
    annotation_id: Optional[int] = Field(None, description="关联场景标注ID")
    action: str = Field(..., description="运控动作: wave/bow/turn/wait/nod", max_length=20)
    voice_text: Optional[str] = Field(None, description="语音播报文本")


class TaskPointResponse(BaseRespEntity):
    """巡逻点位响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="点位ID")
    task_id: int = Field(..., description="任务ID")
    sort_order: int = Field(..., description="排序")
    point_name: Optional[str] = Field(None, description="点位名称")
    annotation_id: Optional[int] = Field(None, description="关联场景标注ID")
    action: str = Field(..., description="运控动作")
    voice_text: Optional[str] = Field(None, description="语音播报文本")


# ==================== 机器人简要 Schema ====================

class TaskRobotBrief(BaseRespEntity):
    """任务关联机器人简要信息"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="机器人ID")
    name: str = Field(..., description="机器人名称")
    status: Optional[str] = Field(None, description="机器人状态")


# ==================== 任务 CRUD Schema ====================

class TaskQueryParams(BaseReqEntity):
    """任务查询参数"""
    name: Optional[str] = Field(None, description="任务名称，支持模糊查询")
    task_type: Optional[str] = Field(None, description="任务类型: patrol/broadcast")
    enabled: BoolField = Field(None, description="启用状态")


class TaskCreate(BaseReqEntity):
    """创建任务"""
    name: str = Field(..., description="任务名称", min_length=2, max_length=20)
    task_type: str = Field(..., description="任务类型: patrol/broadcast")
    points: Optional[List[TaskPointCreate]] = Field(None, description="巡逻点位列表")
    broadcast_text: Optional[str] = Field(None, description="播报文本")
    broadcast_count: Optional[str] = Field(None, description="播报次数: 1/2/3/5/loop")
    robot_ids: List[int] = Field(..., description="绑定的机器人ID列表", min_length=1)
    schedule_enabled: bool = Field(False, description="是否启用定时调度")
    schedule_date: Optional[date] = Field(None, description="调度日期")
    schedule_start_time: Optional[time] = Field(None, description="调度开始时间")
    schedule_repeat_cycle: Optional[str] = Field(None, description="重复周期: 逗号分隔 mon,tue,wed,thu,fri,sat,sun")

    @field_validator('schedule_repeat_cycle')
    @classmethod
    def validate_repeat_cycle(cls, v):
        return _validate_repeat_cycle(v)


class TaskUpdate(BaseReqEntity):
    """更新任务"""
    name: Optional[str] = Field(None, description="任务名称", min_length=2, max_length=20)
    task_type: Optional[str] = Field(None, description="任务类型")
    points: Optional[List[TaskPointCreate]] = Field(None, description="巡逻点位列表")
    broadcast_text: Optional[str] = Field(None, description="播报文本")
    broadcast_count: Optional[str] = Field(None, description="播报次数")
    robot_ids: Optional[List[int]] = Field(None, description="绑定的机器人ID列表")
    schedule_enabled: Optional[bool] = Field(None, description="是否启用定时调度")
    schedule_date: Optional[date] = Field(None, description="调度日期")
    schedule_start_time: Optional[time] = Field(None, description="调度开始时间")
    schedule_repeat_cycle: Optional[str] = Field(None, description="重复周期: 逗号分隔 mon,tue,wed,thu,fri,sat,sun")

    @field_validator('schedule_repeat_cycle')
    @classmethod
    def validate_repeat_cycle(cls, v):
        return _validate_repeat_cycle(v)


class TaskResponseData(BaseEntity):
    """任务响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="任务ID")
    name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型")
    enabled: EnableStatusField = Field(..., description="启用状态: 1-启用, 2-禁用")
    status: str = Field(..., description="执行状态")
    broadcast_text: Optional[str] = Field(None, description="播报文本")
    broadcast_count: Optional[str] = Field(None, description="播报次数")
    schedule_enabled: bool = Field(..., description="是否启用定时调度")
    schedule_date: Optional[str] = Field(None, description="调度日期")
    schedule_start_time: Optional[str] = Field(None, description="调度开始时间")
    schedule_repeat_cycle: Optional[str] = Field(None, description="重复周期")
    point_count: int = Field(0, description="巡逻点位数量")
    points: Optional[List[TaskPointResponse]] = Field(None, description="巡逻点位列表")
    robots: Optional[List[TaskRobotBrief]] = Field(None, description="关联机器人列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class TaskToggleEnabled(BaseReqEntity):
    """切换启用/禁用"""
    enabled: bool = Field(..., description="启用状态")


# ==================== 执行记录 Schema ====================

class TaskExecutionQueryParams(BaseReqEntity):
    """执行记录查询参数"""
    task_name: Optional[str] = Field(None, description="任务名称")
    status: Optional[str] = Field(None, description="执行状态: completed/failed/cancelled")
    start_time: Optional[str] = Field(None, description="开始时间(起)")
    end_time: Optional[str] = Field(None, description="结束时间(止)")


class TaskExecutionResponseData(BaseEntity):
    """执行记录响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="执行记录ID")
    task_id: int = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    task_type: str = Field(..., description="任务类型")
    status: str = Field(..., description="执行状态")
    progress: int = Field(..., description="进度百分比")
    current_position: Optional[str] = Field(None, description="当前位置")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    ended_at: Optional[datetime] = Field(None, description="结束时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    robot_id: Optional[int] = Field(None, description="机器人ID")
    robot_name: Optional[str] = Field(None, description="机器人名称")
    triggered_by: str = Field(..., description="触发方式")
    created_at: datetime = Field(..., description="创建时间")


class TaskExecutionDetailResponseData(TaskExecutionResponseData):
    """执行记录详情响应（含点位）"""
    points: Optional[List[TaskPointResponse]] = Field(None, description="任务点位列表")
