# Visual 6: Line chart dua seri
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Kalender[Bulan]
#   - Kalender[Bulan Parsial]
#   - Penjualan[Metode Pembayaran]
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

d = dataset.copy()
d["Bulan Parsial"] = d["Bulan Parsial"].astype(bool)
d["_k"] = d["Bulan"].map(kunci_bulan)
pv = d.pivot_table(index=["_k", "Bulan"], columns="Metode Pembayaran", values="Total Penjualan", aggfunc="sum", fill_value=0).sort_index(level=0)
parsial = d.groupby("_k")["Bulan Parsial"].max()
WARNA = {"Transfer": BLUE, "Tunai": ORANGE}

fig, ax = plt.subplots()
x = np.arange(len(pv))
for m in pv.columns:
    y = pv[m].values; c = WARNA.get(m, GRAY_D)
    ax.plot(x, y, color=c, lw=2, label=m, zorder=2)
    for xi, yi, k in zip(x, y, pv.index.get_level_values(0)):
        ax.scatter(xi, yi, s=30, zorder=3, facecolor="white" if parsial.get(k, False) else c, edgecolor=c, lw=1.5)
ax.set_xticks(x); ax.set_xticklabels(pv.index.get_level_values(1), rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: "Rp%d jt" % round(v / 1e6)))
ax.set_ylim(0, max(pv.values.max() * 1.15, 1)); ax.grid(axis="x", visible=False)
ax.legend(frameon=False, ncol=2, loc="upper left", fontsize=8.5)
judul(ax, "6 · Transfer dan tunai per bulan")
catatan(fig, "○ = bulan parsial (data belum sebulan penuh).")
selesai(fig, 0.06)
