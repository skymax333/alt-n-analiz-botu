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
st.caption("XAU/USD • Ons Altın • Hacim + fiyat hareketi analizi")


def analiz_yap():

    altin = yf.download(
        "XAUUSD=X",
        period="5d",
        interval="1h",
        auto_adjust=False,
        progress=False
    )

    if altin.empty:
        st.error("XAU/USD verisi alınamadı.")
        return

    if isinstance(altin.columns, pd.MultiIndex):
        altin.columns = altin.columns.get_level_values(0)

    altin["Hacim_Ort"] = altin["Volume"].rolling(5).mean()

    altin["Sinyal"] = "BEKLE"

    al = (
        (altin["Close"] > altin["Open"]) &
        (altin["Close"] > altin["Close"].rolling(5).mean())
    )

    sat = (
        (altin["Close"] < altin["Open"]) &
        (altin["Close"] < altin["Close"].rolling(5).mean())
    )

    altin.loc[al, "Sinyal"] = "AL"
    altin.loc[sat, "Sinyal"] = "SAT"

    tablo = altin[
        ["Close", "Volume", "Hacim_Ort", "Sinyal"]
    ].copy()

    tablo = tablo.reset_index()

    tablo.columns = [
        "Tarih",
        "XAU/USD Fiyatı",
        "Hacim",
        "Hacim Ort.",
        "Sinyal"
    ]

    tablo["Tarih"] = (
        pd.to_datetime(tablo["Tarih"], utc=True)
        .dt.tz_convert("Europe/Istanbul")
        .dt.strftime("%d.%m.%Y %H:%M")
    )

    tablo["XAU/USD Fiyatı"] = tablo["XAU/USD Fiyatı"].round(2)
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
        "Son XAU/USD Fiyatı",
        f"{son['XAU/USD Fiyatı']:.2f} USD"
    )

    turkiye_saati = datetime.now(
        ZoneInfo("Europe/Istanbul")
    )

    st.caption(
        "Son güncelleme: "
        + turkiye_saati.strftime("%d.%m.%Y %H:%M:%S")
        + " (Türkiye saati)"
    )


if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()

analiz_yap()import streamlit as st
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
st.caption("XAU/USD • Ons Altın • Hacim + fiyat hareketi analizi")


def analiz_yap():

    altin = yf.download(
        "XAUUSD=X",
        period="5d",
        interval="1h",
        auto_adjust=False,
        progress=False
    )

    if altin.empty:
        st.error("XAU/USD verisi alınamadı.")
        return

    if isinstance(altin.columns, pd.MultiIndex):
        altin.columns = altin.columns.get_level_values(0)

    altin["Hacim_Ort"] = altin["Volume"].rolling(5).mean()

    altin["Sinyal"] = "BEKLE"

    al = (
        (altin["Close"] > altin["Open"]) &
        (altin["Close"] > altin["Close"].rolling(5).mean())
    )

    sat = (
        (altin["Close"] < altin["Open"]) &
        (altin["Close"] < altin["Close"].rolling(5).mean())
    )

    altin.loc[al, "Sinyal"] = "AL"
    altin.loc[sat, "Sinyal"] = "SAT"

    tablo = altin[
        ["Close", "Volume", "Hacim_Ort", "Sinyal"]
    ].copy()

    tablo = tablo.reset_index()

    tablo.columns = [
        "Tarih",
        "XAU/USD Fiyatı",
        "Hacim",
        "Hacim Ort.",
        "Sinyal"
    ]

    tablo["Tarih"] = (
        pd.to_datetime(tablo["Tarih"], utc=True)
        .dt.tz_convert("Europe/Istanbul")
        .dt.strftime("%d.%m.%Y %H:%M")
    )

    tablo["XAU/USD Fiyatı"] = tablo["XAU/USD Fiyatı"].round(2)
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
        "Son XAU/USD Fiyatı",
        f"{son['XAU/USD Fiyatı']:.2f} USD"
    )

    turkiye_saati = datetime.now(
        ZoneInfo("Europe/Istanbul")
    )

    st.caption(
        "Son güncelleme: "
        + turkiye_saati.strftime("%d.%m.%Y %H:%M:%S")
        + " (Türkiye saati)"
    )


if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()

analiz_yap()
