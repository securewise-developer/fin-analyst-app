from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    fmp_api_key: str = os.getenv("FMP_API_KEY", "")
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "")

    price_lookback_days: int = int(os.getenv("PRICE_LOOKBACK_DAYS", "730"))

    @property
    def have_fmp(self) -> bool:
        return bool(self.fmp_api_key)

SETTINGS = Settings()
