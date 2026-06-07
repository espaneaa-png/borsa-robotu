import time
import threading
import pandas as pd
import yfinance as yf
import requests
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = "8942579926:AAEXPwqqxeo5kXozOSjc83OsrxONkMN5iz8"
CHAT_ID = "8686065642"

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

def telegram_mesaj_gonder(mesaj):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram mesaj hatası: {e}")

def rsi_hesapla(seri, periyot=14):
    delta = seri.diff()
    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)
    ortalama_kazanc = kazanc.ewm(com=periyot - 1, adjust=False).mean()
    ortalama_kayip = kayip.ewm(com=periyot - 1, adjust=False).mean()
    rs = ortalama_kazanc / (ortalama_kayip + 1e-10)
    return 100 - (100 / (1 + rs))

def borsa_taramasi_ve_sinyal():
    asiri_alim_listesi = []
    asiri_satim_listesi = []
    
    try:
        toplu_veri = yf.download(BIST_100_TICKERS, period="1mo", interval="1d", group_by='ticker', progress=False)
        
        for sembol in BIST_100_TICKERS:
            try:
                if sembol not in toplu_veri.columns.levels[0]:
                    continue
                veri = toplu_veri[sembol].dropna()
                if len(veri) < 15:
                    continue
                    
                guncel_fiyat = round(veri['Close'].iloc[-1], 2)
                veri['RSI'] = rsi_hesapla(veri['Close'], 14)
                rsi_degeri = round(veri['RSI'].iloc[-1], 2)
                hisse_adi = sembol.replace(".IS", "")
                
                if rsi_degeri >= 70:
                    asiri_alim_listesi.append(f"• *{hisse_adi}*: Fiyat: {guncel_fiyat} TL | RSI: {rsi_degeri} ⚠️")
                elif rsi_degeri <= 30:
                    asiri_satim_listesi.append(f"• *{hisse_adi}*: Fiyat: {guncel_fiyat} TL | RSI: {rsi_degeri} ✅")
            except:
                continue
    except Exception as e:
        print(f"Veri çekme hatası: {e}")
        return "Borsa verileri çekilirken bir hata oluştu."

    rapor_mesaji = "📊 *BIST 100 AKILLI TARAMA RAPORU*\n"
    rapor_mesaji += "───────────────────\n\n"
    
    rapor_mesaji += "🟢 *AŞIRI SATIM (ALIM FIRSATI - RSI ≤ 30):*\n"
    if asiri_satim_listesi:
        rapor_mesaji += "\n".join(asiri_satim_listesi) + "\n\n"
    else:
        rapor_mesaji += "Şu an bu kritere uyan hisse bulunamadı.\n\n"
        
    rapor_mesaji += "🔴 *AŞIRI ALIM (DİKKATLİ OLUN - RSI ≥ 70):*\n"
    if asiri_alim_listesi:
        rapor_mesaji += "\n".join(asiri_alim_listesi) + "\n"
    else:
        rapor_mesaji += "Şu an bu kritere uyan hisse bulunamadı.\n"
        
    rapor_mesaji += "\n🤖 _Robot taramayı başarıyla tamamladı._"
    return rapor_mesaji

def arka_plan_taramasi():
    """Robotun Render açıldığında İLK MESAJI atmasını ve sonrasında her 12 saatte bir çalışmasını sağlar"""
    print("Arka plan tarama döngüsü başladı...")
    # Sunucu ilk açıldığında hemen bir test taraması yapıp cebe gönderir
    time.sleep(10) 
    mesaj = borsa_taramasi_ve_sinyal()
    telegram_mesaj_gonder(mesaj)
    
    while True:
        # 12 saatte bir (43200 saniye) otomatik olarak arka planda tarama yapar
        time.sleep(43200)
        mesaj = borsa_taramasi_ve_sinyal()
        telegram_mesaj_gonder(mesaj)

# Robotun kapanmasını önlemek için arka plan döngüsünü ayrı bir iş parçacığında (thread) başlatıyoruz
threading.Thread(target=arka_plan_taramasi, daemon=True).start()

@app.route('/')
def home():
    # Render sunucusu bu sayfayı açık görerek 'Live' durumunda tutacak
    return "<h1>BIST 100 Robotu Arka Planda Aktif Olarak Calisiyor!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)