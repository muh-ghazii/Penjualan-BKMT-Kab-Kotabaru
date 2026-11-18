"""Dashboard Penjualan Produk BKMT Kabupaten Kotabaru (Streamlit, interaktif).

Fitur interaktif:
  - filter multi-pilih (bulan, kategori, kecamatan, saluran, metode pembayaran) di sidebar
  - 10 grafik Plotly: hover tooltip, zoom, pan, simpan sebagai gambar, klik legenda
  - klik batang/bagian grafik untuk memfilter seluruh dashboard (cross-filter)
  - tab tabel data + unduh CSV

Jalankan dari folder repository:
    pip install -r streamlit/requirements.txt
    streamlit run streamlit/app.py

Versi statis lama (gambar PNG matplotlib) ada di streamlit/app_statis.py.
"""
import base64
import json
import re
import zlib
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "powerbi" / "BKMT_PowerBI_Data.xlsx"
PETA_SRC = ROOT / "powerbi" / "python_visuals" / "v04_peta_kecamatan.py"

BLUE, ORANGE, AQUA = "#2A78D6", "#EB6834", "#1BAF7A"
GRAY, INK, INK2, GRID = "#C9C8C2", "#111827", "#4B5563", "#E6E5E0"
PALET = [BLUE, ORANGE, AQUA, "#8D8C86", "#9B59B6", "#F2B134", "#D6336C"]
HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.set_page_config(page_title="Dashboard Penjualan BKMT Kotabaru", layout="wide")
st.markdown("""
<style>
.block-container{padding-top:3rem;padding-bottom:1rem;max-width:1900px}
[data-testid="stMetric"]{background:#fff;border:1px solid #E1E6EE;border-radius:8px;padding:10px 14px}
[data-testid="stMetricValue"]{font-size:1.6rem}
h1{font-size:1.65rem !important;margin-bottom:0 !important}
</style>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ format
def rp(v):
    return "Rp" + format(int(round(v)), ",").replace(",", ".")


def jt(v, d=1):
    return ("Rp%.*f jt" % (d, v / 1e6)).replace(".", ",")


def ribuan(v):
    return format(int(round(v)), ",").replace(",", ".")


def pct(v, d=1):
    return ("%.*f%%" % (d, v * 100)).replace(".", ",")


# ------------------------------------------------------------------ data
@st.cache_data
def muat():
    x = pd.ExcelFile(DATA)
    return x.parse("Penjualan"), x.parse("Kecamatan"), x.parse("Kalender")


@st.cache_data
def muat_peta():
    """Batas kecamatan (GADM) yang tertanam di skrip visual 4 Power BI."""
    teks = PETA_SRC.read_text(encoding="utf-8")
    baris = re.search(r"^PETA = .*$", teks, re.M).group(0)
    ns = {"zlib": zlib, "base64": base64, "json": json}
    exec(baris, ns)
    return ns["PETA"]


P, K, C = muat()
PETA = muat_peta()
BULAN = list(C.drop_duplicates("Bulan").sort_values("Bulan Urut")["Bulan"])
PARSIAL = set(C.loc[C["Bulan Parsial"], "Bulan"])
KATEGORI = ["Setelan", "Kain", "Selendang", "Tas", "Bros"]
KECAMATAN = list(K["Kecamatan"])
SALURAN = sorted(P["Saluran Penjualan"].unique())
METODE = sorted(P["Metode Pembayaran"].unique())
NAMA_PETA = dict(zip(K["Kecamatan"], K["Nama Peta"]))

# ------------------------------------------------------------------ filter (sidebar + klik grafik)
FILTER_KEYS = ("f_bulan", "f_kat", "f_kec", "f_sal", "f_met")
for k in FILTER_KEYS:
    st.session_state.setdefault(k, [])
st.session_state.setdefault("ver", 0)   # naik tiap klik/reset supaya pilihan grafik ikut dibersihkan

# Klik pada grafik disimpan dulu di "_pending", lalu diterapkan di sini sebelum widget sidebar dibuat
# (Streamlit tidak mengizinkan mengubah nilai widget setelah widget itu dibuat).
if "_pending" in st.session_state:
    _k, _v = st.session_state.pop("_pending")
    if _v not in st.session_state[_k]:
        st.session_state[_k] = st.session_state[_k] + [_v]


def reset_filter():
    for k in FILTER_KEYS:
        st.session_state[k] = []
    st.session_state["ver"] += 1


with st.sidebar:
    st.header("Filter")
    st.caption("Kosongkan pilihan = tampilkan semua. Klik batang/irisan pada grafik juga ikut memfilter.")
    f_bulan = st.multiselect("Bulan", BULAN, key="f_bulan")
    f_kat = st.multiselect("Kategori Produk", KATEGORI, key="f_kat")
    f_kec = st.multiselect("Kecamatan", KECAMATAN, key="f_kec")
    f_sal = st.multiselect("Saluran Penjualan", SALURAN, key="f_sal")
    f_met = st.multiselect("Metode Pembayaran", METODE, key="f_met")
    st.button("Reset semua filter", width="stretch", on_click=reset_filter)

p = P.merge(C, on="Tanggal", how="left")
if f_bulan:
    p = p[p["Bulan"].isin(f_bulan)]
if f_kat:
    p = p[p["Kategori Produk"].isin(f_kat)]
if f_kec:
    p = p[p["Kecamatan"].isin(f_kec)]
if f_sal:
    p = p[p["Saluran Penjualan"].isin(f_sal)]
if f_met:
    p = p[p["Metode Pembayaran"].isin(f_met)]
kal = C[C["Bulan"].isin(f_bulan)] if f_bulan else C

# ------------------------------------------------------------------ kepala + KPI
st.title("Dashboard Penjualan Produk BKMT Kabupaten Kotabaru")
st.caption("Jun 2025 – Jun 2026 · %s dari %s transaksi sesuai filter · arahkan kursor ke grafik untuk detail, "
           "klik untuk memfilter" % (ribuan(len(p)), ribuan(len(P))))

total, trx, unit = p["Total"].sum(), len(p), p["Jumlah"].sum()
setelan = p.loc[p["Kategori Produk"] == "Setelan", "Total"].sum()
m = st.columns(5)
m[0].metric("Total Penjualan", jt(total))
m[1].metric("Jumlah Transaksi", ribuan(trx))
m[2].metric("Unit Terjual", ribuan(unit))
m[3].metric("Rata-rata per Transaksi", rp(total / trx) if trx else "–")
m[4].metric("Porsi Setelan", pct(setelan / total) if total else "–")

if trx == 0:
    st.warning("Tidak ada transaksi untuk kombinasi filter ini. Ubah atau reset filter di sidebar.")
    st.stop()


# ------------------------------------------------------------------ helper grafik
def rapikan(fig, judul, tinggi=420, legend=True):
    fig.update_layout(
        title=dict(text="<b>%s</b>" % judul, x=0.0, xanchor="left", font=dict(size=14, color=INK)),
        height=tinggi, margin=dict(l=10, r=10, t=60, b=10), template="plotly_white",
        font=dict(color=INK2), showlegend=legend, hoverlabel=dict(bgcolor="white"),
        legend=dict(orientation="h", y=-0.18, x=0),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def minta_filter(kolom_state, nilai):
    """Antrekan nilai ke filter sidebar, lalu jalankan ulang halaman."""
    if nilai is None:
        return
    if isinstance(nilai, (list, tuple)):
        nilai = nilai[0]
    if nilai in st.session_state[kolom_state]:
        return
    st.session_state["_pending"] = (kolom_state, nilai)
    st.session_state["ver"] += 1
    st.rerun()


def klik(fig, key, kolom_state, nilai_dari="y"):
    """Tampilkan grafik; bila batang/irisan diklik, nilainya ditambahkan ke filter di sidebar."""
    ev = st.plotly_chart(fig, key="%s_%d" % (key, st.session_state["ver"]), on_select="rerun",
                         selection_mode="points", width="stretch", config={"displaylogo": False})
    pts = ev.selection.points if ev and ev.selection else []
    if pts:
        pt = pts[0]
        minta_filter(kolom_state, pt.get(nilai_dari) if nilai_dari in pt else pt.get("label", pt.get("customdata")))


def grup(df, by, **agg):
    return df.groupby(by, as_index=False).agg(**agg)


# ------------------------------------------------------------------ 10 grafik, urut 1-10 dari kiri ke kanan, atas ke bawah
tab_dash, tab_data = st.tabs(["Dashboard", "Data transaksi"])
with tab_dash:
    c1, c2, c3 = st.columns(3)

    # 1
    with c1:
        d = grup(p, ["Bulan", "Bulan Urut"], T=("Total", "sum")).sort_values("Bulan Urut")
        d["parsial"] = d["Bulan"].isin(PARSIAL)
        fig = go.Figure(go.Scatter(
            x=d["Bulan"], y=d["T"], mode="lines+markers+text", line=dict(color=BLUE, width=2.5),
            marker=dict(size=9, color=["white" if x else BLUE for x in d["parsial"]], line=dict(color=BLUE, width=2)),
            text=[jt(v) for v in d["T"]], textposition="top center", textfont=dict(size=10),
            customdata=[[jt(v), "bulan parsial" if x else "bulan penuh"] for v, x in zip(d["T"], d["parsial"])],
            hovertemplate="<b>%{x}</b><br>Penjualan: %{customdata[0]}<br>%{customdata[1]}<extra></extra>"))
        pen = d[~d["parsial"]]
        jdl = "1 · Tren penjualan bulanan"
        if len(pen) > 1:
            hi, lo = pen.loc[pen["T"].idxmax()], pen.loc[pen["T"].idxmin()]
            jdl = "1 · Tren bulanan: tertinggi %s (%s), terendah %s (%s)" % (hi["Bulan"], jt(hi["T"]), lo["Bulan"], jt(lo["T"]))
        rapikan(fig, jdl, legend=False)
        fig.update_yaxes(range=[0, d["T"].max() * 1.2], tickprefix="Rp", ticksuffix=" jt", tickformat=".0f", tickvals=None)
        fig.update_yaxes(tickformat=",.0s")
        fig.update_xaxes(categoryorder="array", categoryarray=list(d["Bulan"]))
        fig.update_layout(annotations=[dict(text="○ = bulan parsial (belum sebulan penuh)", xref="paper", yref="paper",
                                            x=0, y=-0.22, showarrow=False, font=dict(size=10, color=INK2))])
        klik(fig, "g1", "f_bulan", "x")

    # 2
    with c2:
        d = grup(p, "Kategori Produk", T=("Total", "sum")).sort_values("T")
        fig = go.Figure(go.Bar(
            x=d["T"], y=d["Kategori Produk"], orientation="h", marker_color=BLUE,
            text=[jt(v) for v in d["T"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Penjualan: Rp%{x:,.0f}<extra></extra>"))
        rapikan(fig, "2 · Penjualan per kategori produk (klik untuk filter)", legend=False)
        fig.update_xaxes(range=[0, d["T"].max() * 1.25], tickformat=",.0s")
        klik(fig, "g2", "f_kat", "y")

    # 3
    with c3:
        d = grup(p, "Jenis Produk", T=("Total", "sum")).sort_values("T")
        fig = go.Figure(go.Bar(
            x=d["T"], y=d["Jenis Produk"], orientation="h", marker_color=BLUE,
            text=[jt(v) for v in d["T"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Penjualan: Rp%{x:,.0f}<extra></extra>"))
        rapikan(fig, "3 · Penjualan per jenis produk", legend=False)
        fig.update_xaxes(range=[0, d["T"].max() * 1.25], tickformat=",.0s")
        fig.update_yaxes(automargin=True)
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    c1, c2, c3 = st.columns(3)

    # 4
    with c1:
        pk = grup(p, "Kecamatan", T=("Total", "sum")).merge(K[["Kecamatan", "Nama Peta", "Penduduk 2024"]], on="Kecamatan")
        pk["Per Jiwa"] = pk["T"] / pk["Penduduk 2024"]
        per_peta = pk.groupby("Nama Peta")["T"].sum()
        vmax = max(per_peta.max(), 1)
        info = {n: pk[pk["Nama Peta"] == n] for n in per_peta.index}
        skala = [[0, "#CDE2FB"], [0.4, "#6DA7EC"], [0.7, "#2A78D6"], [1, "#104281"]]
        fig = go.Figure()
        for nama, cincin in PETA.items():
            ada = nama in per_peta.index
            nilai = per_peta[nama] if ada else 0
            if ada:
                baris = info[nama]
                tip = "<br>".join("%s: %s (%s)" % (r["Kecamatan"], jt(r["T"]), pct(r["T"] / total)) for _, r in baris.iterrows())
                hover = "<b>%s</b><br>%s<extra></extra>" % (nama, tip)
                warna = px.colors.sample_colorscale(skala, [nilai / vmax])[0]
            else:
                hover = "<b>%s</b><br>belum ada transaksi<extra></extra>" % nama
                warna = "#F1F0EC"
            for r in cincin:
                xs, ys = [q[0] for q in r], [q[1] for q in r]
                fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=warna, line=dict(color="white", width=0.6),
                                         hoveron="fills", hovertemplate=hover, showlegend=False))
        rapikan(fig, "4 · Peta penjualan per kecamatan", legend=False)
        fig.update_xaxes(visible=False, range=[115.45, 116.62], scaleanchor="y", scaleratio=1)
        fig.update_yaxes(visible=False, range=[-4.80, -2.25])
        fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})
        urut = pk.sort_values("T", ascending=False)
        st.caption("Terbesar: **%s** (%s). Biru lebih gelap = penjualan lebih besar; abu-abu = belum ada transaksi. "
                   "P. Laut Sigam digabung dengan P. Laut Utara pada peta GADM." % (urut.iloc[0]["Kecamatan"], pct(urut.iloc[0]["T"] / total)))

    # 5
    with c2:
        d = grup(p, "Saluran Penjualan", T=("Total", "sum")).sort_values("T", ascending=False)
        fig = go.Figure(go.Pie(
            labels=d["Saluran Penjualan"], values=d["T"], hole=0.55, sort=False, marker=dict(colors=PALET),
            textinfo="percent", hovertemplate="<b>%{label}</b><br>Rp%{value:,.0f} (%{percent})<extra></extra>"))
        rapikan(fig, "5 · Saluran penjualan")
        fig.update_layout(legend=dict(orientation="h", y=-0.05))
        klik(fig, "g5", "f_sal", "label")

    # 6
    with c3:
        d = grup(p, ["Bulan", "Bulan Urut", "Metode Pembayaran"], T=("Total", "sum")).sort_values("Bulan Urut")
        fig = px.bar(d, x="Bulan", y="T", color="Metode Pembayaran", barmode="stack",
                     color_discrete_map={"Transfer": BLUE, "Tunai": ORANGE},
                     category_orders={"Bulan": [b for b in BULAN if b in set(d["Bulan"])]},
                     custom_data=["Metode Pembayaran"])
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{customdata[0]}: Rp%{y:,.0f}<extra></extra>")
        rapikan(fig, "6 · Transfer vs tunai per bulan")
        fig.update_yaxes(title=None, tickformat=",.0s")
        fig.update_xaxes(title=None)
        klik(fig, "g6", "f_met", "customdata")

    c1, c2, c3 = st.columns(3)

    # 7
    with c1:
        d = grup(p, "Kategori Produk", U=("Jumlah", "sum"), T=("Total", "sum"))
        d["Porsi Unit"] = d["U"] / d["U"].sum()
        d["Porsi Nilai"] = d["T"] / d["T"].sum()
        d["Kategori Produk"] = pd.Categorical(d["Kategori Produk"], KATEGORI, ordered=True)
        d = d.sort_values("Kategori Produk")
        fig = go.Figure()
        fig.add_bar(name="Porsi unit terjual", x=d["Kategori Produk"], y=d["Porsi Unit"], marker_color=GRAY,
                    text=[pct(v, 0) for v in d["Porsi Unit"]], textposition="outside",
                    customdata=d[["U"]], hovertemplate="<b>%{x}</b><br>Porsi unit: %{y:.1%} (%{customdata[0]} unit)<extra></extra>")
        fig.add_bar(name="Porsi nilai penjualan", x=d["Kategori Produk"], y=d["Porsi Nilai"], marker_color=BLUE,
                    text=[pct(v, 0) for v in d["Porsi Nilai"]], textposition="outside",
                    customdata=d[["T"]], hovertemplate="<b>%{x}</b><br>Porsi nilai: %{y:.1%} (Rp%{customdata[0]:,.0f})<extra></extra>")
        rapikan(fig, "7 · Porsi unit vs porsi nilai penjualan per kategori")
        fig.update_layout(barmode="group")
        fig.update_yaxes(tickformat=".0%", range=[0, max(d["Porsi Unit"].max(), d["Porsi Nilai"].max()) * 1.25])
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    # 8
    with c2:
        d = grup(p, ["Saluran Penjualan", "Metode Pembayaran"], N=("ID Transaksi", "count"))
        fig = px.bar(d, x="Saluran Penjualan", y="N", color="Metode Pembayaran", barmode="group", text="N",
                     color_discrete_map={"Transfer": BLUE, "Tunai": ORANGE})
        fig.update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y} transaksi<extra></extra>", textposition="outside")
        rapikan(fig, "8 · Transaksi per saluran dan metode")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    # 9
    with c3:
        d = grup(p, ["Kecamatan", "Kategori Produk"], T=("Total", "sum"))
        z = d.pivot(index="Kecamatan", columns="Kategori Produk", values="T").reindex(index=KECAMATAN, columns=KATEGORI).fillna(0)
        teks = [[jt(v) if v else "" for v in row] for row in z.values]
        fig = go.Figure(go.Heatmap(
            z=z.values, x=list(z.columns), y=list(z.index), colorscale=skala, text=teks, texttemplate="%{text}",
            hovertemplate="<b>%{y}</b> · %{x}<br>Penjualan: Rp%{z:,.0f}<extra></extra>", colorbar=dict(title="Rp", thickness=10)))
        rapikan(fig, "9 · Penjualan kecamatan × kategori produk", legend=False)
        fig.update_yaxes(autorange="reversed", gridcolor="white")
        fig.update_xaxes(gridcolor="white")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

    c1 = st.container()

    # 10
    with c1:
        h = grup(p, ["Hari", "Hari Urut"], T=("Total", "sum")).sort_values("Hari Urut")
        h["N"] = h["Hari"].map(kal.groupby("Hari").size())
        h["Rata"] = h["T"] / h["N"]
        fig = go.Figure(go.Bar(
            x=h["Hari"], y=h["Rata"], marker_color=[ORANGE if v == h["Rata"].max() else BLUE for v in h["Rata"]],
            text=[jt(v) for v in h["Rata"]], textposition="outside",
            hovertemplate="<b>%{x}</b><br>Rata-rata per hari: Rp%{y:,.0f}<extra></extra>"))
        rapikan(fig, "10 · Rata-rata penjualan per hari dalam seminggu", legend=False)
        fig.update_xaxes(categoryorder="array", categoryarray=HARI)
        fig.update_yaxes(range=[0, h["Rata"].max() * 1.2], tickformat=",.0s")
        st.plotly_chart(fig, width="stretch", config={"displaylogo": False})

# ------------------------------------------------------------------ tab data
with tab_data:
    tampil = p[["ID Transaksi", "Tanggal", "Kecamatan", "Kategori Produk", "Jenis Produk", "Ukuran", "Jumlah",
                "Harga Satuan", "Total", "Saluran Penjualan", "Metode Pembayaran"]]
    st.dataframe(tampil, width="stretch", hide_index=True, height=520)
    st.download_button("Unduh data terfilter (CSV)", tampil.to_csv(index=False).encode("utf-8-sig"),
                       file_name="penjualan_bkmt_terfilter.csv", mime="text/csv")

st.caption("Sumber data: [Data Penjualan BKMT Kab. Kotabaru (Kaggle)](https://www.kaggle.com/datasets/mghazirakhmadi/data-penjualan-bkmt-kab-kotabaru) · "
           "Muhammad Ghazi Rakhmadi · 2410817310009 · UAS Visualisasi Data")
