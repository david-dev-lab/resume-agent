"""
简历编排：默认「确定性」流程 draft→critique→（按需）一次 refine；
仍保留 create_resume_agent 供需要 Tool 式交互时使用。
"""
from __future__ import annotations

import asyncio

from pydantic_ai import Agent

from .context import ResumeWorkspace, StatusCallback
from .model_factory import create_chat_model
from .models import Resume
from .resume_prompts import ResumePrompts
from .steps import run_critique, run_draft, run_refine, should_run_refine
from .tools import register_resume_tools


def _silent_status(msg: str, color: str = "") -> None:
    pass


def create_resume_agent(
    model_name: str,
    prompts: ResumePrompts,
    status: StatusCallback | None = None,
) -> Agent[ResumeWorkspace, Resume]:
    status = status or _silent_status
    model = create_chat_model(model_name)

    agent = Agent(
        model,
        deps_type=ResumeWorkspace,
        output_type=Resume,
        instructions=prompts.get_orchestrator_instructions(),
    )
    register_resume_tools(agent, model, prompts, status)
    return agent


async def build_resume_async(
    jd_text: str,
    raw_thoughts: str,
    model_name: str,
    prompts: ResumePrompts,
    status: StatusCallback | None = None,
) -> Resume:
    """draft → 评审 → 至多一次精修；不再经外层 LLM 反复调度工具。"""
    status = status or _silent_status
    model = create_chat_model(model_name)
    workspace = ResumeWorkspace(jd_text=jd_text, raw_thoughts=raw_thoughts)
    status(
        "🤖 简历生成（draft → 评审 → 按需一次精修）...",
        "\033[95m",
    )
    await run_draft(workspace, model, prompts, status)
    await run_critique(workspace, model, prompts, status)
    if should_run_refine(workspace):
        await run_refine(workspace, model, prompts, status)
    assert workspace.draft is not None
    return workspace.draft


def build_resume(
    jd_text: str,
    raw_thoughts: str,
    model_name: str,
    prompts: ResumePrompts,
    status: StatusCallback | None = None,
) -> Resume:
    """阻塞运行（内部 asyncio.run）；CLI / 脚本默认用此入口。"""
    return asyncio.run(build_resume_async(jd_text, raw_thoughts, model_name, prompts, status))
