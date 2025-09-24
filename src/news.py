from __future__ import annotations
from typing import List, Dict
import datetime as dt
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def fetch_news(symbol: str, limit: int = 12) -> List[Dict]:
    t = yf.Ticker(symbol)
    items = getattr(t, "news", []) or []
    news = []
    for it in items[:limit]:
        content = it.get("content", "")
        if content:
            title = content.get("title", "")
            summary = content.get("summary", "")
            pub = content.get("pubDate")
            ts = dt.datetime.fromtimestamp(pub) if isinstance(pub, (int, float)) else dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))
            url = content.get("link")

            combined_text = f"{title}. {summary}" if summary else title
            score = analyzer.polarity_scores(combined_text)["compound"] if combined_text else 0.0

            news.append({"title": title,"summary":summary, "time": ts.isoformat() if ts else None, "url": url, "sentiment": score})
    
    print(f"Fetched {len(news)} news items for {symbol}")
    #print("News:", news)
    return news

def summarize_news_sentiment(news: List[Dict]) -> Dict:
    if not news:
        print("No news items to summarize sentiment.")
        return {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
    vals = [n.get("sentiment", 0.0) for n in news]
    
    print(f"News sentiment values: {vals}")
    return {"avg": sum(vals) / len(vals), "min": min(vals), "max": max(vals), "count": len(vals)}
