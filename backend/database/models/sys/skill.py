#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysSkill(Base):
    """
    提示词技能表
    结构化技能包：主指令（Markdown）+ 附属文件（sys_skill_file）；绑定智能体后拼入 system prompt
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="技能名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="技能编码")
    instruction: Mapped[str] = mapped_column(Text, nullable=False, comment="主指令（Markdown 提示词）")
    description: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="技能描述")
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("code", name="uk_sys_skill_code"),
    )


class SysSkillFile(Base):
    """
    技能附属文件表
    随主表整体替换（先删后插），不单独维护；内容为文本，路径经正则校验防穿越
    """

    skill_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属技能 ID（sys_skill.id）"
    )
    path: Mapped[str] = mapped_column(String(128), nullable=False, comment="相对路径（禁绝对路径与 ..）")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="文件文本内容")
    file_size: Mapped[int] = mapped_column(Integer, default=0, comment="文件大小（字节）")

    __table_args__ = (
        UniqueConstraint("skill_id", "path", name="uk_sys_skill_file_path"),
    )
