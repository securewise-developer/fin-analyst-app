from __future__ import annotations
import time
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import json

from app.utils.helpers import (
    get_market_conditions,
    generate_trading_context,
    create_trading_alert,
    save_trading_alerts,
    get_active_trading_signals,
    load_text_if_exists,
    normalize_price_df
)
from app.core.synthesize import synthesize_report
from app.core.grading import to_grade, overall_score

class TradingMonitor:
    """Günlük trading izleme ve bildirim sistemi"""
    
    def __init__(self, symbols: List[str], update_interval: int = 15):
        self.symbols = symbols
        self.update_interval = update_interval  # dakika
        self.alerts_history = []
        self.last_analysis = {}
        
    def analyze_symbol(self, symbol: str) -> Dict:
        """Tek bir sembol için analiz yapar"""
        try:
            # Gerçek veri toplama
            from app.data.providers.yahoo_provider import YahooProvider
            from app.utils.indicators import compute_indicators, latest_signals
            from app.utils.fundamentals import compute_fundamental_ratios
            from app.services.news_service import fetch_news, summarize_news_sentiment
            
            provider = YahooProvider()
            
            # 1. Gerçek fiyat verileri
            px = provider.price_history(symbol, period_days=252)  # 1 yıl
            if px.empty:
                raise Exception(f"Fiyat verisi alınamadı: {symbol}")
            #print(px)
            
            # Mevcut fiyat
            current_price = px['Close'].iloc[-1]
            print(f"  Current {symbol} price: ${current_price.iloc[0]:.2f}")
            
            # 2. Teknik göstergeler
            px_normalized = normalize_price_df(px)
            ind_df = compute_indicators(px_normalized)
            tech = latest_signals(ind_df)
            
            # 3. Temel veriler
            raw_fund = provider.fundamentals(symbol, "equity")
            fund = compute_fundamental_ratios(raw_fund, "equity")
            
            # 4. Haber verileri
            news_items = fetch_news(symbol, limit=12)
            news_sent = summarize_news_sentiment(news_items)
            
            # 5. Şirket profili
            profile = provider.company_profile(symbol)
            
            # 6. Know-how
            knowhow = load_text_if_exists("knowhow.txt")
            
            # Gerçek verilerle payload oluştur
            payload = {
                "symbol": symbol,
                "security_type": "equity",
                "as_of": datetime.now().isoformat(),
                "profile": profile,
                "fundamentals": fund,
                "technicals": tech,
                "news_items": news_items,
                "news_sentiment": news_sent,
                "knowhow": knowhow,
                "current_price": current_price
            }
            
            # Analiz raporu oluştur
            report = synthesize_report(payload)
            
            # Grade hesapla
            fund_score = report.fundamentals_summary.score
            tech_score = report.technicals_summary.score
            news_score = report.news_summary.score
            overall = overall_score(fund_score, tech_score, news_score)
            grade = to_grade(overall)
            
            analysis_result = {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "grade": grade,
                "overall_score": overall,
                "current_price": current_price,
                "trading_signal": report.trading_signal.dict(),
                "market_alerts": [alert.dict() for alert in report.market_alerts],
                "risk_factors": report.risk_factors,
                "catalyst_events": report.catalyst_events,
                "overall_analysis": getattr(report, 'overall_analysis', 'N/A'),
                "key_drivers": getattr(report, 'key_drivers', []),
                "contrarian_views": getattr(report, 'contrarian_views', 'N/A')
            }
            
            self.last_analysis[symbol] = analysis_result
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            e.stack_trace
            return {"symbol": symbol, "error": str(e)}
    
    def check_trading_opportunities(self) -> List[Dict]:
        """Trading fırsatlarını kontrol eder"""
        opportunities = []
        
        for symbol in self.symbols:
            if symbol not in self.last_analysis:
                continue
                
            analysis = self.last_analysis[symbol]
            
            # Grade A veya B olan ve yüksek güven seviyesi olan sinyalleri bul
            if (analysis.get("grade") in ["A", "B"] and 
                analysis.get("trading_signal", {}).get("confidence", 0) > 0.7):
                
                opportunities.append({
                    "symbol": symbol,
                    "grade": analysis["grade"],
                    "confidence": analysis["trading_signal"]["confidence"],
                    "action": analysis["trading_signal"]["action"],
                    "timestamp": analysis["timestamp"]
                })
        
        return opportunities
    
    def generate_market_alerts(self) -> List[Dict]:
        """Piyasa uyarıları oluşturur"""
        alerts = []
        
        for symbol in self.symbols:
            if symbol not in self.last_analysis:
                continue
                
            analysis = self.last_analysis[symbol]
            
            # Yüksek volatilite uyarısı
            if analysis.get("overall_score", 0) > 0.8:
                alerts.append(create_trading_alert(
                    symbol=symbol,
                    alert_type="HIGH_VOLATILITY",
                    severity="HIGH",
                    message=f"{symbol} için yüksek volatilite tespit edildi. Grade: {analysis['grade']}",
                    action_required=True
                ))
            
            # Düşük grade uyarısı
            if analysis.get("grade") in ["D", "F"]:
                alerts.append(create_trading_alert(
                    symbol=symbol,
                    alert_type="FUNDAMENTAL_CHANGE",
                    severity="MEDIUM",
                    message=f"{symbol} için düşük grade: {analysis['grade']}. Dikkatli olun.",
                    action_required=False
                ))
        
        return alerts
    
    def run_analysis_cycle(self):
        """Analiz döngüsünü çalıştırır"""
        print(f"Starting analysis cycle at {datetime.now().strftime('%H:%M:%S')}")
        
        # Tüm sembolleri analiz et
        for symbol in self.symbols:
            print(f"Analyzing {symbol}...")
            result = self.analyze_symbol(symbol)
            
            # Detaylı analiz sonuçlarını göster
            if 'trading_signal' in result:
                signal = result['trading_signal']
                print(f"  Signal: {signal.get('action', 'N/A')} (Confidence: {signal.get('confidence', 'N/A'):.2f})")
                
                # Gerekçeleri göster
                if signal.get('fundamental_reasons'):
                    print(f"  Fundamental Reasons: {', '.join(signal['fundamental_reasons'])}")
                if signal.get('technical_reasons'):
                    print(f"  Technical Reasons: {', '.join(signal['technical_reasons'])}")
                if signal.get('news_catalysts'):
                    print(f"  News Catalysts: {', '.join(signal['news_catalysts'])}")
                if signal.get('market_timing'):
                    print(f"  Market Timing: {signal['market_timing']}")
            
            time.sleep(1)  # API rate limiting için
        
        # Trading fırsatlarını kontrol et
        opportunities = self.check_trading_opportunities()
        if opportunities:
            print(f"Found {len(opportunities)} trading opportunities:")
            for opp in opportunities:
                print(f"  {opp['symbol']}: {opp['action']} (Grade: {opp['grade']}, Confidence: {opp['confidence']:.2f})")
        
        # Piyasa uyarıları oluştur
        alerts = self.generate_market_alerts()
        if alerts:
            print(f"Generated {len(alerts)} market alerts")
            save_trading_alerts(alerts)
        
        print(f"Analysis cycle completed at {datetime.now().strftime('%H:%M:%S')}")
    
    def start_monitoring(self):
        """Monitoring'i başlatır"""
        print(f"Starting trading monitor for symbols: {', '.join(self.symbols)}")
        print(f"Update interval: {self.update_interval} minutes")
        
        # İlk analizi hemen yap
        self.run_analysis_cycle()
        
        # Periyodik analiz planla
        schedule.every(self.update_interval).minutes.do(self.run_analysis_cycle)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1 dakika bekle
        except KeyboardInterrupt:
            print("\nTrading monitor stopped by user")
    
    def get_summary_report(self) -> Dict:
        """Özet rapor döndürür"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "symbols_monitored": len(self.symbols),
            "last_analysis": {},
            "trading_opportunities": self.check_trading_opportunities(),
            "active_alerts": len(self.generate_market_alerts())
        }
        
        for symbol in self.symbols:
            if symbol in self.last_analysis:
                summary["last_analysis"][symbol] = {
                    "grade": self.last_analysis[symbol].get("grade"),
                    "score": self.last_analysis[symbol].get("overall_score"),
                    "last_update": self.last_analysis[symbol].get("timestamp")
                }
        
        return summary

def main():
    """Ana fonksiyon - test için"""
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    monitor = TradingMonitor(symbols, update_interval=15)
    
    # Test analizi
    print("Running test analysis...")
    for symbol in symbols[:2]:  # İlk 2 sembolü test et
        result = monitor.analyze_symbol(symbol)
        print(f"\n{symbol} Analysis:")
        print(f"  Grade: {result.get('grade', 'N/A')}")
        print(f"  Score: {result.get('overall_score', 'N/A'):.2f}")
        if 'trading_signal' in result:
            signal = result['trading_signal']
            print(f"  Action: {signal.get('action', 'N/A')}")
            print(f"  Confidence: {signal.get('confidence', 'N/A'):.2f}")

if __name__ == "__main__":
    main()
