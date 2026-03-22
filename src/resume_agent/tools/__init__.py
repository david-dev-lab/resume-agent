"""Pydantic AI 工具注册（按能力拆文件，便于扩展）。"""
from __future__ import annotations

from pydantic_ai import Agent

from ..context import ResumeWorkspace, StatusCallback
from ..models import Resume
from ..resume_prompts import ResumePrompts
from .critique import register_critique_tool
from .draft import register_draft_tool
from .refine import register_refine_tool


def register_resume_tools(
    agent: Agent[ResumeWorkspace, Resume],
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    register_draft_tool(agent, model, prompts, status)
    register_critique_tool(agent, model, prompts, status)
    register_refine_tool(agent, model, prompts, status)
