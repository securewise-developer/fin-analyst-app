from __future__ import annotations
import yaml
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def load_text_if_exists(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""

def load_yaml(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

def normalize_price_df(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume",
        "Open": "Open", "High": "High", "Low": "Low", "Close": "Close", "Volume": "Volume"
    }
    df = df.rename(columns=rename_map)
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()

def generate_trading_context(
    time_horizon: str = "intraday",
    risk_tolerance: str = "moderate"
) -> Dict[str, str]:
    """Trading bağlamı oluşturur"""
    return {
        "time_horizon": time_horizon,
        "risk_tolerance": risk_tolerance,
        "volatility_level": get_market_conditions()["volatility_level"]
    }

def create_trading_alert(
    symbol: str,
    alert_type: str,
    severity: str,
    message: str,
    action_required: bool = False
) -> Dict[str, any]:
    """Trading uyarısı oluşturur"""
    from datetime import timedelta
    return {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "alert_type": alert_type,
        "severity": severity,
        "message": message,
        "action_required": action_required,
        "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
    }

def save_trading_alerts(alerts: List[Dict], filename: str = "trading_alerts.json"):
    """Trading uyarılarını dosyaya kaydeder"""
    import json
    alerts_file = Path(filename)
    existing_alerts = []
    
    if alerts_file.exists():
        try:
            existing_alerts = json.loads(alerts_file.read_text())
        except json.JSONDecodeError:
            existing_alerts = []
    
    # Sadece son 100 uyarıyı sakla
    all_alerts = existing_alerts + alerts
    if len(all_alerts) > 100:
        all_alerts = all_alerts[-100:]
    
    alerts_file.write_text(json.dumps(all_alerts, indent=2, ensure_ascii=False))

def get_active_trading_signals(symbols: List[str]) -> Dict[str, Dict]:
    """Aktif trading sinyallerini döndürür"""
    from datetime import timedelta
    signals = {}
    for symbol in symbols:
        # Burada gerçek trading sinyalleri üretilebilir
        # Şimdilik örnek veri döndürüyoruz
        signals[symbol] = {
            "last_updated": datetime.now().isoformat(),
            "signal_strength": "NEUTRAL",
            "confidence": 0.5,
            "next_update": (datetime.now() + timedelta(minutes=15)).isoformat()
        }
    return signals

def get_market_status() -> Dict[str, any]:
    """Piyasa durumunu kontrol eder"""
    now = datetime.now()
    
    # ABD piyasa saatleri (ET - Eastern Time)
    current_hour = now.hour
    
    # Piyasa saatleri (UTC)
    market_open = 14  # 9:30 AM ET = 14:30 UTC
    market_close = 21  # 4:00 PM ET = 21:00 UTC
    
    # Hafta sonu kontrolü
    is_weekend = now.weekday() >= 5  # Cumartesi = 5, Pazar = 6
    
    if is_weekend:
        status = "CLOSED_WEEKEND"
        next_open = "Monday 9:30 AM ET"
        message = "Piyasa hafta sonu kapalı. Pazartesi 9:30 AM ET'de açılacak."
        trading_recommended = False
        reason = "Hafta sonu trading yapılamaz"
    elif market_open <= current_hour < market_close:
        status = "OPEN"
        next_open = "Today 4:00 PM ET"
        message = "Piyasa açık. Aktif trading yapılabilir."
        trading_recommended = True
        reason = "Normal piyasa saatleri"
    elif current_hour < market_open:
        status = "PRE_MARKET"
        next_open = "Today 9:30 AM ET"
        message = "Pre-market seansı. Dikkatli trading yapılabilir."
        trading_recommended = True
        reason = "Pre-market seansı (sınırlı likidite)"
    else:  # current_hour >= market_close
        status = "AFTER_HOURS"
        next_open = "Tomorrow 9:30 AM ET"
        message = "After-hours seansı. Dikkatli trading yapılabilir."
        trading_recommended = True
        reason = "After-hours seansı (sınırlı likidite)"
    
    return {
        "status": status,
        "current_time": now.strftime("%H:%M:%S UTC"),
        "market_open": market_open,
        "market_close": market_close,
        "next_open": next_open,
        "message": message,
        "trading_recommended": trading_recommended,
        "reason": reason,
        "is_weekend": is_weekend,
        "current_hour": current_hour
    }

def get_trading_recommendations_by_market_status(market_status: Dict) -> Dict[str, any]:
    """Piyasa durumuna göre trading önerileri"""
    status = market_status["status"]
    
    if status == "CLOSED_WEEKEND":
        return {
            "action": "NO_TRADING",
            "reason": "Hafta sonu piyasa kapalı",
            "recommendations": [
                "Geçmiş hafta performansını değerlendirin",
                "Gelecek hafta için strateji planlayın",
                "Portföy risk yönetimini gözden geçirin",
                "Önemli haberleri takip edin"
            ],
            "risk_level": "NONE",
            "liquidity": "NONE"
        }
    elif status == "OPEN":
        return {
            "action": "ACTIVE_TRADING",
            "reason": "Normal piyasa saatleri",
            "recommendations": [
                "Gerçek zamanlı fiyatları takip edin",
                "Stop-loss emirlerini aktif tutun",
                "Likidite yüksek, spread düşük",
                "Normal risk yönetimi uygulayın"
            ],
            "risk_level": "NORMAL",
            "liquidity": "HIGH"
        }
    elif status in ["PRE_MARKET", "AFTER_HOURS"]:
        return {
            "action": "CAUTIOUS_TRADING",
            "reason": f"{status.replace('_', ' ').title()} seansı",
            "recommendations": [
                "Likidite düşük, spread yüksek",
                "Küçük pozisyonlarla işlem yapın",
                "Stop-loss emirlerini dikkatli ayarlayın",
                "Normal saatlerdeki fiyatlardan farklı olabilir",
                "Risk yönetimini sıkılaştırın"
            ],
            "risk_level": "HIGH",
            "liquidity": "LOW"
        }
    
    return {
        "action": "UNKNOWN",
        "reason": "Bilinmeyen piyasa durumu",
        "recommendations": ["Durumu kontrol edin"],
        "risk_level": "UNKNOWN",
        "liquidity": "UNKNOWN"
    }

def should_generate_trading_signals(market_status: Dict) -> bool:
    """Trading sinyali üretilmeli mi?"""
    return market_status["trading_recommended"]

def get_market_conditions() -> Dict[str, str]:
    """Güncel piyasa koşullarını döndürür"""
    now = datetime.now()
    hour = now.hour
    
    # Piyasa durumunu kontrol et
    market_status = get_market_status()
    
    # Basit saat bazlı piyasa koşulları
    if market_status["status"] == "OPEN":
        if 14 <= hour <= 16:  # 9:30 AM - 11:30 AM ET
            market_phase = "OPENING_SESSION"
            volatility = "HIGH"
        elif 16 < hour <= 19:  # 11:30 AM - 2:30 PM ET
            market_phase = "MID_SESSION"
            volatility = "MEDIUM"
        elif 19 < hour <= 21:  # 2:30 PM - 4:00 PM ET
            market_phase = "CLOSING_SESSION"
            volatility = "HIGH"
        else:
            market_phase = "UNKNOWN"
            volatility = "UNKNOWN"
    else:
        market_phase = market_status["status"]
        volatility = "LOW" if market_status["status"] in ["PRE_MARKET", "AFTER_HOURS"] else "NONE"
    
    return {
        "market_phase": market_phase,
        "volatility_level": volatility,
        "session_time": f"{hour:02d}:00",
        "market_status": market_status["status"],
        "trading_recommended": market_status["trading_recommended"]
    }
