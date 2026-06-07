import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# Sayfa Genişlik Ayarı
st.set_page_config(page_title="BIST 100 Algoritmik Analiz", layout="wide")

st.title("🤖 BIST 100 Saatlik Sinyal & Backtest (Geçmiş Testi) Robotu")
st.markdown("Bu program, seçtiğiniz hissenin **saatlik verilerini** inceler, indikatör stratejisine göre geçmişte ne kadar kazandıracağını hesaplar ve anlık öneri sunar.")

# Yan Menü Ayarları
st.sidebar.header("⚙️ Strateji ve Zaman Ayarları")

BIST_100_TICKERS = [
    "THYAO.IS", "TUPRS.IS", "EREGL.IS", "ASELS.IS", "AKBNK.IS", "BIMAS.IS", "KCHOL.IS", "SAHOL.IS", "ISCTR.IS", "SASA.IS",
    "AGROT.IS", "ASTOR.IS", "FROTO.IS", "GARAN.IS", "KONTR.IS", "KOZAL.IS", "MGROS.IS", "PETKM.IS", "PGSUS.IS", "SISE.IS"
]

secilen_hisse = st.sidebar.selectbox("Hisse Seçin:", BIST_100_TICKERS)

# Saatlik veride Yahoo Finance en fazla geçmiş 2 ayı (60 gün) destekler
st.sidebar.info("💡 Saatlik (1h) analizlerde Yahoo Finance kuralı gereği son 60 günlük geçmiş test edilir.")

# İndikatör Sınır Ayarları (Kullanıcı değiştirebilsin)
st.sidebar.subheader("🎯 RSI Strateji Sınırları")
rsi_alt_sinir = st.sidebar.slider("AL Sinyali İçin RSI Alt Sınır (Aşırı Satım)", 15, 40, 30)
rsi_ust_sinir = st.sidebar.slider("SAT Sinyali İçin RSI Üst Sınır (Aşırı Alım)", 60, 85, 70)

# Veri Çekme (Saatlik periyotta)
@st.cache_data
def saatlik_veri_indir(sembol):
    # period="2mo", interval="1h" -> Son 2 ayın saatlik verileri
    veri = yf.download(sembol, period="2mo", interval="1h")
    if isinstance(veri.columns, pd.MultiIndex):
        veri.columns = veri.columns.get_level_values(0)
    return veri

veri = saatlik_veri_indir(secilen_hisse)

if not veri.empty and len(veri) > 15:
    # 1. İndikatörleri Hesapla
    veri['RSI'] = RSIIndicator(close=veri['Close'], window=14).rsi()
    veri['SMA20'] = SMAIndicator(close=veri['Close'], window=20).sma_indicator()
    
    # Hafta sonu boşluklarını temizle
    veri = veri.dropna()

    # 2. BACKTEST (GEÇMİŞE DÖNÜK SİMÜLASYON) MOTORU
    # Strateji: RSI <= rsi_alt_sinir ise AL, RSI >= rsi_ust_sinir ise SAT
    pozisyon = 0  # 0: Nakit, 1: Hissede
    al_fiyatlari = []
    sat_fiyatlari = []
    sinyaller = [] # Görsel grafikte göstermek için
    
    # Al-Sat geçmişini tutacak liste
    islem_gecmisi = []
    
    for i in range(len(veri)):
        guncel_rsi = veri['RSI'].iloc[i]
        guncel_fiyat = veri['Close'].iloc[i]
        tarih = veri.index[i]
        
        # AL KOŞULU
        if guncel_rsi <= rsi_alt_sinir and pozisyon == 0:
            pozisyon = 1
            al_fiyatlari.append(guncel_fiyat)
            sinyaller.append("AL")
            islem_gecmisi.append({"Tarih/Saat": tarih, "İşlem": "🟢 AL (RSI Dip)", "Fiyat (TL)": round(guncel_fiyat, 2)})
        # SAT KOŞULU
        elif guncel_rsi >= rsi_ust_sinir and pozisyon == 1:
            pozisyon = 0
            sat_fiyatlari.append(guncel_fiyat)
            sinyaller.append("SAT")
            islem_gecmisi.append({"Tarih/Saat": tarih, "İşlem": "🔴 SAT (RSI Zirve)", "Fiyat (TL)": round(guncel_fiyat, 2)})
        else:
            sinyaller.append("BEKLE")
            
    # Toplam kârlılık hesabı
    strateji_kari = 0
    minimum_islem = min(len(al_fiyatlari), len(sat_fiyatlari))
    for k in range(minimum_islem):
        kar_orani = ((sat_fiyatlari[k] - al_fiyatlari[k]) / al_fiyatlari[k]) * 100
        strateji_kari += kar_orani
        
    # Basitçe hisseyi alıp bekleseydik ne olurdu? (Buy & Hold)
    hisse_normal_getiri = ((veri['Close'].iloc[-1] - veri['Close'].iloc[0]) / veri['Close'].iloc[0]) * 100

    # 3. ANNLIK DURUM VE ÖNERİ (En son muma bakarak)
    son_rsi = round(veri['RSI'].iloc[-1], 2)
    son_fiyat = round(veri['Close'].iloc[-1], 2)
    
    if son_rsi <= rsi_alt_sinir:
        oneri = "🟢 KUVVETLİ AL (Hisse Aşırı Ucuzladı)"
        oneri_renk = "green"
    elif son_rsi >= rsi_ust_sinir:
        oneri = "🔴 KUVVETLİ SAT (Hisse Şişti / Kâr Al)"
        oneri_renk = "red"
    else:
        oneri = "🟡 BEKLE / NÖTR (Yeni Sinyal Bekleniyor)"
        oneri_renk = "blue"

    # 4. EKRANA BASMA ALANI
    # Öneri Paneli
    st.markdown(f"### 🎯 Saatlik Güncel Sinyal Önerisi")
    st.info(f"**{secilen_hisse.replace('.IS','')}** için şu anki saatlik durum: **{oneri}** (Anlık Fiyat: {son_fiyat} TL | Güncel RSI: {son_rsi})")

    st.markdown("---")

    # Backtest Sonuç Kartları
    st.subheader("📊 Son 2 Aylık Geçmişe Dönük Performans Raporu")
    c1, c2, c3 = st.columns(3)
    c1.metric("Robotun Toplam Getirisi (% Periyot)", f"{round(strateji_kari, 2)}%", help="Robotun Al-Sat sinyallerine uysaydınız elde edeceğiniz toplam kâr")
    c2.metric("Hissede Bekleme Getirisi (Al-Unut)", f"{round(hisse_normal_getiri, 2)}%", help="Hisseyi 2 ay önce alıp hiç satmasaydınız ne kazanırdınız?")
    c3.metric("Toplam Yapılan Sinyal İşlemi", f"{minimum_islem * 2} Adet (Al+Sat)")

    st.markdown("---")

    # 5. GRAFİK ALANI (Gelişmiş Mum Grafik + Sinyal Noktaları)
    st.subheader("📈 Saatlik Grafik Üzerinde Al/Sat Noktaları")
    fig = go.Figure()

    # Mum Grafik (Candlestick)
    fig.add_trace(go.Candlestick(
        x=veri.index, open=veri['Open'], high=veri['High'], low=veri['Low'], close=veri['Close'],
        name="Saatlik Mumlar"
    ))

    # Grafiğe AL/SAT sinyal ikonlarını ekleme
    veri['Sinyal'] = sinyaller
    al_noktalari = veri[veri['Sinyal'] == "AL"]
    sat_noktalari = veri[veri['Sinyal'] == "SAT"]

    fig.add_trace(go.Scatter(
        x=al_noktalari.index, y=al_noktalari['Close'] * 0.98,
        mode='markers', marker=dict(color='lightgreen', size=12, symbol='triangle-up'), name='Robot AL Noktası'
    ))
    
    fig.add_trace(go.Scatter(
        x=sat_noktalari.index, y=sat_noktalari['Close'] * 1.02,
        mode='markers', marker=dict(color='red', size=12, symbol='triangle-down'), name='Robot SAT Noktası'
    ))

    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

    # 6. İŞLEM DETAY TABLOSU
    st.subheader("📋 Robotun Geçmişte Yaptığı Al-Sat İşlemlerinin Listesi")
    if islem_gecmisi:
        df_gecmis = pd.DataFrame(islem_gecmisi)
        st.dataframe(df_gecmis, use_container_width=True)
    else:
        st.write("Belirttiğiniz RSI sınırlarına son 2 ayda saatlik periyotta uyan geçmiş işlem bulunamadı. Yan menüden sınırları gevşetebilirsiniz (Örn: 35-65).")

else:
    st.error("Veri alınamadı veya seans dışı saatlik veri bulunmuyor.")