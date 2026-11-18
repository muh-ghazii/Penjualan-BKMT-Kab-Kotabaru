# Visual 5: Diagram donat
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Penjualan[Saluran Penjualan]
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

d = dataset.groupby("Saluran Penjualan", as_index=False)["Total Penjualan"].sum().sort_values("Total Penjualan", ascending=False).reset_index(drop=True)
tot = d["Total Penjualan"].sum()
WARNA = {"WhatsApp": AQUA, "Via Pengurus BKMT": GRAY_D, "Langsung": GRAY}
cols = [WARNA.get(n, BLUE) for n in d["Saluran Penjualan"]]

fig = plt.figure()
ax = fig.add_axes([0.0, 0.0, 0.40, 0.88]); ax.grid(False)
ax.pie(d["Total Penjualan"], colors=cols, startangle=90, counterclock=False, wedgeprops=dict(width=0.38, edgecolor="white", linewidth=2))
ax.text(0, 0.07, jt(tot), ha="center", va="center", fontsize=10, fontweight="bold")
ax.text(0, -0.15, "total", ha="center", va="center", fontsize=7.5, color=INK2)
ax.set_aspect("equal")
ax2 = fig.add_axes([0.42, 0.0, 0.58, 0.88]); ax2.set_axis_off(); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
for i, r in d.iterrows():
    y = 0.72 - i * 0.28
    ax2.add_patch(plt.Rectangle((0.0, y - 0.05), 0.05, 0.10, color=cols[i]))
    ax2.text(0.09, y + 0.05, r["Saluran Penjualan"], fontsize=9, fontweight="bold" if i == 0 else "normal", va="center")
    ax2.text(0.09, y - 0.06, "%s  ·  %s" % (pct(r["Total Penjualan"] / tot), jt(r["Total Penjualan"])), fontsize=8, color=INK2, va="center")
fig.suptitle("5 · %s saluran terbesar: %s penjualan" % (d.loc[0, "Saluran Penjualan"], pct(d.loc[0, "Total Penjualan"] / tot)),
             x=0.01, ha="left", fontsize=10.5, fontweight="bold")
plt.show()
