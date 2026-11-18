# Visual 3: Batang vertikal
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Penjualan[Jenis Produk]
#   - [Total Penjualan]  (measure)
# Tempel seluruh isi file ini ke editor skrip Python. Variabel 'dataset' dibuat otomatis oleh Power BI.

# ====== Gaya bersama (sama di semua visual) ======
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

BLUE, ORANGE, AQUA = "#2A78D6", "#EB6834", "#1BAF7A"
GRAY, GRAY_D = "#C9C8C2", "#8D8C86"
INK, INK2, GRID = "#111827", "#4B5563", "#E6E5E0"
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "font.size": 9, "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.titlepad": 10, "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "text.color": INK,
})

def koma(s): return s.replace(".", ",")
def jt(v, d=1): return koma("Rp%.*f jt" % (d, v / 1e6))
def rb(v): return "Rp" + format(int(round(v / 1e3)), ",").replace(",", ".") + " rb"
def pct(v, d=1): return koma("%.*f%%" % (d, v * 100))
def judul(ax, teks, lebar=62): ax.set_title(textwrap.fill(teks, lebar), loc="left")
def catatan(fig, teks, lebar=100): fig.text(0.01, 0.006, textwrap.fill(teks, lebar), fontsize=7, color=INK2, ha="left", va="bottom")
def selesai(fig, bawah=0.0):
    fig.tight_layout(rect=[0, bawah, 1, 1]); plt.show()
BLN = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "Mei": 5, "Jun": 6, "Jul": 7, "Agu": 8, "Sep": 9, "Okt": 10, "Nov": 11, "Des": 12}
def kunci_bulan(s): a, b = s.split(); return int(b) * 100 + BLN[a]   # "Nov 2025" -> 202511
# ====== Visual ======

SINGKAT = {"Setelan 3 in 1 (Baju, Rok, Selendang)": "Setelan\n3 in 1"}
d = dataset.groupby("Jenis Produk", as_index=False)["Total Penjualan"].sum().sort_values("Total Penjualan", ascending=False).reset_index(drop=True)
nama = [SINGKAT.get(n, textwrap.fill(n, 10)) for n in d["Jenis Produk"]]

fig, ax = plt.subplots()
warna = [GRAY] * len(d); warna[0] = BLUE                      # jenis terbesar disorot
ax.bar(nama, d["Total Penjualan"], color=warna, width=0.62)
for i, v in enumerate(d["Total Penjualan"]):
    ax.text(i, v + d["Total Penjualan"].max() * 0.02, koma("%.1f" % (v / 1e6)), ha="center", fontsize=8)
ax.set_ylim(0, d["Total Penjualan"].max() * 1.15)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: "Rp%d jt" % round(v / 1e6)))
ax.tick_params(axis="x", labelsize=7.5); ax.grid(axis="x", visible=False)
if len(d) >= 2:
    judul(ax, "3 · %s = %s× jenis produk terlaris kedua" % (d.loc[0, "Jenis Produk"].split(" (")[0], koma("%.1f" % (d.loc[0, "Total Penjualan"] / d.loc[1, "Total Penjualan"]))))
else:
    judul(ax, "3 · Penjualan per jenis produk")
catatan(fig, "Label = Rp juta.")
selesai(fig, 0.03)
