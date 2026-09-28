import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Altın Analiz Botu",
    page_icon="🟡",
    layout="wide"
)

st.title("🟡 ALTIN ANALİZ BOTU")
st.caption("Hacim + fiyat hareketine göre AL / SAT / BEKLE")

def analiz_yap():
    altin = yf.download(
        "GC=F",
        period="5d",
        interval="1h",
        auto_adjust=False,
        progress=False
    )

    if altin.empty:
        st.error("Veri alınamadı.")
        return

    if isinstance(altin.columns, pd.MultiIndex):
        altin.columns = altin.columns.get_level_values(0)

    altin["Hacim_Ort"] = altin["Volume"].rolling(5).mean()
    altin["Sinyal"] = "BEKLE"

    al = (
        (altin["Volume"] > altin["Hacim_Ort"]) &
        (altin["Close"] > altin["Open"])
    )

    sat = (
        (altin["Volume"] > altin["Hacim_Ort"]) &
        (altin["Close"] < altin["Open"])
    )

    altin.loc[al, "Sinyal"] = "AL"
    altin.loc[sat, "Sinyal"] = "SAT"

    tablo = altin[["Close", "Volume", "Hacim_Ort", "Sinyal"]].copy()
    tablo = tablo.reset_index()

    tablo.columns = ["Tarih", "Altın Fiyatı", "Hacim", "Hacim Ort.", "Sinyal"]

    tablo["Altın Fiyatı"] = tablo["Altın Fiyatı"].round(2)
    tablo["Hacim"] = tablo["Hacim"].round(0)
    tablo["Hacim Ort."] = tablo["Hacim Ort."].round(0)

    st.dataframe(
        tablo.tail(20),
        use_container_width=True,
        hide_index=True
    )

    son = tablo.iloc[-1]

    st.subheader("Son Sinyal")

    if son["Sinyal"] == "AL":
        st.success("🟢 AL")
    elif son["Sinyal"] == "SAT":
        st.error("🔴 SAT")
    else:
        st.warning("🟡 BEKLE")

    st.metric(
        "Son Altın Fiyatı",
        f"{son['Altın Fiyatı']:.2f}"
    )

    st.caption(
        "Son güncelleme: "
        + datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    )

if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()

analiz_yap()