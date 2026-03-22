from __future__ import annotations

from pydantic_ai import Agent, RunContext

from ..context import ResumeWorkspace, StatusCallback
from ..models import Resume
from ..resume_prompts import ResumePrompts
from ..steps import run_draft


def register_draft_tool(
    agent: Agent[ResumeWorkspace, Resume],
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    @agent.tool
    async def draft_resume(ctx: RunContext[ResumeWorkspace]) -> str:
        """根据当前工作区中的 JD 与思绪生成 STAR 简历初稿（结构化）。"""
        await run_draft(ctx.deps, model, prompts, status)
        d = ctx.deps.draft
        assert d is not None
        return (
            f"初稿已写入工作区。match_score={d.match_score}，"
            f"项目条数={len(d.experience)}。"
        )
