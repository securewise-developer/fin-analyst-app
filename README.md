# Fin-Analyst: Financial Analysis & Trading Monitor

Fin-analyst, finansal analiz ve günlük trading için geliştirilmiş kapsamlı bir Python uygulamasıdır. Bu uygulama, hisse senetleri, ETF'ler ve fonlar için detaylı analizler yapar ve trading fırsatlarını tespit eder.

## 🚀 Özellikler

### 📊 Finansal Analiz

- **Temel Analiz**: P/E oranı, debt-to-equity, gross margin gibi temel oranlar
- **Teknik Analiz**: RSI, MACD, SMA200, momentum göstergeleri
- **Haber Analizi**: VADER sentiment analizi ile haber etkisi değerlendirmesi
- **Grade Sistemi**: A'dan F'ye kadar 5 seviyeli değerlendirme sistemi

### 🎯 Trading Monitor

- **Gerçek Zamanlı İzleme**: 15 dakikada bir otomatik analiz
- **Trading Sinyalleri**: BUY/SELL/HOLD önerileri
- **Risk Yönetimi**: Stop-loss, take-profit ve pozisyon büyüklüğü önerileri
- **Piyasa Uyarıları**: Volatilite, haber katalizörleri ve teknik kırılımlar
- **Grade Bazlı Fırsat Tespiti**: A ve B grade fırsatları otomatik tespit

## 🛠️ Kurulum

### Gereksinimler

- Python 3.8+
- pip
- Virtual environment (önerilen)

### Adımlar

```bash
# Repository'yi klonlayın
git clone <repository-url>
cd fin-analyst

# Virtual environment oluşturun
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# veya
.venv\Scripts\activate  # Windows

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

## 📖 Kullanım

### 1. Tek Sembol Analizi

```bash
# Tek bir hisse senedi analizi
python -m src.main --symbol AAPL --type equity --out aapl_report.json
```

### 2. Trading Monitor

```bash
# Tek seferlik analiz
python -m src.main monitor --symbols AAPL MSFT GOOGL --mode once

# Sürekli izleme (15 dakikada bir)
python -m src.main monitor --symbols AAPL MSFT GOOGL TSLA NVDA --mode continuous

# Hızlı day trading (5 dakikada bir)
python -m src.main monitor --symbols QQQ SPY --interval 5 --mode continuous
```

### 3. Özel Ayarlar

```bash
# Özel çıktı dosyası
python -m src.main monitor --symbols AAPL --mode once --out my_analysis.json

# Farklı güncelleme aralığı
python -m src.main monitor --symbols AAPL MSFT --interval 30 --mode continuous
```

## 📈 Grade Sistemi

| Grade | Skor Aralığı | Açıklama        | Trading Önerisi |
| ----- | ------------ | --------------- | --------------- |
| **A** | 0.8 - 1.0    | Mükemmel fırsat | Güçlü BUY       |
| **B** | 0.65 - 0.79  | İyi fırsat      | BUY             |
| **C** | 0.5 - 0.64   | Nötr            | HOLD            |
| **D** | 0.35 - 0.49  | Düşük kalite    | Dikkatli olun   |
| **F** | 0.0 - 0.34   | Kaçının         | Kaçının         |

## 🔔 Bildirim Türleri

### Piyasa Uyarıları

- **HIGH_VOLATILITY**: Yüksek volatilite tespit edildiğinde
- **NEWS_CATALYST**: Önemli haber olayları
- **TECHNICAL_BREAKOUT**: Teknik seviyeler kırıldığında
- **FUNDAMENTAL_CHANGE**: Temel değişiklikler
- **SECTOR_ROTATION**: Sektör değişimleri

### Uyarı Şiddet Seviyeleri

- **LOW**: Düşük öncelik
- **MEDIUM**: Orta öncelik
- **HIGH**: Yüksek öncelik
- **CRITICAL**: Kritik, acil eylem gerekli

## ⚠️ Risk Yönetimi

### Trading İpuçları

1. **Stop-Loss**: Her trade için stop-loss kullanın
2. **Risk-Ödül Oranı**: Minimum 1:2 risk-ödül oranı hedefleyin
3. **Pozisyon Büyüklüğü**: Portföyünüzün maksimum %2-3'ünü riske atın
4. **Grade Odaklı**: Sadece A ve B grade fırsatları değerlendirin

### Günlük Trading Rutini

- **09:00-11:00**: Günlük analizleri gözden geçirin
- **11:00-14:00**: Piyasa koşullarını izleyin
- **14:00-16:00**: Günlük performansı değerlendirin

## 🔧 Teknik Detaylar

### Dosya Yapısı

```
fin-analyst/
├── src/
│   ├── main.py              # Ana CLI uygulaması
│   ├── trading_monitor.py   # Trading izleme sistemi
│   ├── synthesize.py        # LLM analiz sistemi
│   ├── report_schema.py     # Veri modelleri
│   ├── grade.py             # Grade hesaplama
│   ├── utils.py             # Yardımcı fonksiyonlar
│   └── ...                  # Diğer modüller
├── rubrics/                 # Grade konfigürasyonları
├── requirements.txt          # Python bağımlılıkları
└── TRADING_GUIDE.md         # Detaylı trading kılavuzu
```

### Veri Sağlayıcıları

- **Yahoo Finance**: Fiyat verileri ve temel bilgiler
- **Financial Modeling Prep (FMP)**: Detaylı finansal veriler
- **News APIs**: Haber ve sentiment analizi

## 📊 Örnek Çıktılar

### Trading Özet Raporu

```json
{
  "timestamp": "2025-08-30T00:38:15.974657",
  "symbols_monitored": 2,
  "trading_opportunities": [
    {
      "symbol": "AAPL",
      "grade": "B",
      "confidence": 0.75,
      "action": "BUY",
      "timestamp": "2025-08-30T00:38:04.176203"
    }
  ],
  "active_alerts": 0
}
```

### Analiz Raporu

```json
{
  "symbol": "AAPL",
  "grade": "B",
  "overall_score": 0.71,
  "trading_signal": {
    "action": "BUY",
    "confidence": 0.75,
    "entry_price": 150.0,
    "stop_loss": 145.0,
    "take_profit": 160.0
  }
}
```

## 🚨 Önemli Notlar

- **Yatırım Tavsiyesi Değildir**: Bu uygulama sadece analiz amaçlıdır
- **Risk Yönetimi**: Her zaman risk yönetimi yapın
- **Profesyonel Danışmanlık**: Önemli kararlar için profesyonel danışmanlık alın
- **Test**: Gerçek trading öncesi demo hesapta test edin

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📞 Destek

- **GitHub Issues**: Hata raporları ve öneriler için
- **Discussions**: Genel sorular ve tartışmalar için
- **Wiki**: Detaylı dokümantasyon için

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

---

**⚠️ Uyarı**: Bu uygulama sadece eğitim ve analiz amaçlıdır. Yatırım kararları kendi sorumluluğunuzdadır. Her zaman risk yönetimi yapın ve profesyonel finansal danışmanlık alın.
