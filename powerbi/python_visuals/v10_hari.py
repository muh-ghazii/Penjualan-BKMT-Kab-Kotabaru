# Visual 10: Batang per hari
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Kalender[Hari]
#   - [Penjualan per Hari]  (measure)
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

HARI = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
d = dataset.groupby("Hari", as_index=False)["Penjualan per Hari"].sum()
d["_o"] = d["Hari"].map(lambda h: HARI.index(h) if h in HARI else 99)
d = d.sort_values("_o").reset_index(drop=True)
v = d["Penjualan per Hari"]

fig, ax = plt.subplots()
warna = [GRAY] * len(d); warna[int(v.idxmin())] = ORANGE       # hari terendah disorot
ax.bar(d["Hari"], v, color=warna, width=0.62)
for i, vi in enumerate(v):
    ax.text(i, vi + v.max() * 0.02, "%d" % round(vi / 1e3), ha="center", fontsize=8)
ax.set_ylim(0, v.max() * 1.15)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda t, _: "Rp%d rb" % round(t / 1e3)))
ax.grid(axis="x", visible=False)
lo, hi = d.loc[v.idxmin()], d.loc[v.idxmax()]
judul(ax, "10 · Terendah %s (%s/hari), tertinggi %s (%s/hari)" % (lo["Hari"], rb(lo["Penjualan per Hari"]), hi["Hari"], rb(hi["Penjualan per Hari"])))
catatan(fig, "Rata-rata penjualan per hari kalender; hari tanpa transaksi ikut dihitung. Label = Rp ribu.")
selesai(fig, 0.03)
