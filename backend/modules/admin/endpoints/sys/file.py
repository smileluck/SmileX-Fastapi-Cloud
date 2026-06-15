#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件管理接口
"""
import logging
from typing import List
from urllib.parse import quote

from fastapi import APIRouter, Depends, UploadFile, File, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from database.db_manager import get_session
from core.response.response_schema import ResponseModel, ResponsePageModel
from app.models.common.page import PageRequest, get_page_params, get_paginated_results
from modules.admin.deps.auth.user_manager import current_user
from modules.admin.deps.auth.permission import require_permission
from database.models.sys.user import SysUser
from modules.admin.services.sys.file_service import FileService
from modules.admin.schemas.sys.file import (
    SysFileQueryParams,
    SysFileUploadResponse,
    SysFileListResponse,
)
from core.security.oauth.jwt import JWTAuthManager
from core.storage import get_storage_backend

logger = logging.getLogger(__name__)

file_router = APIRouter(
    prefix="/file", tags=["系统管理/文件管理"], dependencies=[Depends(current_user)]
)

# 预览路由独立，不走 router 级别的 current_user 依赖
# 浏览器通过 <img>/<video> src 直接访问，不会携带 Authorization header
preview_router = APIRouter(prefix="/file", tags=["系统管理/文件管理"])


@file_router.post(
    "/upload",
    response_model=ResponseModel[SysFileUploadResponse],
    summary="单文件上传",
    dependencies=[Depends(require_permission("sys:file:upload"))],
)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """上传单个文件"""
    file_data = await file.read()
    sys_file = await FileService.upload_file(
        db=db,
        file_data=file_data,
        original_name=file.filename or "unknown",
        mime_type=file.content_type or "application/octet-stream",
        created_by=user.id,
    )
    await db.commit()
    return ResponseModel(data=SysFileUploadResponse.model_validate(sys_file), msg="上传成功")


@file_router.post(
    "/upload/batch",
    response_model=ResponseModel[List[SysFileUploadResponse]],
    summary="多文件上传",
    dependencies=[Depends(require_permission("sys:file:upload"))],
)
async def upload_files(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_session),
    user: SysUser = Depends(current_user),
):
    """批量上传文件"""
    file_tuples = []
    for f in files:
        data = await f.read()
        file_tuples.append((data, f.filename or "unknown", f.content_type or "application/octet-stream"))

    sys_files = await FileService.upload_files(db=db, files=file_tuples, created_by=user.id)
    await db.commit()
    return ResponseModel(
        data=[SysFileUploadResponse.model_validate(f) for f in sys_files],
        msg=f"成功上传 {len(sys_files)} 个文件",
    )


@file_router.get(
    "/list",
    response_model=ResponsePageModel[SysFileListResponse],
    summary="获取文件列表",
    dependencies=[Depends(require_permission("sys:file:list"))],
)
async def get_file_list(
    page_params: PageRequest = Depends(get_page_params),
    query_params: SysFileQueryParams = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """分页获取文件列表"""
    query_params.page = page_params.page
    query_params.page_size = page_params.page_size

    query = FileService.build_file_query(query_params)
    page_data = await get_paginated_results(
        db=db,
        page_params=page_params,
        query=query,
        schema=SysFileListResponse,
    )
    return ResponsePageModel(data=page_data)


@file_router.get(
    "/{file_id}",
    response_model=ResponseModel[SysFileListResponse],
    summary="获取文件详情",
    dependencies=[Depends(require_permission("sys:file:list"))],
)
async def get_file(
    file_id: int,
    db: AsyncSession = Depends(get_session),
):
    """获取单个文件元数据"""
    sys_file = await FileService.get_file(db, file_id)
    return ResponseModel(data=SysFileListResponse.model_validate(sys_file))


@file_router.get(
    "/{file_id}/download",
    summary="下载文件",
    dependencies=[Depends(require_permission("sys:file:download"))],
)
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_session),
):
    """下载文件"""
    sys_file = await FileService.get_file(db, file_id)
    storage = get_storage_backend()
    full_path = storage.get_full_path(sys_file.file_path)
    encoded_name = quote(sys_file.original_name)
    return FileResponse(
        full_path,
        media_type=sys_file.mime_type,
        filename=sys_file.original_name,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_name}"},
    )


@preview_router.get(
    "/{file_id}/preview",
    summary="在线预览文件",
)
async def preview_file(
    file_id: int,
    token: str = Query(..., description="访问令牌"),
    request: Request = None,
    db: AsyncSession = Depends(get_session),
):
    """在线预览文件（图片/视频），通过 query 参数 token 鉴权，支持 Range 请求"""
    raw_token = token.removeprefix("Bearer ")
    try:
        JWTAuthManager.decode_token(raw_token)
    except Exception:
        return Response(status_code=401, content="Unauthorized")

    sys_file = await FileService.get_file(db, file_id)
    storage = get_storage_backend()
    total_size = storage.file_size(sys_file.file_path)

    range_header = request.headers.get("range") if request else None
    if range_header:
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if range_match[1] else total_size - 1
        end = min(end, total_size - 1)
        return StreamingResponse(
            storage.stream(sys_file.file_path, start, end),
            status_code=206,
            media_type=sys_file.mime_type,
            headers={
                "Content-Range": f"bytes {start}-{end}/{total_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(end - start + 1),
                "Cache-Control": "private, max-age=3600",
            },
        )

    return StreamingResponse(
        storage.stream(sys_file.file_path),
        media_type=sys_file.mime_type,
        headers={
            "Accept-Ranges": "bytes",
            "Content-Length": str(total_size),
            "Cache-Control": "private, max-age=3600",
        },
    )


@file_router.delete(
    "/batch",
    response_model=ResponseModel,
    summary="批量删除文件",
    dependencies=[Depends(require_permission("sys:file:delete"))],
)
async def batch_delete_files(
    file_ids: List[int],
    db: AsyncSession = Depends(get_session),
):
    """批量软删除文件"""
    count = await FileService.batch_delete_files(db, file_ids)
    await db.commit()
    return ResponseModel(msg=f"成功删除 {count} 个文件", data={"delete_count": count})


@file_router.delete(
    "/{file_id}",
    response_model=ResponseModel,
    summary="删除文件",
    dependencies=[Depends(require_permission("sys:file:delete"))],
)
async def delete_file(
    file_id: int,
    db: AsyncSession = Depends(get_session),
):
    """软删除单个文件"""
    await FileService.delete_file(db, file_id)
    await db.commit()
    return ResponseModel(msg="删除文件成功")
