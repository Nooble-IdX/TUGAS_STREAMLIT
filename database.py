"""
database.py
Layer akses data (SQLite) untuk Sistem Informasi Akuntansi Toko Parfum "Aromatic".
Berisi skema tabel, fungsi CRUD data master, transaksi, jurnal, dan query laporan/statistik.
"""

import sqlite3
import os
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aromatic_siak.db")


# ---------------------------------------------------------------------------
# KONEKSI & INISIALISASI
# ---------------------------------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS produk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            kategori TEXT NOT NULL,
            satuan TEXT NOT NULL DEFAULT 'pcs',
            harga_beli INTEGER NOT NULL DEFAULT 0,
            harga_jual INTEGER NOT NULL DEFAULT 0,
            stok INTEGER NOT NULL DEFAULT 0,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS pelanggan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            alamat TEXT,
            telepon TEXT,
            email TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS supplier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kode TEXT UNIQUE NOT NULL,
            nama TEXT NOT NULL,
            kontak TEXT,
            alamat TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS jurnal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_transaksi TEXT UNIQUE NOT NULL,
            tanggal TEXT NOT NULL,
            kategori TEXT NOT NULL,
            keterangan TEXT NOT NULL,
            debit INTEGER NOT NULL DEFAULT 0,
            kredit INTEGER NOT NULL DEFAULT 0,
            saldo INTEGER NOT NULL DEFAULT 0,
            ref_tipe TEXT,
            ref_id INTEGER,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS pembelian (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_transaksi TEXT UNIQUE NOT NULL,
            tanggal TEXT NOT NULL,
            supplier_id INTEGER NOT NULL,
            produk_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            harga_satuan INTEGER NOT NULL,
            total INTEGER NOT NULL,
            keterangan TEXT,
            created_at TEXT,
            FOREIGN KEY (supplier_id) REFERENCES supplier(id),
            FOREIGN KEY (produk_id) REFERENCES produk(id)
        );

        CREATE TABLE IF NOT EXISTS penjualan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            no_transaksi TEXT UNIQUE NOT NULL,
            tanggal TEXT NOT NULL,
            pelanggan_id INTEGER NOT NULL,
            produk_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            harga_satuan INTEGER NOT NULL,
            total INTEGER NOT NULL,
            keterangan TEXT,
            created_at TEXT,
            FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(id),
            FOREIGN KEY (produk_id) REFERENCES produk(id)
        );
        """
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# HELPER NOMOR TRANSAKSI & SALDO
# ---------------------------------------------------------------------------

def _next_code(cur, table, prefix, width=3):
    cur.execute(f"SELECT COUNT(*) as c FROM {table}")
    n = cur.fetchone()["c"] + 1
    return f"{prefix}{n:0{width}d}"


def next_kode_produk():
    conn = get_connection()
    kode = _next_code(conn.cursor(), "produk", "PRF-")
    conn.close()
    return kode


def next_kode_pelanggan():
    conn = get_connection()
    kode = _next_code(conn.cursor(), "pelanggan", "PLG-")
    conn.close()
    return kode


def next_kode_supplier():
    conn = get_connection()
    kode = _next_code(conn.cursor(), "supplier", "SUP-")
    conn.close()
    return kode


def next_no_transaksi(prefix):
    """Menghasilkan nomor transaksi unik berbasis jumlah baris jurnal yang sudah memakai prefix ybs."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as c FROM jurnal WHERE no_transaksi LIKE ?", (f"{prefix}-%",))
    n = cur.fetchone()["c"] + 1
    conn.close()
    return f"{prefix}-{n:04d}"


def get_saldo_terakhir():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT saldo FROM jurnal ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row["saldo"] if row else 0


def tambah_jurnal(no_transaksi, tanggal, kategori, keterangan, debit, kredit, ref_tipe=None, ref_id=None):
    conn = get_connection()
    cur = conn.cursor()
    saldo_lama = get_saldo_terakhir()
    saldo_baru = saldo_lama + debit - kredit
    cur.execute(
        """INSERT INTO jurnal (no_transaksi, tanggal, kategori, keterangan, debit, kredit, saldo,
                                ref_tipe, ref_id, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (no_transaksi, str(tanggal), kategori, keterangan, debit, kredit, saldo_baru,
         ref_tipe, ref_id, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()
    return saldo_baru


# ---------------------------------------------------------------------------
# CRUD: PRODUK
# ---------------------------------------------------------------------------

def tambah_produk(kode, nama, kategori, satuan, harga_beli, harga_jual, stok):
    conn = get_connection()
    conn.execute(
        """INSERT INTO produk (kode, nama, kategori, satuan, harga_beli, harga_jual, stok, created_at)
           VALUES (?,?,?,?,?,?,?,?)""",
        (kode, nama, kategori, satuan, harga_beli, harga_jual, stok, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_produk_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM produk ORDER BY id", conn)
    conn.close()
    return df


def get_produk_list():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM produk ORDER BY nama").fetchall()
    conn.close()
    return rows


def update_stok_produk(produk_id, delta):
    conn = get_connection()
    conn.execute("UPDATE produk SET stok = stok + ? WHERE id = ?", (delta, produk_id))
    conn.commit()
    conn.close()


def hapus_produk(produk_id):
    conn = get_connection()
    conn.execute("DELETE FROM produk WHERE id = ?", (produk_id,))
    conn.commit()
    conn.close()


def update_produk(produk_id, nama, kategori, satuan, harga_beli, harga_jual, stok):
    conn = get_connection()
    conn.execute(
        """UPDATE produk SET nama=?, kategori=?, satuan=?, harga_beli=?, harga_jual=?, stok=?
           WHERE id=?""",
        (nama, kategori, satuan, harga_beli, harga_jual, stok, produk_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD: PELANGGAN
# ---------------------------------------------------------------------------

def tambah_pelanggan(kode, nama, alamat, telepon, email):
    conn = get_connection()
    conn.execute(
        """INSERT INTO pelanggan (kode, nama, alamat, telepon, email, created_at)
           VALUES (?,?,?,?,?,?)""",
        (kode, nama, alamat, telepon, email, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_pelanggan_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM pelanggan ORDER BY id", conn)
    conn.close()
    return df


def get_pelanggan_list():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM pelanggan ORDER BY nama").fetchall()
    conn.close()
    return rows


def hapus_pelanggan(pelanggan_id):
    conn = get_connection()
    conn.execute("DELETE FROM pelanggan WHERE id = ?", (pelanggan_id,))
    conn.commit()
    conn.close()


def update_pelanggan(pelanggan_id, nama, alamat, telepon, email):
    conn = get_connection()
    conn.execute(
        "UPDATE pelanggan SET nama=?, alamat=?, telepon=?, email=? WHERE id=?",
        (nama, alamat, telepon, email, pelanggan_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# CRUD: SUPPLIER
# ---------------------------------------------------------------------------

def tambah_supplier(kode, nama, kontak, alamat):
    conn = get_connection()
    conn.execute(
        "INSERT INTO supplier (kode, nama, kontak, alamat, created_at) VALUES (?,?,?,?,?)",
        (kode, nama, kontak, alamat, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_supplier_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM supplier ORDER BY id", conn)
    conn.close()
    return df


def get_supplier_list():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM supplier ORDER BY nama").fetchall()
    conn.close()
    return rows


def hapus_supplier(supplier_id):
    conn = get_connection()
    conn.execute("DELETE FROM supplier WHERE id = ?", (supplier_id,))
    conn.commit()
    conn.close()


def update_supplier(supplier_id, nama, kontak, alamat):
    conn = get_connection()
    conn.execute(
        "UPDATE supplier SET nama=?, kontak=?, alamat=? WHERE id=?",
        (nama, kontak, alamat, supplier_id),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# TRANSAKSI: PEMBELIAN
# ---------------------------------------------------------------------------

def catat_pembelian(tanggal, supplier_id, produk_id, qty, harga_satuan, keterangan):
    total = qty * harga_satuan
    no_transaksi = next_no_transaksi("PB")

    conn = get_connection()
    conn.execute(
        """INSERT INTO pembelian (no_transaksi, tanggal, supplier_id, produk_id, qty,
                                   harga_satuan, total, keterangan, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (no_transaksi, str(tanggal), supplier_id, produk_id, qty, harga_satuan, total,
         keterangan, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    update_stok_produk(produk_id, qty)
    tambah_jurnal(no_transaksi, tanggal, "Pembelian", keterangan or "Pembelian bahan/produk parfum",
                  debit=0, kredit=total, ref_tipe="pembelian", ref_id=None)
    return no_transaksi, total


def get_pembelian_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT pb.no_transaksi, pb.tanggal, s.nama AS supplier, p.nama AS produk,
                  pb.qty, pb.harga_satuan, pb.total, pb.keterangan
           FROM pembelian pb
           JOIN supplier s ON s.id = pb.supplier_id
           JOIN produk p ON p.id = pb.produk_id
           ORDER BY pb.id DESC""",
        conn,
    )
    conn.close()
    return df


# ---------------------------------------------------------------------------
# TRANSAKSI: PENJUALAN
# ---------------------------------------------------------------------------

def catat_penjualan(tanggal, pelanggan_id, produk_id, qty, harga_satuan, keterangan):
    total = qty * harga_satuan
    no_transaksi = next_no_transaksi("PJ")

    conn = get_connection()
    conn.execute(
        """INSERT INTO penjualan (no_transaksi, tanggal, pelanggan_id, produk_id, qty,
                                   harga_satuan, total, keterangan, created_at)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (no_transaksi, str(tanggal), pelanggan_id, produk_id, qty, harga_satuan, total,
         keterangan, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()

    update_stok_produk(produk_id, -qty)
    tambah_jurnal(no_transaksi, tanggal, "Penjualan", keterangan or "Penjualan produk parfum",
                  debit=total, kredit=0, ref_tipe="penjualan", ref_id=None)
    return no_transaksi, total


def get_penjualan_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT pj.no_transaksi, pj.tanggal, pl.nama AS pelanggan, p.nama AS produk,
                  pj.qty, pj.harga_satuan, pj.total, pj.keterangan
           FROM penjualan pj
           JOIN pelanggan pl ON pl.id = pj.pelanggan_id
           JOIN produk p ON p.id = pj.produk_id
           ORDER BY pj.id DESC""",
        conn,
    )
    conn.close()
    return df


# ---------------------------------------------------------------------------
# JURNAL UMUM (manual, mis. modal, sewa, gaji, listrik, dsb - mengikuti pola Tugas 4)
# ---------------------------------------------------------------------------

def catat_jurnal_manual(tanggal, kategori, keterangan, debit, kredit):
    no_transaksi = next_no_transaksi("JU")
    saldo = tambah_jurnal(no_transaksi, tanggal, kategori, keterangan, debit, kredit,
                           ref_tipe="manual", ref_id=None)
    return no_transaksi, saldo


def get_jurnal_df(start_date=None, end_date=None, kategori=None):
    import pandas as pd
    conn = get_connection()
    query = "SELECT no_transaksi, tanggal, kategori, keterangan, debit, kredit, saldo FROM jurnal WHERE 1=1"
    params = []
    if start_date:
        query += " AND date(tanggal) >= date(?)"
        params.append(str(start_date))
    if end_date:
        query += " AND date(tanggal) <= date(?)"
        params.append(str(end_date))
    if kategori and kategori != "Semua":
        query += " AND kategori = ?"
        params.append(kategori)
    query += " ORDER BY id ASC"
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


def get_kategori_jurnal_list():
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT kategori FROM jurnal ORDER BY kategori").fetchall()
    conn.close()
    return [r["kategori"] for r in rows]


def hapus_jurnal(jurnal_id):
    """Hapus 1 entri jurnal lalu hitung ulang saldo berjalan seluruh baris berikutnya."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM jurnal WHERE id = ?", (jurnal_id,))
    conn.commit()

    rows = cur.execute("SELECT id, debit, kredit FROM jurnal ORDER BY id ASC").fetchall()
    saldo = 0
    for r in rows:
        saldo = saldo + r["debit"] - r["kredit"]
        cur.execute("UPDATE jurnal SET saldo = ? WHERE id = ?", (saldo, r["id"]))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# STATISTIK / DASHBOARD
# ---------------------------------------------------------------------------

def get_stats():
    conn = get_connection()
    cur = conn.cursor()

    total_produk = cur.execute("SELECT COUNT(*) c FROM produk").fetchone()["c"]
    total_pelanggan = cur.execute("SELECT COUNT(*) c FROM pelanggan").fetchone()["c"]
    total_supplier = cur.execute("SELECT COUNT(*) c FROM supplier").fetchone()["c"]

    total_debit = cur.execute("SELECT COALESCE(SUM(debit),0) s FROM jurnal").fetchone()["s"]
    total_kredit = cur.execute("SELECT COALESCE(SUM(kredit),0) s FROM jurnal").fetchone()["s"]
    saldo_kas = get_saldo_terakhir()

    total_penjualan = cur.execute("SELECT COALESCE(SUM(total),0) s FROM penjualan").fetchone()["s"]
    total_pembelian = cur.execute("SELECT COALESCE(SUM(total),0) s FROM pembelian").fetchone()["s"]
    total_qty_terjual = cur.execute("SELECT COALESCE(SUM(qty),0) s FROM penjualan").fetchone()["s"]

    stok_menipis = cur.execute("SELECT COUNT(*) c FROM produk WHERE stok <= 5").fetchone()["c"]

    conn.close()
    return {
        "total_produk": total_produk,
        "total_pelanggan": total_pelanggan,
        "total_supplier": total_supplier,
        "total_debit": total_debit,
        "total_kredit": total_kredit,
        "saldo_kas": saldo_kas,
        "total_penjualan": total_penjualan,
        "total_pembelian": total_pembelian,
        "total_qty_terjual": total_qty_terjual,
        "stok_menipis": stok_menipis,
        "laba_kotor": total_penjualan - total_pembelian,
    }


def get_saldo_harian_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT tanggal, saldo FROM jurnal ORDER BY id ASC""", conn
    )
    conn.close()
    return df


def get_produk_terlaris_df(limit=10):
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT p.nama AS produk, SUM(pj.qty) AS total_qty, SUM(pj.total) AS total_omzet
           FROM penjualan pj JOIN produk p ON p.id = pj.produk_id
           GROUP BY pj.produk_id ORDER BY total_qty DESC LIMIT ?""",
        conn, params=[limit],
    )
    conn.close()
    return df


def get_kategori_pengeluaran_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT kategori, SUM(kredit) AS total_kredit
           FROM jurnal WHERE kredit > 0 GROUP BY kategori ORDER BY total_kredit DESC""",
        conn,
    )
    conn.close()
    return df


def get_penjualan_per_bulan_df():
    import pandas as pd
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT strftime('%Y-%m', tanggal) AS bulan, SUM(total) AS total_penjualan, SUM(qty) AS total_qty
           FROM penjualan GROUP BY bulan ORDER BY bulan""",
        conn,
    )
    conn.close()
    return df


def is_db_empty():
    conn = get_connection()
    cur = conn.cursor()
    c = cur.execute("SELECT COUNT(*) c FROM produk").fetchone()["c"]
    conn.close()
    return c == 0


# ---------------------------------------------------------------------------
# SEED DATA (mengacu pada Laporan Tugas 4 - tema Toko Parfum "Aromatic")
# ---------------------------------------------------------------------------

def seed_data():
    """Mengisi data awal supaya aplikasi langsung bisa didemokan / dinilai."""
    if not is_db_empty():
        return

    # --- Master: Produk ---
    produk_awal = [
        ("Parfum Aromatic Musk 50ml", "Parfum Pria", "botol", 45000, 85000, 40),
        ("Parfum Aromatic Rose 50ml", "Parfum Wanita", "botol", 45000, 85000, 35),
        ("Parfum Aromatic Ocean 30ml", "Parfum Pria", "botol", 30000, 55000, 50),
        ("Parfum Aromatic Vanilla 30ml", "Parfum Wanita", "botol", 30000, 55000, 45),
        ("Bibit Parfum Premium", "Bahan Baku", "liter", 400000, 0, 20),
        ("Botol Kemasan 50ml", "Bahan Baku", "pcs", 2500, 0, 300),
        ("Botol Kemasan 30ml", "Bahan Baku", "pcs", 1800, 0, 300),
        ("Alkohol Parfum 96%", "Bahan Baku", "liter", 35000, 0, 60),
    ]
    for nama, kategori, satuan, hb, hj, stok in produk_awal:
        tambah_produk(next_kode_produk(), nama, kategori, satuan, hb, hj, stok)

    # --- Master: Pelanggan ---
    pelanggan_awal = [
        ("Toko Wangi Sejahtera", "Jl. Sudirman No.12, Kudus", "0851-1000-2001", "wangisejahtera@mail.com"),
        ("Butik Melati", "Jl. AKBP R. Agil Kusumadya, Kudus", "0851-1000-2002", "butikmelati@mail.com"),
        ("Reseller Andi Pratama", "Jl. Loram Kulon, Kudus", "0851-1000-2003", "andi.reseller@mail.com"),
        ("Minimarket Segar", "Jl. Pantura, Kudus", "0851-1000-2004", "minisegar@mail.com"),
        ("Reseller Dewi Lestari", "Jl. Mejobo, Kudus", "0851-1000-2005", "dewi.reseller@mail.com"),
    ]
    for nama, alamat, telp, email in pelanggan_awal:
        tambah_pelanggan(next_kode_pelanggan(), nama, alamat, telp, email)

    # --- Master: Supplier ---
    supplier_awal = [
        ("CV Bibit Wangi Nusantara", "0812-3000-1001", "Surabaya, Jawa Timur"),
        ("PT Kemasan Jaya Abadi", "0812-3000-1002", "Semarang, Jawa Tengah"),
        ("UD Alkohol Murni", "0812-3000-1003", "Kudus, Jawa Tengah"),
    ]
    for nama, kontak, alamat in supplier_awal:
        tambah_supplier(next_kode_supplier(), nama, kontak, alamat)

    # --- Jurnal awal mengikuti pola Laporan Tugas 4 (modal, pembelian bahan, penjualan, beban) ---
    jurnal_awal = [
        ("2026-05-01", "Modal", "Hutang Bank - modal usaha awal", 500000000, 0),
        ("2026-05-02", "Pembelian", "Beli bibit parfum", 0, 50000000),
        ("2026-05-03", "Penjualan", "Penjualan parfum grosir", 75000000, 0),
        ("2026-05-04", "Pembelian", "Beli botol kemasan", 0, 12500000),
        ("2026-05-05", "Beban Operasional", "Bayar sewa tempat", 0, 8000000),
        ("2026-05-06", "Penjualan", "Penjualan eceran", 15000000, 0),
        ("2026-05-07", "Beban Operasional", "Bayar listrik dan internet", 0, 2500000),
        ("2026-05-08", "Pembelian", "Beli alkohol dan esens", 0, 18000000),
        ("2026-05-09", "Penjualan", "Pendapatan reseller", 30000000, 0),
        ("2026-05-10", "Beban Operasional", "Bayar gaji karyawan", 0, 10000000),
    ]
    for tgl, kategori, ket, debit, kredit in jurnal_awal:
        catat_jurnal_manual(tgl, kategori, ket, debit, kredit)

    # --- Transaksi penjualan & pembelian contoh agar laporan/statistik terisi ---
    produk_rows = get_produk_list()
    pelanggan_rows = get_pelanggan_list()
    supplier_rows = get_supplier_list()

    def pid(nama_part):
        for r in produk_rows:
            if nama_part in r["nama"]:
                return r["id"]
        return produk_rows[0]["id"]

    contoh_penjualan = [
        ("2026-05-11", 0, "Musk", 10, 85000),
        ("2026-05-13", 1, "Rose", 8, 85000),
        ("2026-05-15", 2, "Ocean", 15, 55000),
        ("2026-05-18", 3, "Vanilla", 12, 55000),
        ("2026-05-20", 4, "Musk", 6, 85000),
        ("2026-06-02", 0, "Rose", 9, 85000),
        ("2026-06-05", 2, "Ocean", 20, 55000),
        ("2026-06-10", 1, "Vanilla", 7, 55000),
    ]
    for tgl, pel_idx, prod_key, qty, harga in contoh_penjualan:
        catat_penjualan(tgl, pelanggan_rows[pel_idx]["id"], pid(prod_key), qty, harga,
                         f"Penjualan {prod_key} ke {pelanggan_rows[pel_idx]['nama']}")

    contoh_pembelian = [
        ("2026-05-02", 0, "Bibit Parfum Premium", 5, 400000),
        ("2026-05-04", 1, "Botol Kemasan 50ml", 200, 2500),
        ("2026-05-08", 2, "Alkohol Parfum", 30, 35000),
    ]
    for tgl, sup_idx, prod_key, qty, harga in contoh_pembelian:
        catat_pembelian(tgl, supplier_rows[sup_idx]["id"], pid(prod_key), qty, harga,
                         f"Pembelian {prod_key} dari {supplier_rows[sup_idx]['nama']}")
