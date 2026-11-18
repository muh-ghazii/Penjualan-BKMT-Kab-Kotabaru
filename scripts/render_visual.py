"""Gambar ulang 10 visualisasi dashboard sebagai PNG (folder Gambar Visualisasi/), tanpa membuka Power BI.

Skrip ini meniru tabel `dataset` yang dikirim Power BI ke setiap visual Python (tanpa filter),
lalu menjalankan 10 skrip di powerbi/python_visuals/. Hasilnya identik dengan dashboard Power BI
dan dipakai di laporan, PPT, dan poster.

    python scripts/render_visual.py          # semua visual
    python scripts/render_visual.py 4 9      # hanya visual 4 dan 9
"""
import sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
x = pd.ExcelFile(ROOT / "powerbi/BKMT_PowerBI_Data.xlsx")
P, K, C = x.parse("Penjualan"), x.parse("Kecamatan"), x.parse("Kalender")
PK = P.merge(C, on="Tanggal")


def S(df, by, **agg):  # sama dengan measure DAX: kelompokkan lalu agregasikan
    return df.groupby(by, as_index=False).agg(**agg)


TOT = {"Total Penjualan": ("Total", "sum")}
D = {
    1: S(PK, ["Bulan", "Bulan Parsial"], **TOT),
    2: S(P, ["Kategori Produk"], **TOT),
    3: S(P, ["Jenis Produk"], **TOT),
    4: S(P, ["Kecamatan"], **TOT).merge(K[["Kecamatan", "Nama Peta", "Penduduk 2024"]], on="Kecamatan").rename(columns={"Penduduk 2024": "Penduduk"}),
    5: S(P, ["Saluran Penjualan"], **TOT),
    6: S(PK, ["Bulan", "Bulan Parsial", "Metode Pembayaran"], **TOT),
    7: S(P, ["Kategori Produk"], **{"Unit Terjual": ("Jumlah", "sum"), **TOT}),
    8: S(P, ["Saluran Penjualan", "Metode Pembayaran"], **{"Jumlah Transaksi": ("ID Transaksi", "count")}),
    9: S(P, ["Kecamatan", "Kategori Produk"], **TOT),
}
hari = S(PK, ["Hari"], t=("Total", "sum"))
hari["Penjualan per Hari"] = hari["t"] / hari["Hari"].map(C.groupby("Hari").size())  # DIVIDE([Total], COUNTROWS(Kalender))
D[10] = hari[["Hari", "Penjualan per Hari"]]

out = ROOT / "Gambar Visualisasi"
out.mkdir(exist_ok=True)
for n in [int(a) for a in sys.argv[1:]] or range(1, 11):
    f = next((ROOT / "powerbi/python_visuals").glob(f"v{n:02d}_*.py"))
    def show(*a, **k):
        fig = plt.gcf(); fig.set_size_inches(6.4, 3.6); plt.tight_layout()
        fig.savefig(out / (f.stem + ".png"), dpi=300, facecolor="white"); plt.close("all")
    plt.show = show
    exec(compile(f.read_text(encoding="utf-8"), str(f), "exec"), {"dataset": D[n].copy(), "__name__": "__main__"})
    print(f.stem + ".png")
