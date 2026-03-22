"""
确定性步骤：draft → critique →（按需）一次 refine。
供 build_resume 主路径与 Tool 注册共用，避免外层 LLM 反复评修导致分数螺旋下降。
"""
from __future__ import annotations

from pydantic_ai import Agent

from .context import MAX_REFINE_CALLS, ResumeWorkspace, StatusCallback
from .models import LayoutStatus, Resume, ResumeCritique
from .resume_prompts import ResumePrompts
from .textutil import one_line


def _blend_match_score(before: int, after: int) -> int:
    """精修若以去捏造为主，模型常把分打穿；限制相对初稿跌幅。"""
    return max(after, before - 10)


async def run_draft(
    workspace: ResumeWorkspace,
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    status("✍️  工具 draft_resume：正在起草初稿...", "\033[94m")
    sub = Agent(
        model,
        output_type=Resume,
        instructions=prompts.get_draft_prompt(),
    )
    r = await sub.run(
        "【硬性约束】experience 中每条项目必须对应下方「乱麻思绪」中的事实，禁止新增用户未写的公司/项目。\n\n"
        f"【目标 JD】:\n{workspace.jd_text}\n\n【我的乱麻思绪】:\n{workspace.raw_thoughts}",
    )
    workspace.draft = r.output
    titles = " / ".join(e.project_name for e in r.output.experience[:4])
    status(
        f"📝 初稿 | match {r.output.match_score} | 项目 {len(r.output.experience)} 条 | {titles}",
        "\033[94m",
    )


async def run_critique(
    workspace: ResumeWorkspace,
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    if workspace.draft is None:
        raise RuntimeError("run_critique: draft 为空")
    status("🧐 工具 critique_resume：正在评审...", "\033[93m")
    sub = Agent(
        model,
        output_type=ResumeCritique,
        instructions=prompts.get_critic_prompt(),
    )
    r = await sub.run(
        "【用户原始思绪 — 简历事实仅能来源于此，不得编造】:\n"
        f"{workspace.raw_thoughts}\n\n"
        f"【目标 JD】:\n{workspace.jd_text}\n\n"
        f"【生成的简历】:\n{workspace.draft.model_dump_json()}",
    )
    workspace.critique = r.output
    workspace.critique_calls += 1
    status(
        f"📋 评审 | {r.output.score}分 | 需修改:{r.output.needs_revision} | "
        f"{one_line(r.output.critique, 160)}",
        "\033[93m",
    )


async def run_refine(
    workspace: ResumeWorkspace,
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
) -> None:
    if workspace.draft is None or workspace.critique is None:
        raise RuntimeError("run_refine: 缺少 draft 或 critique")
    before = workspace.draft
    status("✨ 工具 refine_resume：正在精修...", "\033[96m")
    sub = Agent(
        model,
        output_type=Resume,
        instructions=prompts.get_refine_prompt(),
    )
    r = await sub.run(
        "【用户原始思绪 — 仅允许保留、润色其中出现的事实，禁止新增项目/公司】:\n"
        f"{workspace.raw_thoughts}\n\n"
        f"【目标 JD】:\n{workspace.jd_text}\n\n"
        f"【Critic 意见】:\n{workspace.critique.model_dump_json()}\n\n"
        f"【简历初稿】:\n{before.model_dump_json()}",
    )
    blended = _blend_match_score(before.match_score, r.output.match_score)
    out = r.output.model_copy(update={"match_score": blended})
    workspace.draft = out
    workspace.refine_calls += 1
    names_before = [e.project_name for e in before.experience]
    names_after = [e.project_name for e in out.experience]
    status(
        f"🔧 精修 | match {before.match_score}→{out.match_score} | "
        f"项目 {len(before.experience)}→{len(out.experience)} | "
        f"标题: {one_line(' / '.join(names_after), 120)}",
        "\033[96m",
    )
    if set(names_before) != set(names_after):
        status(
            f"   ⚠️ 项目名称相对初稿有变动: {names_before} → {names_after}（应仍来自用户思绪）",
            "\033[96m",
        )


async def run_refine_layout(
    workspace: ResumeWorkspace,
    model,
    prompts: ResumePrompts,
    status: StatusCallback,
    layout_status: LayoutStatus,
    feedback_msg: str,
) -> None:
    if workspace.draft is None:
        raise RuntimeError("run_refine_layout: draft 为空")
    before = workspace.draft
    status(
        f"📐 工具 refine_layout：{layout_status.value} — {one_line(feedback_msg, 100)}",
        "\033[35m",
    )
    sub = Agent(
        model,
        output_type=Resume,
        instructions=prompts.get_layout_refine_prompt(),
    )
    r = await sub.run(
        "【用户原始思绪 — 仅允许保留、润色其中出现的事实，禁止新增项目/公司】:\n"
        f"{workspace.raw_thoughts}\n\n"
        f"【目标 JD】:\n{workspace.jd_text}\n\n"
        f"【版面校验状态】{layout_status.value}\n"
        f"【版面反馈】:\n{feedback_msg}\n\n"
        f"【当前简历 JSON】:\n{before.model_dump_json()}",
    )
    blended = _blend_match_score(before.match_score, r.output.match_score)
    out = r.output.model_copy(update={"match_score": blended})
    workspace.draft = out
    status(
        f"📐 版面精修 | match {before.match_score}→{out.match_score} | {layout_status.value}",
        "\033[35m",
    )


# 与 orchestrator 共用的分支条件（单一精修关口）
REFINE_SCORE_CUTOFF = 86


def should_run_refine(workspace: ResumeWorkspace) -> bool:
    if workspace.critique is None or workspace.refine_calls >= MAX_REFINE_CALLS:
        return False
    cr = workspace.critique
    return bool(cr.needs_revision or cr.score < REFINE_SCORE_CUTOFF)
