"""
utils.py
Fungsi bantu: format mata uang, ikon kategori, dan CSS kustom untuk tampilan modern.

CATATAN PENTING:
Streamlit Cloud dapat menampilkan aplikasi dalam mode gelap (mengikuti pengaturan
sistem/browser pengguna atau pengaturan "Theme" di dashboard Cloud), terlepas dari
`.streamlit/config.toml`. Agar tampilan kartu, form, dan tombol kustom selalu terbaca
di kedua mode, seluruh warna di bawah ini di-set eksplisit dengan `!important` pada
elemen-elemen yang kita beri latar terang, alih-alih mengandalkan warna teks bawaan tema.
"""

import streamlit as st


def format_rupiah(nilai) -> str:
    try:
        nilai = int(nilai)
    except (TypeError, ValueError):
        nilai = 0
    minus = "-" if nilai < 0 else ""
    return f"{minus}Rp {abs(nilai):,.0f}".replace(",", ".")


# ---------------------------------------------------------------------------
# IKON
# ---------------------------------------------------------------------------

KATEGORI_ICON = {
    "Parfum Pria": "🧔‍♂️🧴",
    "Parfum Wanita": "💃🧴",
    "Parfum Unisex": "🧴",
    "Bahan Baku": "🧪",
    "Kemasan": "📦",
}

KATEGORI_JURNAL_ICON = {
    "Modal": "🏦",
    "Pembelian": "🛍️",
    "Penjualan": "💰",
    "Beban Operasional": "🧾",
    "Pendapatan Lain": "✨",
    "Hutang": "📄",
    "Piutang": "📥",
    "Lainnya": "🔖",
}


def icon_kategori_produk(kategori: str) -> str:
    return KATEGORI_ICON.get(kategori, "🌸")


def icon_kategori_jurnal(kategori: str) -> str:
    return KATEGORI_JURNAL_ICON.get(kategori, "🔖")


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

        :root {
            --clr-primary: #7B4B94;
            --clr-primary-dark: #5B3470;
            --clr-primary-light: #F3E9F7;
            --clr-accent: #F2A65A;
            --clr-bg: #FAF7FC;
            --clr-text: #2b2b2b;
            --clr-text-soft: #6b6b6b;
        }

        /* ============ LATAR UTAMA ============ */
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        .main { background-color: var(--clr-bg) !important; }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* ============ HEADER BRAND ============ */
        .app-header {
            padding: 1.4rem 1.8rem;
            border-radius: 18px;
            background: linear-gradient(120deg, #7B4B94 0%, #B76CB0 50%, #F2A65A 100%);
            color: white !important;
            margin-bottom: 1.4rem;
            box-shadow: 0 8px 24px rgba(123, 75, 148, 0.25);
        }
        .app-header h1, .app-header p { color: white !important; }
        .app-header h1 { margin: 0; font-size: 1.7rem; font-weight: 700; }
        .app-header p { margin: 0.2rem 0 0 0; opacity: 0.95; font-size: 0.92rem; }

        /* ============ KPI CARDS ============ */
        .kpi-card {
            background: #FFFFFF !important;
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 4px 14px rgba(80, 40, 100, 0.10);
            border: 1px solid #EEE3F3;
            border-left: 5px solid var(--clr-primary);
            height: 100%;
        }
        .kpi-card .kpi-icon { font-size: 1.3rem; margin-bottom: 0.15rem; }
        .kpi-card .kpi-label {
            font-size: 0.78rem;
            color: #8a7a92 !important;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .kpi-card .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2b2b2b !important;
            margin-top: 0.15rem;
        }
        .kpi-card .kpi-sub {
            font-size: 0.78rem;
            color: #9a8fa3 !important;
            margin-top: 0.1rem;
        }

        .badge {
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
        }
        .badge-green { background:#E4F7E9; color:#1E8449 !important; }
        .badge-red { background:#FBEAEA; color:#C0392B !important; }
        .badge-orange { background:#FDF1E0; color:#C87F0A !important; }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--clr-primary-dark) !important;
            margin: 0.6rem 0 0.7rem 0;
            border-left: 4px solid var(--clr-accent);
            padding-left: 0.6rem;
        }

        /* ============ METRIC BAWAAN STREAMLIT ============ */
        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            border: 1px solid #EEE3F3;
            border-radius: 14px;
            padding: 0.8rem 1rem;
        }
        div[data-testid="stMetricLabel"] * { color: #8a7a92 !important; }
        div[data-testid="stMetricValue"] { color: var(--clr-primary-dark) !important; }

        /* ============ TOMBOL ============ */
        .stButton>button, button[data-testid="stFormSubmitButton"], .stDownloadButton>button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            border: 1px solid #D9C6E3 !important;
            color: var(--clr-primary-dark) !important;
            background: #FFFFFF !important;
        }
        .stButton>button[kind="primary"],
        button[data-testid="stFormSubmitButton"][kind="primary"],
        .stButton>button[kind="primaryFormSubmit"],
        button[kind="primaryFormSubmit"] {
            background: linear-gradient(120deg, #7B4B94, #9A5FAE) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 12px rgba(123,75,148,0.35);
        }
        .stButton>button[kind="primary"]:hover,
        button[data-testid="stFormSubmitButton"][kind="primary"]:hover,
        button[kind="primaryFormSubmit"]:hover {
            background: linear-gradient(120deg, #6a3f81, #8a4f9d) !important;
            color: #FFFFFF !important;
        }

        /* ============ FORM & KOMPONEN INPUT ============ */
        div[data-testid="stForm"] {
            background: #FFFFFF !important;
            padding: 1.3rem 1.5rem;
            border-radius: 16px;
            border: 1px solid #EEE3F3;
            box-shadow: 0 4px 14px rgba(80, 40, 100, 0.08);
        }

        /* Paksa semua teks (label, caption, radio, dsb) di dalam form & kartu putih jadi gelap
           supaya tetap terbaca meskipun tema aplikasi sedang gelap. */
        div[data-testid="stForm"] label,
        div[data-testid="stForm"] label p,
        div[data-testid="stForm"] p,
        div[data-testid="stForm"] span,
        div[data-testid="stForm"] [data-testid="stWidgetLabel"] p,
        div[data-testid="stForm"] [data-testid="stMarkdownContainer"] p {
            color: #3a2a44 !important;
        }
        div[data-testid="stForm"] [data-testid="stCaptionContainer"] * {
            color: #6b5a75 !important;
        }

        /* Kotak input teks / angka / textarea / tanggal */
        div[data-testid="stForm"] input,
        div[data-testid="stForm"] textarea {
            background-color: #FBF8FD !important;
            color: #2b2b2b !important;
            border: 1px solid #D9C6E3 !important;
            border-radius: 8px !important;
        }

        /* Kotak selectbox / multiselect (komponen BaseWeb) */
        div[data-testid="stForm"] div[data-baseweb="select"] > div,
        div[data-testid="stForm"] div[data-baseweb="base-input"] {
            background-color: #FBF8FD !important;
            color: #2b2b2b !important;
            border: 1px solid #D9C6E3 !important;
            border-radius: 8px !important;
        }
        div[data-testid="stForm"] div[data-baseweb="select"] * { color: #2b2b2b !important; }

        /* Tombol +/- pada number_input */
        div[data-testid="stForm"] button[data-testid="stNumberInputStepUp"],
        div[data-testid="stForm"] button[data-testid="stNumberInputStepDown"] {
            background-color: #F3E9F7 !important;
            color: #5B3470 !important;
            border: 1px solid #D9C6E3 !important;
        }

        /* Radio button di dalam form */
        div[data-testid="stForm"] [data-testid="stRadio"] label { color: #3a2a44 !important; }

        /* Menu dropdown selectbox yang muncul sebagai popover (di luar form secara DOM) */
        ul[data-testid="stSelectboxVirtualDropdown"] li,
        ul[data-testid="stSelectboxVirtualDropdown"] li * {
            color: #2b2b2b !important;
            background-color: #FFFFFF !important;
        }
        ul[data-testid="stSelectboxVirtualDropdown"] li:hover {
            background-color: var(--clr-primary-light) !important;
        }

        /* Kalender date_input */
        div[data-baseweb="calendar"] { background-color: #FFFFFF !important; }

        /* ============ TABS ============ */
        button[data-baseweb="tab"] {
            font-weight: 600;
            border-radius: 10px 10px 0 0;
        }
        button[data-baseweb="tab"] p { font-size: 0.95rem; }

        /* ============ DATAFRAME ============ */
        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #EEE3F3;
        }

        /* ============ EXPANDER ============ */
        details {
            background: #FFFFFF !important;
            border: 1px solid #EEE3F3 !important;
            border-radius: 12px !important;
        }
        details summary { color: var(--clr-primary-dark) !important; font-weight: 600; }

        /* ============ SIDEBAR ============ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #5B3470 0%, #7B4B94 100%) !important;
        }
        section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
        section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.25) !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str = "", icon: str = ""):
    icon_html = f'<div class="kpi-icon">{icon}</div>' if icon else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            {icon_html}
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
