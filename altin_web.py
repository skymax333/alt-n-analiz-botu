import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, time
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Altın Analiz Botu",
    page_icon="🟡",
    layout="wide"
)

st.title("🟡 ALTIN ANALİZ BOTU")
st.caption("Gerçek Yahoo Finance verisi • Hacim + fiyat hareketi analizi")

TR_TZ = ZoneInfo("Europe/Istanbul")
NY_TZ = ZoneInfo("America/New_York")


def piyasa_durumu():
    simdi = datetime.now(NY_TZ)

    # Cumartesi
    if simdi.weekday() == 5:
        return False, "🔴 PİYASA KAPALI"

    # Pazar günü 18:00 ET'den önce kapalı
    if simdi.weekday() == 6 and simdi.time() < time(18, 0):
        return False, "🔴 PİYASA KAPALI"

    # Cuma 17:00 ET'den sonra kapalı
    if simdi.weekday() == 4 and simdi.time() >= time(17, 0):
        return False, "🔴 PİYASA KAPALI"

    # Her gün 17:00 - 18:00 ET bakım arası
    if time(17, 0) <= simdi.time() < time(18, 0):
        return False, "🔴 PİYASA KAPALI"

    return True, "🟢 PİYASA AÇIK"


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

    tablo = altin[
        ["Close", "Volume", "Hacim_Ort", "Sinyal"]
    ].copy()

    tablo = tablo.reset_index()

    tablo.columns = [
        "Tarih",
        "Altın Fiyatı",
        "Hacim",
        "Hacim Ort.",
        "Sinyal"
    ]

    # Türkiye saatine çevir
    tablo["Tarih"] = (
        pd.to_datetime(tablo["Tarih"], utc=True)
        .dt.tz_convert("Europe/Istanbul")
        .dt.strftime("%d.%m.%Y %H:%M")
    )

    tablo["Altın Fiyatı"] = tablo["Altın Fiyatı"].round(2)
    tablo["Hacim"] = tablo["Hacim"].round(0)
    tablo["Hacim Ort."] = tablo["Hacim Ort."].round(0)

    acik, durum = piyasa_durumu()

    if acik:
        st.success(durum)
    else:
        st.error(durum)

    st.dataframe(
        tablo.tail(20),
        use_container_width=True,
        hide_index=True
    )

    son = tablo.iloc[-1]

    st.subheader("Son Sinyal")

    if not acik:
        st.warning(
            "🔴 Piyasa kapalı. Yeni sinyal üretilmiyor."
        )
    elif son["Sinyal"] == "AL":
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
        + datetime.now(TR_TZ).strftime("%d.%m.%Y %H:%M:%S")
        + " 🇹🇷"
    )


if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()

analiz_yap()
