#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步导出任务服务
"""
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.sys.export_task import SysExportTask
from database.models.sys.export_template import SysExportTemplate
from core.config import settings
from core.exception.errors import NotFoundError, CustomError
from core.i18n import t
from core.response import CustomErrorCode
from core.utils.excel_export import build_excel_bytes, ExportColumn
from modules.admin.exports import get_export_config
from modules.admin.schemas.sys.export_task import ExportTaskSubmit

logger = logging.getLogger(__name__)

EXPORT_DIR = os.path.join(settings.UPLOAD_LOCAL.BASE_DIR, "exports")

# 导出任务超时与保留配置
EXPORT_PENDING_TIMEOUT_MINUTES = 30
EXPORT_PROCESSING_TIMEOUT_MINUTES = 30
EXPORT_RETENTION_DAYS = 7


def _ensure_export_dir():
    os.makedirs(EXPORT_DIR, exist_ok=True)


def _resolve_columns_and_config(db: AsyncSession, task: SysExportTask):
    """
    根据任务决定使用模块默认列还是模板自定义列。
    返回 (columns: list[ExportColumn], config: ModuleExportConfig)
    """
    config = get_export_config(task.module_key)

    if task.template_id:
        template = db.get(SysExportTemplate, task.template_id)
        if template:
            col_defs = json.loads(template.columns)
            columns = [
                ExportColumn(
                    field=c["field"],
                    header=c["header"],
                    width=c.get("width", 20),
                )
                for c in col_defs
            ]
            return columns, config

    return config.columns, config


class ExportTaskService:

    @staticmethod
    async def submit_task(
        db: AsyncSession,
        user_id: int,
        submit: ExportTaskSubmit,
    ) -> SysExportTask:
        if not submit.module_key and not submit.template_id:
            raise CustomError(
                msg=t("export_task.module_or_template_required"),
                error=CustomErrorCode.BAD_REQUEST,
            )

        # 优先使用 template_id
        if submit.template_id:
            template = await db.get(SysExportTemplate, submit.template_id)
            if not template:
                raise NotFoundError(msg=t("export_task.template_not_found", id=submit.template_id))
            module_key = template.module_key
            task_name = template.name
            template_id = submit.template_id
        else:
            module_key = submit.module_key
            template_id = None
            config = get_export_config(module_key)
            task_name = config.name

        task = SysExportTask(
            task_name=task_name,
            module_key=module_key,
            template_id=template_id,
            query_params_json=json.dumps(submit.query_params, ensure_ascii=False),
            status="pending",
            created_by=user_id,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)

        return task

    @staticmethod
    async def process_pending_tasks(db: AsyncSession) -> int:
        """扫描并执行 pending 任务，返回处理数量"""
        stmt = (
            select(SysExportTask)
            .where(SysExportTask.status == "pending")
            .order_by(SysExportTask.created_at.asc())
            .limit(10)
        )
        result = await db.execute(stmt)
        tasks = result.scalars().all()

        processed = 0
        for task in tasks:
            try:
                await ExportTaskService._execute_single_task(db, task.id)
                processed += 1
            except Exception as e:
                logger.error(f"处理导出任务 {task.id} 异常: {e}", exc_info=True)
        return processed

    @staticmethod
    async def _execute_single_task(db: AsyncSession, task_id: int):
        """在已有会话中执行单个导出任务（含行锁抢占）"""
        result = await db.execute(
            select(SysExportTask)
            .where(SysExportTask.id == task_id)
            .with_for_update()
        )
        task = result.scalar_one_or_none()
        if not task or task.status != "pending":
            return

        task.status = "processing"
        task.started_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(task)

        try:
            config = get_export_config(task.module_key)
            template = None
            columns = config.columns

            if task.template_id:
                template = await db.get(SysExportTemplate, task.template_id)
                if template:
                    col_defs = json.loads(template.columns)
                    columns = [
                        ExportColumn(
                            field=c["field"],
                            header=c["header"],
                            width=c.get("width", 20),
                            table=c.get("table"),
                        )
                        for c in col_defs
                    ]

            joins_config = None
            if template and template.joins_config:
                joins_config = json.loads(template.joins_config)

            if joins_config:
                rows = await ExportTaskService._execute_join_query(db, columns, joins_config)
            else:
                query_params_dict = json.loads(task.query_params_json)
                params_cls = config.query_params_class
                query_params = params_cls(**query_params_dict) if params_cls else query_params_dict
                query = config.build_query_fn(query_params)
                result = await db.execute(query)
                rows = result.unique().scalars().all()

            excel_bytes = build_excel_bytes(columns, rows, sheet_name=config.name)

            _ensure_export_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{task.id}_{task.module_key}_{timestamp}.xlsx"
            file_path = os.path.join(EXPORT_DIR, filename)

            with open(file_path, "wb") as f:
                f.write(excel_bytes)

            task.status = "completed"
            task.total_rows = len(rows)
            task.file_path = file_path
            task.file_size = len(excel_bytes)
            task.finished_at = datetime.now(timezone.utc)
            await db.commit()

            logger.info(f"导出任务 {task_id} 完成，共 {len(rows)} 行，文件: {filename}")

        except Exception as e:
            logger.error(f"导出任务 {task_id} 失败: {e}", exc_info=True)
            task.status = "failed"
            task.error_message = str(e)
            task.finished_at = datetime.now(timezone.utc)
            await db.commit()

        await ExportTaskService._notify_user(task)

    @staticmethod
    async def _execute_join_query(
        db: AsyncSession,
        columns: list[ExportColumn],
        joins_config: list[dict],
    ) -> list[dict]:
        """
        基于 SQLAlchemy Core 动态构建跨表 JOIN 查询。
        返回 dict 列表，key 格式为 "table_name.field_name"。
        """
        from sqlalchemy import Table, Column as SaColumn
        from database.models.base import Base

        metadata = Base.metadata

        # 确定涉及的表（去重）
        involved_tables = set()
        for col in columns:
            if col.table:
                involved_tables.add(col.table)
        for join_item in joins_config:
            involved_tables.add(join_item["table"])

        # 获取 Table 对象
        tables: dict[str, Table] = {}
        for table_name in involved_tables:
            if table_name not in metadata.tables:
                raise ValueError(t("export_task.table_not_in_metadata", table=table_name))
            tables[table_name] = metadata.tables[table_name]

        # 构建 SELECT 列表
        select_cols = []
        for col in columns:
            tbl_name = col.table
            if tbl_name and tbl_name in tables:
                tbl = tables[tbl_name]
                if col.field in tbl.c:
                    select_cols.append(tbl.c[col.field].label(f"{tbl_name}.{col.field}"))
                else:
                    raise ValueError(t("export_task.column_not_found", table=tbl_name, column=col.field))

        # 从第一个列的表作为主表开始构建查询
        base_table_name = columns[0].table or list(involved_tables)[0]
        base_table = tables[base_table_name]
        query = select(*select_cols)

        # 添加 JOIN
        join_type_map = {"left": "left", "inner": "inner", "right": "right"}
        for join_item in joins_config:
            join_table = tables[join_item["table"]]
            join_type = join_type_map.get(join_item.get("type", "left"), "left")

            # 构建 ON 条件
            on_conditions = []
            for on_pair in join_item["on"]:
                left_ref = on_pair["left"]   # e.g. "sys_user.id"
                right_ref = on_pair["right"]  # e.g. "sys_user_role.user_id"

                left_table_name, left_field = left_ref.rsplit(".", 1)
                right_table_name, right_field = right_ref.rsplit(".", 1)

                left_col = tables[left_table_name].c[left_field]
                right_col = tables[right_table_name].c[right_field]
                on_conditions.append(left_col == right_col)

            on_clause = on_conditions[0]
            for cond in on_conditions[1:]:
                on_clause = on_clause & cond

            if join_type == "left":
                query = query.join(join_table, on_clause, isouter=True)
            elif join_type == "right":
                query = query.join(join_table, on_clause, full=False)
                # SQLAlchemy Core 不直接支持 RIGHT JOIN，用 select_from 反转
            else:
                query = query.join(join_table, on_clause)

        result = await db.execute(query)
        raw_rows = result.all()

        # 转换为 dict 列表
        row_dicts = []
        for row in raw_rows:
            row_dict = {}
            for idx, col in enumerate(row._fields):
                row_dict[col] = row[idx]
            row_dicts.append(row_dict)

        return row_dicts

    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> SysExportTask:
        result = await db.execute(
            select(SysExportTask).where(SysExportTask.id == task_id)
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundError(msg=t("export_task.not_found", id=task_id))
        return task

    @staticmethod
    async def get_task_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        status: str | None = None,
    ) -> Tuple[List[SysExportTask], int]:
        base_query = select(SysExportTask).where(
            SysExportTask.created_by == user_id
        ).order_by(SysExportTask.created_at.desc())

        if status:
            base_query = base_query.where(SysExportTask.status == status)

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        paginated = base_query.offset(offset).limit(page_size)
        result = await db.execute(paginated)
        tasks = result.scalars().all()

        return tasks, total

    @staticmethod
    async def download_file(db: AsyncSession, task_id: int) -> str:
        task = await ExportTaskService.get_task(db, task_id)
        if task.status != "completed":
            raise CustomError(
                msg=t("export_task.cannot_download_status", status=task.status),
                error=CustomErrorCode.BAD_REQUEST,
            )
        if not task.file_path or not os.path.exists(task.file_path):
            raise NotFoundError(msg=t("export_task.file_not_found"))
        return task.file_path

    @staticmethod
    async def timeout_and_cleanup_tasks(db: AsyncSession) -> dict:
        """标记超时任务为失败并清理过期任务，返回统计信息"""
        now = datetime.now(timezone.utc)
        pending_timeout = now - timedelta(minutes=EXPORT_PENDING_TIMEOUT_MINUTES)
        processing_timeout = now - timedelta(minutes=EXPORT_PROCESSING_TIMEOUT_MINUTES)
        retention_cutoff = now - timedelta(days=EXPORT_RETENTION_DAYS)

        timed_out = 0
        cleaned = 0

        # pending 超时
        result = await db.execute(
            select(SysExportTask).where(
                SysExportTask.status == "pending",
                SysExportTask.created_at < pending_timeout,
            )
        )
        for task in result.scalars().all():
            task.status = "failed"
            task.error_message = "任务排队超时，已失效"
            task.finished_at = now
            timed_out += 1

        # processing 超时
        result = await db.execute(
            select(SysExportTask).where(
                SysExportTask.status == "processing",
                SysExportTask.started_at < processing_timeout,
            )
        )
        for task in result.scalars().all():
            if task.file_path and os.path.exists(task.file_path):
                os.remove(task.file_path)
            task.status = "failed"
            task.error_message = "任务执行超时，已失效"
            task.finished_at = now
            timed_out += 1

        await db.commit()

        # 清理过期 completed/failed
        stmt = select(SysExportTask).where(
            SysExportTask.created_at < retention_cutoff,
            SysExportTask.status.in_(["completed", "failed"]),
        )
        result = await db.execute(stmt)
        old_tasks = result.scalars().all()

        for task in old_tasks:
            if task.file_path and os.path.exists(task.file_path):
                os.remove(task.file_path)
            cleaned += 1

        if old_tasks:
            delete_stmt = delete(SysExportTask).where(
                SysExportTask.id.in_([t.id for t in old_tasks])
            )
            await db.execute(delete_stmt)
            await db.commit()

        return {"timed_out": timed_out, "cleaned": cleaned}

    @staticmethod
    async def cleanup_old_tasks(db: AsyncSession, days: int = 7) -> int:
        """手动清理过期导出任务（保留兼容旧接口）"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=days)
        stmt = select(SysExportTask).where(
            SysExportTask.created_at < cutoff,
            SysExportTask.status.in_(["completed", "failed"]),
        )
        result = await db.execute(stmt)
        old_tasks = result.scalars().all()

        cleaned = 0
        for task in old_tasks:
            if task.file_path and os.path.exists(task.file_path):
                os.remove(task.file_path)
            cleaned += 1

        if old_tasks:
            delete_stmt = delete(SysExportTask).where(
                SysExportTask.id.in_([t.id for t in old_tasks])
            )
            await db.execute(delete_stmt)
            await db.commit()
        return cleaned

    @staticmethod
    async def _notify_user(task: SysExportTask) -> None:
        """通过 WebSocket 通知任务创建者状态变更"""
        try:
            from core.websocket import get_connection_manager

            manager = get_connection_manager()
            if not manager:
                return

            await manager.send_to_user(
                task.created_by,
                {
                    "type": "export_task",
                    "task_id": task.id,
                    "status": task.status,
                    "task_name": task.task_name,
                    "error_message": task.error_message,
                },
            )
        except Exception:
            logger.exception(f"推送导出任务 {task.id} 状态失败")
