"""Dashboard Penjualan Produk BKMT Kabupaten Kotabaru (Streamlit).

Isi sama dengan dashboard Power BI dan laporan: 3 slicer, 5 kartu KPI, dan 10 visualisasi.
Kesepuluh grafik digambar oleh skrip yang sama dengan visual Python Power BI
(powerbi/python_visuals/), sehingga tampilannya identik.

Jalankan dari folder repository:
    pip install -r streamlit/requirements.txt
    streamlit run streamlit/app.py
"""
import io
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "powerbi" / "BKMT_PowerBI_Data.xlsx"
VIS = ROOT / "powerbi" / "python_visuals"

st.set_page_config(page_title="Dashboard Penjualan BKMT Kotabaru", page_icon="📊", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:3.4rem;padding-bottom:1rem;max-width:1900px}
[data-testid="stMetric"]{background:#fff;border:1px solid #E1E6EE;border-radius:8px;padding:10px 14px}
[data-testid="stMetricValue"]{font-size:1.6rem}
[data-testid="stImage"] img{border:1px solid #E1E6EE;border-radius:8px;background:#fff}
h1{font-size:1.65rem !important;margin-bottom:0 !important}
</style>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ data
@st.cache_data
def muat():
    x = pd.ExcelFile(DATA)
    P, K, C = x.parse("Penjualan"), x.parse("Kecamatan"), x.parse("Kalender")
    return P, K, C


P, K, C = muat()
BULAN = list(C.drop_duplicates("Bulan").sort_values("Bulan Urut")["Bulan"])
KATEGORI = ["Setelan", "Kain", "Selendang", "Tas", "Bros"]
KECAMATAN = list(K["Kecamatan"])
# Lebar (piksel) tiap visual pada kanvas Power BI 1920 × 1080; tinggi semuanya 280 piksel
LEBAR = {1: 760, 6: 560, 10: 536, 2: 600, 3: 680, 7: 576, 4: 520, 9: 560, 5: 340, 8: 424}


def rp(v):
    return "Rp" + format(int(round(v)), ",").replace(",", ".")


def jt(v):
    return ("Rp%.1f jt" % (v / 1e6)).replace(".", ",")


def ribuan(v):
    return format(int(round(v)), ",").replace(",", ".")


# ------------------------------------------------------------------ dataset tiap visual (meniru Power BI)
def dataset(n, bulan, kat, kec):
    """Tabel `dataset` yang akan dikirim Power BI ke visual Python ke-n, sesuai filter slicer."""
    p = P.copy()
    c = C.copy()
    if bulan != "Semua":
        c = c[c["Bulan"] == bulan]
        p = p[p["Tanggal"].isin(c["Tanggal"])]
    if kat != "Semua":
        p = p[p["Kategori Produk"] == kat]
    if kec != "Semua":
        p = p[p["Kecamatan"] == kec]
    pk = p.merge(c, on="Tanggal")
    tot = {"Total Penjualan": ("Total", "sum")}
    g = lambda df, by, **a: df.groupby(by, as_index=False).agg(**a)
    if n == 1:
        return g(pk, ["Bulan", "Bulan Parsial"], **tot)
    if n == 2:
        return g(p, ["Kategori Produk"], **tot)
    if n == 3:
        return g(p, ["Jenis Produk"], **tot)
    if n == 4:
        return g(p, ["Kecamatan"], **tot).merge(K[["Kecamatan", "Nama Peta", "Penduduk 2024"]], on="Kecamatan").rename(
            columns={"Penduduk 2024": "Penduduk"})
    if n == 5:
        return g(p, ["Saluran Penjualan"], **tot)
    if n == 6:
        return g(pk, ["Bulan", "Bulan Parsial", "Metode Pembayaran"], **tot)
    if n == 7:
        return g(p, ["Kategori Produk"], **{"Unit Terjual": ("Jumlah", "sum"), **tot})
    if n == 8:
        return g(p, ["Saluran Penjualan", "Metode Pembayaran"], **{"Jumlah Transaksi": ("ID Transaksi", "count")})
    if n == 9:
        return g(p, ["Kecamatan", "Kategori Produk"], **tot)
    if n == 10:  # DIVIDE([Total Penjualan], COUNTROWS(Kalender)) per hari
        h = g(pk, ["Hari"], t=("Total", "sum"))
        h["Penjualan per Hari"] = h["t"] / h["Hari"].map(c.groupby("Hari").size())
        return h[["Hari", "Penjualan per Hari"]]


@st.cache_data(show_spinner=False)
def gambar(n, bulan, kat, kec):
    """Jalankan skrip visual Python ke-n dan kembalikan PNG-nya (None bila tidak ada data)."""
    d = dataset(n, bulan, kat, kec)
    if d is None or d.empty:
        return None
    script = next(VIS.glob(f"v{n:02d}_*.py"))
    hasil = {}

    def tampilkan(*a, **k):
        fig = plt.gcf()
        fig.set_size_inches(LEBAR[n] / 72, 280 / 72)   # ukuran sama dengan visual di Power BI
        fig.tight_layout()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, facecolor="white")
        hasil["png"] = buf.getvalue()
        plt.close("all")

    asli = plt.show
    plt.show = tampilkan
    try:
        exec(compile(script.read_text(encoding="utf-8"), str(script), "exec"), {"dataset": d.copy(), "__name__": "__main__"})
    except Exception:
        plt.close("all")
        return None
    finally:
        plt.show = asli
    return hasil.get("png")


# ------------------------------------------------------------------ kepala + slicer
kiri, kanan = st.columns([1.15, 1])
with kiri:
    st.title("Dashboard Penjualan Produk BKMT Kabupaten Kotabaru")
    st.caption("Jun 2025 – Jun 2026 · 1.089 transaksi · isi dan nomor visual sama dengan laporan dan dashboard Power BI")
with kanan:
    s1, s2, s3 = st.columns(3)
    bulan = s1.selectbox("Bulan", ["Semua"] + BULAN)
    kat = s2.selectbox("Kategori Produk", ["Semua"] + KATEGORI)
    kec = s3.selectbox("Kecamatan", ["Semua"] + KECAMATAN)

# ------------------------------------------------------------------ KPI
p = P
if bulan != "Semua":
    p = p[p["Tanggal"].isin(C.loc[C["Bulan"] == bulan, "Tanggal"])]
if kat != "Semua":
    p = p[p["Kategori Produk"] == kat]
if kec != "Semua":
    p = p[p["Kecamatan"] == kec]
total, trx, unit = p["Total"].sum(), len(p), p["Jumlah"].sum()
setelan = p.loc[p["Kategori Produk"] == "Setelan", "Total"].sum()
m = st.columns(5)
m[0].metric("Total Penjualan", jt(total))
m[1].metric("Jumlah Transaksi", ribuan(trx))
m[2].metric("Unit Terjual", ribuan(unit))
m[3].metric("Rata-rata per Transaksi", rp(total / trx) if trx else "–")
m[4].metric("Porsi Setelan", (("%.1f%%" % (setelan / total * 100)).replace(".", ",")) if total else "–")

if trx == 0:
    st.warning("Tidak ada transaksi untuk kombinasi filter ini. Ubah salah satu slicer.")
    st.stop()


# ------------------------------------------------------------------ 10 visual, tiga baris seperti Power BI
def tampil(kolom, n):
    png = gambar(n, bulan, kat, kec)
    if png:
        kolom.image(png, width="stretch")
    else:
        kolom.info(f"Visual {n}: tidak ada data untuk filter ini.")


with st.spinner("Menggambar visual…"):
    for nomor in ([1, 6, 10], [2, 3, 7], [4, 9, 5, 8]):
        cols = st.columns([LEBAR[n] for n in nomor])
        for kol, n in zip(cols, nomor):
            tampil(kol, n)

st.caption("Sumber data: [Data Penjualan BKMT Kab. Kotabaru (Kaggle)](https://www.kaggle.com/datasets/mghazirakhmadi/data-penjualan-bkmt-kab-kotabaru) · "
           "Muhammad Ghazi Rakhmadi · 2410817310009 · UAS Visualisasi Data")
