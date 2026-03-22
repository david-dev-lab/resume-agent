"""统一构造 OpenAI 兼容 Chat 模型（支持 DeepSeek 等）。"""
import os

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


def create_chat_model(model_name: str) -> OpenAIChatModel:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置环境变量 OPENAI_API_KEY（见 .env.example）")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
    return OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(api_key=api_key, base_url=base_url),
    )
