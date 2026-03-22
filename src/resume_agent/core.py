import sys

from .models import Resume
from .orchestrator import build_resume
from .resume_prompts import ResumePrompts


class ResumeAgent:
    """对外门面：Pydantic AI 编排（工具化 Draft/Critique/Refine），非固定流水线。"""

    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.prompts = ResumePrompts()

    def _emit_status(self, message: str, color: str = "\033[94m") -> None:
        print(f"{color}{message}\033[0m")
        sys.stdout.flush()

    def build_resume(self, raw_thoughts: str, jd_text: str) -> Resume:
        return build_resume(
            jd_text,
            raw_thoughts,
            self.model,
            self.prompts,
            status=lambda m, c: self._emit_status(m, c),
        )
