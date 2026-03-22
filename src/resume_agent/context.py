"""Agent 依赖与工作区：跨 Tool 共享。"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import Resume, ResumeCritique

StatusCallback = Callable[[str, str], None]


# Tool 模式防刷；主路径见 steps（单次评修）
MAX_CRITIQUE_CALLS = 2
MAX_REFINE_CALLS = 1


@dataclass
class ResumeWorkspace:
    jd_text: str
    raw_thoughts: str
    draft: Resume | None = None
    critique: ResumeCritique | None = None
    critique_calls: int = 0
    refine_calls: int = 0
