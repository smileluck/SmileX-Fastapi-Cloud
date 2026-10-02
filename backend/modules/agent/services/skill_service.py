#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
技能管理服务
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import delete, func, select, Select
from sqlalchemy.ext.asyncio import AsyncSession

from core.exception.errors import CustomError, NotFoundError
from core.i18n import t
from core.response.response_code import CustomErrorCode
from database.models.sys.skill import SysSkill, SysSkillFile
from modules.agent.schemas.skill import SkillCreate, SkillFileItem, SkillQueryParams, SkillUpdate
from modules.agent.utils import archive_and_soft_delete

logger = logging.getLogger(__name__)

# 附属文件路径：相对路径段（字母数字开头，可含 . _ - 与子目录），禁绝对路径与 ..
SKILL_FILE_PATH_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._\-]*(/[a-zA-Z0-9][a-zA-Z0-9._\-]*)*$")
MAX_FILES = 10
MAX_FILE_SIZE = 32 * 1024


@dataclass
class SkillContent:
    """用于 system prompt 拼装的技能内容"""

    name: str
    description: str = ""
    instruction: str = ""
    files: list[SysSkillFile] = field(default_factory=list)


def normalize_files(files: list[SkillFileItem]) -> list[tuple[str, str]]:
    """
    归一化附属文件列表：trim、空 path 丢弃、正则与 .. 校验、上限与查重。
    返回 [(path, content)]；不合法抛 CustomError。
    """
    normalized: list[tuple[str, str]] = []
    seen_paths: set[str] = set()
    for item in files:
        path = (item.path or "").strip()
        content = item.content or ""
        if not path:
            continue
        if not SKILL_FILE_PATH_RE.match(path) or ".." in path:
            raise CustomError(
                error=CustomErrorCode.SKILL_NOT_FOUND,
                msg=t("error.skill.bad_path", path=path),
            )
        if len(content.encode("utf-8")) > MAX_FILE_SIZE:
            raise CustomError(
                error=CustomErrorCode.SKILL_NOT_FOUND,
                msg=t("error.skill.file_too_large", path=path),
            )
        if path in seen_paths:
            raise CustomError(
                error=CustomErrorCode.SKILL_NOT_FOUND,
                msg=t("error.skill.duplicate_path", path=path),
            )
        seen_paths.add(path)
        normalized.append((path, content))

    if len(normalized) > MAX_FILES:
        raise CustomError(
            error=CustomErrorCode.SKILL_NOT_FOUND,
            msg=t("error.skill.too_many_files", max=MAX_FILES),
        )
    return normalized


class SkillService:
    """技能管理服务类"""

    @staticmethod
    def build_skill_query(query_params: SkillQueryParams) -> Select:
        """构建技能分页查询条件"""
        from sqlalchemy import and_

        base_query = select(SysSkill)
        conditions = [SysSkill.deleted_at.is_(None)]
        if query_params.status is not None:
            conditions.append(SysSkill.status == query_params.status)
        if query_params.name:
            conditions.append(SysSkill.name.like(f"%{query_params.name}%"))
        if query_params.code:
            conditions.append(SysSkill.code.like(f"%{query_params.code}%"))
        return base_query.where(and_(*conditions)).order_by(SysSkill.id.desc())

    @staticmethod
    async def get_skill(db: AsyncSession, skill_id: int) -> SysSkill:
        """获取单个技能（含附属文件），不存在则抛 NotFoundError"""
        result = await db.execute(
            select(SysSkill).where(SysSkill.id == skill_id, SysSkill.deleted_at.is_(None))
        )
        skill = result.scalar_one_or_none()
        if not skill:
            raise NotFoundError(msg=t("error.skill.not_found", id=skill_id))
        return skill

    @staticmethod
    async def load_files(db: AsyncSession, skill_id: int) -> list[SysSkillFile]:
        """装载技能附属文件（按路径排序）"""
        result = await db.execute(
            select(SysSkillFile)
            .where(SysSkillFile.skill_id == skill_id)
            .order_by(SysSkillFile.path.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def _ensure_code_unique(db: AsyncSession, code: str, exclude_id: Optional[int] = None) -> None:
        """校验技能编码唯一（排除自身）"""
        from sqlalchemy import and_

        conditions = [SysSkill.code == code, SysSkill.deleted_at.is_(None)]
        if exclude_id is not None:
            conditions.append(SysSkill.id != exclude_id)
        result = await db.execute(select(SysSkill.id).where(and_(*conditions)))
        if result.scalar_one_or_none() is not None:
            raise CustomError(
                error=CustomErrorCode.SKILL_CODE_EXIST,
                msg=t("error.skill.code_exist", code=code),
            )

    @staticmethod
    async def _replace_files(db: AsyncSession, skill_id: int, files: list[tuple[str, str]]) -> None:
        """整体替换附属文件（先物理删后批量插入）"""
        await db.execute(delete(SysSkillFile).where(SysSkillFile.skill_id == skill_id))
        for path, content in files:
            db.add(
                SysSkillFile(
                    skill_id=skill_id,
                    path=path,
                    content=content,
                    file_size=len(content.encode("utf-8")),
                )
            )

    @staticmethod
    async def create_skill(db: AsyncSession, payload: SkillCreate) -> SysSkill:
        """创建技能（主指令 + 附属文件）"""
        logger.info("创建技能，编码: %s", payload.code)
        await SkillService._ensure_code_unique(db, payload.code)
        normalized = normalize_files(payload.files)

        skill = SysSkill(
            name=payload.name,
            code=payload.code,
            description=payload.description,
            instruction=payload.instruction,
            remark=payload.remark,
            status=payload.status,
        )
        db.add(skill)
        await db.flush()
        await SkillService._replace_files(db, skill.id, normalized)
        await db.commit()
        await db.refresh(skill)
        logger.info("创建技能成功，ID: %s", skill.id)
        return skill

    @staticmethod
    async def update_skill(db: AsyncSession, skill_id: int, payload: SkillUpdate) -> SysSkill:
        """更新技能（编码不可改；files None=不变、空数组=清空）"""
        logger.info("更新技能，ID: %s", skill_id)
        skill = await SkillService.get_skill(db, skill_id)

        update_data = payload.model_dump(exclude_unset=True)
        update_data.pop("code", None)
        files = update_data.pop("files", None)
        for key, value in update_data.items():
            if hasattr(skill, key) and value is not None:
                setattr(skill, key, value)
        if files is not None:
            await SkillService._replace_files(db, skill_id, normalize_files(files))

        await db.commit()
        await db.refresh(skill)
        logger.info("更新技能成功，ID: %s", skill_id)
        return skill

    @staticmethod
    async def delete_skill(db: AsyncSession, skill_id: int) -> bool:
        """删除技能；被智能体绑定时拒绝"""
        from modules.agent.services.agent_service import AgentService

        logger.info("删除技能，ID: %s", skill_id)
        skill = await SkillService.get_skill(db, skill_id)

        used = await AgentService.count_agents_using_skill(db, skill.code)
        if used > 0:
            raise CustomError(
                error=CustomErrorCode.SKILL_IN_USE,
                msg=t("error.skill.in_use"),
            )

        # 物理删附属文件 + 软删主表（归档唯一列）
        await db.execute(delete(SysSkillFile).where(SysSkillFile.skill_id == skill_id))
        await archive_and_soft_delete(db, skill, "code")
        logger.info("删除技能成功，ID: %s", skill_id)
        return True

    @staticmethod
    async def check_enabled(db: AsyncSession, code: str) -> SysSkill:
        """校验技能存在且启用（供智能体绑定校验）"""
        result = await db.execute(
            select(SysSkill).where(
                SysSkill.code == code, SysSkill.deleted_at.is_(None)
            )
        )
        skill = result.scalar_one_or_none()
        if skill is None or not skill.status:
            raise CustomError(
                error=CustomErrorCode.SKILL_NOT_FOUND,
                msg=t("error.skill.not_found_or_disabled", code=code),
            )
        return skill

    @staticmethod
    async def get_contents(db: AsyncSession, codes: list[str]) -> list[SkillContent]:
        """
        按绑定顺序返回启用技能的内容（含附属文件）。
        缺失/禁用跳过不阻断对话。
        """
        if not codes:
            return []
        result = await db.execute(
            select(SysSkill).where(
                SysSkill.code.in_(codes),
                SysSkill.deleted_at.is_(None),
                SysSkill.status.is_(True),
            )
        )
        found = {skill.code: skill for skill in result.scalars().all()}
        if not found:
            return []

        files_result = await db.execute(
            select(SysSkillFile).where(SysSkillFile.skill_id.in_([s.id for s in found.values()]))
        )
        files_by_skill: dict[int, list[SysSkillFile]] = {}
        for file in files_result.scalars().all():
            files_by_skill.setdefault(file.skill_id, []).append(file)

        contents: list[SkillContent] = []
        seen: set[str] = set()
        for code in codes:
            skill = found.get(code)
            if skill is None or code in seen:
                continue
            seen.add(code)
            contents.append(
                SkillContent(
                    name=skill.name,
                    description=skill.description or "",
                    instruction=skill.instruction,
                    files=sorted(files_by_skill.get(skill.id, []), key=lambda f: f.path),
                )
            )
        return contents

    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        """技能总数（监控统计用）"""
        result = await db.execute(
            select(func.count()).select_from(SysSkill).where(SysSkill.deleted_at.is_(None))
        )
        return result.scalar() or 0
