#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
机器人参数配置服务
处理语音合成配置与人脸识别TTS配置的业务逻辑
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, Select
from typing import List, Tuple

from database.models.business.robot_voice_config import RobotVoiceConfig
from database.models.business.robot_face_recognition import RobotFaceRecognition
from core.exception.errors import NotFoundError
from app.models.common.page import PageRequest, get_paginated_results
from modules.robot.schemas.robot_config import (
    RobotVoiceConfigSchema,
    RobotFaceRecognitionCreate,
    RobotFaceRecognitionUpdate,
)

logger = logging.getLogger(__name__)


class RobotConfigService:
    """
    机器人参数配置服务类
    """

    # ==================== 语音配置 ====================

    @staticmethod
    async def get_voice_config(db: AsyncSession, robot_id: int) -> RobotVoiceConfig:
        """
        获取指定机器人的语音配置，不存在则返回默认空对象
        """
        try:
            result = await db.execute(
                select(RobotVoiceConfig)
                .where(RobotVoiceConfig.robot_id == robot_id)
                .where(RobotVoiceConfig.deleted_at.is_(None))
            )
            config = result.scalar_one_or_none()
            if not config:
                logger.info("机器人 %d 语音配置不存在，返回默认空对象", robot_id)
                return RobotVoiceConfig(
                    robot_id=robot_id,
                    wake_word="",
                    tts_voice="female",
                    tts_speed=50,
                    tts_volume=80,
                )
            return config
        except Exception as e:
            logger.error("获取语音配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def save_voice_config(
        db: AsyncSession, schema: RobotVoiceConfigSchema
    ) -> RobotVoiceConfig:
        """
        保存语音配置（按 robot_id upsert）
        """
        try:
            logger.info("保存语音配置，请求数据: %s", schema.model_dump(exclude_none=True))

            result = await db.execute(
                select(RobotVoiceConfig)
                .where(RobotVoiceConfig.robot_id == schema.robot_id)
                .where(RobotVoiceConfig.deleted_at.is_(None))
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.wake_word = schema.wake_word
                existing.tts_voice = schema.tts_voice
                existing.tts_speed = schema.tts_speed
                existing.tts_volume = schema.tts_volume
                await db.commit()
                await db.refresh(existing)
                logger.info("更新语音配置成功，ID: %d", existing.id)
                return existing
            else:
                config = RobotVoiceConfig(
                    robot_id=schema.robot_id,
                    wake_word=schema.wake_word,
                    tts_voice=schema.tts_voice,
                    tts_speed=schema.tts_speed,
                    tts_volume=schema.tts_volume,
                )
                db.add(config)
                await db.commit()
                await db.refresh(config)
                logger.info("创建语音配置成功，ID: %d", config.id)
                return config

        except Exception as e:
            await db.rollback()
            logger.error("保存语音配置失败: %s", str(e), exc_info=True)
            raise

    # ==================== 人脸识别TTS配置 ====================

    @staticmethod
    def build_face_query() -> Select:
        """
        构建人脸识别TTS查询对象
        """
        return (
            select(RobotFaceRecognition)
            .where(RobotFaceRecognition.deleted_at.is_(None))
            .order_by(RobotFaceRecognition.id.desc())
        )

    @staticmethod
    async def get_face_list(
        db: AsyncSession, page_params: PageRequest
    ) -> Tuple[List[RobotFaceRecognition], int]:
        """
        获取人脸识别TTS配置列表（分页）
        """
        try:
            query = RobotConfigService.build_face_query()
            page_data = await get_paginated_results(
                db=db,
                page_params=page_params,
                query=query,
                schema=None,
            )
            return page_data.records, page_data.total
        except Exception as e:
            logger.error("获取人脸识别TTS列表失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def get_face(db: AsyncSession, face_id: int) -> RobotFaceRecognition:
        """
        获取单个人脸识别TTS配置
        """
        try:
            result = await db.execute(
                select(RobotFaceRecognition)
                .where(RobotFaceRecognition.id == face_id)
                .where(RobotFaceRecognition.deleted_at.is_(None))
            )
            face = result.scalar_one_or_none()
            if not face:
                raise NotFoundError(msg=f"人脸识别配置 {face_id} 不存在")
            return face
        except NotFoundError:
            raise
        except Exception as e:
            logger.error("获取人脸识别TTS配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def create_face(
        db: AsyncSession, schema: RobotFaceRecognitionCreate
    ) -> RobotFaceRecognition:
        """
        创建人脸识别TTS配置
        """
        try:
            logger.info(
                "创建人脸识别TTS配置，请求数据: %s",
                schema.model_dump(exclude_none=True),
            )
            face = RobotFaceRecognition(
                person_name=schema.person_name,
                photo_url=schema.photo_url,
                broadcast_text=schema.broadcast_text,
            )
            db.add(face)
            await db.commit()
            await db.refresh(face)
            logger.info("创建人脸识别TTS配置成功，ID: %d", face.id)
            return face
        except Exception as e:
            await db.rollback()
            logger.error("创建人脸识别TTS配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def update_face(
        db: AsyncSession, face_id: int, schema: RobotFaceRecognitionUpdate
    ) -> RobotFaceRecognition:
        """
        更新人脸识别TTS配置
        """
        try:
            logger.info(
                "更新人脸识别TTS配置，ID: %d，请求数据: %s",
                face_id,
                schema.model_dump(exclude_none=True),
            )
            face = await RobotConfigService.get_face(db, face_id)
            update_data = schema.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(face, field, value)
            await db.commit()
            await db.refresh(face)
            logger.info("更新人脸识别TTS配置成功，ID: %d", face.id)
            return face
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error("更新人脸识别TTS配置失败: %s", str(e), exc_info=True)
            raise

    @staticmethod
    async def delete_face(db: AsyncSession, face_id: int) -> bool:
        """
        删除人脸识别TTS配置（软删除）
        """
        try:
            logger.info("删除人脸识别TTS配置，ID: %d", face_id)
            face = await RobotConfigService.get_face(db, face_id)
            face.soft_delete()
            await db.commit()
            logger.info("删除人脸识别TTS配置成功，ID: %d", face_id)
            return True
        except NotFoundError:
            raise
        except Exception as e:
            await db.rollback()
            logger.error("删除人脸识别TTS配置失败: %s", str(e), exc_info=True)
            raise
