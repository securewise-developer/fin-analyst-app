from __future__ import annotations
import argparse
from ast import List
import datetime as dt
from pathlib import Path
from typing import Literal

from .config import SETTINGS
from .data_providers.yahoo_provider import YahooProvider
from .data_providers.fmp_provider import FMPProvider
from .indicators import compute_indicators, latest_signals
from .fundamentals import compute_fundamental_ratios
from .news import fetch_news, summarize_news_sentiment
from .synthesize import synthesize_report
from .utils import load_text_if_exists, normalize_price_df
from .grade import fundamentals_score, technicals_score, news_score, overall_score, to_grade
from .trading_monitor import TradingMonitor
import logging

SecurityType = Literal["equity", "etf", "fund"]

def choose_provider():
    if SETTINGS.have_fmp:
        return FMPProvider()
    return YahooProvider()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--type", default="equity", choices=["equity", "etf", "fund"])
    ap.add_argument("--lookback", type=int, default=SETTINGS.price_lookback_days)
    ap.add_argument("--out", default="report.json")
    args = ap.parse_args()

    provider = choose_provider()

    # 1) Prices & technicals
    px = provider.price_history(args.symbol, period_days=args.lookback)
    px = normalize_price_df(px)
    ind_df = compute_indicators(px)
    tech = latest_signals(ind_df)

    # 2) Fundamentals
    raw_fund = provider.fundamentals(args.symbol, args.type)
    fund = compute_fundamental_ratios(raw_fund, args.type)

    # 3) News
    # news_items = provider.fetch_stock_news(args.symbol, limit=12)
    news_items = fetch_news(args.symbol, limit=12)
    news_sent = summarize_news_sentiment(news_items)

    # 4) Profile & know-how
    profile = provider.company_profile(args.symbol)
    knowhow = load_text_if_exists("knowhow.txt")

    # 5) LLM synthesis (structured JSON)
    payload = dict(
        symbol=args.symbol,
        security_type=args.type,
        as_of=dt.datetime.utcnow().isoformat(),
        profile=profile,
        fundamentals=fund,
        technicals=tech,
        news_items=news_items,
        news_sentiment=news_sent,
        knowhow=knowhow,
    )
    report = synthesize_report(payload)

    # 6) Save outputs
    out_path = Path(args.out)
    out_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    print(f"Saved → {out_path}")

    fs = fundamentals_score(fund)
    ts = technicals_score(tech)
    ns = news_score(news_sent)
    final = overall_score(fs, ts, ns)
    letter = to_grade(final)

    score_payload = {"fundamentals": fs, "technicals": ts, "news": ns, "overall": final, "grade": letter}
    score_path = out_path.with_name(out_path.stem + "_score.json")
    score_path.write_text(json_dumps_pretty(score_payload), encoding="utf-8")

    print("Scoring:", score_payload)

def trading_monitor_main():
    """Trading monitor için ana fonksiyon"""
    ap = argparse.ArgumentParser(description="Günlük trading monitoring sistemi")
    ap.add_argument("--symbols", nargs="+", required=True, help="İzlenecek semboller")
    ap.add_argument("--interval", type=int, default=15, help="Güncelleme aralığı (dakika)")
    ap.add_argument("--mode", choices=["once", "continuous"], default="once", help="Çalışma modu")
    ap.add_argument("--out", default="trading_summary.json", help="Özet rapor dosyası")
    ap.add_argument("--detailed", action="store_true", help="Detaylı rapor oluştur")
    
    args = ap.parse_args()
    
    run_trading_monitor(
        symbols=args.symbols,
        interval=args.interval,
        mode=args.mode,
        out=args.out,
        detailed=args.detailed,
    )


def json_dumps_pretty(obj) -> str:
    import json
    return json.dumps(obj, indent=2, ensure_ascii=False)

def run_trading_monitor(
    symbols: List[str],
    interval: int = 1,
    mode: str = "once",
    out: str = "trading_summary.json",
    detailed: bool = False):
    """
    Core function that runs the trading monitor logic.
    Can be called directly from code OR via trading_monitor_main().
    """
    monitor = TradingMonitor(symbols, interval)

    if mode == "once":
        logging.info("Running single analysis cycle...")
        monitor.run_analysis_cycle()

        # Build summary
        summary = monitor.get_summary_report()

        if detailed:
            detailed_summary = {
                **summary,
                "detailed_analysis": {},
            }
            for symbol in symbols:
                if symbol in monitor.last_analysis:
                    analysis = monitor.last_analysis[symbol]
                    detailed_summary["detailed_analysis"][symbol] = {
                        "grade": analysis.get("grade"),
                        "score": analysis.get("overall_score"),
                        "trading_signal": analysis.get("trading_signal", {}),
                        "risk_factors": analysis.get("risk_factors", []),
                        "catalyst_events": analysis.get("catalyst_events", []),
                        "overall_analysis": analysis.get("overall_analysis"),
                        "key_drivers": analysis.get("key_drivers", []),
                        "contrarian_views": analysis.get("contrarian_views"),
                    }

            summary = detailed_summary

        out_path = Path(out)
        out_path.write_text(json_dumps_pretty(summary), encoding="utf-8")
        logging.info(f"Summary saved → {out_path}")

        if detailed:
            _print_detailed_report(symbols, monitor)

    elif mode == "continuous":
        logging.info("Starting continuous monitoring...")
        monitor.start_monitoring()

def _print_detailed_report(symbols, monitor):
    """Helper to pretty-print detailed results to console (optional for CLI)."""
    print("\n" + "=" * 50)
    print("DETAYLI TRADING ANALİZİ")
    print("=" * 50)
    for symbol in symbols:
        if symbol in monitor.last_analysis:
            analysis = monitor.last_analysis[symbol]
            print(f"\n📊 {symbol} ANALİZİ:")
            print(f"  Grade: {analysis.get('grade', 'N/A')}")
            print(f"  Score: {analysis.get('overall_score', 'N/A'):.2f}")

            signal = analysis.get("trading_signal", {})
            if signal:
                print(f"  🎯 Trading Signal: {signal.get('action', 'N/A')}")
                print(f"  🎯 Confidence: {signal.get('confidence', 'N/A'):.2f}")
                print(f"  🎯 Time Horizon: {signal.get('time_horizon', 'N/A')}")
                if signal.get("fundamental_reasons"):
                    print("  📈 Fundamental Reasons:")
                    for r in signal["fundamental_reasons"]:
                        print(f"    • {r}")
                if signal.get("technical_reasons"):
                    print("  📊 Technical Reasons:")
                    for r in signal["technical_reasons"]:
                        print(f"    • {r}")
                if signal.get("news_catalysts"):
                    print("  📰 News Catalysts:")
                    for c in signal["news_catalysts"]:
                        print(f"    • {c}")
                if signal.get("market_timing"):
                    print(f"  ⏰ Market Timing: {signal['market_timing']}")

            if analysis.get("risk_factors"):
                print("  ⚠️ Risk Factors:")
                for r in analysis["risk_factors"]:
                    print(f"    • {r}")

            if analysis.get("key_drivers"):
                print("  🚀 Key Drivers:")
                for d in analysis["key_drivers"]:
                    print(f"    • {d}")

            if analysis.get("contrarian_views"):
                print(f"  🤔 Contrarian Views: {analysis['contrarian_views']}")

if __name__ == "__main__":
    # Eğer trading monitor komutu kullanılıyorsa
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        sys.argv.pop(1)  # "monitor" komutunu kaldır
        trading_monitor_main(symbols=List.empty)
    else:
        main()
