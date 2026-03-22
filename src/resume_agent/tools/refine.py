from __future__ import annotations

from pydantic_ai import Agent, RunContext

from ..context import MAX_REFINE_CALLS, ResumeWorkspace, StatusCallback
from ..models import Resume
from ..resume_prompts import ResumePrompts
from ..steps import run_refine


def register_refine_tool(
    agent: Agent[ResumeWorkspace, Resume],
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    @agent.tool
    async def refine_resume(ctx: RunContext[ResumeWorkspace]) -> str:
        """根据评审意见对工作区简历精修；需已有初稿与评审结果。"""
        if ctx.deps.draft is None:
            return "错误：工作区无初稿，请先 draft_resume。"
        if ctx.deps.critique is None:
            return "错误：尚无评审结果，请先 critique_resume。"
        if ctx.deps.refine_calls >= MAX_REFINE_CALLS:
            return (
                "精修次数已达上限。请直接输出最终 Resume JSON，禁止再调用 refine_resume。"
            )
        await run_refine(ctx.deps, model, prompts, status)
        d = ctx.deps.draft
        assert d is not None
        return (
            f"精修已写回工作区（第{ctx.deps.refine_calls}/{MAX_REFINE_CALLS}轮）。"
            f"match_score={d.match_score}。"
        )
