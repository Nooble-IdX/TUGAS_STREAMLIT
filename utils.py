"""
utils.py
Fungsi bantu: format mata uang, dan CSS kustom untuk tampilan modern.
"""

import streamlit as st


def format_rupiah(nilai) -> str:
    try:
        nilai = int(nilai)
    except (TypeError, ValueError):
        nilai = 0
    minus = "-" if nilai < 0 else ""
    return f"{minus}Rp {abs(nilai):,.0f}".replace(",", ".")


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

        :root {
            --clr-primary: #7B4B94;
            --clr-primary-dark: #5B3470;
            --clr-accent: #F2A65A;
            --clr-bg: #FAF7FC;
        }

        .main { background-color: var(--clr-bg); }

        /* Sembunyikan menu bawaan streamlit yang tidak perlu */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        /* Header brand */
        .app-header {
            padding: 1.4rem 1.8rem;
            border-radius: 18px;
            background: linear-gradient(120deg, #7B4B94 0%, #B76CB0 50%, #F2A65A 100%);
            color: white;
            margin-bottom: 1.4rem;
            box-shadow: 0 8px 24px rgba(123, 75, 148, 0.25);
        }
        .app-header h1 {
            margin: 0;
            font-size: 1.7rem;
            font-weight: 700;
        }
        .app-header p {
            margin: 0.2rem 0 0 0;
            opacity: 0.92;
            font-size: 0.92rem;
        }

        /* KPI Cards */
        .kpi-card {
            background: white;
            border-radius: 16px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            border-left: 5px solid var(--clr-primary);
            height: 100%;
        }
        .kpi-card .kpi-label {
            font-size: 0.8rem;
            color: #7a7a7a;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }
        .kpi-card .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #2b2b2b;
            margin-top: 0.15rem;
        }
        .kpi-card .kpi-sub {
            font-size: 0.78rem;
            color: #9a9a9a;
            margin-top: 0.1rem;
        }

        .badge {
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 600;
        }
        .badge-green { background:#E4F7E9; color:#1E8449; }
        .badge-red { background:#FBEAEA; color:#C0392B; }
        .badge-orange { background:#FDF1E0; color:#C87F0A; }

        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--clr-primary-dark);
            margin: 0.4rem 0 0.6rem 0;
            border-left: 4px solid var(--clr-accent);
            padding-left: 0.6rem;
        }

        div[data-testid="stMetricValue"] { color: var(--clr-primary-dark); }

        .stButton>button {
            border-radius: 10px;
            font-weight: 600;
        }
        .stButton>button[kind="primary"] {
            background: var(--clr-primary);
            border: none;
        }

        div[data-testid="stForm"] {
            background: white;
            padding: 1.2rem 1.4rem;
            border-radius: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.05);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #5B3470 0%, #7B4B94 100%);
        }
        section[data-testid="stSidebar"] * { color: white !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)
