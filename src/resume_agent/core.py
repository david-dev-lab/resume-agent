import os
import json
import yaml
import sys
from openai import OpenAI
from dotenv import load_dotenv
from .models import ResumeFull, ResumeCritique

load_dotenv()

class PromptManager:
    """Prompt 仓库管理类"""
    def __init__(self, prompt_file: str = "default.yaml"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "prompts", prompt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            self.prompts = yaml.safe_load(f)

    def get_draft_prompt(self) -> str:
        p = self.prompts
        return f"{p['role_definition']}\n{p['core_principles']}\n{p['field_guide']}"

    def get_critic_prompt(self) -> str:
        return self.prompts['critic_instruction']

    def get_refine_prompt(self) -> str:
        return self.prompts['refine_instruction']

class ResumeAgent:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        )
        self.model = model
        self.prompt_manager = PromptManager()
        
    def _print_status(self, message: str, color: str = "\033[94m"):
        """简洁的彩色状态输出"""
        print(f"{color}{message}\033[0m")
        sys.stdout.flush()

    def _call_llm(self, system_prompt: str, user_prompt: str, response_model):
        try:
            schema_json = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n请严格按此 JSON Schema 输出:\n{schema_json}"},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            raw_content = response.choices[0].message.content
            return response_model.model_validate_json(raw_content)
        except Exception as e:
            self._print_status(f"❌ LLM 调用异常: {str(e)}", "\033[91m")
            raise e

    def tailor(self, raw_thoughts: str, jd_text: str) -> ResumeFull:
        """核心流程：Draft -> Critic -> Refine"""
        
        # --- Phase 1: Draft ---
        self._print_status("✍️  正在起草简历初稿...")
        draft_prompt = self.prompt_manager.get_draft_prompt()
        resume = self._call_llm(
            system_prompt=draft_prompt,
            user_prompt=f"【目标 JD】:\n{jd_text}\n\n【我的乱麻思绪】:\n{raw_thoughts}",
            response_model=ResumeFull
        )
        
        # --- Phase 2: Critique ---
        critique_prompt = self.prompt_manager.get_critic_prompt()
        critique = self._call_llm(
            system_prompt=critique_prompt,
            user_prompt=f"【目标 JD】:\n{jd_text}\n\n【生成的简历】:\n{resume.model_dump_json()}",
            response_model=ResumeCritique
        )
        
        # 仅当质量不佳时才显示评分和意见，避免噪音
        if critique.score < 90:
            self._print_status(f"🧐 简历初评: {critique.score}分", "\033[93m") # 黄色警告
            if critique.needs_revision:
                self._print_status(f"💡 优化建议: {critique.critique[:100]}...", "\033[90m") # 灰色详情

        # --- Phase 3: Refine ---
        if critique.needs_revision and critique.score < 90:
            self._print_status("✨ 正在根据意见精修简历...", "\033[96m") # 青色
            refine_prompt = self.prompt_manager.get_refine_prompt()
            resume = self._call_llm(
                system_prompt=refine_prompt,
                user_prompt=f"【目标 JD】:\n{jd_text}\n\n【Critic 意见】:\n{critique.model_dump_json()}\n\n【简历初稿】:\n{resume.model_dump_json()}",
                response_model=ResumeFull
            )
        else:
            self._print_status("✅ 简历质量达标，直接输出。", "\033[92m") # 绿色

        return resume
