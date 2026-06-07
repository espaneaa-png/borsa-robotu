import time
import requests
import re
from flask import Flask
from threading import Thread

# Sunucunun kapanmaması için canlı tutma sistemi (Flask)
app = Flask('')

@app.route('/')
def home():
    return "Borsa Robotu Bulutta Aktif Çalışıyor!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# Telegram Bilgileriniz
TELEGRAM_TOKEN = "8942579926:AAEXPwqqxeo5kXozOSjc83OsrxONkMN5iz8"
CHAT_ID = "8686065642"

def bist100_listesi_al():
    try:
        url = "https://tr.wikipedia.org/wiki/BIST_100"
        yanit = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        hisseler = re.findall(r"<td>([A-Z0-9]{5})\s*</td>", yanit)
        if not hisseler:
            return ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS", "SASA.IS", "SISE.IS", "AKBNK.IS", "YKBNK.IS", "GARAN.IS", "ISCTR.IS"]
        return [f"{h}.IS" for h in set(hisseler)]
    except:
        return ["THYAO.IS", "ASELS.IS", "EREGL.IS", "TUPRS.IS"]

def rsi_hesapla(fiyatlar, periyot=14):
    if len(fiyatlar) <= periyot: return 50
    degisimler = [fiyatlar[i] - fiyatlar[i-1] for i in range(1, len(fiyatlar))]
    kazanclar = [d if d > 0 else 0 for d in degisimler]
    kayiplar = [-d if d < 0 else 0 for d in degisimler]
    ort_kazanc = sum(kazanclar[:periyot]) / periyot
    ort_kayip = sum(kayiplar[:periyot]) / periyot
    if ort_kayip == 0: return 100
    for i in range(periyot, len(degisimler)):
        ort_kazanc = (ort_kazanc * (periyot - 1) + kazanclar[i]) / periyot
        ort_kayip = (ort_kayip * (periyot - 1) + kayiplar[i]) / periyot
    if ort_kayip == 0: return 100
    rs = ort_kazanc / ort_kayip
    return 100 - (100 / (1 + rs))

def robot_dongusu():
    print("BIST 100 Bulut Tarama Robotu Baslatildi...")
    while True:
        bist100 = bist100_listesi_al()
        print(f"--- Toplam {len(bist100)} hisse taranıyor... ---")
        
        for sembol in bist100:
            try:
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sembol}?range=1mo&interval=1d"
                headers = {"User-Agent": "Mozilla/5.0"}
                yanit = requests.get(url, headers=headers).json()
                fiyatlar = yanit["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                fiyatlar = [f for f in fiyatlar if f is not None]
                
                if not fiyatlar: continue
                
                guncel_fiyat = fiyatlar[-1]
                guncel_rsi = rsi_hesapla(fiyatlar)
                
                if guncel_rsi < 30:
                    print(f"ALIS SINYALI: {sembol} RSI={guncel_rsi:.2f}")
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"🚨 BIST 100 ALIS SINYALI!\n{sembol} - Fiyat: {guncel_fiyat:.2f}\nRSI: {guncel_rsi:.2f}"})
                elif guncel_rsi > 70:
                    print(f"SATIS SINYALI: {sembol} RSI={guncel_rsi:.2f}")
                    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": f"📢 BIST 100 SATIS SINYALI!\n{sembol} - Fiyat: {guncel_fiyat:.2f}\nRSI: {guncel_rsi:.2f}"})
                
                time.sleep(1.5)
            except:
                pass
                
        print("Tarama bitti. 10 dakika bekleniyor...")
        time.sleep(600)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    robot_dongusu()