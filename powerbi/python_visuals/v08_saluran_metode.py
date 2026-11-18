# Visual 8: Batang bertumpuk 100%
# Tarik field ini ke kotak 'Values' pada visual Python (semua tanpa diringkas / Don't summarize):
#   - Penjualan[Saluran Penjualan]
#   - Penjualan[Metode Pembayaran]
#   - [Jumlah Transaksi]  (measure)
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

URUT = ["WhatsApp", "Via Pengurus BKMT", "Langsung"]
pv = dataset.pivot_table(index="Saluran Penjualan", columns="Metode Pembayaran", values="Jumlah Transaksi", aggfunc="sum", fill_value=0)
pv = pv.reindex([s for s in URUT if s in pv.index] + [s for s in pv.index if s not in URUT])
pr = pv.div(pv.sum(axis=1), axis=0)
WARNA = {"Transfer": BLUE, "Tunai": ORANGE}

fig, ax = plt.subplots()
y = np.arange(len(pr))[::-1]; kiri = np.zeros(len(pr))
for m in pr.columns:
    v = pr[m].values; c = WARNA.get(m, GRAY_D)
    ax.barh(y, v, left=kiri, height=0.55, color=c, edgecolor="white", lw=1.5, label=m)
    for yi, l, vi in zip(y, kiri, v):
        if vi > 0.06: ax.text(l + vi / 2, yi, pct(vi), ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    kiri = kiri + v
ax.set_yticks(y); ax.set_yticklabels(pr.index); ax.set_xlim(0, 1)
ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=0)); ax.grid(False)
ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.1), fontsize=8.5)
judul(ax, "8 · Metode bayar di tiap saluran (% transaksi)")
selesai(fig)
