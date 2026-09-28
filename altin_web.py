import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Altın Analiz Botu",
    page_icon="🟡",
    layout="wide"
)

st.title("🟡 ALTIN ANALİZ BOTU")
st.caption("Altın (GC=F) • Ons altın vadeli fiyat analizi")


def analiz_yap():

    try:
        altin = yf.download(
            "GC=F",
            period="5d",
            interval="1h",
            auto_adjust=False,
            progress=False
        )

        if altin.empty:
            st.error("Altın verisi alınamadı.")
            return

        if isinstance(altin.columns, pd.MultiIndex):
            altin.columns = altin.columns.get_level_values(0)

        altin["Ortalama"] = altin["Close"].rolling(5).mean()

        altin["Sinyal"] = "BEKLE"

        al = (
            (altin["Close"] > altin["Open"]) &
            (altin["Close"] > altin["Ortalama"])
        )

        sat = (
            (altin["Close"] < altin["Open"]) &
            (altin["Close"] < altin["Ortalama"])
        )

        altin.loc[al, "Sinyal"] = "AL"
        altin.loc[sat, "Sinyal"] = "SAT"

        tablo = altin[
            ["Close", "Open", "Ortalama", "Sinyal"]
        ].copy()

        tablo = tablo.reset_index()

        tablo.columns = [
            "Tarih",
            "Altın Fiyatı",
            "Açılış",
            "Ortalama",
            "Sinyal"
        ]

        tablo["Tarih"] = (
            pd.to_datetime(tablo["Tarih"], utc=True)
            .dt.tz_convert("Europe/Istanbul")
            .dt.strftime("%d.%m.%Y %H:%M")
        )

        tablo["Altın Fiyatı"] = tablo["Altın Fiyatı"].round(2)
        tablo["Açılış"] = tablo["Açılış"].round(2)
        tablo["Ortalama"] = tablo["Ortalama"].round(2)

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
            f"{son['Altın Fiyatı']:.2f} USD/ons"
        )

        turkiye_saati = datetime.now(
            ZoneInfo("Europe/Istanbul")
        )

        st.caption(
            "Son güncelleme: "
            + turkiye_saati.strftime("%d.%m.%Y %H:%M:%S")
            + " (Türkiye saati)"
        )

        st.info(
            "Not: GC=F, Yahoo Finance üzerindeki altın vadeli işlem verisidir. "
            "Sinyaller teknik analiz amaçlıdır ve yatırım tavsiyesi değildir."
        )

    except Exception as hata:
        st.error("Veri alınırken hata oluştu.")
        st.code(str(hata))


if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()


analiz_yap()
