import time
import threading
import pandas as pd
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
        r = requests.post(url, json=payload)
        print(f"Telegram Yanit_Kodu: {r.status_code}")
    except Exception as e:
        print(f"Telegram mesaj hatasi: {e}")

def rsi_hesapla(seri, periyot=14):
    if len(seri) < periyot:
        return pd.Series([50] * len(seri))
    delta = seri.diff()
    kazanc = delta.clip(lower=0)
    kayip = -delta.clip(upper=0)
    ortalama_kazanc = kazanc.ewm(com=periyot - 1, adjust=False).mean()
    ortalama_kayip = kayip.ewm(com=periyot - 1, adjust=False).mean()
    rs = ortalama_kazanc / (ortalama_kayip + 1e-10)
    return 100 - (100 / (1 + rs))

def yahoo_veri_cek(sembol):
    bitis = int(time.time())
    baslangic = bitis - (60 * 60 * 24 * 60) 
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sembol}?period1={baslangic}&period2={bitis}&interval=1d"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        veri_json = r.json()
        kapanislar = veri_json['chart']['result'][0]['indicators']['quote'][0]['close']
        kapanis_serisi = pd.Series(kapanislar).dropna()
        return kapanis_serisi
    except:
        return None

def borsa_taramasi_ve_sinyal():
    print("Guvenli modda BIST 100 taramasi basladi...")
    asiri_alim_listesi = []
    asiri_satim_listesi = []
    
    for sembol in BIST_100_TICKERS:
        kapanis_serisi = yahoo_veri_cek(sembol)
        if kapanis_serisi is None or len(kapanis_serisi) < 15:
            continue
            
        guncel_fiyat = round(kapanis_serisi.iloc[-1], 2)
        rsi_serisi = rsi_hesapla(kapanis_serisi, 14)
        rsi_degeri = round(rsi_serisi.iloc[-1], 2)
        hisse_adi = sembol.replace(".IS", "")
        
        if rsi_degeri >= 70:
            asiri_alim_listesi.append(f"• *{hisse_adi}*: {guncel_fiyat} TL | RSI: {rsi_degeri} ⚠️")
        elif rsi_degeri <= 30:
            asiri_satim_listesi.append(f"• *{hisse_adi}*: {guncel_fiyat} TL | RSI: {rsi_degeri} ✅")
        
        time.sleep(0.1)

    rapor_mesaji = "📊 *BIST 100 HESAPLANAN EN SON SİNYALLER*\n"
    rapor_mesaji += "───────────────────\n\n"
    
    rapor_mesaji += "🟢 *AŞIRI SATIM (ALIM FIRSATI - RSI ≤ 30):*\n"
    if asiri_satim_listesi:
        rapor_mesaji += "\n".join(asiri_satim_listesi) + "\n\n"
    else:
        rapor_mesaji += "Su an bu kritere uyan hisse bulunamadi.\n\n"
        
    rapor_mesaji += "🔴 *AŞIRI ALIM (DİKKATLİ OLUN - RSI ≥ 70):*\n"
    if asiri_alim_listesi:
        rapor_mesaji += "\n".join(asiri_alim_listesi) + "\n"
    else:
        rapor_mesaji += "Su an bu kritere uyan hisse bulunamadi.\n"
        
    rapor_mesaji += "\n🤖 _Robot taramayi basariyla tamamladi._"
    return rapor_mesaji

def arka_plan_taramasi():
    print("Arka plan tarama dongusu aktif hale geldi.")
    # Sunucu acilir acilmaz ilk mesajı gonderir
    mesaj = borsa_taramasi_ve_sinyal()
    telegram_mesaj_gonder(mesaj)
    
    while True:
        # 12 saatte bir calisacak
        time.sleep(43200)
        mesaj = borsa_taramasi_ve_sinyal()
        telegram_mesaj_gonder(mesaj)

threading.Thread(target=arka_plan_taramasi, daemon=True).start()

@app.route('/')
def home():
    return "<h1>BIST 100 Robotu Arka Planda Hatasiz Calisiyor!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)