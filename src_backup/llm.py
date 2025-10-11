from __future__ import annotations
from langchain_openai import ChatOpenAI
from src.config import SETTINGS

def build_llm():
    return ChatOpenAI(
        api_key=SETTINGS.openai_api_key,
        model=SETTINGS.openai_model,
        temperature=0.2,
    )
