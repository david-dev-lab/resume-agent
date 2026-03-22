from __future__ import annotations

from pydantic_ai import Agent, RunContext

from ..context import (
    MAX_CRITIQUE_CALLS,
    ResumeWorkspace,
    StatusCallback,
)
from ..models import Resume
from ..resume_prompts import ResumePrompts
from ..steps import run_critique
from ..textutil import one_line


def register_critique_tool(
    agent: Agent[ResumeWorkspace, Resume],
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    @agent.tool
    async def critique_resume(ctx: RunContext[ResumeWorkspace]) -> str:
        """对当前工作区中的简历初稿做评审，产出分数与修改建议。"""
        if ctx.deps.draft is None:
            return "错误：工作区尚无初稿，请先调用 draft_resume。"
        if ctx.deps.refine_calls >= 1:
            return (
                "已精修过，禁止再次评审。请直接输出最终 Resume JSON，勿再调用工具。"
            )
        if ctx.deps.critique_calls >= MAX_CRITIQUE_CALLS:
            return "评审次数已达上限。请直接输出最终 Resume，勿再调用工具。"
        await run_critique(ctx.deps, model, prompts, status)
        c = ctx.deps.critique
        assert c is not None
        return (
            f"评审完成。score={c.score}，needs_revision={c.needs_revision}。"
            f" 要点: {one_line(c.critique, 200)}"
        )
