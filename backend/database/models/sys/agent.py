#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class SysAgentProvider(Base):
    """
    AI 模型供应商配置表
    api_key 仅存 AES-GCM 密文，接口永不回显明文；base_url 兼容 OpenAI 协议
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="供应商名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="供应商编码")
    base_url: Mapped[str] = mapped_column(String(255), nullable=False, comment="OpenAI 兼容 API 基础地址")
    api_key_enc: Mapped[Optional[str]] = mapped_column(
        String(512), default=None, comment="API Key 密文（AES-256-GCM base64）"
    )
    api_key_mask: Mapped[Optional[str]] = mapped_column(
        String(32), default=None, comment="API Key 掩码（仅展示用）"
    )
    protocol: Mapped[str] = mapped_column(String(32), default="openai", comment="调用协议，预留多协议扩展")
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("code", name="uk_sys_agent_provider_code"),
    )


class SysAgentModel(Base):
    """
    供应商下的模型配置表
    """

    provider_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属供应商 ID（sys_agent_provider.id）"
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="模型名称（上游模型 ID）")
    model_type: Mapped[str] = mapped_column(
        String(32), default="chat", comment="模型类型：chat-对话/embedding-向量化/rerank-重排"
    )
    display_name: Mapped[Optional[str]] = mapped_column(String(64), default=None, comment="展示名称")
    context_window: Mapped[int] = mapped_column(Integer, default=0, comment="上下文窗口（token，0=未知）")
    max_output: Mapped[int] = mapped_column(Integer, default=0, comment="单次最大输出（token，0=上游默认）")
    supports_tools: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否支持工具调用")
    input_price: Mapped[float] = mapped_column(Float, default=0.0, comment="每千 token 输入单价（0=未设置）")
    output_price: Mapped[float] = mapped_column(Float, default=0.0, comment="每千 token 输出单价（0=未设置）")
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("provider_id", "name", name="uk_sys_agent_model_provider_name"),
    )


class SysAgent(Base):
    """
    智能体配置表
    tools 为 JSON 文本数组，元素为内置工具名或 "mcp:<server_code>:<tool_name>"；skills 为技能编码数组
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="智能体名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="智能体编码")
    model_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="绑定模型 ID（sys_agent_model.id，逻辑引用）",
    )
    system_prompt: Mapped[Optional[str]] = mapped_column(Text, default=None, comment="系统提示词")
    temperature: Mapped[float] = mapped_column(Float, default=0.0, comment="温度（0-2，0=未设置）")
    top_p: Mapped[float] = mapped_column(Float, default=0.0, comment="Top-P（0-1，0=未设置）")
    max_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="单次最大输出（token，0=上游默认）")
    tools: Mapped[Optional[str]] = mapped_column(String(512), default=None, comment="绑定的工具名 JSON 数组文本")
    skills: Mapped[Optional[str]] = mapped_column(String(512), default=None, comment="绑定的技能编码 JSON 数组文本")
    knowledge_ids: Mapped[Optional[str]] = mapped_column(
        String(512), default=None, comment="绑定的知识库 ID JSON 数组文本"
    )
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("code", name="uk_sys_agent_code"),
        # 显式命名避免与 sys_agent_model 表的 ix_sys_agent_model_id 索引同名冲突
        Index("ix_sys_agent_model_ref", "model_id"),
    )


class SysAgentConversation(Base):
    """
    智能体会话表
    归属用户本人；agent_name 冗余存储，Agent 删除后历史仍可读
    """

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="归属用户 ID")
    agent_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="关联智能体 ID（逻辑引用，不级联）"
    )
    agent_name: Mapped[str] = mapped_column(String(20), default="", comment="智能体名称冗余（Agent 删除后历史可读）")
    title: Mapped[str] = mapped_column(String(64), default="", comment="会话标题")

    last_msg_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), init=False, default=None, comment="最近消息时间"
    )


class SysAgentConversationMsg(Base):
    """
    会话消息表
    追加流水；随会话物理删除，不提供单独修改
    """

    conversation_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属会话 ID（sys_agent_conversation.id）"
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False, comment="消息角色：user/assistant")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="assistant 消息的 usage.total_tokens")


class SysAgentUsageLog(Base):
    """
    智能体 token 用量计量流水表
    每次对话一条（含无状态调试）；按保留期由定时任务清理
    """

    agent_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="智能体 ID")
    model_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="模型 ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="用户 ID")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="输入 token 数")
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="输出 token 数")
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, comment="总 token 数")
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, comment="耗时（毫秒）")


# 知识库文档处理状态（sys_agent_knowledge_doc.status）
DOC_STATUS_PENDING = 0
DOC_STATUS_PROCESSING = 1
DOC_STATUS_COMPLETED = 2
DOC_STATUS_FAILED = 3


class SysAgentKnowledge(Base):
    """
    智能体知识库表
    向量存储于 Qdrant（每库一个 collection kb_{id}）；embedding_model_id 创建后锁定，换模型走全量重建
    """

    name: Mapped[str] = mapped_column(String(20), nullable=False, comment="知识库名称")
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True, comment="知识库编码")
    embedding_model_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="向量化模型 ID（sys_agent_model.id，须为 model_type=embedding）",
    )
    description: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="知识库描述")
    doc_count: Mapped[int] = mapped_column(Integer, default=0, comment="文档数量（冗余计数）")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="切片数量（冗余计数）")
    remark: Mapped[Optional[str]] = mapped_column(String(200), default=None, comment="备注")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态：True-启用，False-禁用")

    __table_args__ = (
        UniqueConstraint("code", name="uk_sys_agent_knowledge_code"),
    )


class SysAgentKnowledgeDoc(Base):
    """
    知识库文档表
    上传时同步提取全文存 content（重切片的源）；切片/向量化在后台任务完成，status 为状态机
    """

    knowledge_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属知识库 ID（sys_agent_knowledge.id）"
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="文件名")
    file_type: Mapped[str] = mapped_column(String(16), default="", comment="文件扩展名（小写，无点）")
    file_size: Mapped[int] = mapped_column(Integer, default=0, comment="原始文件大小（字节）")
    content_hash: Mapped[str] = mapped_column(String(64), default="", comment="内容 SHA-256（同库去重）")
    content: Mapped[Optional[str]] = mapped_column(Text, default=None, comment="提取后的全文文本")
    char_count: Mapped[int] = mapped_column(Integer, default=0, comment="全文长度（字符）")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="切片数量")
    status: Mapped[int] = mapped_column(
        Integer, default=DOC_STATUS_PENDING, comment="处理状态：0-待处理 1-处理中 2-完成 3-失败"
    )
    error_msg: Mapped[Optional[str]] = mapped_column(String(500), default=None, comment="失败原因")

    __table_args__ = (
        Index("ix_sys_agent_knowledge_doc_kb_hash", "knowledge_id", "content_hash"),
    )


class SysAgentKnowledgeChunk(Base):
    """
    知识库切片表（元数据账目）
    向量与切片正文存 Qdrant（point id = 本表 id，payload 含 doc_id/content）；对账以本表数量为准
    """

    knowledge_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属知识库 ID"
    )
    doc_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True, comment="所属文档 ID（sys_agent_knowledge_doc.id）"
    )
    chunk_index: Mapped[int] = mapped_column(Integer, default=0, comment="切片序号（文档内从 0 递增）")
    char_count: Mapped[int] = mapped_column(Integer, default=0, comment="切片长度（字符）")
