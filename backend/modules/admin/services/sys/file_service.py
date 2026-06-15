#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件管理服务
"""
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, Select

from database.models.sys.file import SysFile
from core.config import settings
from core.exception.errors import NotFoundError
from core.storage import (
    get_storage_backend,
    validate_file_extension,
    validate_file_size,
    generate_stored_name,
)
from database.utils.timezone import timezone
from modules.admin.schemas.sys.file import SysFileQueryParams

logger = logging.getLogger(__name__)


class FileService:

    @staticmethod
    def build_file_query(query_params: SysFileQueryParams) -> Select:
        """构建文件查询对象"""
        base_query = select(SysFile).where(SysFile.deleted_at.is_(None))

        conditions = []
        if query_params.original_name:
            conditions.append(SysFile.original_name.ilike(f"%{query_params.original_name}%"))
        if query_params.extension:
            conditions.append(SysFile.extension == query_params.extension.lower())
        if query_params.storage_platform:
            conditions.append(SysFile.storage_platform == query_params.storage_platform)

        if conditions:
            base_query = base_query.where(and_(*conditions))

        base_query = base_query.order_by(SysFile.created_at.desc())
        return base_query

    @staticmethod
    async def upload_file(
        db: AsyncSession,
        file_data: bytes,
        original_name: str,
        mime_type: str,
        created_by: int,
    ) -> SysFile:
        """上传单个文件"""
        upload_cfg = settings.UPLOAD_LOCAL
        ext = validate_file_extension(original_name, upload_cfg.ALLOWED_EXTENSIONS)
        validate_file_size(len(file_data), upload_cfg.MAX_FILE_SIZE)

        stored_name = generate_stored_name(ext)
        now = timezone.now()
        path_prefix = f"{now.strftime('%Y/%m/%d')}"

        storage = get_storage_backend()
        file_path = await storage.save(file_data, stored_name, path_prefix)

        sys_file = SysFile(
            original_name=original_name,
            stored_name=stored_name,
            file_path=file_path,
            file_size=len(file_data),
            mime_type=mime_type,
            extension=ext,
            storage_platform=settings.STORAGE.PLATFORM,
            created_by=created_by,
        )
        db.add(sys_file)
        await db.flush()
        await db.refresh(sys_file)

        logger.info(f"文件上传成功: {original_name} -> {file_path}")
        return sys_file

    @staticmethod
    async def upload_files(
        db: AsyncSession,
        files: list[tuple[bytes, str, str]],
        created_by: int,
    ) -> list[SysFile]:
        """批量上传文件，单个失败不影响其他"""
        results = []
        for file_data, filename, mime_type in files:
            try:
                sys_file = await FileService.upload_file(
                    db, file_data, filename, mime_type, created_by
                )
                results.append(sys_file)
            except Exception as e:
                logger.error(f"文件上传失败: {filename}, 错误: {e}")
                raise e
        return results

    @staticmethod
    async def get_file(db: AsyncSession, file_id: int) -> SysFile:
        """获取单个文件"""
        result = await db.execute(
            select(SysFile).where(SysFile.id == file_id, SysFile.deleted_at.is_(None))
        )
        sys_file = result.scalar_one_or_none()
        if not sys_file:
            raise NotFoundError(msg=f"文件 {file_id} 不存在")
        return sys_file

    @staticmethod
    async def get_file_content(db: AsyncSession, file_id: int) -> tuple[SysFile, bytes]:
        """获取文件元数据和二进制内容"""
        sys_file = await FileService.get_file(db, file_id)
        storage = get_storage_backend()
        content = await storage.read(sys_file.file_path)
        return sys_file, content

    @staticmethod
    async def delete_file(db: AsyncSession, file_id: int) -> None:
        """软删除文件"""
        sys_file = await FileService.get_file(db, file_id)
        sys_file.soft_delete()
        await db.flush()

    @staticmethod
    async def batch_delete_files(db: AsyncSession, file_ids: list[int]) -> int:
        """批量软删除文件"""
        count = 0
        for file_id in file_ids:
            try:
                await FileService.delete_file(db, file_id)
                count += 1
            except NotFoundError:
                logger.warning(f"文件不存在，跳过: {file_id}")
            except Exception as e:
                logger.error(f"删除文件失败: {file_id}, 错误: {e}")
                raise e
        return count
