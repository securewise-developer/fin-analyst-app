# Günlük Trading Kılavuzu

Bu kılavuz, fin-analyst uygulamasının günlük trading özelliklerini nasıl kullanacağınızı açıklar.

## 🚀 Yeni Özellikler

### 1. Trading Sinyalleri

- **BUY/SELL/HOLD** önerileri
- Güven seviyesi (0-1 arası)
- Giriş/çıkış fiyat önerileri
- Stop-loss ve take-profit seviyeleri
- Pozisyon büyüklüğü önerileri

### 2. Anlık Bildirimler

- Piyasa uyarıları (HIGH_VOLATILITY, NEWS_CATALYST, vb.)
- Uyarı şiddeti (LOW, MEDIUM, HIGH, CRITICAL)
- Acil eylem önerileri
- İzlenmesi gereken noktalar

### 3. Günlük Trading İzleme

- 15 dakikada bir otomatik analiz
- Grade bazlı fırsat tespiti
- Risk faktörleri ve katalizör olaylar
- Gün içi trading fırsatları

## 📊 Kullanım

### Tek Seferlik Analiz

```bash
# Tek sembol analizi
python src/main.py --symbol AAPL --type equity

# Trading monitor ile tek seferlik analiz
python src/main.py monitor --symbols AAPL MSFT GOOGL --mode once
```

### Sürekli İzleme

```bash
# Sürekli monitoring (15 dakikada bir güncelleme)
python src/main.py monitor --symbols AAPL MSFT GOOGL TSLA NVDA --mode continuous --interval 15
```

### Özel Ayarlar

```bash
# 5 dakikada bir güncelleme
python src/main.py monitor --symbols QQQ SPY --interval 5 --mode continuous

# Özel çıktı dosyası
python src/main.py monitor --symbols AAPL --mode once --out my_analysis.json
```

## 📈 Trading Sinyalleri

### Grade Sistemi

- **A (0.8-1.0)**: Mükemmel fırsat, yüksek güven
- **B (0.65-0.79)**: İyi fırsat, orta-yüksek güven
- **C (0.5-0.64)**: Nötr, dikkatli olun
- **D (0.35-0.49)**: Düşük kalite, riskli
- **F (0.0-0.34)**: Kaçının, yüksek risk

### Trading Aksiyonları

- **BUY**: Güçlü alım sinyali
- **SELL**: Güçlü satım sinyali
- **HOLD**: Mevcut pozisyonu koruyun

## 🔔 Bildirim Türleri

### 1. HIGH_VOLATILITY

- Yüksek volatilite tespit edildiğinde
- Acil eylem gerekebilir

### 2. NEWS_CATALYST

- Önemli haber olayları
- Fiyat hareketlerini tetikleyebilir

### 3. TECHNICAL_BREAKOUT

- Teknik seviyeler kırıldığında
- Trend değişimi sinyali

### 4. FUNDAMENTAL_CHANGE

- Temel değişiklikler
- Uzun vadeli etki

### 5. SECTOR_ROTATION

- Sektör değişimleri
- Portföy ayarlaması gerekebilir

## ⚠️ Risk Yönetimi

### Stop-Loss Önerileri

- Her trade için stop-loss seviyesi
- Risk-ödül oranı hesaplaması
- Pozisyon büyüklüğü önerileri

### Risk Faktörleri

- Piyasa volatilitesi
- Sektör riskleri
- Likidite riskleri
- Zaman riski

## 📱 Günlük Trading Rutini

### Sabah (09:00-11:00)

- Günlük analizleri gözden geçirin
- Yüksek grade fırsatları tespit edin
- Günlük trading planını oluşturun

### Öğle (11:00-14:00)

- Piyasa koşullarını izleyin
- Teknik sinyalleri takip edin
- Pozisyon ayarlamaları yapın

### Akşam (14:00-16:00)

- Günlük performansı değerlendirin
- Yarın için plan yapın
- Risk yönetimini gözden geçirin

## 🎯 En İyi Uygulamalar

### 1. Grade Odaklı Trading

- Sadece A ve B grade fırsatları değerlendirin
- C grade'leri dikkatle izleyin
- D ve F grade'lerden kaçının

### 2. Risk Yönetimi

- Her trade için maksimum %2-3 risk
- Stop-loss seviyelerini mutlaka kullanın
- Pozisyon büyüklüğünü risk toleransınıza göre ayarlayın

### 3. Zaman Yönetimi

- Piyasa açılış ve kapanış saatlerinde dikkatli olun
- Haber zamanlarında volatiliteyi bekleyin
- Hafta sonu pozisyonlarını değerlendirin

### 4. Sürekli Öğrenme

- Trading sonuçlarını kaydedin
- Başarılı stratejileri tekrarlayın
- Hatalardan ders alın

## 🔧 Teknik Detaylar

### Dosya Yapısı

```
fin-analyst/
├── src/
│   ├── trading_monitor.py    # Trading izleme sistemi
│   ├── synthesize.py         # Güncellenmiş analiz sistemi
│   ├── report_schema.py      # Trading alanları eklendi
│   └── utils.py              # Trading yardımcı fonksiyonları
├── trading_alerts.json       # Trading uyarıları
└── trading_summary.json      # Özet raporlar
```

### Güncelleme Aralıkları

- **15 dakika**: Standart günlük trading
- **5 dakika**: Aktif day trading
- **30 dakika**: Swing trading
- **1 saat**: Position trading

## 📞 Destek

Herhangi bir sorunuz veya öneriniz için:

- GitHub Issues kullanın
- Kod incelemesi yapın
- Test sonuçlarını paylaşın

---

**⚠️ Önemli Not**: Bu uygulama sadece analiz amaçlıdır. Yatırım kararları kendi sorumluluğunuzdadır. Her zaman risk yönetimi yapın ve profesyonel finansal danışmanlık alın.
