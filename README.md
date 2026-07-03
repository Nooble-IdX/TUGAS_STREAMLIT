# 🌸 SIAK Aromatic — Sistem Informasi Akuntansi Toko Parfum

Aplikasi web akuntansi berbasis **Streamlit**, dikembangkan dari *Laporan Praktikum Tugas 4 SIAK*
(pencatatan debit/kredit/saldo di Jupyter Notebook) untuk memenuhi ketentuan **UAS SIAK Genap 2025/2026**:
data master, transaksi, dan laporan dalam satu sistem web.

**Tema transaksi**: Usaha Toko Parfum "Aromatic".

## ✨ Fitur

| Modul | Isi |
|---|---|
| **Dashboard** | KPI (saldo kas, penjualan, pembelian, laba), grafik tren saldo, penjualan bulanan, produk terlaris, komposisi pengeluaran |
| **Data Master** | CRUD Produk (parfum & bahan baku), Pelanggan, Supplier |
| **Transaksi** | Penjualan (otomatis kurangi stok + catat jurnal debit), Pembelian (tambah stok + catat jurnal kredit), Jurnal Umum manual (modal, beban, dll — saldo berjalan otomatis) |
| **Laporan** | Laporan data master, Buku besar/jurnal (filter tanggal & kategori, unduh CSV), Laba rugi sederhana (dengan waterfall chart), Rekap penjualan & pembelian |

## 🗂️ Struktur Proyek

```
siak_parfum/
├── app.py                 # Entry point Streamlit (navigasi & semua halaman)
├── database.py             # Layer SQLite: skema, CRUD, query laporan/statistik, seed data
├── utils.py                 # Format rupiah & styling CSS modern
├── requirements.txt
├── .streamlit/config.toml   # Tema warna
└── aromatic_siak.db         # Dibuat otomatis saat pertama dijalankan
```

## 🚀 Menjalankan secara lokal

```bash
pip install -r requirements.txt
streamlit run app.py
```

Buka `http://localhost:8501` di browser. Data contoh (produk, pelanggan, supplier, transaksi)
otomatis terisi (seed) saat database masih kosong, sehingga aplikasi langsung siap didemokan.

## ☁️ Deploy ke Streamlit Community Cloud

1. Push folder ini ke repository GitHub (public/private).
2. Buka [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Pilih repo, branch, dan set **Main file path** = `app.py`.
4. Klik **Deploy**.

> **Catatan penyimpanan**: Streamlit Community Cloud menggunakan *ephemeral filesystem* —
> file `aromatic_siak.db` akan ter-reset setiap kali aplikasi di-redeploy/restart/sleep.
> Untuk demo/penilaian tugas ini tidak masalah (data seed otomatis terisi ulang). Jika ingin
> penyimpanan permanen, ganti `database.py` agar terhubung ke database eksternal (mis. Supabase/
> PostgreSQL) menggunakan `st.secrets` untuk kredensialnya.

## 👤 Identitas

- NIM: 202553012
- Nama: Ahmad Farih Maulana
- Kelas: A
- Program Studi Sistem Informasi, Fakultas Teknik, Universitas Muria Kudus
- Mata Kuliah: Sistem Informasi Akuntansi dan Keuangan (SOB104)
- Dosen: Dr. Ir. Arif Setiawan, S.Kom, M.Cs, IPM
