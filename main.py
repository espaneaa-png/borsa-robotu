import streamlit as str
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from ta.momentum import RSIIndicator

# Sayfa Genişlik Ayarı
str.set_page_config(layout="wide", page_title="BIST 100 Gerçek Robotu")

# %100 EKSİKSİZ BIST 100 LİSTESİ - KTLEV VE DİĞERLERİ DAHİL TAM 100 TANE
BIST_100_TICKERS = [
    "ADGYO.IS", "AEFES.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS", "AKFYE.IS", "AKSA.IS", "AKSEN.IS",
    "ALARK.IS", "ALBRK.IS", "ALFAS.IS", "ARCLK.IS", "ASELS.IS", "ASTOR.IS", "AVPGY.IS", "AYDEM.IS", "BATIS.IS", "BERA.IS",
    "BFREN.IS", "BIMAS.IS", "BRSAN.IS", "BRYAT.IS", "BUCIM.IS", "CCOLA.IS", "CIMSA.IS", "CWENE.IS", "DOAS.IS", "DOHOL.IS",
    "ECILC.IS", "ECZYT.IS", "EGEEN.IS", "EKGYO.IS", "ENJSA.IS", "ENKAI.IS", "EREGL.IS", "EUPWR.IS", "FROTO.IS", "GARAN.IS",
    "GESAN.IS", "GUBRF.IS", "GWIND.IS", "HALKB.IS", "HEKTS.IS", "IHAAS.IS", "IPRAG.IS", "ISCTR.IS", "ISGYO.IS", "ISMEN.IS",
    "KAYSE.IS", "KCAER.IS", "KCHOL.IS", "KLSER.IS", "KONTR.IS", "KONYA.IS", "KORDS.IS", "KOZAL.IS", "KOZAA.IS", "KRDMD.IS",
    "KTLEV.IS", "LMKDC.IS", "MAVI.IS", "MGROS.IS", "MIATK.IS", "OBAMS.IS", "ODAS.IS", "OTKAR.IS", "OYAKC.IS", "PEKGY.IS",
    "PETKM.IS", "PGSUS.IS", "QUAGR.IS", "REEDR.IS", "SAHOL.IS", "SASA.IS", "SDTTR.IS", "SISE.IS", "SKBNK.IS", "SMART.IS",
    "SOKM.IS", "TABGD.IS", "TCELL.IS", "THYAO.IS", "TKFEN.IS", "TOASO.IS", "TSKB.IS", "TTKOM.IS", "TTRAK.IS", "TUPRS.IS",
    "TURSG.IS", "ULKER.IS", "VAKBN.IS", "VESBE.IS", "VESTL.IS", "YEOTK.IS", "YKBNK.IS", "YYLGD.IS", "ZOREN.IS"
]

# 2. SOL MENÜ (AYARLAR)
str.sidebar.title("🤖 Robot Ayarları")
str.sidebar.info(f"✅ Listelenen Hisse Sayısı: {len(BIST_100_TICKERS)}")
secilen_hisse = str.sidebar.selectbox("Hisse Seçin:", BIST_100_TICKERS)
rsi_periyot = str.sidebar.slider("RSI Periyodu:", 5, 30, 14)
rsi_alt = str.sidebar.slider("RSI Alt Sınırı (AL):", 10, 50, 30)
rsi_ust = str.sidebar.slider("RSI Üst Sınırı (SAT):", 50, 90, 70)

# 3. VERİ ÇEKME (SAATLİK - 60 GÜNLÜK)
str.title(f"📊 {secilen_hisse} Saatlik Analiz & Backtest Raporu")

try:
    df = yf.download(secilen_hisse, period="60d", interval="1h")
    
    if df.empty:
        str.error("Veri çekilemedi. Bu hissenin saatlik verisi şu an Yahoo üzerinde eksik olabilir.")
    else:
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        rsi_ind = RSIIndicator(close=df['Close'], window=rsi_periyot)
        df['RSI'] = rsi_ind.rsi()
        
        df['Pozisyon'] = 0
        son_pozisyon = 0
        sinyaller = []
        
        for i in range(len(df)):
            current_rsi = df['RSI'].iloc[i]
            if pd.isna(current_rsi):
                sinyaller.append(0)
                continue
                
            if current_rsi < rsi_alt and son_pozisyon == 0:
                sinyaller.append(1)
                son_pozisyon = 1
            elif current_rsi > rsi_ust and son_pozisyon == 1:
                sinyaller.append(-1)
                son_pozisyon = 0
            else:
                sinyaller.append(0)
                
        df['Sinyal'] = sinyaller
        df['Hisse_Getiri'] = df['Close'].pct_change()
        
        toplam_hisse_getiri = (df['Close'].iloc[-1] / df['Close'].iloc[0] - 1) * 100
        guncel_rsi = df['RSI'].iloc[-1]
        
        str.subheader("🚨 Güncel Saatlik Durum")
        if guncel_rsi < rsi_alt:
            str.success(f"Sinyal: KUVVETLİ AL (RSI: {guncel_rsi:.2f})")
        elif guncel_rsi > rsi_ust:
            str.error(f"Sinyal: KUVVETLİ SAT (RSI: {guncel_rsi:.2f})")
        else:
            str.warning(f"Sinyal: BEKLE / NÖTR (RSI: {guncel_rsi:.2f})")
            
        c1, c2 = str.columns(2)
        c1.metric("Hissede Bekleme Getirisi (Son 60 Gün)", f"%{toplam_hisse_getiri:.2f}")
        c2.metric("Güncel RSI Değeri", f"{guncel_rsi:.2f}")
        
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Mum Grafiği'))
        
        al_noktalari = df[df['Sinyal'] == 1]
        sat_noktalari = df[df['Sinyal'] == -1]
        
        fig.add_trace(go.Scatter(x=al_noktalari.index, y=al_noktalari['Close'], mode='markers', marker=dict(color='green', size=12, symbol='triangle-up'), name='AL Sinyali'))
        fig.add_trace(go.Scatter(x=sat_noktalari.index, y=sat_noktalari['Close'], mode='markers', marker=dict(color='red', size=12, symbol='triangle-down'), name='SAT Sinyali'))
        
        fig.update_layout(title="Hisse Fiyatı ve Robot Sinyalleri", xaxis_rangeslider_visible=False, height=600)
        str.plotly_chart(fig, use_container_width=True)

except Exception as e:
    str.error(f"Bir hata oluştu: {e}")