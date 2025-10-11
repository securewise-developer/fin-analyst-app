"""
Main Financial Analyzer - Core business logic orchestrator.

This module contains the main analyzer that coordinates all financial analysis operations.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from app.config import get_config
from app.core.trading_monitor import TradingMonitor
from app.data.providers.base import MarketDataProvider
from app.data.providers.yahoo_provider import YahooProvider
from app.data.providers.fmp_provider import FMPProvider

logger = logging.getLogger(__name__)


class FinancialAnalyzer:
    """
    Main financial analyzer that orchestrates all analysis operations.
    """
    
    def __init__(self, config=None):
        """Initialize the analyzer with configuration."""
        self.config = config or get_config()
        self.provider = self._choose_provider()
        
    def _choose_provider(self) -> MarketDataProvider:
        """Choose the appropriate data provider based on configuration."""
        if self.config.have_fmp:
            logger.info("Using FMP provider")
            return FMPProvider()
        else:
            logger.info("Using Yahoo Finance provider")
            return YahooProvider()
    
    def analyze_symbols(
        self,
        symbols: List[str],
        detailed: bool = True,
        mode: str = "once",
        output_file: str = "trading_summary.json"
    ) -> str:
        """
        Analyze a list of financial symbols.
        
        Args:
            symbols: List of symbols to analyze
            detailed: Whether to include detailed analysis
            mode: Analysis mode ('once' or 'continuous')
            output_file: Output file path for results
            
        Returns:
            Path to the output file containing results
        """
        logger.info(f"Starting analysis for symbols: {symbols}")
        
        # Create trading monitor
        monitor = TradingMonitor(
            symbols=symbols,
            update_interval=self.config.DEFAULT_UPDATE_INTERVAL
        )
        
        if mode == "once":
            # Run single analysis cycle
            monitor.run_analysis_cycle()
            
            # Get summary
            summary = monitor.get_summary_report()
            
            if detailed:
                # Add detailed analysis
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
            
            # Save results
            output_path = Path(output_file)
            output_path.write_text(
                self._json_dumps_pretty(summary), 
                encoding="utf-8"
            )
            
            logger.info(f"Analysis results saved to {output_path}")
            return str(output_path)
            
        elif mode == "continuous":
            # Start continuous monitoring
            logger.info("Starting continuous monitoring...")
            monitor.start_monitoring()
            return output_file
        
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'once' or 'continuous'")
    
    def analyze_single_symbol(
        self,
        symbol: str,
        security_type: str = "equity",
        lookback_days: Optional[int] = None
    ) -> Dict:
        """
        Analyze a single symbol and return detailed results.
        
        Args:
            symbol: Financial symbol to analyze
            security_type: Type of security ('equity', 'etf', 'fund')
            lookback_days: Number of days to look back for price data
            
        Returns:
            Dictionary containing analysis results
        """
        from app.utils.indicators import compute_indicators, latest_signals
        from app.utils.fundamentals import compute_fundamental_ratios
        from app.services.news_service import NewsService
        from app.core.synthesize import synthesize_report
        from app.core.grading import fundamentals_score, technicals_score, news_score, overall_score, to_grade
        from app.utils.helpers import normalize_price_df, load_text_if_exists
        
        logger.info(f"Analyzing single symbol: {symbol}")
        
        lookback_days = lookback_days or self.config.PRICE_LOOKBACK_DAYS
        
        # 1. Get price data and technical indicators
        px = self.provider.price_history(symbol, period_days=lookback_days)
        px = normalize_price_df(px)
        ind_df = compute_indicators(px)
        tech = latest_signals(ind_df)
        
        # 2. Get fundamentals
        raw_fund = self.provider.fundamentals(symbol, security_type)
        fund = compute_fundamental_ratios(raw_fund, security_type)
        
        # 3. Get news and sentiment
        news_service = NewsService()
        news_items = news_service.fetch_news(symbol, limit=12)
        news_sent = news_service.summarize_news_sentiment(news_items)
        
        # 4. Get company profile
        profile = self.provider.company_profile(symbol)
        
        # 5. Load know-how
        knowhow = load_text_if_exists("knowhow.txt")
        
        # 6. Create payload for LLM synthesis
        payload = {
            "symbol": symbol,
            "security_type": security_type,
            "as_of": datetime.now().isoformat(),
            "profile": profile,
            "fundamentals": fund,
            "technicals": tech,
            "news_items": news_items,
            "news_sentiment": news_sent,
            "knowhow": knowhow,
        }
        
        # 7. Generate LLM report
        report = synthesize_report(payload)
        
        # 8. Calculate scores and grade
        fs = fundamentals_score(fund)
        ts = technicals_score(tech)
        ns = news_score(news_sent)
        final_score = overall_score(fs, ts, ns)
        grade = to_grade(final_score)
        
        # 9. Return complete analysis
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "grade": grade,
            "scores": {
                "fundamentals": fs,
                "technicals": ts,
                "news": ns,
                "overall": final_score
            },
            "report": report.model_dump() if hasattr(report, 'model_dump') else report,
            "raw_data": {
                "fundamentals": fund,
                "technicals": tech,
                "news_sentiment": news_sent,
                "profile": profile
            }
        }
    
    def get_configuration_status(self) -> Dict:
        """Get the current configuration status."""
        return {
            "data_provider": "FMP" if self.config.have_fmp else "Yahoo Finance",
            "openai_configured": bool(self.config.OPENAI_API_KEY),
            "slack_configured": self.config.have_slack,
            "fmp_configured": self.config.have_fmp,
            "price_lookback_days": self.config.PRICE_LOOKBACK_DAYS,
            "update_interval": self.config.DEFAULT_UPDATE_INTERVAL
        }
    
    @staticmethod
    def _json_dumps_pretty(obj) -> str:
        """Pretty print JSON with proper formatting."""
        import json
        return json.dumps(obj, indent=2, ensure_ascii=False)
