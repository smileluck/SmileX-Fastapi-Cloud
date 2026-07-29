#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本地文件存储后端
"""
import os
from collections.abc import AsyncGenerator

import aiofiles

from core.exception.errors import NotFoundError
from core.i18n import t
from .base import StorageBackend

_DEFAULT_CHUNK_SIZE = 64 * 1024  # 64 KB


class LocalStorageBackend(StorageBackend):
    """本地文件系统存储"""

    def __init__(self, base_dir: str = "uploads"):
        self._base_dir = base_dir

    def _resolve(self, file_path: str) -> str:
        full_path = os.path.join(self._base_dir, file_path)
        if not os.path.exists(full_path):
            raise NotFoundError(msg=t("storage.file_not_found"))
        return full_path

    async def save(self, file_data: bytes, stored_name: str, path_prefix: str) -> str:
        dir_path = os.path.join(self._base_dir, path_prefix)
        os.makedirs(dir_path, exist_ok=True)

        file_path = f"{path_prefix}/{stored_name}"
        full_path = os.path.join(self._base_dir, path_prefix, stored_name)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_data)

        return file_path

    async def read(self, file_path: str) -> bytes:
        full_path = self._resolve(file_path)
        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete(self, file_path: str) -> bool:
        full_path = os.path.join(self._base_dir, file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def get_full_url(self, file_path: str) -> str:
        return f"/uploads/{file_path}"

    def file_size(self, file_path: str) -> int:
        return os.path.getsize(self._resolve(file_path))

    def get_full_path(self, file_path: str) -> str:
        return self._resolve(file_path)

    async def stream(
        self, file_path: str, start: int = 0, end: int | None = None, chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> AsyncGenerator[bytes, None]:
        full_path = self._resolve(file_path)
        total = os.path.getsize(full_path)
        if end is None:
            end = total - 1

        async with aiofiles.open(full_path, "rb") as f:
            await f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = await f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
