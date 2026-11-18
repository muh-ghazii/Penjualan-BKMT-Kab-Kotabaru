# Visual Python di Power BI (alternatif untuk 10 visualisasi)

Sepuluh skrip `v01…v10` menggambar ulang 10 visualisasi Tabel 4 laporan UTS dengan matplotlib. Angkanya sama dengan visual bawaan dan dengan tabel cek di `PANDUAN_POWERBI.md` (sudah diuji dengan data simulasi dari `BKMT_PowerBI_Data.xlsx`, termasuk saat difilter satu kecamatan).

## Syarat (sekali saja)

1. Pasang Python 3.11 di komputer yang sama dengan Power BI Desktop (3.12 ke atas belum tentu didukung).
2. Di Command Prompt: `pip install pandas matplotlib`
3. Power BI → **File → Options and settings → Options → Python scripting** → pastikan *Detected Python home directories* menunjuk ke Python tadi.
4. Selesaikan dulu **Langkah 1–3** di `PANDUAN_POWERBI.md` (impor tiga tabel, relasi, measure). Skrip memakai measure ini, jadi buat minimal lima measure berikut dari `measures_DAX.txt`: `Total Penjualan`, `Jumlah Transaksi`, `Unit Terjual`, `Penjualan per Hari`, `Penduduk`.

## Membuat satu visual

1. Panel Visualisasi → ikon **Py** (baris kelima, di sebelah ikon R). Klik **Enable** jika diminta.
2. Tarik field ke kotak **Values** sesuai tabel di bawah. Field angka dari kolom (bukan measure) harus *Don't summarize*; di rancangan ini semua field angka adalah measure, jadi aman.
3. Di editor skrip (bagian bawah), hapus isi bawaan, tempel **seluruh isi** file skrip, lalu klik **Run script** (ikon ▶).
4. Atur posisi dan ukuran seperti di `Layout_Dashboard_PowerBI.png`.

| Skrip | Field untuk Values |
|---|---|
| v01 tren bulanan | `Kalender[Bulan]`, `Kalender[Bulan Parsial]`, `Total Penjualan` |
| v02 kategori | `Penjualan[Kategori Produk]`, `Total Penjualan` |
| v03 jenis produk | `Penjualan[Jenis Produk]`, `Total Penjualan` |
| v04 peta kecamatan | `Kecamatan[Kecamatan]`, `Kecamatan[Nama Peta]`, `Total Penjualan`, `Penduduk` |
| v05 donat saluran | `Penjualan[Saluran Penjualan]`, `Total Penjualan` |
| v06 transfer vs tunai | `Kalender[Bulan]`, `Kalender[Bulan Parsial]`, `Penjualan[Metode Pembayaran]`, `Total Penjualan` |
| v07 porsi unit vs nilai | `Penjualan[Kategori Produk]`, `Unit Terjual`, `Total Penjualan` |
| v08 saluran × metode | `Penjualan[Saluran Penjualan]`, `Penjualan[Metode Pembayaran]`, `Jumlah Transaksi` |
| v09 heatmap | `Penjualan[Kecamatan]`, `Penjualan[Kategori Produk]`, `Total Penjualan` |
| v10 per hari | `Kalender[Hari]`, `Penjualan per Hari` |

Visual 4 memuat batas kecamatan di dalam skripnya (±22 ribu karakter), jadi tidak butuh file TopoJSON. Batas editor skrip Power BI adalah 32.766 karakter, dan skrip ini masih di bawahnya.

## Yang berbeda dari visual bawaan

- **Gambar statis.** Klik pada batang atau irisan tidak memfilter visual lain, dan tidak ada tooltip. Visual Python tetap *mengikuti* slicer dan filter halaman, dan judulnya dihitung ulang di skrip.
- **Lebih lambat.** Setiap perubahan filter menjalankan ulang skrip (beberapa detik).
- **Hanya jalan di Power BI Desktop pada komputer yang punya Python.** Di Power BI Service, hanya paket tertentu yang didukung dan visual dirender ulang di server. Untuk tangkapan layar atau PDF dari Desktop, ini tidak jadi masalah.
- **Jangan tarik kolom urutan** (`Bulan Urut`, `Kategori Urut`, dan sejenisnya). Kolom angka yang diringkas dengan Sum akan menghasilkan urutan yang salah; skrip sudah mengurutkan sendiri dari nama bulan, hari, dan kategori.
- **Jangan campur `Kecamatan[Kecamatan]` dan `Penjualan[Kecamatan]`** dalam satu visual: namanya sama dan salah satunya akan tertimpa. v04 memakai tabel Kecamatan, v09 memakai tabel Penjualan.
- **Jika muncul `ServiceError_ExecuteSemanticQueryTransformError` dan rinciannya tidak berisi apa pun**, jangan mengubah skrip: periksa data. Penyebab yang pernah terjadi adalah tipe kolom yang salah di Power Query (`Bulan` terbaca sebagai tanggal, bukan teks). Perbaikannya ada di `PANDUAN_POWERBI.md`, Langkah 1 butir 4. Kolom pengurut (*Sort by column*) tidak diperlukan untuk visual Python.
