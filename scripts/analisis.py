"""
Analisis Data Penjualan Produk BKMT Kabupaten Kotabaru (UAS Visualisasi Data)
Muhammad Ghazi Rakhmadi - 2410817310009

Alur: Raw -> Validasi & Cleaning -> Processing (agregasi) -> KPI -> Uji pola
(Grafik dibuat oleh scripts/render_visual.py dari 10 skrip visual Python Power BI,
 dashboard web oleh scripts/build_dashboard.py.)
Jalankan dari folder root repository:
    python scripts/analisis.py
Output:
    data/processed/*.csv      tabel hasil agregasi (dipakai Power BI / laporan)
    data/processed/ringkasan_uji.json  hasil uji statistik
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/data_penjualan_bkmt_kotabaru.xlsx"
EXT = ROOT / "data/external"
OUT = ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)

BULAN_ID = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
HARI_ID = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]


# ================================================================ 1. RAW + VALIDASI
df = pd.read_excel(RAW)
validasi = {
    "baris": len(df), "kolom": df.shape[1],
    "nilai_kosong": int(df.isna().sum().sum()),
    "duplikat_baris": int(df.duplicated().sum()),
    "id_unik": bool(df["ID Transaksi"].is_unique),
    "total_konsisten": bool((df["Jumlah"] * df["Harga Satuan (Rp)"] == df["Total (Rp)"]).all()),
    "tanggal_min": str(df["Tanggal"].min().date()), "tanggal_maks": str(df["Tanggal"].max().date()),
}

# ================================================================ 2. CLEANING / FITUR
df = df.rename(columns={"Total (Rp)": "Total", "Harga Satuan (Rp)": "Harga"})
for c in ["Kecamatan", "Kategori Produk", "Jenis Produk", "Ukuran", "Saluran Penjualan", "Metode Pembayaran"]:
    df[c] = df[c].astype(str).str.strip()
df["Ukuran"] = df["Ukuran"].replace("-", "Tidak berlaku")
df["Bulan"] = df["Tanggal"].dt.to_period("M")
df["Bulan_str"] = df["Bulan"].astype(str)
df["Bulan_parsial"] = df["Bulan_str"].isin(["2025-06", "2026-06"])
df["Hari"] = df["Tanggal"].dt.dayofweek.map(dict(enumerate(HARI_ID)))
df["Hari_no"] = df["Tanggal"].dt.dayofweek
df["Tipe_Pesanan"] = np.where(df["Jumlah"] >= 5, "Borongan (>=5 unit)", "Reguler (1-4 unit)")
df["Wilayah"] = np.where(df["Kecamatan"] == "Pulau Laut Utara", "Pulau Laut Utara (lokasi toko)", "Luar Pulau Laut Utara")

# Catatan kualitas: Nama Pembeli tidak dapat dipakai sebagai ID pelanggan
nama_kec = df.groupby("Nama Pembeli")["Kecamatan"].nunique()
validasi["nama_unik"] = int(nama_kec.size)
validasi["nama_lebih_dari_1_kecamatan_pct"] = round(float((nama_kec > 1).mean() * 100), 1)

df.drop(columns=["Bulan"]).to_csv(OUT / "data_bersih.csv", index=False)

# ================================================================ 3. KPI
TOTAL, N, UNIT = int(df.Total.sum()), len(df), int(df.Jumlah.sum())
kpi = {
    "total_penjualan": TOTAL, "jumlah_transaksi": N, "unit_terjual": UNIT,
    "rata_rata_transaksi": round(TOTAL / N), "median_transaksi": int(df.Total.median()),
    "porsi_setelan_pct": round(df.loc[df["Kategori Produk"] == "Setelan", "Total"].sum() / TOTAL * 100, 1),
    "porsi_borongan_pct": round(df.loc[df.Jumlah >= 5, "Total"].sum() / TOTAL * 100, 1),
    "porsi_transfer_pct": round(df.loc[df["Metode Pembayaran"] == "Transfer", "Total"].sum() / TOTAL * 100, 1),
}

# ================================================================ 4. AGREGASI
def agg(by):
    g = df.groupby(by).agg(Transaksi=("Total", "size"), Unit=("Jumlah", "sum"), Penjualan=("Total", "sum"))
    g["Porsi_Penjualan_pct"] = (g.Penjualan / TOTAL * 100).round(1)
    g["Porsi_Transaksi_pct"] = (g.Transaksi / N * 100).round(1)
    g["Porsi_Unit_pct"] = (g.Unit / UNIT * 100).round(1)
    g["Rata2_Transaksi"] = (g.Penjualan / g.Transaksi).round(0)
    return g

bulanan = agg("Bulan_str")
bulanan["Hari_aktif"] = df.groupby("Bulan_str")["Tanggal"].nunique()
bulanan["Borongan"] = df[df.Jumlah >= 5].groupby("Bulan_str").Total.sum()
bulanan["Reguler"] = df[df.Jumlah < 5].groupby("Bulan_str").Total.sum()
bulanan = bulanan.fillna(0)
kategori = agg("Kategori Produk").sort_values("Penjualan", ascending=False)
jenis = agg("Jenis Produk").sort_values("Penjualan", ascending=False)
saluran = agg("Saluran Penjualan").sort_values("Penjualan", ascending=False)
metode = agg("Metode Pembayaran")
pend = pd.read_csv(EXT / "penduduk_kecamatan_kotabaru_2024.csv")
kec = agg("Kecamatan").sort_values("Penjualan", ascending=False)
kec = kec.join(pend.set_index("kecamatan_dataset")[["penduduk_2024"]])
kec["Penjualan_per_jiwa"] = (kec.Penjualan / kec.penduduk_2024).round(0)
kec["Peringkat_total"] = kec.Penjualan.rank(ascending=False).astype(int)
kec["Peringkat_per_jiwa"] = kec.Penjualan_per_jiwa.rank(ascending=False).astype(int)
sal_met = pd.crosstab(df["Saluran Penjualan"], df["Metode Pembayaran"], values=df.Total, aggfunc="sum")
sal_met_pct = (sal_met.div(sal_met.sum(axis=1), axis=0) * 100).round(1)
sal_met_trx_pct = (pd.crosstab(df["Saluran Penjualan"], df["Metode Pembayaran"], normalize="index") * 100).round(1)
wil_sal = pd.crosstab(df.Wilayah, df["Saluran Penjualan"], values=df.Total, aggfunc="sum")
wil_sal_pct = (wil_sal.div(wil_sal.sum(axis=1), axis=0) * 100).round(1)
kec_kat_pct = (pd.crosstab(df.Kecamatan, df["Kategori Produk"], values=df.Total, aggfunc="sum", normalize="index") * 100).round(1)
nhari = pd.Series(pd.date_range(df.Tanggal.min(), df.Tanggal.max())).dt.dayofweek.value_counts().sort_index()
hari = df.groupby("Hari_no").agg(Transaksi=("Total", "size"), Penjualan=("Total", "sum"))
hari["Jumlah_hari_kalender"] = nhari
hari["Penjualan_per_hari"] = (hari.Penjualan / hari.Jumlah_hari_kalender).round(0)
hari["Transaksi_per_hari"] = (hari.Transaksi / hari.Jumlah_hari_kalender).round(2)
hari.index = [HARI_ID[i] for i in hari.index]
setelan_ukuran = df[df["Kategori Produk"] == "Setelan"].groupby("Ukuran").agg(Unit=("Jumlah", "sum"), Penjualan=("Total", "sum"))
setelan_ukuran = setelan_ukuran.reindex(["M", "L", "XL", "XXL", "XXXL"])
setelan_ukuran["Porsi_Unit_pct"] = (setelan_ukuran.Unit / setelan_ukuran.Unit.sum() * 100).round(1)
borongan = agg("Tipe_Pesanan")
borongan_kat = df[df.Jumlah >= 5].groupby("Kategori Produk").agg(Transaksi=("Total", "size"), Penjualan=("Total", "sum"))
pay_bulan = pd.crosstab(df.Bulan_str, df["Metode Pembayaran"], values=df.Total, aggfunc="sum")

for name, t in {"penjualan_bulanan": bulanan, "penjualan_kategori": kategori, "penjualan_jenis_produk": jenis,
                "penjualan_saluran": saluran, "penjualan_metode": metode, "penjualan_kecamatan": kec,
                "saluran_x_metode_pct": sal_met_pct, "wilayah_x_saluran_pct": wil_sal_pct,
                "kecamatan_x_kategori_pct": kec_kat_pct, "penjualan_hari": hari, "setelan_per_ukuran": setelan_ukuran,
                "tipe_pesanan": borongan, "metode_bulanan": pay_bulan}.items():
    t.to_csv(OUT / f"{name}.csv")

# ================================================================ 5. UJI POLA (agar insight tidak sekadar kebetulan)
full = df[~df.Bulan_parsial]
mt = full.groupby("Bulan_str").Total.sum()
rng = np.random.default_rng(42)
v, lab = full.Total.values, full.Bulan_str.values
perm_sd = np.array([pd.Series(rng.permutation(v)).groupby(lab).sum().std() for _ in range(5000)])
uji = {
    "bulanan_sd_observasi": round(float(mt.std())), "bulanan_sd_acak_rata2": round(float(perm_sd.mean())),
    "bulanan_p_permutasi": round(float((perm_sd >= mt.std()).mean()), 3),
    "bulanan_rata2_bulan_penuh": round(float(mt.mean())),
    "korelasi_borongan_vs_total_bulanan": round(float(bulanan.loc[mt.index, "Borongan"].corr(mt)), 2),
    "hari_chi2": round(float(stats.chisquare(df.Hari_no.value_counts().sort_index(), nhari / nhari.sum() * N)[0]), 1),
    "hari_p": float(stats.chisquare(df.Hari_no.value_counts().sort_index(), nhari / nhari.sum() * N)[1]),
    "kecamatan_x_kategori_p": float(stats.chi2_contingency(pd.crosstab(df.Kecamatan, df["Kategori Produk"]))[1]),
    "kecamatan_x_saluran_p": float(stats.chi2_contingency(pd.crosstab(df.Kecamatan, df["Saluran Penjualan"]))[1]),
    "saluran_x_metode_p": float(stats.chi2_contingency(pd.crosstab(df["Saluran Penjualan"], df["Metode Pembayaran"]))[1]),
    "nilai_trx_antar_kecamatan_kruskal_p": float(stats.kruskal(*[g.Total.values for _, g in df.groupby("Kecamatan")])[1]),
}
(OUT / "ringkasan_uji.json").write_text(json.dumps({"validasi": validasi, "kpi": kpi, "uji": uji}, indent=2, ensure_ascii=False))

print(json.dumps({"validasi": validasi, "kpi": kpi, "uji": uji}, indent=1, ensure_ascii=False))
print(kec[["Penjualan", "penduduk_2024", "Penjualan_per_jiwa", "Peringkat_total", "Peringkat_per_jiwa"]])
print(wil_sal_pct); print(hari); print(setelan_ukuran); print(borongan); print(borongan_kat)
