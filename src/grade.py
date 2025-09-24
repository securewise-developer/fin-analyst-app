from __future__ import annotations
from typing import Dict
from src.utils import load_yaml

RUBRIC = load_yaml("rubrics/grade_config_shortterm.yaml")

def clamp(x: float, lo=0.0, hi=1.0) -> float:
    return max(lo, min(hi, x))

def fundamentals_score(fund: Dict) -> float:
    w = RUBRIC.get("fundamentals", {})
    score = 0.5
    gm = fund.get("gross_margin")
    if gm is not None:
        score += 0.2 if gm >= w.get("min_gross_margin", 0.25) else -0.2
    rev = fund.get("rev_growth_yoy")
    if rev is not None:
        score += 0.1 if rev >= w.get("min_rev_cagr_3y", 0.05) else -0.1
    dte = fund.get("debt_to_equity")
    if dte is not None:
        score += 0.1 if dte <= w.get("max_net_debt_to_ebitda", 3.0) else -0.1
    return clamp(score)

def technicals_score(tech: Dict) -> float:
    w = RUBRIC.get("technicals", {})
    score = 0.5
    rsi = tech.get("rsi14")
    if rsi is not None:
        if rsi < w.get("rsi_oversold", 30):
            score += 0.1
        elif rsi > w.get("rsi_overbought", 70):
            score -= 0.1
    if tech.get("above_sma200"):
        score += w.get("above_sma200_bonus", 0.1)
    if tech.get("macd_bull"):
        score += w.get("macd_signal_bias", 0.05)
    return clamp(score)

def news_score(news_sent: Dict) -> float:
    base = 0.5 + 0.3 * (news_sent.get("avg", 0.0))  # VADER -1..1 → ~0.2 aralık
    return clamp(base)

def overall_score(fund_s: float, tech_s: float, news_s: float) -> float:
    ww = RUBRIC.get("weights", {"fundamentals": 0.5, "technicals": 0.3, "news": 0.2})
    return clamp(
        fund_s * ww.get("fundamentals", 0.5)
        + tech_s * ww.get("technicals", 0.3)
        + news_s * ww.get("news", 0.2)
    )

def to_grade(score: float) -> str:
    if score >= 0.8:
        return "A"
    if score >= 0.65:
        return "B"
    if score >= 0.5:
        return "C"
    if score >= 0.35:
        return "D"
    return "F"
