"""从 YAML 加载 System Prompt（Draft / Critic / Refine / Agent 编排）。"""
import os
from typing import Any

import yaml


class ResumePrompts:
    def __init__(self, prompt_file: str = "default.yaml") -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "prompts", prompt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            self.prompts: dict[str, Any] = yaml.safe_load(f)

    def get_draft_prompt(self) -> str:
        p = self.prompts
        return f"{p['role_definition']}\n{p['core_principles']}\n{p['field_guide']}"

    def get_critic_prompt(self) -> str:
        return self.prompts["critic_instruction"]

    def get_refine_prompt(self) -> str:
        return self.prompts["refine_instruction"]

    def get_orchestrator_instructions(self) -> str:
        return self.prompts["orchestrator_instructions"]
