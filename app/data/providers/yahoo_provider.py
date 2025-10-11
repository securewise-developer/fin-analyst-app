from __future__ import annotations
import yfinance as yf
import pandas as pd
from .base import MarketDataProvider, SecurityType

class YahooProvider(MarketDataProvider):
    def price_history(self, symbol: str, period_days: int = 730, interval: str = "1d") -> pd.DataFrame:
        period = f"{max(1, period_days)}d"
        df = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
        if not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError(f"No price data for {symbol}")
        return df

    def fundamentals(self, symbol: str, sec_type: SecurityType = "equity") -> dict:
        t = yf.Ticker(symbol)
        info = getattr(t, "fast_info", None)
        base_info = {}
        try:
            base_info = t.get_info() if hasattr(t, "get_info") else getattr(t, "info", {})
        except Exception:
            base_info = getattr(t, "info", {}) or {}
        out = {"symbol": symbol, "type": sec_type}
        keys = [
            "trailingPE","forwardPE","priceToBook","enterpriseToEbitda","profitMargins",
            "grossMargins","operatingMargins","returnOnEquity","revenueGrowth","ebitdaMargins",
            "debtToEquity","heldPercentInsiders","heldPercentInstitutions","freeCashflow",
            "totalCash","totalDebt","beta","shortRatio","dividendYield",
        ]
        for k in keys:
            if k in base_info:
                out[k] = base_info.get(k)
        if sec_type != "equity":
            for k in ["category","yield","annualReportExpenseRatio","totalAssets"]:
                if k in base_info:
                    out[k] = base_info.get(k)
        return out

    def company_profile(self, symbol: str) -> dict:
        t = yf.Ticker(symbol)
        try:
            info = t.get_info() if hasattr(t, "get_info") else getattr(t, "info", {})
        except Exception:
            info = getattr(t, "info", {}) or {}
        keys = ["longName","sector","industry","country","website","longBusinessSummary"]
        return {k: info.get(k) for k in keys if k in info}
