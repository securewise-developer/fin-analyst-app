from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal, Optional
import pandas as pd

SecurityType = Literal["equity", "etf", "fund"]

class MarketDataProvider(ABC):
    @abstractmethod
    def price_history(self, symbol: str, period_days: int = 730, interval: str = "1d") -> pd.DataFrame:
        """Columns: [Open, High, Low, Close, Adj Close, Volume], index=Datetime"""
        raise NotImplementedError

    @abstractmethod
    def fundamentals(self, symbol: str, sec_type: SecurityType = "equity") -> dict:
        """Return a dict of fundamental fields. For ETF/fund, include AUM, expense_ratio, holdings if available."""
        raise NotImplementedError

    @abstractmethod
    def company_profile(self, symbol: str) -> dict:
        """Basic profile/info (sector, industry, country, website)."""
        raise NotImplementedError
