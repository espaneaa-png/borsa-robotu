import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

# Basit RSI Hesaplama Fonksiyonu
def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50  # Yeterli veri yoksa nötr döndür
    
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(diff))
            
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    if avg_loss == 0:
        return 100
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

# Basit Hareketli Ortalama Hesaplama
def calculate_sma(prices, period):
    if len(prices) < period:
        return None
    return round(sum(prices[-period:]) / period, 2)

@app.route('/')
def home():
    # Test amaçlı örnek hisse verileri (Gerçekte API'den veya web scraping ile çekilebilir)
    # Son 20 günlük hayali kapanış fiyatları
    hisse_verileri = {
        "THYAO": [280, 282, 285, 283, 287, 289, 292, 290, 294, 296, 295, 298, 301, 305, 303, 306, 308, 310, 312, 315],
        "EREGL": [50, 49.5, 49, 48.5, 48, 47.5, 47, 46.8, 46.5, 46, 45.8, 45.5, 45, 44.8, 44.5, 44.2, 44, 43.8, 43.5, 43],
        "ASELS": [60, 61, 60.5, 61.5, 62, 62.5, 63, 63.5, 64, 64.5, 65, 65.5, 66, 66.5, 67, 67.5, 68, 68.5, 69, 70]
    }
    
    rapor = {}
    
    for hisse, fiyatlar in hisse_verileri.items():
        guncel_fiyat = fiyatlar[-1]
        rsi_degeri = calculate_rsi(fiyatlar)
        sma_20 = calculate_sma(fiyatlar, 10) # Örnek amaçlı periyot kısa tutulmuştur
        
        # Sinyal Üretim Mantığı
        durum = "NÖTR"
        if rsi_degeri < 30:
            durum = "AŞIRI SATIM (ALIM FIRSATI OLABİLİR)"
        elif rsi_degeri > 70:
            durum = "AŞIRI ALIM (DİKKATLİ OLUNMALI)"
        elif guncel_fiyat > sma_20:
            durum = "GÜÇLÜ YÜKSELİŞ TRENDİ"
            
        rapor[hisse] = {
            "Güncel Fiyat": f"{guncel_fiyat} TL",
            "RSI (14)": rsi_degeri,
            "SMA Ortalaması": f"{sma_20} TL",
            "Sinyal/Analiz": durum
        }
        
    return jsonify({
        "Sistem Durumu": "BIST 100 Akıllı Tarama Robotu Aktif",
        "Analiz Sonuçları": rapor
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)