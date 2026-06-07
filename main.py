import time
import pandas as pd
import yfinance as yf
import requests
from flask import Flask

app = Flask(__name__)

# Telegram Bilgilerin (Sistem bunları kullanarak sana mesaj atacak)
BOT_TOKEN = "8942579926:AAEXPwqqxeo5kXozOSjc83OsrxONkMN5iz8"
CHAT_ID = "8686065642"

# BIST 100 Hisselerinin Tam Listesi
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
    """Robotun senin telefonuna mesaj atmasını sağlayan fonksiyon"""
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
    print("BIST 100 Taraması başlatılıyor...")
    
    asiri_alim_listesi = []