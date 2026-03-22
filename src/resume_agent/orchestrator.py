"""
简历编排：默认「确定性」流程 draft→critique→（按需）一次 refine；
仍保留 create_resume_agent 供需要 Tool 式交互时使用。
"""
from __future__ import annotations

import asyncio

from pydantic_ai import Agent

from .context import MAX_LAYOUT_RETRIES, ResumeWorkspace, StatusCallback
from .model_factory import create_chat_model
from .models import LayoutStatus, Resume
from .resume_prompts import ResumePrompts
from .steps import (
    run_critique,
    run_draft,
    run_refine,
    run_refine_layout,
    should_run_refine,
)
from .tools import register_resume_tools
from .tools.layout_validator import validate_html_layout
from .utils import render_html


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
    template_name: str = "swiss_single_column.html",
    max_layout_retries: int = MAX_LAYOUT_RETRIES,
) -> Resume:
    """draft → 评审 → 至多一次精修 → Playwright 感知版面循环直至 PERFECT 或达上限。"""
    status = status or _silent_status
    model = create_chat_model(model_name)
    workspace = ResumeWorkspace(jd_text=jd_text, raw_thoughts=raw_thoughts)
    status(
        "🤖 简历生成（draft → 评审 → 按需精修 → 版面感知循环）...",
        "\033[95m",
    )
    await run_draft(workspace, model, prompts, status)
    await run_critique(workspace, model, prompts, status)
    if should_run_refine(workspace):
        await run_refine(workspace, model, prompts, status)
    assert workspace.draft is not None

    for attempt in range(max_layout_retries):
        html_content = render_html(workspace.draft.model_dump(), template_name)
        status(
            f"📏 版面校验 ({attempt + 1}/{max_layout_retries}) | 模板 {template_name}",
            "\033[90m",
        )
        layout_status, feedback_msg = await validate_html_layout(html_content)
        if layout_status == LayoutStatus.PERFECT:
            status(f"✅ {feedback_msg}", "\033[92m")
            break
        status(f"⚠️ {feedback_msg}", "\033[93m")
        if attempt < max_layout_retries - 1:
            await run_refine_layout(
                workspace, model, prompts, status, layout_status, feedback_msg
            )
        else:
            status("📏 已达版面重试上限，保留当前 JSON。", "\033[93m")

    assert workspace.draft is not None
    return workspace.draft


def build_resume(
    jd_text: str,
    raw_thoughts: str,
    model_name: str,
    prompts: ResumePrompts,
    status: StatusCallback | None = None,
    template_name: str = "swiss_single_column.html",
    max_layout_retries: int = MAX_LAYOUT_RETRIES,
) -> Resume:
    """阻塞运行（内部 asyncio.run）；CLI / 脚本默认用此入口。"""
    return asyncio.run(
        build_resume_async(
            jd_text,
            raw_thoughts,
            model_name,
            prompts,
            status,
            template_name=template_name,
            max_layout_retries=max_layout_retries,
        )
    )
