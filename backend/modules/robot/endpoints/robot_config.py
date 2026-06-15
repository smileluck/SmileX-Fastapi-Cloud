#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人参数配置相关接口
"""
import logging
from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response.response_schema import (
    ResponseModel,
    ResponsePageModel,
    response_base,
)
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from core.decorators.operation_log import log_operation
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.admin.services.sys.file_service import FileService
from modules.admin.schemas.sys.file import SysFileUploadResponse

from modules.robot.services.robot_config_service import RobotConfigService
from modules.robot.schemas.robot_config import (
    RobotVoiceConfigSchema,
    RobotVoiceConfigResponse,
    RobotFaceRecognitionCreate,
    RobotFaceRecognitionUpdate,
    RobotFaceRecognitionResponse,
    TestWakeWordRequest,
    TestTTSRequest,
)

logger = logging.getLogger(__name__)

robot_config_router = APIRouter(
    prefix="/config", tags=["机器人参数配置"], dependencies=[Depends(current_user)]
)


# ==================== 语音合成配置 ====================


@robot_config_router.get(
    "/voice",
    response_model=ResponseModel[RobotVoiceConfigResponse],
)
async def get_voice_config(
    robot_id: int,
    db: AsyncSession = Depends(get_session),
):
    """
    获取语音合成配置
    """
    try:
        logger.info("获取语音合成配置接口被调用，robot_id: %d", robot_id)
        config = await RobotConfigService.get_voice_config(db, robot_id)
        response_data = RobotVoiceConfigResponse.model_validate(config)
        logger.info("获取语音合成配置接口成功")
        return response_base.success(data=response_data)
    except Exception as e:
        logger.error("获取语音合成配置接口失败: %s", str(e), exc_info=True)
        raise


@robot_config_router.post(
    "/voice",
    response_model=ResponseModel[RobotVoiceConfigResponse],
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
@log_operation(module="robot", action="update", description="保存语音合成配置")
async def save_voice_config(
    request: Request,
    config_in: RobotVoiceConfigSchema,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    保存语音合成配置
    """
    try:
        logger.info("保存语音合成配置接口被调用")
        config = await RobotConfigService.save_voice_config(db, config_in)
        response_data = RobotVoiceConfigResponse.model_validate(config)
        logger.info("保存语音合成配置接口成功")
        return response_base.success(data=response_data, msg="保存成功")
    except Exception as e:
        logger.error("保存语音合成配置接口失败: %s", str(e), exc_info=True)
        raise


@robot_config_router.post(
    "/voice/test-wake-word",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
async def test_wake_word(
    body: TestWakeWordRequest,
    db: AsyncSession = Depends(get_session),
):
    """
    测试唤醒词（空壳端点）
    """
    logger.info("测试唤醒词接口被调用，文本: %s", body.text)
    return response_base.success(msg="测试指令已下发")


@robot_config_router.post(
    "/voice/test-tts",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
async def test_tts(
    body: TestTTSRequest,
    db: AsyncSession = Depends(get_session),
):
    """
    测试TTS语音合成（空壳端点）
    """
    logger.info("测试TTS接口被调用，音色: %s", body.voice)
    return response_base.success(msg="测试指令已下发")


# ==================== 人脸识别TTS配置 ====================


@robot_config_router.post(
    "/face/upload",
    response_model=ResponseModel[SysFileUploadResponse],
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
async def upload_face_photo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    上传人脸识别人像
    """
    file_data = await file.read()
    sys_file = await FileService.upload_file(
        db=db,
        file_data=file_data,
        original_name=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        created_by=user.id,
    )
    await db.commit()
    return response_base.success(
        data=SysFileUploadResponse.model_validate(sys_file),
        msg="上传成功",
    )


@robot_config_router.get(
    "/face",
    response_model=ResponsePageModel[RobotFaceRecognitionResponse],
    dependencies=[Depends(require_permission("robot:config:list"))],
)
async def get_face_list(
    page_params: PageRequest = Depends(get_page_params),
    db: AsyncSession = Depends(get_session),
):
    """
    获取人脸识别TTS配置列表
    """
    try:
        logger.info("获取人脸识别TTS列表接口被调用")
        query = RobotConfigService.build_face_query()
        page_data = await get_paginated_results(
            db=db,
            page_params=page_params,
            query=query,
            schema=RobotFaceRecognitionResponse,
        )
        logger.info("获取人脸识别TTS列表接口成功，共 %d 条记录", page_data.total)
        return response_base.page(data=page_data)
    except Exception as e:
        logger.error("获取人脸识别TTS列表接口失败: %s", str(e), exc_info=True)
        raise


@robot_config_router.post(
    "/face",
    response_model=ResponseModel[RobotFaceRecognitionResponse],
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
@log_operation(module="robot", action="create", description="创建人脸识别TTS配置")
async def create_face(
    request: Request,
    face_in: RobotFaceRecognitionCreate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    创建人脸识别TTS配置
    """
    try:
        logger.info("创建人脸识别TTS配置接口被调用")
        face = await RobotConfigService.create_face(db, face_in)
        response_data = RobotFaceRecognitionResponse.model_validate(face)
        logger.info("创建人脸识别TTS配置接口成功，ID: %d", face.id)
        return response_base.success(data=response_data, msg="创建成功")
    except Exception as e:
        logger.error("创建人脸识别TTS配置接口失败: %s", str(e), exc_info=True)
        raise


@robot_config_router.put(
    "/face/{face_id}",
    response_model=ResponseModel[RobotFaceRecognitionResponse],
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
@log_operation(module="robot", action="update", description="更新人脸识别TTS配置")
async def update_face(
    face_id: int,
    request: Request,
    face_in: RobotFaceRecognitionUpdate,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    更新人脸识别TTS配置
    """
    try:
        logger.info("更新人脸识别TTS配置接口被调用，ID: %d", face_id)
        face = await RobotConfigService.update_face(db, face_id, face_in)
        response_data = RobotFaceRecognitionResponse.model_validate(face)
        logger.info("更新人脸识别TTS配置接口成功，ID: %d", face_id)
        return response_base.success(data=response_data, msg="更新成功")
    except Exception as e:
        logger.error("更新人脸识别TTS配置接口失败: %s", str(e), exc_info=True)
        raise


@robot_config_router.delete(
    "/face/{face_id}",
    response_model=ResponseModel,
    dependencies=[Depends(require_permission("robot:config:edit"))],
)
@log_operation(module="robot", action="delete", description="删除人脸识别TTS配置")
async def delete_face(
    face_id: int,
    request: Request,
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """
    删除人脸识别TTS配置
    """
    try:
        logger.info("删除人脸识别TTS配置接口被调用，ID: %d", face_id)
        await RobotConfigService.delete_face(db, face_id)
        logger.info("删除人脸识别TTS配置接口成功，ID: %d", face_id)
        return response_base.success(msg="删除成功")
    except Exception as e:
        logger.error("删除人脸识别TTS配置接口失败: %s", str(e), exc_info=True)
        raise
