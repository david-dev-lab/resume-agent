import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .models import ResumeFull

load_dotenv()

class ResumeAgent:
    def __init__(self, model: str = "deepseek-chat"):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
        )
        self.model = model
        
    def tailor(self, raw_thoughts: str, jd_text: str) -> ResumeFull:
            # 获取 Pydantic V2 Schema
            schema_json = json.dumps(ResumeFull.model_json_schema(), ensure_ascii=False)
            
            system_prompt = f"""
            你是一位拥有20年经验的资深技术招聘官和简历专家。
            你的任务是将用户提供的 [乱麻思绪]（碎片化信息）重写为一份针对 [目标 JD] 的高匹配度简历数据。

            ### 核心原则 (Critical):
            1. **STAR 法则**：所有 [experience.optimized_bullets] 必须严格遵循 Situation(情境) -> Task(任务) -> Action(行动) -> Result(结果) 的结构。
            2. **量化指标**：Result 部分必须包含具体的量化数据（如：性能提升50%，节约成本30%，QPS从1k提升至10k）。如果没有具体数据，请根据上下文合理估算一个保守值或强调定性成果。
            3. **关键词匹配**：仔细分析 [目标 JD] 中的技术关键词，并将其自然地融入到简历的 [skills] 和 [experience] 中。
            4. **格式严格**：教育经历 (education) 必须包含 start_year, end_year, school, degree, major 字段。

            ### 输出要求：
            - **JSON Only**: 仅返回符合以下 Schema 的 JSON 字符串。
            - **No Markdown**: 不要使用 ```json 代码块包裹。
            - **Schema**: 
            {schema_json}

            ### 字段填充指南：
            - 如果 [乱麻思绪] 缺少必要信息（如姓名、联系方式），请填入 "[待补充]"。
            - [match_score]：请根据用户经历与 JD 的匹配程度，客观打分 (0-100)。
            """

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"【目标 JD】:\n{jd_text}\n\n【我的乱麻思绪】:\n{raw_thoughts}"}
                    ],
                    response_format={"type": "json_object"}
                )

                raw_content = response.choices[0].message.content
                # print(f"DEBUG: AI Output -> {raw_content}") # Debug usage

                return ResumeFull.model_validate_json(raw_content)

            except Exception as e:
                print("❌ 简历生成或解析失败。")
                if 'raw_content' in locals():
                    print(f"AI 原始返回 (前500字符): {raw_content[:500]}...")
                raise e
