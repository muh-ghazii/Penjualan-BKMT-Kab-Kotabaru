"""Rakit dashboard web (dashboard/index.html + dashboard/data.js).

Isi dashboard web sama dengan dashboard Power BI: 3 slicer, 5 kartu KPI, dan 10 visualisasi
(nomor dan judul sama dengan laporan). Data diambil dari powerbi/BKMT_PowerBI_Data.xlsx dan
batas wilayah dari skrip visual Python peta (powerbi/python_visuals/v04_peta_kecamatan.py).

    python scripts/build_dashboard.py              # menulis dashboard/data.js dan dashboard/index.html
    python scripts/build_dashboard.py satu.html    # tambahan: versi satu file (data disisipkan)
"""
import base64, json, re, sys, zlib
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
X = ROOT / "powerbi/BKMT_PowerBI_Data.xlsx"
P = pd.read_excel(X, "Penjualan")
K = pd.read_excel(X, "Kecamatan")

dims = {
    "kec": list(K["Kecamatan"]),
    "kat": ["Setelan", "Kain", "Selendang", "Tas", "Bros"],
    "jenis": list(P.sort_values("Jenis Urut")["Jenis Produk"].drop_duplicates()),
    "sal": ["WhatsApp", "Via Pengurus BKMT", "Langsung"],
    "met": ["Transfer", "Tunai"],
}
idx = {k: {v: i for i, v in enumerate(vs)} for k, vs in dims.items()}
rows = [[r.Tanggal.strftime("%Y-%m-%d"), idx["kec"][r.Kecamatan], idx["kat"][r._4], idx["jenis"][r._5],
         idx["sal"][r._10], idx["met"][r._11], int(r.Jumlah), int(r.Total)]
        for r in P.itertuples()]

src = (ROOT / "powerbi/python_visuals/v04_peta_kecamatan.py").read_text(encoding="utf-8")
b64 = re.search(r'b64decode\("([^"]+)"\)', src).group(1)
peta = json.loads(zlib.decompress(base64.b64decode(b64)).decode())
geo = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"name": n}, "geometry": {"type": "MultiPolygon", "coordinates": [[ring] for ring in rings]}}
    for n, rings in peta.items()]}

data = {
    "dims": dims, "rows": rows,
    "penduduk": dict(zip(K["Kecamatan"], K["Penduduk 2024"].astype(int))),
    "namaPeta": dict(zip(K["Kecamatan"], K["Nama Peta"])),
    "mulai": "2025-06-23", "akhir": "2026-06-27", "geo": geo,
}
js = "window.BKMT=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
(ROOT / "dashboard/data.js").write_text(js, encoding="utf-8")

body = (ROOT / "dashboard/_body.html").read_text(encoding="utf-8")
(ROOT / "dashboard/index.html").write_text(body.replace("<!--DATA-->", '<script src="data.js"></script>'), encoding="utf-8")
if len(sys.argv) > 1:
    Path(sys.argv[1]).write_text(body.replace("<!--DATA-->", "<script>" + js + "</script>"), encoding="utf-8")
print("ok", len(rows), "baris")
