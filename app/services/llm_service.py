from __future__ import annotations
from langchain_openai import ChatOpenAI
from app.config import get_config

def build_llm():
    config = get_config()
    return ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        temperature=0.2,
    )
