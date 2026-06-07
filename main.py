import pandas as pd
import yfinance as yf
from flask import Flask, render_template_string

app = Flask(__name__)

# BIST 100 Hisselerinin Yahoo Finance Kodları
BIST_100_TICKERS = [
    "AEFES.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS", "AKFYE.IS", "AKSA.IS", "AKSEN.IS", "ALARK.IS",
    "ALBRK.IS", "ALFAS.IS", "ANACM.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "BERA.IS", "BEXIM.IS", "BIENY.IS", "BIMAS.IS",
    "BIOEN.IS", "BOBET.IS", "BRSAN.IS", "BRYAT.IS", "BUCIM.IS", "CCOLA.IS", "CATES.IS", "CIMSA.IS", "CWENE.IS", "DOAS.IS",
    "DOHOL.IS", "ECILC.IS", "EUPWR.IS", "ECZYT.IS", "EGEEN.IS", "EKGYO.IS", "ENJSA.IS", "ENKAI.IS", "EREGL.IS", "FROTO.IS",
    "GARAN.IS", "GESAN.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", "INVEO.IS", "IPEKE.IS", "ISCTR.IS", "ISGYO.IS",
    "ISMEN.IS", "IZMDC.IS", "KARDMD.IS", "KAYSE.IS", "KCAER.IS", "KCHOL.IS", "KLSER.IS", "KONTR.IS", "KORDS.IS", "KOZAA.IS",
    "KOZAL.IS", "KRDMD.IS", "MAVI.IS", "MHRGY.IS", "MIATK.IS", "MGROS.IS", "ODAS.IS", "OTKAR.IS", "OYAKC.IS", "PETKM.IS",
    "PGSUS.IS", "QUAGR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SOKM.IS", "TABGD.IS",
    "TARKM.IS", "TAVHL.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUKAS.IS",
    "TUPRS.IS", "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS"
]

def rsi_hesapla(seri, periyot=14):
    delta = seri.diff()
    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)
    
    ortalama_kazanc = kazanc.ewm(com=periyot - 1, adjust=False).mean()
    ortalama_kayip = kayip.ewm(com=periyot - 1, adjust=False).mean()
    
    rs = ortalama_kazanc / (ortalama_kayip + 1e-10)
    return 100 - (100 / (1 + rs))

def bist_taramasi_yap():
    sonuclar = {}
    
    # Render ücretsiz sunucusu yorulmasın diye ilk aşamada en popüler 20 hisseyi canlı taratıyoruz
    # (İleride istersen listeyi daha da büyütebiliriz)
    taranacak_hisseler = BIST_100_TICKERS[:25] 
    
    for sembol in taranacak_hisseler:
        try:
            hisse = yf.Ticker(sembol)
            veri = hisse.history(period="1mo", interval="1d")
            
            if len(veri) < 15:
                continue
                
            guncel_fiyat = round(veri['Close'].iloc[-1], 2)
            
            # RSI Hesaplama
            veri['RSI'] = rsi_hesapla(veri['Close'], 14)
            rsi_degeri = round(veri['RSI'].iloc[-1], 2)
            
            # Hareketli Ortalama (SMA 20)
            sma_degeri = round(veri['Close'].rolling(window=14).mean().iloc[-1], 2)
            
            hisse_adi = sembol.replace(".IS", "")
            
            # Sinyal Üretme
            if rsi_degeri >= 70:
                sinyal = "⚠️ AŞIRI ALIM (DİKKATLİ OLUN)"
            elif rsi_degeri <= 30:
                sinyal = "✅ AŞIRI SATIM (ALIM FIRSATI)"
            else:
                sinyal = "⚖️ NÖTR (BEKLEMEDE)"
                
            sonuclar[hisse_adi] = {
                "Güncel Fiyat": f"{guncel_fiyat} TL",
                "RSI (14)": rsi_degeri,
                "SMA Ortalaması": f"{sma_degeri} TL",
                "Sinyal/Analiz": sinyal
            }
        except:
            continue
            
    return sonuclar

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BIST Canlı Tarama Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #121824; color: #e2e8f0; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .container { max-width: 1000px; width: 100%; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        h1 { text-align: center; color: #38bdf8; }
        .status-bar { text-align: center; font-size: 0.95rem; color: #34d399; background: rgba(52, 211, 153, 0.1); padding: 8px; border-radius: 6px; margin-bottom: 25px; font-weight: 600; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 14px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #38bdf8; }
        tr:hover { background-color: #243249; }
        .badge { padding: 6px 12px; border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
        .badge-danger { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
        .badge-success { background-color: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
        .badge-warning { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    </style>
</head>
<body>
<div class="container">
    <h1>📊 BIST 100 Canlı Otomatik Tarama Robotu</h1>
    <div class="status-bar">🟢 Sistem Durumu: Canlı Veriler Aktif Olarak Çekiliyor</div>
    <table>
        <thead>
            <tr>
                <th>Hisse Adı</th>
                <th>Canlı Fiyat</th>
                <th>RSI (14)</th>
                <th>SMA Ortalaması</th>
                <th>Robot Sinyali</th>
            </tr>
        </thead>
        <tbody>
            {% for hisse, detay in data.items() %}
            <tr>
                <td style="font-weight: bold; color: #f1f5f9;">{{ hisse }}</td>
                <td>{{ detay['Güncel Fiyat'] }}</td>
                <td style="font-weight: bold; color: #38bdf8;">{{ detay['RSI (14)'] }}</td>
                <td>{{ detay['SMA Ortalaması'] }}</td>
                <td>
                    {% if 'AŞIRI ALIM' in detay['Sinyal/Analiz'] %}
                        <span class="badge badge-danger">{{ detay['Sinyal/Analiz'] }}</span>
                    {% elif 'AŞIRI SATIM' in detay['Sinyal/Analiz'] %}
                        <span class="badge badge-success">{{ detay['Sinyal/Analiz'] }}</span>
                    {% else %}
                        <span class="badge badge-warning">{{ detay['Sinyal/Analiz'] }}</span>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    canli_veriler = bist_taramasi_yap()
    return render_template_string(HTML_TEMPLATE, data=canli_veriler)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)