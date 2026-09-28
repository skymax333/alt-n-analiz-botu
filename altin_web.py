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

    acilis = None
    kapanis = None

    # PAZAR
    if gun == 6:

        if saat < 17:
            durum = "KAPALI"

            acilis = simdi_ct.replace(
                hour=17, minute=0, second=0, microsecond=0
            )

        else:
            durum = "AÇIK"

            kapanis = simdi_ct + timedelta(days=1)
            kapanis = kapanis.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

    # PAZARTESİ - PERŞEMBE
    elif gun in [0, 1, 2, 3]:

        if saat < 16:

            durum = "AÇIK"

            kapanis = simdi_ct.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

        elif saat < 17:

            durum = "KAPALI"

            acilis = simdi_ct.replace(
                hour=17, minute=0, second=0, microsecond=0
            )

        else:

            durum = "AÇIK"

            kapanis = simdi_ct + timedelta(days=1)
            kapanis = kapanis.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

    # CUMA
    elif gun == 4:

        if saat < 16:

            durum = "AÇIK"

            kapanis = simdi_ct.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

        else:

            durum = "KAPALI"

            gun_sayisi = 2

            acilis = simdi_ct + timedelta(days=gun_sayisi)
            acilis = acilis.replace(
                hour=17, minute=0, second=0, microsecond=0
            )

    # CUMARTESİ
    else:

        durum = "KAPALI"

        acilis = simdi_ct + timedelta(days=1)
        acilis = acilis.replace(
            hour=17, minute=0, second=0, microsecond=0
        )

    # Geri sayım
    hedef = kapanis if durum == "AÇIK" else acilis

    kalan = hedef - simdi_ct

    toplam_saniye = max(0, int(kalan.total_seconds()))

    gun_sayisi = toplam_saniye // 86400
    saat_sayisi = (toplam_saniye % 86400) // 3600
    dakika_sayisi = (toplam_saniye % 3600) // 60

    geri_sayim = (
        f"{gun_sayisi} gün "
        f"{saat_sayisi} saat "
        f"{dakika_sayisi} dakika"
    )

    hedef_tr = hedef.astimezone(turkiye)

    return (
        durum,
        simdi_tr,
        geri_sayim,
        hedef_tr
    )


durum, turkiye_saati, geri_sayim, hedef_tr = piyasa_durumu()


# =========================
# PİYASA DURUMU EKRANI
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


if durum == "AÇIK":

    st.write(
        "⏳ Kapanışa kalan süre:",
        f"*{geri_sayim}*"
    )

    st.caption(
        "Kapanış: "
        + hedef_tr.strftime("%d.%m.%Y %H:%M")
        + " (Türkiye saati)"
    )

else:

    st.write(
        "⏳ Açılışa kalan süre:",
        f"*{geri_sayim}*"
    )

    st.caption(
        "Açılış: "
        + hedef_tr.strftime("%d.%m.%Y %H:%M")
        + " (Türkiye saati)"
    )


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

        st.info(
            "ℹ️ GC=F, Yahoo Finance üzerindeki altın vadeli işlem verisidir. "
            "AL/SAT/BEKLE sinyalleri teknik analiz amaçlıdır; "
            "yatırım tavsiyesi değildir."
        )

    except Exception as hata:

        st.error("Veri alınırken hata oluştu.")
        st.code(str(hata))


# =========================
# YENİLE
# =========================

if st.button("🔄 VERİYİ YENİLE"):
    st.rerun()


analiz_yap()
