"""
app.py
======
Sistem Informasi Akuntansi (SIAK) Toko Parfum "Aromatic"
Pengembangan dari Tugas 4 (jurnal debit/kredit/saldo Jupyter Notebook)
menjadi aplikasi web full-featured berbasis Streamlit untuk keperluan UAS.

Fitur:
- Data Master   : Produk, Pelanggan, Supplier (CRUD)
- Transaksi     : Pembelian, Penjualan, Jurnal Umum (otomatis hitung saldo berjalan)
- Laporan       : Laporan Master, Buku Besar/Jurnal, Laba Rugi, Penjualan & Pembelian
- Dashboard     : KPI & statistik interaktif (grafik tren, produk terlaris, dsb.)

Jalankan lokal   : streamlit run app.py
Identitas        : 202553012 - Ahmad Farih Maulana - Sistem Informasi - UMK
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime

import database as db
from utils import format_rupiah, inject_css, kpi_card, section_title

# ---------------------------------------------------------------------------
# KONFIGURASI HALAMAN
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SIAK Aromatic - Sistem Informasi Akuntansi Toko Parfum",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
db.init_db()
db.seed_data()

# ---------------------------------------------------------------------------
# SIDEBAR NAVIGASI
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 0.6rem 0 1rem 0;">
            <div style="font-size:2.4rem;">🌸</div>
            <div style="font-weight:700; font-size:1.15rem;">SIAK Aromatic</div>
            <div style="font-size:0.75rem; opacity:0.85;">Sistem Informasi Akuntansi<br/>Toko Parfum</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        from streamlit_option_menu import option_menu
        menu = option_menu(
            menu_title=None,
            options=["Dashboard", "Data Master", "Transaksi", "Laporan", "Tentang"],
            icons=["speedometer2", "box-seam", "receipt-cutoff", "bar-chart-line", "info-circle"],
            default_index=0,
            styles={
                "container": {"padding": "0", "background-color": "transparent"},
                "icon": {"font-size": "16px"},
                "nav-link": {"font-size": "14.5px", "margin": "3px 0", "border-radius": "10px"},
                "nav-link-selected": {"background-color": "#F2A65A", "color": "#3a2140", "font-weight": "700"},
            },
        )
    except ImportError:
        menu = st.radio(
            "Navigasi",
            ["Dashboard", "Data Master", "Transaksi", "Laporan", "Tentang"],
            label_visibility="collapsed",
        )

    st.markdown("---")
    st.caption("👤 202553012 - Ahmad Farih Maulana")
    st.caption("🏫 Sistem Informasi - UMK")
    st.caption("📚 UAS SIAK Genap 2025/2026")

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div class="app-header">
        <h1>🌸 SIAK Aromatic</h1>
        <p>Sistem Informasi Akuntansi Toko Parfum — Data Master, Transaksi, Jurnal, dan Laporan Terintegrasi</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ===========================================================================
# HALAMAN: DASHBOARD
# ===========================================================================

def halaman_dashboard():
    stats = db.get_stats()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Saldo Kas", format_rupiah(stats["saldo_kas"]), "Saldo berjalan terakhir")
    with c2:
        kpi_card("Total Penjualan", format_rupiah(stats["total_penjualan"]),
                  f"{stats['total_qty_terjual']} pcs terjual")
    with c3:
        kpi_card("Total Pembelian", format_rupiah(stats["total_pembelian"]), "Belanja bahan/produk")
    with c4:
        laba = stats["laba_kotor"]
        badge = "badge-green" if laba >= 0 else "badge-red"
        label = "Laba Kotor" if laba >= 0 else "Rugi Kotor"
        kpi_card(label, format_rupiah(laba), "Penjualan − Pembelian")

    st.write("")
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        kpi_card("Jumlah Produk", str(stats["total_produk"]), "Item dalam katalog")
    with c6:
        kpi_card("Jumlah Pelanggan", str(stats["total_pelanggan"]), "Pelanggan terdaftar")
    with c7:
        kpi_card("Jumlah Supplier", str(stats["total_supplier"]), "Mitra pemasok")
    with c8:
        warn = "⚠️ Perlu restock" if stats["stok_menipis"] > 0 else "✅ Stok aman"
        kpi_card("Stok Menipis", str(stats["stok_menipis"]), warn)

    st.write("")
    st.write("")

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        section_title("📈 Tren Saldo Kas Berjalan")
        df_saldo = db.get_saldo_harian_df()
        if not df_saldo.empty:
            df_saldo = df_saldo.reset_index().rename(columns={"index": "urutan"})
            fig = px.area(
                df_saldo, x="urutan", y="saldo",
                labels={"urutan": "Urutan Transaksi", "saldo": "Saldo (Rp)"},
            )
            fig.update_traces(line_color="#7B4B94", fillcolor="rgba(123,75,148,0.18)")
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10), height=320,
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data jurnal.")

        section_title("📊 Penjualan per Bulan")
        df_bulan = db.get_penjualan_per_bulan_df()
        if not df_bulan.empty:
            fig2 = px.bar(
                df_bulan, x="bulan", y="total_penjualan",
                labels={"bulan": "Bulan", "total_penjualan": "Total Penjualan (Rp)"},
                text_auto=".2s",
                color_discrete_sequence=["#F2A65A"],
            )
            fig2.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320,
                                plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Belum ada data penjualan.")

    with col_right:
        section_title("🏆 Produk Terlaris")
        df_top = db.get_produk_terlaris_df(8)
        if not df_top.empty:
            fig3 = px.bar(
                df_top.sort_values("total_qty"), x="total_qty", y="produk", orientation="h",
                labels={"total_qty": "Jumlah Terjual", "produk": ""},
                text_auto=True, color_discrete_sequence=["#7B4B94"],
            )
            fig3.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320,
                                plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Belum ada data penjualan.")

        section_title("🥧 Komposisi Pengeluaran")
        df_kat = db.get_kategori_pengeluaran_df()
        if not df_kat.empty:
            fig4 = px.pie(
                df_kat, names="kategori", values="total_kredit", hole=0.5,
                color_discrete_sequence=px.colors.sequential.Sunset,
            )
            fig4.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Belum ada data pengeluaran.")


# ===========================================================================
# HALAMAN: DATA MASTER
# ===========================================================================

def halaman_master():
    tab1, tab2, tab3 = st.tabs(["🧴 Produk Parfum", "🧑‍🤝‍🧑 Pelanggan", "🚚 Supplier"])

    # --- PRODUK ---
    with tab1:
        section_title("Tambah Produk Baru")
        with st.form("form_produk", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                nama = st.text_input("Nama Produk *")
                kategori = st.selectbox(
                    "Kategori",
                    ["Parfum Pria", "Parfum Wanita", "Parfum Unisex", "Bahan Baku", "Kemasan"],
                )
            with c2:
                satuan = st.selectbox("Satuan", ["botol", "pcs", "liter", "ml", "unit"])
                harga_beli = st.number_input("Harga Beli (Rp)", min_value=0, step=1000, value=0)
            with c3:
                harga_jual = st.number_input("Harga Jual (Rp)", min_value=0, step=1000, value=0)
                stok = st.number_input("Stok Awal", min_value=0, step=1, value=0)

            submitted = st.form_submit_button("💾 Simpan Produk", type="primary", use_container_width=True)
            if submitted:
                if not nama.strip():
                    st.error("Nama produk wajib diisi.")
                else:
                    kode = db.next_kode_produk()
                    db.tambah_produk(kode, nama.strip(), kategori, satuan, int(harga_beli), int(harga_jual), int(stok))
                    st.success(f"Produk '{nama}' berhasil ditambahkan dengan kode {kode}.")
                    st.rerun()

        section_title("Daftar Produk")
        df_produk = db.get_produk_df()
        if df_produk.empty:
            st.info("Belum ada data produk.")
        else:
            df_show = df_produk.copy()
            df_show["harga_beli"] = df_show["harga_beli"].apply(format_rupiah)
            df_show["harga_jual"] = df_show["harga_jual"].apply(format_rupiah)
            cols = ["kode", "nama", "kategori", "satuan", "harga_beli", "harga_jual", "stok"]
            st.dataframe(df_show[cols], use_container_width=True, hide_index=True)

            with st.expander("🗑️ Hapus Produk"):
                opsi = {f"{r.kode} - {r.nama}": r.id for r in df_produk.itertuples()}
                pilih = st.selectbox("Pilih produk", list(opsi.keys()), key="del_produk")
                if st.button("Hapus Produk Terpilih", key="btn_del_produk"):
                    db.hapus_produk(opsi[pilih])
                    st.success("Produk dihapus.")
                    st.rerun()

    # --- PELANGGAN ---
    with tab2:
        section_title("Tambah Pelanggan Baru")
        with st.form("form_pelanggan", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nama = st.text_input("Nama Pelanggan *")
                telepon = st.text_input("No. Telepon")
            with c2:
                alamat = st.text_area("Alamat", height=80)
                email = st.text_input("Email")

            submitted = st.form_submit_button("💾 Simpan Pelanggan", type="primary", use_container_width=True)
            if submitted:
                if not nama.strip():
                    st.error("Nama pelanggan wajib diisi.")
                else:
                    kode = db.next_kode_pelanggan()
                    db.tambah_pelanggan(kode, nama.strip(), alamat, telepon, email)
                    st.success(f"Pelanggan '{nama}' berhasil ditambahkan dengan kode {kode}.")
                    st.rerun()

        section_title("Daftar Pelanggan")
        df_pel = db.get_pelanggan_df()
        if df_pel.empty:
            st.info("Belum ada data pelanggan.")
        else:
            st.dataframe(
                df_pel[["kode", "nama", "alamat", "telepon", "email"]],
                use_container_width=True, hide_index=True,
            )
            with st.expander("🗑️ Hapus Pelanggan"):
                opsi = {f"{r.kode} - {r.nama}": r.id for r in df_pel.itertuples()}
                pilih = st.selectbox("Pilih pelanggan", list(opsi.keys()), key="del_pelanggan")
                if st.button("Hapus Pelanggan Terpilih", key="btn_del_pelanggan"):
                    db.hapus_pelanggan(opsi[pilih])
                    st.success("Pelanggan dihapus.")
                    st.rerun()

    # --- SUPPLIER ---
    with tab3:
        section_title("Tambah Supplier Baru")
        with st.form("form_supplier", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nama = st.text_input("Nama Supplier *")
                kontak = st.text_input("Kontak (No. HP/Telp)")
            with c2:
                alamat = st.text_area("Alamat", height=80)

            submitted = st.form_submit_button("💾 Simpan Supplier", type="primary", use_container_width=True)
            if submitted:
                if not nama.strip():
                    st.error("Nama supplier wajib diisi.")
                else:
                    kode = db.next_kode_supplier()
                    db.tambah_supplier(kode, nama.strip(), kontak, alamat)
                    st.success(f"Supplier '{nama}' berhasil ditambahkan dengan kode {kode}.")
                    st.rerun()

        section_title("Daftar Supplier")
        df_sup = db.get_supplier_df()
        if df_sup.empty:
            st.info("Belum ada data supplier.")
        else:
            st.dataframe(
                df_sup[["kode", "nama", "kontak", "alamat"]],
                use_container_width=True, hide_index=True,
            )
            with st.expander("🗑️ Hapus Supplier"):
                opsi = {f"{r.kode} - {r.nama}": r.id for r in df_sup.itertuples()}
                pilih = st.selectbox("Pilih supplier", list(opsi.keys()), key="del_supplier")
                if st.button("Hapus Supplier Terpilih", key="btn_del_supplier"):
                    db.hapus_supplier(opsi[pilih])
                    st.success("Supplier dihapus.")
                    st.rerun()


# ===========================================================================
# HALAMAN: TRANSAKSI
# ===========================================================================

def halaman_transaksi():
    tab1, tab2, tab3 = st.tabs(["🛒 Transaksi Penjualan", "📦 Transaksi Pembelian", "📝 Jurnal Umum"])

    # --- PENJUALAN ---
    with tab1:
        produk_rows = db.get_produk_list()
        pelanggan_rows = db.get_pelanggan_list()

        if not produk_rows or not pelanggan_rows:
            st.warning("Tambahkan data Produk dan Pelanggan terlebih dahulu di menu Data Master.")
        else:
            section_title("Input Transaksi Penjualan")
            with st.form("form_penjualan", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    tanggal = st.date_input("Tanggal", value=date.today())
                    pelanggan_opsi = {f"{r['kode']} - {r['nama']}": r["id"] for r in pelanggan_rows}
                    pel_pilih = st.selectbox("Pelanggan", list(pelanggan_opsi.keys()))
                with c2:
                    produk_opsi = {f"{r['kode']} - {r['nama']} (stok: {r['stok']})": r for r in produk_rows}
                    prod_pilih = st.selectbox("Produk", list(produk_opsi.keys()))
                    prod_row = produk_opsi[prod_pilih]

                c3, c4 = st.columns(2)
                with c3:
                    qty = st.number_input("Jumlah (Qty)", min_value=1, step=1, value=1)
                with c4:
                    harga = st.number_input(
                        "Harga Satuan (Rp)", min_value=0, step=1000,
                        value=int(prod_row["harga_jual"]),
                    )
                keterangan = st.text_input("Keterangan", value=f"Penjualan {prod_row['nama']}")

                st.caption(f"💰 Estimasi total: **{format_rupiah(qty * harga)}**")

                submitted = st.form_submit_button("✅ Simpan Transaksi Penjualan", type="primary", use_container_width=True)
                if submitted:
                    if qty > prod_row["stok"]:
                        st.error(f"Stok tidak mencukupi. Stok tersedia: {prod_row['stok']}.")
                    else:
                        no_trx, total = db.catat_penjualan(
                            tanggal, pelanggan_opsi[pel_pilih], prod_row["id"], int(qty), int(harga), keterangan
                        )
                        st.success(f"Transaksi {no_trx} tersimpan. Total: {format_rupiah(total)}")
                        st.rerun()

        section_title("Riwayat Penjualan")
        df_pj = db.get_penjualan_df()
        if df_pj.empty:
            st.info("Belum ada transaksi penjualan.")
        else:
            df_show = df_pj.copy()
            df_show["harga_satuan"] = df_show["harga_satuan"].apply(format_rupiah)
            df_show["total"] = df_show["total"].apply(format_rupiah)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

    # --- PEMBELIAN ---
    with tab2:
        produk_rows = db.get_produk_list()
        supplier_rows = db.get_supplier_list()

        if not produk_rows or not supplier_rows:
            st.warning("Tambahkan data Produk dan Supplier terlebih dahulu di menu Data Master.")
        else:
            section_title("Input Transaksi Pembelian")
            with st.form("form_pembelian", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    tanggal = st.date_input("Tanggal", value=date.today(), key="tgl_beli")
                    supplier_opsi = {f"{r['kode']} - {r['nama']}": r["id"] for r in supplier_rows}
                    sup_pilih = st.selectbox("Supplier", list(supplier_opsi.keys()))
                with c2:
                    produk_opsi = {f"{r['kode']} - {r['nama']}": r for r in produk_rows}
                    prod_pilih = st.selectbox("Produk / Bahan", list(produk_opsi.keys()), key="prod_beli")
                    prod_row = produk_opsi[prod_pilih]

                c3, c4 = st.columns(2)
                with c3:
                    qty = st.number_input("Jumlah (Qty)", min_value=1, step=1, value=1, key="qty_beli")
                with c4:
                    harga = st.number_input(
                        "Harga Satuan (Rp)", min_value=0, step=1000,
                        value=int(prod_row["harga_beli"]), key="harga_beli_input",
                    )
                keterangan = st.text_input("Keterangan", value=f"Pembelian {prod_row['nama']}", key="ket_beli")

                st.caption(f"💰 Estimasi total: **{format_rupiah(qty * harga)}**")

                submitted = st.form_submit_button("✅ Simpan Transaksi Pembelian", type="primary", use_container_width=True)
                if submitted:
                    no_trx, total = db.catat_pembelian(
                        tanggal, supplier_opsi[sup_pilih], prod_row["id"], int(qty), int(harga), keterangan
                    )
                    st.success(f"Transaksi {no_trx} tersimpan. Total: {format_rupiah(total)}")
                    st.rerun()

        section_title("Riwayat Pembelian")
        df_pb = db.get_pembelian_df()
        if df_pb.empty:
            st.info("Belum ada transaksi pembelian.")
        else:
            df_show = df_pb.copy()
            df_show["harga_satuan"] = df_show["harga_satuan"].apply(format_rupiah)
            df_show["total"] = df_show["total"].apply(format_rupiah)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

    # --- JURNAL UMUM ---
    with tab3:
        section_title("Input Jurnal Umum (mis. Modal, Sewa, Gaji, Listrik)")
        st.caption("Mengikuti pola Tugas 4: satu transaksi hanya mengisi salah satu sisi Debit atau Kredit.")
        with st.form("form_jurnal", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                tanggal = st.date_input("Tanggal", value=date.today(), key="tgl_jurnal")
                kategori = st.selectbox(
                    "Kategori",
                    ["Modal", "Beban Operasional", "Pendapatan Lain", "Hutang", "Piutang", "Lainnya"],
                )
            with c2:
                keterangan = st.text_input("Keterangan *")
                jenis = st.radio("Jenis Transaksi", ["Debit (menambah saldo)", "Kredit (mengurangi saldo)"], horizontal=True)

            nilai = st.number_input("Nilai (Rp)", min_value=0, step=10000, value=0)

            submitted = st.form_submit_button("✅ Simpan Jurnal", type="primary", use_container_width=True)
            if submitted:
                if not keterangan.strip():
                    st.error("Keterangan wajib diisi.")
                elif nilai <= 0:
                    st.error("Nilai harus lebih dari 0.")
                else:
                    debit = int(nilai) if jenis.startswith("Debit") else 0
                    kredit = int(nilai) if jenis.startswith("Kredit") else 0
                    no_trx, saldo = db.catat_jurnal_manual(tanggal, kategori, keterangan.strip(), debit, kredit)
                    st.success(f"Jurnal {no_trx} tersimpan. Saldo berjalan: {format_rupiah(saldo)}")
                    st.rerun()


# ===========================================================================
# HALAMAN: LAPORAN
# ===========================================================================

def halaman_laporan():
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🗂️ Laporan Data Master", "📒 Buku Besar / Jurnal", "💵 Laba Rugi Sederhana", "📈 Penjualan & Pembelian"]
    )

    # --- LAPORAN MASTER ---
    with tab1:
        section_title("Rekap Data Master")
        sub1, sub2, sub3 = st.tabs(["Produk", "Pelanggan", "Supplier"])
        with sub1:
            df = db.get_produk_df()
            if df.empty:
                st.info("Belum ada data.")
            else:
                df_show = df.copy()
                df_show["harga_beli"] = df_show["harga_beli"].apply(format_rupiah)
                df_show["harga_jual"] = df_show["harga_jual"].apply(format_rupiah)
                st.dataframe(df_show[["kode", "nama", "kategori", "satuan", "harga_beli", "harga_jual", "stok"]],
                             use_container_width=True, hide_index=True)
                st.download_button("⬇️ Unduh CSV Produk", df.to_csv(index=False).encode("utf-8"),
                                    "laporan_produk.csv", "text/csv")
        with sub2:
            df = db.get_pelanggan_df()
            if df.empty:
                st.info("Belum ada data.")
            else:
                st.dataframe(df[["kode", "nama", "alamat", "telepon", "email"]],
                             use_container_width=True, hide_index=True)
                st.download_button("⬇️ Unduh CSV Pelanggan", df.to_csv(index=False).encode("utf-8"),
                                    "laporan_pelanggan.csv", "text/csv")
        with sub3:
            df = db.get_supplier_df()
            if df.empty:
                st.info("Belum ada data.")
            else:
                st.dataframe(df[["kode", "nama", "kontak", "alamat"]],
                             use_container_width=True, hide_index=True)
                st.download_button("⬇️ Unduh CSV Supplier", df.to_csv(index=False).encode("utf-8"),
                                    "laporan_supplier.csv", "text/csv")

    # --- BUKU BESAR / JURNAL ---
    with tab2:
        section_title("Buku Besar (Jurnal Debit - Kredit - Saldo Berjalan)")
        c1, c2, c3 = st.columns(3)
        with c1:
            start_date = st.date_input("Dari tanggal", value=None, key="jurnal_start")
        with c2:
            end_date = st.date_input("Sampai tanggal", value=None, key="jurnal_end")
        with c3:
            kategori_list = ["Semua"] + db.get_kategori_jurnal_list()
            kategori_pilih = st.selectbox("Kategori", kategori_list)

        df_jurnal = db.get_jurnal_df(
            start_date if start_date else None,
            end_date if end_date else None,
            kategori_pilih,
        )

        if df_jurnal.empty:
            st.info("Tidak ada data jurnal pada filter yang dipilih.")
        else:
            df_show = df_jurnal.copy()
            df_show["debit"] = df_show["debit"].apply(format_rupiah)
            df_show["kredit"] = df_show["kredit"].apply(format_rupiah)
            df_show["saldo"] = df_show["saldo"].apply(format_rupiah)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            total_debit = df_jurnal["debit"].sum()
            total_kredit = df_jurnal["kredit"].sum()
            saldo_akhir = df_jurnal["saldo"].iloc[-1]

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Debit", format_rupiah(total_debit))
            m2.metric("Total Kredit", format_rupiah(total_kredit))
            m3.metric("Saldo Akhir", format_rupiah(saldo_akhir))

            st.download_button("⬇️ Unduh CSV Jurnal", df_jurnal.to_csv(index=False).encode("utf-8"),
                                "buku_besar_jurnal.csv", "text/csv")

    # --- LABA RUGI ---
    with tab3:
        section_title("Laporan Laba Rugi Sederhana")
        stats = db.get_stats()

        df_beban = db.get_kategori_pengeluaran_df()
        beban_operasional = 0
        if not df_beban.empty:
            beban_operasional = df_beban[df_beban["kategori"] == "Beban Operasional"]["total_kredit"].sum()

        pendapatan = stats["total_penjualan"]
        hpp = stats["total_pembelian"]
        laba_kotor = pendapatan - hpp
        laba_bersih = laba_kotor - beban_operasional

        laporan = pd.DataFrame(
            {
                "Komponen": ["Pendapatan Penjualan", "Harga Pokok Pembelian (HPP)", "Laba Kotor",
                             "Beban Operasional", "Laba/Rugi Bersih"],
                "Nilai": [pendapatan, -hpp, laba_kotor, -beban_operasional, laba_bersih],
            }
        )
        laporan["Nilai (Rp)"] = laporan["Nilai"].apply(format_rupiah)
        st.dataframe(laporan[["Komponen", "Nilai (Rp)"]], use_container_width=True, hide_index=True)

        warna = "normal" if laba_bersih >= 0 else "inverse"
        st.metric("Estimasi Laba/Rugi Bersih", format_rupiah(laba_bersih), delta=None)

        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total", "relative", "total"],
            x=["Pendapatan", "HPP", "Laba Kotor", "Beban Ops.", "Laba Bersih"],
            y=[pendapatan, -hpp, 0, -beban_operasional, 0],
            connector={"line": {"color": "#bbb"}},
            decreasing={"marker": {"color": "#C0392B"}},
            increasing={"marker": {"color": "#1E8449"}},
            totals={"marker": {"color": "#7B4B94"}},
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=380, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    # --- LAPORAN PENJUALAN & PEMBELIAN ---
    with tab4:
        section_title("Rekap Penjualan per Produk")
        df_top = db.get_produk_terlaris_df(20)
        if df_top.empty:
            st.info("Belum ada data penjualan.")
        else:
            df_show = df_top.copy()
            df_show["total_omzet"] = df_show["total_omzet"].apply(format_rupiah)
            st.dataframe(df_show, use_container_width=True, hide_index=True)

        section_title("Grafik Penjualan per Bulan")
        df_bulan = db.get_penjualan_per_bulan_df()
        if not df_bulan.empty:
            fig = px.line(df_bulan, x="bulan", y="total_penjualan", markers=True,
                          labels={"bulan": "Bulan", "total_penjualan": "Total Penjualan (Rp)"},
                          color_discrete_sequence=["#7B4B94"])
            fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=320, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Belum ada data penjualan bulanan.")

        section_title("Riwayat Pembelian Lengkap")
        df_pb = db.get_pembelian_df()
        if df_pb.empty:
            st.info("Belum ada data pembelian.")
        else:
            df_show = df_pb.copy()
            df_show["harga_satuan"] = df_show["harga_satuan"].apply(format_rupiah)
            df_show["total"] = df_show["total"].apply(format_rupiah)
            st.dataframe(df_show, use_container_width=True, hide_index=True)


# ===========================================================================
# HALAMAN: TENTANG
# ===========================================================================

def halaman_tentang():
    section_title("Tentang Aplikasi")
    st.markdown(
        """
        **SIAK Aromatic** adalah pengembangan dari *Laporan Praktikum Tugas 4 — Sistem Informasi Akuntansi*
        (pencatatan debit, kredit, dan saldo berjalan berbasis Python Jupyter Notebook) menjadi aplikasi
        web akuntansi yang fungsional menggunakan **Python + Streamlit**, sesuai ketentuan UAS mata kuliah
        Sistem Informasi Akuntansi dan Keuangan.

        **Tema transaksi**: Usaha Toko Parfum "Aromatic" (produksi & penjualan parfum, reseller, dan grosir).

        ### Cakupan Fitur
        1. **Data Master** — Produk parfum/bahan baku, Pelanggan, dan Supplier.
        2. **Transaksi** — Penjualan, Pembelian, dan Jurnal Umum (modal, beban, dsb.), dengan
           perhitungan saldo berjalan otomatis (`saldo = saldo_sebelumnya + debit - kredit`),
           mengikuti logika inti dari Tugas 4.
        3. **Laporan** — Laporan data master, buku besar/jurnal (dengan filter tanggal & kategori),
           laba rugi sederhana, serta rekap penjualan & pembelian — semua dapat diunduh sebagai CSV.
        4. **Dashboard Statistik** — KPI ringkas dan visualisasi interaktif (tren saldo kas, penjualan
           bulanan, produk terlaris, komposisi pengeluaran).

        ### Identitas
        - **NIM** : 202553012
        - **Nama** : Ahmad Farih Maulana
        - **Kelas** : A
        - **Program Studi** : Sistem Informasi, Fakultas Teknik, Universitas Muria Kudus
        - **Mata Kuliah** : Sistem Informasi Akuntansi dan Keuangan (SOB104)
        - **Dosen Pengampu** : Dr. Ir. Arif Setiawan, S.Kom, M.Cs, IPM

        ### Teknologi
        - `Streamlit` — antarmuka web interaktif
        - `SQLite` — penyimpanan data lokal (`aromatic_siak.db`)
        - `Pandas` — pengolahan data tabular
        - `Plotly` — visualisasi grafik interaktif

        > Catatan: pada Streamlit Community Cloud, penyimpanan bersifat sementara (akan reset saat
        > aplikasi di-redeploy/restart). Untuk penyimpanan permanen di produksi, database dapat
        > dipindahkan ke layanan seperti PostgreSQL/Supabase.
        """
    )


# ---------------------------------------------------------------------------
# ROUTER
# ---------------------------------------------------------------------------

if menu == "Dashboard":
    halaman_dashboard()
elif menu == "Data Master":
    halaman_master()
elif menu == "Transaksi":
    halaman_transaksi()
elif menu == "Laporan":
    halaman_laporan()
elif menu == "Tentang":
    halaman_tentang()
