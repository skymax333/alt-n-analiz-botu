import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Altın Analiz Botu",
    page_icon="🟡",
    layout="wide"
)

st.title("🟡 ALTIN ANALİZ BOTU")
st.caption("Altın (GC=F) • Ons altın vadeli fiyat analizi")


# =========================
# PİYASA DURUMU
# =========================

def piyasa_durumu():

    turkiye = ZoneInfo("Europe/Istanbul")
    chicago = ZoneInfo("America/Chicago")

    simdi_tr = datetime.now(turkiye)
    simdi_ct = simdi_tr.astimezone(chicago)

    gun = simdi_ct.weekday()
    saat = simdi_ct.hour + simdi_ct.minute / 60

    # Cumartesi
    if gun == 5:
        return "KAPALI", simdi_tr, "Pazar 01:00 civarında açılması bekleniyor."

    # Pazar
    if gun == 6:
        if saat < 17:
            return "KAPALI", simdi_tr, "Pazar 17:00 CT'de açılır."
        else:
            return "AÇIK", simdi_tr, "Piyasa açık."

    # Pazartesi - Perşembe
    if gun in [0, 1, 2, 3]:

        # Günlük bakım arası
        if 16 <= saat < 17:
            return "KAPALI", simdi_tr, "Günlük bakım arası. 17:00 CT'de tekrar açılır."

        return "AÇIK", simdi_tr, "Piyasa açık."

    # Cuma
    if gun == 4:

        if saat >= 16:
            return "KAPALI", simdi_tr, "Hafta sonu nedeniyle piyasa kapandı."

        if saat < 16:
            return "AÇIK", simdi_tr, "Piyasa açık."

    return "KAPALI", simdi_tr, "Piyasa kapalı."


durum, turkiye_saati, durum_aciklama = piyasa_durumu()


# =========================
# EKRANDA PİYASA DURUMU
# =========================

st.subheader("📈 Piyasa Durumu")

col1, col2 = st.columns(2)

with col1:
    if durum == "AÇIK":
        st.success("🟢 PİYASA AÇIK")
    else:
        st.error("🔴 PİYASA KAPALI")

with col2:
    st.info(
        "🇹🇷 Türkiye saati: "
        + turkiye_saati.strftime("%d.%m.%Y %H:%M:%S")
    )

st.caption(durum_aciklama)


# =========================
# ALTIN ANALİZİ
# =========================

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

        st.subheader("📊 Altın Analizi")

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

        st.caption(
            "Son güncelleme: "
            + turkiye_saati.strftime("%d.%m.%Y %H:%M:%S")
            + " (Türkiye saati)"
        )

        st.info(
            "ℹ️ GC=F, Yahoo Finance üzerindeki altın vadeli işlem verisidir. "
            "AL/SAT/BEKLE sinyalleri teknik analiz amaçlıdır; "
            "yatırım tavsiyesi değildir."
        )

    except Exception as hata:

        st.error("Veri alınırken hata oluştu.")
        st.code(str(hata))


# =========================
# YENİLEME
# =========================

if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()


analiz_yap()
