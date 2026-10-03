#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
知识库文本切片器

递归分隔符感知的滑动窗口切片：优先在段落/句子边界断开，块间保留 overlap
字符的上下文。纯函数、无 IO，便于单测与替换（语义切片未来在此扩展）。
"""

# 分隔符层级：从粗到细，最后 "" 兜底硬切
_SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "！", "?", "!", ";", "."]


def _atomic_split(text: str, separators: list[str]) -> list[str]:
    """按分隔符层级递归切成原子段，分隔符保留在段尾"""
    if not separators:
        return [text]
    sep, rest = separators[0], separators[1:]
    segments: list[str] = []
    for seg in text.split(sep):
        if not seg:
            continue
        if rest:
            segments.extend(_atomic_split(seg, rest))
        else:
            segments.append(seg)
    # 分隔符粘回前一段结尾，保持原文可还原
    result: list[str] = []
    for i, seg in enumerate(segments):
        result.append(seg)
        if i < len(segments) - 1:
            result[-1] += sep
    # split 产生的相邻段之间可能跨层级，简单拼回即可；去掉空段
    return [s for s in result if s]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    切片主函数。

    - chunk_size：单块目标长度（字符，软上限，原子段本身不硬切到该值以下）
    - overlap：相邻块重叠长度（字符）
    返回非空切片列表；输入为空返回空列表。
    """
    if not text or not text.strip():
        return []
    chunk_size = max(int(chunk_size), 20)
    overlap = max(0, min(int(overlap), chunk_size // 2))

    atoms = _atomic_split(text, _SEPARATORS)
    chunks: list[str] = []
    buf = ""

    def flush() -> None:
        nonlocal buf
        if buf.strip():
            chunks.append(buf.strip())
        buf = ""

    for atom in atoms:
        # 超长原子段硬切（带 overlap 衔接）
        while len(atom) > chunk_size:
            if buf:
                flush()
            chunks.append(atom[:chunk_size].strip())
            atom = atom[chunk_size - overlap:] if overlap else atom[chunk_size:]
        if not atom:
            continue
        if buf and len(buf) + len(atom) > chunk_size:
            flush()
            if overlap and len(atom) < chunk_size:
                buf = chunks[-1][-overlap:] if chunks else ""
        buf += atom
    flush()
    return [c for c in chunks if c]
