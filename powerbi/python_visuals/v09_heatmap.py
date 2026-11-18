# Visual 9: Heatmap
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Penjualan[Kecamatan]
#   - Penjualan[Kategori Produk]
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

URUT = ["Setelan", "Kain", "Selendang", "Tas", "Bros"]
pv = dataset.pivot_table(index="Kecamatan", columns="Kategori Produk", values="Total Penjualan", aggfunc="sum", fill_value=0)
pv = pv.reindex(columns=[k for k in URUT if k in pv.columns] + [k for k in pv.columns if k not in URUT])
pv = pv.loc[pv.sum(axis=1).sort_values(ascending=False).index]
pr = pv.div(pv.sum(axis=1), axis=0)

fig, ax = plt.subplots()
cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list("b", ["#F4F8FE", "#86B6EF", "#1C5CAB"])
ax.imshow(pr.values, cmap=cmap, vmin=0, vmax=0.8, aspect="auto")
for i in range(pr.shape[0]):
    for j in range(pr.shape[1]):
        v = pr.values[i, j]
        ax.text(j, i, "%d" % round(v * 100), ha="center", va="center", fontsize=8.5, color="white" if v > 0.45 else INK)
ax.set_xticks(range(pr.shape[1])); ax.set_xticklabels(pr.columns)
ax.set_yticks(range(pr.shape[0])); ax.set_yticklabels(pr.index)
ax.set_xticks(np.arange(-.5, pr.shape[1]), minor=True); ax.set_yticks(np.arange(-.5, pr.shape[0]), minor=True)
ax.grid(which="minor", color="white", lw=2); ax.grid(which="major", visible=False)
ax.tick_params(which="both", length=0)
for s in ax.spines.values(): s.set_visible(False)
judul(ax, "9 · Komposisi kategori di tiap kecamatan (tiap baris = 100%)")
catatan(fig, "Angka = % nilai penjualan di dalam tiap kecamatan.")
selesai(fig, 0.03)
