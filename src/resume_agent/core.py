import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .models import ResumeFull, ResumeCritique

load_dotenv()

class ResumeAgent:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        )
        self.model = model
        
    def _call_llm(self, system_prompt: str, user_prompt: str, response_model):
        """通用 LLM 调用封装，支持 Pydantic 结构化输出"""
        try:
            # 获取 Pydantic V2 Schema
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
            print(f"❌ LLM 调用失败 ({response_model.__name__}): {str(e)}")
            if 'raw_content' in locals():
                print(f"AI 原始返回 (前500字符): {raw_content[:500]}...")
            raise e

    def tailor(self, raw_thoughts: str, jd_text: str) -> ResumeFull:
        """核心流程：起草 -> 批评 -> 修正 (Critic-Refine Loop)"""
        
        # --- Phase 1: Draft (起草初稿) ---
        print("🤖 [Writer] 正在基于乱麻思绪起草简历初稿...")
        draft_prompt = f"""
        你是一位拥有20年经验的资深技术招聘官和简历专家。
        你的任务是将用户提供的 [乱麻思绪]（碎片化信息）重写为一份针对 [目标 JD] 的高匹配度简历数据。

        ### 核心原则 (Critical):
        1. **STAR 法则**：所有 [experience.optimized_bullets] 必须严格遵循 Situation(情境) -> Task(任务) -> Action(行动) -> Result(结果) 的结构。
        2. **量化指标**：Result 部分必须包含具体的量化数据（如：性能提升50%，节约成本30%，QPS从1k提升至10k）。如果没有具体数据，请根据上下文合理估算一个保守值或强调定性成果。
        3. **关键词匹配**：仔细分析 [目标 JD] 中的技术关键词，并将其自然地融入到简历的 [skills] 和 [experience] 中。
        4. **格式严格**：教育经历 (education) 必须包含 start_year, end_year, school, degree, major 字段。

        ### 字段填充指南：
        - 如果 [乱麻思绪] 缺少必要信息（如姓名、联系方式），请填入 "[待补充]"。
        - [match_score]：请根据用户经历与 JD 的匹配程度，客观打分 (0-100)。
        """
        resume = self._call_llm(
            system_prompt=draft_prompt,
            user_prompt=f"【目标 JD】:\n{jd_text}\n\n【我的乱麻思绪】:\n{raw_thoughts}",
            response_model=ResumeFull
        )
        
        # --- Phase 2: Critique (自我批评) ---
        print("🤔 [Critic] 正在自我审视简历质量...")
        critique_prompt = f"""
        你是一位极其挑剔的面试官。请基于 [目标 JD] 对这份生成的 [简历 JSON] 进行严格审查。
        
        ### 审查重点：
        1. **量化是否足够？** (有没有具体的数字支撑？)
        2. **关键词是否覆盖？** (JD 里的核心技术栈是否在简历中体现？)
        3. **STAR 法则是否清晰？** (动作和结果是否明确？)
        
        请直接输出批评意见和评分。如果简历质量较差（缺乏量化、遗漏关键技能），请将 `needs_revision` 设为 true。
        """
        critique = self._call_llm(
            system_prompt=critique_prompt,
            user_prompt=f"【目标 JD】:\n{jd_text}\n\n【生成的简历】:\n{resume.model_dump_json()}",
            response_model=ResumeCritique
        )
        
        print(f"📊 [Critic 评分]: {critique.score} / 100")
        print(f"💡 [Critic 意见]: {critique.critique}")
        if critique.missing_keywords:
            print(f"⚠️ [缺失关键词]: {', '.join(critique.missing_keywords)}")

        # --- Phase 3: Refine (按需修正) ---
        if critique.needs_revision and critique.score < 90:
            print("🔧 [Refiner] 检测到质量未达标，正在根据批评意见进行重写...")
            refine_prompt = f"""
            你是一位简历优化专家。
            请根据 [Critic 的批评意见] 和 [目标 JD]，对之前的 [简历初稿] 进行深度优化。
            
            ### 修正指令：
            1. **补充缺失关键词**：将 Critic 指出的缺失关键词自然地融入到项目经历或技能列表中。
            2. **增强量化数据**：针对 Critic 指出的量化不足之处，通过合理推算或强调定性成果来增强说服力。
            3. **保持真实**：不要编造从未发生过的经历，但可以优化表达方式。
            
            请输出一份完美的、修正后的简历 JSON。
            """
            resume = self._call_llm(
                system_prompt=refine_prompt,
                user_prompt=f"【目标 JD】:\n{jd_text}\n\n【Critic 意见】:\n{critique.model_dump_json()}\n\n【简历初稿】:\n{resume.model_dump_json()}",
                response_model=ResumeFull
            )
            print("✅ [Refiner] 简历优化完成！")
        else:
            print("✨ [Resume Agent] 简历质量达标，直接输出！")

        return resume
