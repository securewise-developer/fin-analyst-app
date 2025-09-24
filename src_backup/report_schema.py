from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class SectionScore(BaseModel):
    rationale: str = Field(..., description="Kısa, maddeli gerekçe")
    score: float = Field(..., description="0–1 arası sekme skoru (grade hesaplamada kullanılacak)")

class TradingSignal(BaseModel):
    action: Literal["BUY", "SELL", "HOLD"] = Field(..., description="Trading aksiyonu")
    confidence: float = Field(..., description="0-1 arası güven seviyesi")
    entry_price: Optional[float] = Field(None, description="Giriş fiyatı önerisi")
    exit_price: Optional[float] = Field(None, description="Çıkış fiyatı önerisi")
    stop_loss: Optional[float] = Field(None, description="Stop loss seviyesi")
    take_profit: Optional[float] = Field(None, description="Take profit seviyesi")
    position_size: Optional[str] = Field(None, description="Pozisyon büyüklüğü önerisi")
    time_horizon: str = Field(..., description="Trading zaman dilimi (intraday, swing, position)")
    risk_reward_ratio: Optional[float] = Field(None, description="Risk-ödül oranı")
    
    # Detaylı gerekçe alanları
    fundamental_reasons: List[str] = Field(default_factory=list, description="Temel analiz gerekçeleri")
    technical_reasons: List[str] = Field(default_factory=list, description="Teknik analiz gerekçeleri")
    news_catalysts: List[str] = Field(default_factory=list, description="Haber katalizörleri")
    risk_factors: List[str] = Field(default_factory=list, description="Risk faktörleri")
    market_timing: str = Field(..., description="Piyasa zamanlaması gerekçesi")
    sector_outlook: Optional[str] = Field(None, description="Sektör görünümü")

class MarketAlert(BaseModel):
    alert_type: Literal["HIGH_VOLATILITY", "NEWS_CATALYST", "TECHNICAL_BREAKOUT", "FUNDAMENTAL_CHANGE", "SECTOR_ROTATION"] = Field(..., description="Uyarı türü")
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(..., description="Uyarı şiddeti")
    description: str = Field(..., description="Uyarı açıklaması")
    immediate_action: str = Field(..., description="Acil eylem önerisi")
    monitoring_points: List[str] = Field(default_factory=list, description="İzlenmesi gereken noktalar")
    
    # Detaylı gerekçe
    root_cause: str = Field(..., description="Uyarının ana sebebi")
    impact_analysis: str = Field(..., description="Etki analizi")
    historical_context: Optional[str] = Field(None, description="Tarihsel bağlam")

class AnalysisReport(BaseModel):
    symbol: str
    as_of: str
    security_type: Literal["equity", "etf", "fund"]

    fundamentals_summary: SectionScore
    technicals_summary: SectionScore
    news_summary: SectionScore

    key_flags: List[str] = Field(default_factory=list, description="Kırmızı/yeşil bayraklar")
    overall_commentary: str
    
    # Trading specific fields
    trading_signal: TradingSignal = Field(..., description="Trading sinyali ve önerileri")
    market_alerts: List[MarketAlert] = Field(default_factory=list, description="Piyasa uyarıları")
    intraday_opportunities: List[str] = Field(default_factory=list, description="Gün içi fırsatlar")
    risk_factors: List[str] = Field(default_factory=list, description="Risk faktörleri")
    catalyst_events: List[str] = Field(default_factory=list, description="Yaklaşan katalizör olaylar")
    
    # Genel değerlendirme
    overall_analysis: str = Field(..., description="Genel analiz ve gerekçe")
    key_drivers: List[str] = Field(default_factory=list, description="Ana sürücü faktörler")
    contrarian_views: Optional[str] = Field(None, description="Karşıt görüşler ve riskler")
