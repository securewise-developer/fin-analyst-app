from __future__ import annotations
import requests
import pandas as pd
import datetime as dt
from .base import MarketDataProvider, SecurityType
from app.config import get_config
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
_BASE = "https://financialmodelingprep.com/api/v3"

class FMPProvider(MarketDataProvider):

    def clean_item(title, ts, url):
        score = analyzer.polarity_scores(title)["compound"] if title else 0.0
        return {
                "title": title,
                "time": ts.isoformat() if ts else None,
                "url": url,
                "sentiment": score
            }

    def _get(self, path: str, **params):
        config = get_config()
        params["apikey"] = config.FMP_API_KEY
        r = requests.get(f"{_BASE}/{path}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def price_history(self, symbol: str, period_days: int = 730, interval: str = "1d") -> pd.DataFrame:
        data = self._get(f"historical-price-full/{symbol}")
        hist = data.get("historical", [])
        df = pd.DataFrame(hist)
        if df.empty:
            raise ValueError(f"No price data for {symbol}")
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date").sort_index().rename(columns={"close": "Close"," open": "Open", "high": "High", "low": "Low", "volume": "Volume"})
        print(f"Fetched {len(df)} price records for {symbol} over {period_days} days")
        print("Price DataFrame:", df.head())
        return df.tail(period_days)

    def fundamentals(self, symbol: str, sec_type: SecurityType = "equity") -> dict:
        out = {"symbol": symbol, "type": sec_type}
        if sec_type == "equity":
            is_ = self._get(f"income-statement/{symbol}", period="annual")[:4]
            bs_ = self._get(f"balance-sheet-statement/{symbol}", period="annual")[:4]
            cf_ = self._get(f"cash-flow-statement/{symbol}", period="annual")[:4]
            profile = self._get(f"profile/{symbol}")
            out.update({"income": is_, "balance": bs_, "cashflow": cf_, "profile": profile})
        else:
            profile = self._get(f"etf-profile/{symbol}")
            holdings = self._get(f"etf-holdings/{symbol}")
            out.update({"profile": profile, "holdings": holdings})
        return out

    def company_profile(self, symbol: str) -> dict:
        profile = self._get(f"profile/{symbol}")
        return profile[0] if isinstance(profile, list) and profile else profile


    def fetch_stock_news(self, symbol: str, limit: int = 10):
        try:
            url = (f"https://financialmodelingprep.com/api/v3/stock_news?"
                f"tickers={symbol}&page=0&limit={limit}"
                f"&apikey={SETTINGS.fmp_api_key}")
            r = requests.get(url, timeout=10)
            data = r.json()
            news = []
            for it in data[:limit]:
                title = it.get("title") or it.get("headline")
                ts = dt.datetime.fromisoformat(it.get("publishedDate")) if it.get("publishedDate") else None
                url = it.get("url")
                news.append(clean_item(title, ts, url))
            return news
        except Exception:
            return []