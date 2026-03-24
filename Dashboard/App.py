from __future__ import annotations
from pathlib import Path
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import base64
from bot.bot_context import build_dashboard_context
from bot.bot_engine import answer_with_snapp_bot
from bot.bot_ui import inject_snapp_bot_css, init_bot_state, render_panel

@st.fragment
def render_snapp_bot_fragment(answer_fn, dashboard_context):
    inject_snapp_bot_css()
    init_bot_state()
    render_panel(answer_fn, dashboard_context)

# PATHS
BASE_DIR = Path(os.environ.get("SNAPP_BASE_DIR", Path(__file__).resolve().parents[1]))
CLEAN_DIR = BASE_DIR / "Clean_Data"
ASSETS_DIR = BASE_DIR / "Dashboard" / "assets"

LOGO_PATH = ASSETS_DIR / "snapp_logo.png"
INSIGHTS_PATH = CLEAN_DIR / "insight_registry.csv"
CLEAN_DIR = Path(os.environ.get("SNAPP_CLEAN_DIR", BASE_DIR / "Clean_Data"))

# PAGE CONFIG

st.set_page_config(
    page_title="Snapp Africa | Kenya Signals Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)
px.defaults.template = "plotly_white"


# CSS 

st.markdown(
    """
    <style>
    :root{
        --snapp-ink:#0b1220;
        --snapp-muted:rgba(11,18,32,0.70);
        --snapp-border:rgba(15,23,42,0.10);
        --snapp-border-strong:rgba(245,158,11,0.42);
        --snapp-border-glow:rgba(245,158,11,0.24);
        --snapp-card:rgba(255,255,255,0.94);
        --snapp-accent:#F59E0B;
        --snapp-accent-2:#FBBF24;
        --snapp-accent-soft:#FFFBEB;
        --snapp-accent-soft2:#FEF3C7;
        --snapp-page-shell:rgba(255,255,255,0.74);
        --snapp-shadow:0 10px 28px rgba(15,23,42,0.06);
        --snapp-shadow-soft:0 18px 40px rgba(15,23,42,0.07);
        --snapp-radius:22px;
    }

    /* GLOBAL BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef7ff 45%, #e5f0ff 100%);
    }

    .stApp, .stApp * {
        color: var(--snapp-ink);
    }

    header[data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.96) !important;
        border-bottom: 1px solid rgba(15,23,42,0.08) !important;
        backdrop-filter: blur(10px) !important;
    }

    /* MAIN PAGE WIDTH + PAGE FRAME */
    .block-container {
        padding-top: 2.9rem !important;
        padding-bottom: 2.4rem !important;
        max-width: 1640px !important;
        width: 96% !important;
        background: var(--snapp-page-shell);
        border: 1px solid rgba(245,158,11,0.10);
        border-radius: 30px;
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.40) inset,
            0 14px 34px rgba(15,23,42,0.05);
        margin-top: 0.9rem;
        margin-bottom: 3.5rem;
        padding-left: 1.35rem !important;
        padding-right: 1.35rem !important;
        backdrop-filter: blur(8px);
    }

    @media (min-width: 1600px){
        .block-container{
            max-width: 1760px !important;
            width: 97% !important;
        }
    }

    /* BRAND BAR */
    .brand-bar{
        background: linear-gradient(
            135deg,
            rgba(255, 251, 235, 1) 0%,
            rgba(254, 243, 199, 0.86) 100%
        );
        border: 1px solid rgba(245,158,11,0.28);
        border-radius: 28px;
        padding: 26px 28px 24px 28px;
        min-height: 190px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
        box-shadow:
            0 18px 40px rgba(15,23,42,0.08),
            0 0 0 5px rgba(245,158,11,0.07);
        position: relative;
        overflow: hidden;
    }

    .brand-bar::before{
        content:"";
        position:absolute;
        inset:0;
        background:
            linear-gradient(
                105deg,
                rgba(255,255,255,0.00) 18%,
                rgba(255,255,255,0.22) 33%,
                rgba(255,255,255,0.00) 48%
            );
        pointer-events:none;
        opacity:.85;
    }

    .brand-lockup{
        display:flex;
        flex-direction:column;
        align-items:center;
        gap:10px;
        text-align:center;
        position:relative;
        z-index:2;
    }

    .logo-badge{
        background: rgba(255,255,255,0.16);
        padding: 12px 20px;
        border-radius: 20px;
        box-shadow:
            0 14px 30px rgba(0,0,0,0.07),
            0 0 0 1px rgba(255,255,255,0.24) inset;
        backdrop-filter: blur(4px);
    }

    .logo-badge img{
        width: 300px;
        max-width: 100%;
        height: auto;
        display:block;
    }

    .brand-name{
        font-size: 34px;
        font-weight: 950;
        margin: 0;
        line-height: 1.06;
        letter-spacing: -0.4px;
    }

    .dash-title{
        font-size: 16px;
        font-weight: 700;
        margin-top: 2px;
        color: rgba(11,18,32,0.78);
    }

    .brand-link{
        display:inline-flex;
        align-items:center;
        justify-content:center;
        gap:8px;
        margin-top: 6px;
        padding: 8px 14px;
        border-radius: 999px;
        text-decoration: none !important;
        font-size: 13px;
        font-weight: 700;
        color: #7c4a03 !important;
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(245,158,11,0.24);
        box-shadow:
            0 8px 20px rgba(15,23,42,0.05),
            0 0 0 1px rgba(255,255,255,0.30) inset;
        transition:
            transform 0.22s ease,
            box-shadow 0.22s ease,
            background 0.22s ease,
            border-color 0.22s ease;
    }

    .brand-link:hover{
        transform: translateY(-1px);
        background: rgba(255,255,255,0.82);
        border-color: rgba(245,158,11,0.40);
        box-shadow:
            0 12px 24px rgba(245,158,11,0.12),
            0 0 0 4px rgba(245,158,11,0.08);
        color: #5f3903 !important;
    }

    /* TABS OUTER GLEAM BAR */
    div[data-testid="stTabs"]{
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255,255,255,0.84);
        border: 1px solid rgba(245,158,11,0.22);
        border-radius: 20px;
        padding: 10px 12px 9px 12px;
        margin-bottom: 14px;
        box-shadow:
            0 10px 30px rgba(15,23,42,0.05),
            0 0 0 1px rgba(255,255,255,0.55) inset,
            0 0 0 4px rgba(245,158,11,0.05);
        backdrop-filter: blur(10px);
    }

    div[data-testid="stTabs"]::before{
        content:"";
        position:absolute;
        inset:0;
        border-radius:20px;
        padding:1px;
        background: linear-gradient(
            90deg,
            rgba(245,158,11,0.40),
            rgba(251,191,36,0.18),
            rgba(245,158,11,0.40)
        );
        -webkit-mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events:none;
    }

    div[data-baseweb="tab-list"]{
        gap: 8px !important;
        flex-wrap: wrap !important;
    }

    button[data-baseweb="tab"]{
        position: relative;
        border-radius: 12px !important;
        padding: 8px 12px !important;
        background: rgba(255,255,255,0.00) !important;
        font-weight: 800 !important;
        transition:
            transform 0.20s ease,
            background 0.20s ease,
            box-shadow 0.20s ease,
            border-color 0.20s ease !important;
    }

    button[data-baseweb="tab"]::before{
        content:"";
        position:absolute;
        inset:0;
        border-radius:12px;
        border:1px solid transparent;
        transition: all 0.20s ease;
        pointer-events:none;
    }

    button[data-baseweb="tab"] > div,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] p{
        font-size: 14px !important;
        font-weight: 800 !important;
        color: rgba(11,18,32,0.76) !important;
        letter-spacing: 0.2px;
        transition: color 0.20s ease !important;
    }

    button[data-baseweb="tab"]:hover{
        transform: translateY(-1px);
        background: rgba(255,251,235,0.80) !important;
        box-shadow:
            0 8px 18px rgba(245,158,11,0.08),
            0 0 0 3px rgba(245,158,11,0.06);
    }

    button[data-baseweb="tab"]:hover::before{
        border-color: rgba(245,158,11,0.28);
    }

    button[data-baseweb="tab"]:hover > div,
    button[data-baseweb="tab"]:hover span,
    button[data-baseweb="tab"]:hover p{
        color: #8a5204 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"]{
        background: rgba(255,251,235,0.96) !important;
        box-shadow:
            0 10px 18px rgba(245,158,11,0.10),
            0 0 0 1px rgba(245,158,11,0.18);
        font-weight: 900 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"]::before{
        border-color: rgba(245,158,11,0.36);
    }

    button[data-baseweb="tab"][aria-selected="true"] > div,
    button[data-baseweb="tab"][aria-selected="true"] span,
    button[data-baseweb="tab"][aria-selected="true"] p{
        color: var(--snapp-accent) !important;
        font-weight: 900 !important;
    }

    /* REMOVE YELLOW TAB UNDERLINE */
    div[data-baseweb="tab-highlight"]{
        display: none !important;
        height: 0 !important;
        background: transparent !important;
    }

    /* KPI METRICS */
    div[data-testid="stMetric"]{
        background: rgba(255,255,255,0.92);
        border: 1px solid rgba(245,158,11,0.26) !important;
        border-radius: 17px;
        padding: 14px 15px;
        box-shadow:
            0 10px 24px rgba(15,23,42,0.04),
            0 0 0 1px rgba(255,255,255,0.45) inset,
            0 0 0 3px rgba(245,158,11,0.04);
    }

    div[data-testid="stMetricLabel"]{
        font-size: 13px !important;
        font-weight: 650 !important;
        color: rgba(11,18,32,0.80) !important;
    }

    div[data-testid="stMetricValue"]{
        font-size: 32px !important;
        font-weight: 900 !important;
        line-height: 1.15 !important;
    }

    div[data-testid="stMetricDelta"]{
        font-size: 12px !important;
        font-weight: 600 !important;
    }

    /* CHART CARDS */
    .chart-card{
        background: linear-gradient(
            180deg,
            rgba(255,255,255,0.98) 0%,
            rgba(255,253,247,0.96) 100%
        );
        border: 1px solid rgba(245,158,11,0.34);
        border-radius: 20px;
        padding: 14px 14px 10px 14px;
        box-shadow:
            0 14px 30px rgba(15,23,42,0.06),
            0 0 0 1px rgba(255,255,255,0.62) inset,
            0 0 0 4px rgba(245,158,11,0.08),
            0 0 22px rgba(245,158,11,0.10);
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        transition:
            transform 0.20s ease,
            box-shadow 0.20s ease,
            border-color 0.20s ease;
    }

    .chart-card:hover{
        transform: translateY(-2px);
        border-color: rgba(245,158,11,0.42);
        box-shadow:
            0 18px 36px rgba(15,23,42,0.08),
            0 0 0 1px rgba(255,255,255,0.68) inset,
            0 0 0 4px rgba(245,158,11,0.10),
            0 0 30px rgba(245,158,11,0.14);
    }

    .chart-card::before{
        content:"";
        position:absolute;
        inset:0;
        border-radius:20px;
        padding:1px;
        background: linear-gradient(
            135deg,
            rgba(245,158,11,0.46),
            rgba(255,255,255,0.12),
            rgba(251,191,36,0.34)
        );
        -webkit-mask:
            linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        pointer-events:none;
        z-index: 3;
    }

    .chart-card::after{
        content:"";
        position:absolute;
        top:0;
        left:0;
        right:0;
        height:4px;
        background: linear-gradient(90deg, var(--snapp-accent) 0%, var(--snapp-accent-2) 100%);
        z-index:2;
    }

    .chart-title{
        font-size: 15px;
        font-weight: 850;
        margin: 0 0 10px 0;
        letter-spacing: 0.2px;
        position: relative;
        z-index: 4;
    }

    /* PLOTLY CONTAINER ENHANCER */
    div[data-testid="stPlotlyChart"]{
        border-radius: 16px;
        overflow: hidden;
        background: rgba(255,255,255,0.24);
        box-shadow:
            inset 0 0 0 1px rgba(245,158,11,0.12),
            0 0 0 2px rgba(245,158,11,0.03);
    }

    /* DATAFRAMES / TABLE AREAS */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"]{
        border: 1px solid rgba(245,158,11,0.24);
        border-radius: 16px;
        overflow: hidden;
        box-shadow:
            0 10px 24px rgba(15,23,42,0.04),
            0 0 0 4px rgba(245,158,11,0.05);
        background: rgba(255,255,255,0.95);
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"]{
        border-right: 1px solid rgba(15,23,42,0.08);
        background: rgba(255,255,255,0.82);
        backdrop-filter: blur(10px);
    }

    section[data-testid="stSidebar"] button{
        background: rgba(255,255,255,0.92) !important;
        border: 1px solid rgba(15,23,42,0.10) !important;
        border-radius: 10px !important;
        font-weight: 550 !important;
    }

    section[data-testid="stSidebar"] button:hover{
        background: rgba(255,251,235,0.95) !important;
        border-color: rgba(245,158,11,0.20) !important;
    }

    /* INPUTS / INSIGHT REGISTRY FIX */
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="select"] > div,
    textarea,
    input,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div,
    .stMultiSelect > div > div{
        background: rgba(255,255,255,0.96) !important;
        color: var(--snapp-ink) !important;
        border-radius: 12px !important;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="select"] > div{
        border: 1px solid rgba(15,23,42,0.11) !important;
        box-shadow:
            0 1px 0 rgba(255,255,255,0.55) inset,
            0 6px 16px rgba(15,23,42,0.03);
        transition:
            border-color 0.20s ease,
            box-shadow 0.20s ease,
            background 0.20s ease !important;
    }

    div[data-baseweb="input"] > div:hover,
    div[data-baseweb="base-input"] > div:hover,
    div[data-baseweb="select"] > div:hover{
        border-color: rgba(245,158,11,0.24) !important;
        box-shadow:
            0 0 0 3px rgba(245,158,11,0.05),
            0 8px 18px rgba(15,23,42,0.04);
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"] input,
    textarea{
        color: var(--snapp-ink) !important;
        caret-color: var(--snapp-accent) !important;
        background: transparent !important;
    }

    div[data-baseweb="input"] input::placeholder,
    div[data-baseweb="base-input"] input::placeholder,
    textarea::placeholder{
        color: rgba(11,18,32,0.42) !important;
    }

    ul[role="listbox"]{
        background: rgba(255,255,255,0.99) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(15,23,42,0.08) !important;
        box-shadow: 0 16px 34px rgba(15,23,42,0.08) !important;
    }

    /* BUTTONS */
    .stButton > button,
    .stDownloadButton > button{
        border-radius: 12px !important;
        border: 1px solid rgba(245,158,11,0.22) !important;
        background: linear-gradient(135deg, #fffdf7 0%, #fff7df 100%) !important;
        color: var(--snapp-ink) !important;
        font-weight: 700 !important;
        box-shadow:
            0 10px 22px rgba(15,23,42,0.05),
            0 0 0 1px rgba(255,255,255,0.45) inset;
        transition:
            transform 0.20s ease,
            box-shadow 0.20s ease,
            border-color 0.20s ease,
            background 0.20s ease !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover{
        transform: translateY(-1px);
        border-color: rgba(245,158,11,0.34) !important;
        background: linear-gradient(135deg, #fffefb 0%, #fffbeb 100%) !important;
        box-shadow:
            0 14px 28px rgba(245,158,11,0.11),
            0 0 0 4px rgba(245,158,11,0.06);
    }

    /* TOGGLES */
    div[data-testid="stToggle"] label{
        color: var(--snapp-ink) !important;
        font-weight: 600 !important;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4{
        color: var(--snapp-ink) !important;
        letter-spacing: -0.2px;
    }

    h2{
        font-size: 26px !important;
        font-weight: 900 !important;
    }

    h3{
        font-size: 18px !important;
        font-weight: 800 !important;
    }

    p, li, label, span{
        color: var(--snapp-ink);
    }

    /* HORIZONTAL RULE / DIVIDER SOFTEN */
    hr{
        border-color: rgba(245,158,11,0.14) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# HEADER 

if LOGO_PATH.exists():
    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("utf-8")
    logo_tag = f"<img src='data:image/png;base64,{b64}' alt='Snapp logo'/>"
else:
    logo_tag = "<div style='font-weight:900;color:#F59E0B;font-size:22px;'>S</div>"

header_html = (
    "<div class='brand-bar'>"
        "<div class='brand-lockup'>"
            f"<div class='logo-badge'>{logo_tag}</div>"
            "<div class='brand-text'>"
                "<div class='brand-name'>Kenya Signals Dashboard</div>"
                "<div class='dash-title'></div>"
                "<a class='brand-link' href='https://snapp.africa' target='_blank'>Visit Snapp Africa</a>"
            "</div>"
        "</div>"
    "</div>"
)
st.markdown(header_html, unsafe_allow_html=True)

# SAFE READERS + HELPERS

def _safe_read_csv(path: Path) -> pd.DataFrame:
    try:
        if path.exists():
            return pd.read_csv(path)
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def _norm(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.lower()
    )

def wide_years_to_long(df: pd.DataFrame, id_cols: list[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()
    year_cols = [c for c in df.columns if str(c).isdigit()]
    if not year_cols:
        year_cols = [c for c in df.columns if isinstance(c, (int, float)) and str(int(c)).isdigit()]
    if not year_cols:
        return pd.DataFrame()
    out = df.melt(id_vars=id_cols, value_vars=year_cols, var_name="year", value_name="value")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    return out.dropna(subset=["year"]).sort_values("year")

def wide_to_long(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    if df is None or df.empty or id_col not in df.columns:
        return pd.DataFrame(columns=[id_col, "year", "value"])
    year_cols = [c for c in df.columns if c != id_col]
    out = df.melt(id_vars=[id_col], value_vars=year_cols, var_name="year", value_name="value")
    out["year"] = pd.to_numeric(out["year"], errors="coerce")
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out.dropna(subset=["year"])
    return out

def series_by_label(long_df: pd.DataFrame, label_col: str, label_value: str) -> pd.DataFrame:
    if long_df is None or long_df.empty:
        return pd.DataFrame(columns=["year", "value"])
    s = long_df[long_df[label_col].astype(str).str.strip().str.lower().eq(label_value.strip().lower())].copy()
    s = s.dropna(subset=["year", "value"])
    s = s.groupby("year", as_index=False)["value"].sum().sort_values("year")
    return s

def series_by_contains(long_df: pd.DataFrame, label_col: str, pattern: str) -> pd.DataFrame:
    if long_df is None or long_df.empty:
        return pd.DataFrame(columns=["year", "value"])
    s = long_df[long_df[label_col].astype(str).str.strip().str.lower().str.contains(pattern.lower(), na=False)].copy()
    s = s.dropna(subset=["year", "value"])
    s = s.groupby("year", as_index=False)["value"].sum().sort_values("year")
    return s

def force_light_plotly(fig):
    strong_text = "#0b1220"
    grid = "rgba(15,23,42,0.20)"
    axis_line = "rgba(15,23,42,0.28)"

    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color=strong_text, size=13),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(font=dict(color=strong_text)),
    )
    fig.update_xaxes(
        tickfont=dict(color=strong_text),
        title=dict(font=dict(color=strong_text)),
        showgrid=True,
        gridcolor=grid,
        zeroline=True,
        zerolinecolor=grid,
        showline=True,
        linecolor=axis_line,
        ticks="outside",
        tickcolor=axis_line,
    )
    fig.update_yaxes(
        tickfont=dict(color=strong_text),
        title=dict(font=dict(color=strong_text)),
        showgrid=True,
        gridcolor=grid,
        zeroline=True,
        zerolinecolor=grid,
        showline=True,
        linecolor=axis_line,
        ticks="outside",
        tickcolor=axis_line,
    )
    return fig

def regional_wide_to_long(wide: pd.DataFrame) -> pd.DataFrame:
    if wide is None or wide.empty or "year" not in wide.columns:
        return pd.DataFrame(columns=["year", "country", "indicator", "value"])

    cols = [c for c in wide.columns if c != "year"]
    if not cols:
        return pd.DataFrame(columns=["year", "country", "indicator", "value"])

    df = wide.copy()
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    long_df = df.melt(id_vars=["year"], value_vars=cols, var_name="series", value_name="value")
    long_df["series"] = long_df["series"].astype(str)

    parts = long_df["series"].str.split(r"\s*\|\s*", n=1, expand=True)
    long_df["country"] = parts[0].fillna("").astype(str).str.strip()
    long_df["indicator"] = parts[1].fillna("").astype(str).str.strip()

    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce")
    long_df = long_df.dropna(subset=["year"])
    long_df = long_df.drop(columns=["series"])
    return long_df

# CACHED LOAD + PREP

@st.cache_data(show_spinner=False)
def load_and_prepare_data(clean_dir_str: str) -> dict[str, pd.DataFrame]:
    clean_dir = Path(clean_dir_str)

    fx = _safe_read_csv(clean_dir / "fx_monthly.csv")
    rates = _safe_read_csv(clean_dir / "cbk_rates.csv")
    cpi = _safe_read_csv(clean_dir / "cpi_inflation.csv")
    veh = _safe_read_csv(clean_dir / "knbs_vehicle_registrations.csv")
    lic = _safe_read_csv(clean_dir / "knbs_transport_licenses.csv")
    acc_sum = _safe_read_csv(clean_dir / "knbs_road_accidents_summary.csv")
    acc_class = _safe_read_csv(clean_dir / "knbs_road_accidents_by_type_class.csv")

    trends = _safe_read_csv(clean_dir / "demand_google_trends.csv")
    wb_ctx = _safe_read_csv(clean_dir / "worldbank_demand_context.csv")
    epra = _safe_read_csv(clean_dir / "epra_pump_prices.csv")
    wb_reg = _safe_read_csv(clean_dir / "worldbank_regional_context.csv")

    cpix = _safe_read_csv(clean_dir / "compliance_pressure_index.csv")
    kra_events = _safe_read_csv(clean_dir / "kra_events.csv")
    friction = _safe_read_csv(clean_dir / "friction_map.csv")
    kra_rev = _safe_read_csv(clean_dir / "kpi_kra_revenue.csv")
    esi = _safe_read_csv(clean_dir / "energy_stress_index.csv")

    
    # Parse / clean date fields
    
    if not esi.empty and "month_key" in esi.columns:
        esi = esi.copy()
        esi["month"] = pd.to_datetime(esi["month_key"], errors="coerce")
        esi = esi.dropna(subset=["month"]).sort_values("month")

    for name, df, col in [
        ("fx", fx, "date"),
        ("rates", rates, "date"),
        ("cpi", cpi, "date"),
    ]:
        if not df.empty and col in df.columns:
            df = df.copy()
            df[col] = pd.to_datetime(df[col], errors="coerce")
            df = df.dropna(subset=[col]).sort_values(col)

            if name == "fx":
                fx = df
            elif name == "rates":
                rates = df
            elif name == "cpi":
                cpi = df

    if not trends.empty and "date" in trends.columns:
        trends = trends.copy()
        trends["date"] = pd.to_datetime(trends["date"], errors="coerce")
        trends = trends.dropna(subset=["date"]).sort_values("date")

    if not epra.empty:
        epra = epra.copy()

        if "cycle_start" in epra.columns:
            epra["cycle_start"] = pd.to_datetime(epra["cycle_start"], errors="coerce")
        if "cycle_end" in epra.columns:
            epra["cycle_end"] = pd.to_datetime(epra["cycle_end"], errors="coerce")
        if "city" in epra.columns:
            epra["city"] = epra["city"].astype(str).str.strip()

        sort_cols = [c for c in ["cycle_start", "city"] if c in epra.columns]
        if sort_cols:
            epra = epra.sort_values(sort_cols)

    if not wb_ctx.empty and "year" in wb_ctx.columns:
        wb_ctx = wb_ctx.copy()
        wb_ctx["year"] = pd.to_numeric(wb_ctx["year"], errors="coerce")
        wb_ctx = wb_ctx.dropna(subset=["year"]).sort_values("year")

    if not wb_reg.empty:
        wb_reg = wb_reg.copy()
        if "year" in wb_reg.columns:
            wb_reg["year"] = pd.to_numeric(wb_reg["year"], errors="coerce")
            wb_reg = wb_reg.dropna(subset=["year"]).sort_values("year")
        else:
            wb_reg = pd.DataFrame()

    if not cpix.empty and "period" in cpix.columns:
        cpix = cpix.copy()
        cpix["period"] = pd.to_datetime(cpix["period"], errors="coerce")
        cpix = cpix.dropna(subset=["period"]).sort_values("period")

    if not kra_events.empty and "event_date" in kra_events.columns:
        kra_events = kra_events.copy()
        kra_events["event_date"] = pd.to_datetime(kra_events["event_date"], errors="coerce")
        kra_events = kra_events.dropna(subset=["event_date"]).sort_values("event_date", ascending=False)

    
    # Precompute common long forms
    
    veh_long = (
        wide_to_long(veh, "Type")
        if not veh.empty and "Type" in veh.columns
        else pd.DataFrame(columns=["Type", "year", "value"])
    )

    lic_long = (
        wide_to_long(lic, "License_Type")
        if not lic.empty and "License_Type" in lic.columns
        else pd.DataFrame(columns=["License_Type", "year", "value"])
    )

    acc_sum_long = (
        wide_years_to_long(acc_sum, ["Metric"])
        if not acc_sum.empty and "Metric" in acc_sum.columns
        else pd.DataFrame(columns=["Metric", "year", "value"])
    )

    acc_class_long = (
        wide_years_to_long(acc_class, ["Type", "Class"])
        if not acc_class.empty and {"Type", "Class"}.issubset(acc_class.columns)
        else pd.DataFrame(columns=["Type", "Class", "year", "value"])
    )

    wb_reg_long = (
        regional_wide_to_long(wb_reg)
        if not wb_reg.empty
        else pd.DataFrame(columns=["year", "country", "indicator", "value"])
    )

    
    # Clean known label noise in accident summary
    
    if not acc_sum_long.empty and "Metric" in acc_sum_long.columns:
        acc_sum_long = acc_sum_long.copy()
        acc_sum_long["Metric"] = acc_sum_long["Metric"].astype(str).str.strip()
        acc_sum_long = acc_sum_long[
            ~acc_sum_long["Metric"].isin(["of which:", "Persons Killed or Injured:-"])
        ]

    if not acc_class_long.empty:
        acc_class_long = acc_class_long.copy()
        acc_class_long["Type"] = acc_class_long["Type"].astype(str).str.strip()
        acc_class_long["Class"] = acc_class_long["Class"].astype(str).str.strip()

    return {
        "fx": fx,
        "rates": rates,
        "cpi": cpi,
        "veh": veh,
        "lic": lic,
        "acc_sum": acc_sum,
        "acc_class": acc_class,
        "trends": trends,
        "wb_ctx": wb_ctx,
        "epra": epra,
        "wb_reg": wb_reg,
        "cpix": cpix,
        "kra_events": kra_events,
        "friction": friction,
        "kra_rev": kra_rev,
        "esi": esi,
        "veh_long": veh_long,
        "lic_long": lic_long,
        "acc_sum_long": acc_sum_long,
        "acc_class_long": acc_class_long,
        "wb_reg_long": wb_reg_long,
    }

# LOAD DATA 

data = load_and_prepare_data(str(CLEAN_DIR))

fx = data["fx"]
rates = data["rates"]
cpi = data["cpi"]
veh = data["veh"]
lic = data["lic"]
acc_sum = data["acc_sum"]
acc_class = data["acc_class"]

trends = data["trends"]
wb_ctx = data["wb_ctx"]
epra = data["epra"]
wb_reg = data["wb_reg"]

cpix = data["cpix"]
kra_events = data["kra_events"]
friction = data["friction"]
kra_rev = data["kra_rev"]
esi = data["esi"]

veh_long = data["veh_long"]
lic_long = data["lic_long"]
acc_sum_long = data["acc_sum_long"]
acc_class_long = data["acc_class_long"]
wb_reg_long = data["wb_reg_long"]
# ============================================================
# LATEST VALUES (SAFE)
# ============================================================
latest_fx = None
if not fx.empty and "United States dollar" in fx.columns:
    _tmp = fx.dropna(subset=["United States dollar"])
    if len(_tmp):
        latest_fx = _tmp.iloc[-1]

latest_rates = None
if not rates.empty and "Central Bank Rate" in rates.columns:
    _tmp = rates.dropna(subset=["Central Bank Rate"])
    if len(_tmp):
        latest_rates = _tmp.iloc[-1]

latest_cpi = None
if not cpi.empty and "12-Month Inflation" in cpi.columns:
    _tmp = cpi.dropna(subset=["12-Month Inflation"])
    if len(_tmp):
        latest_cpi = _tmp.iloc[-1]

latest_trends_date = None
if not trends.empty and "date" in trends.columns:
    _tmp = trends.dropna(subset=["date"])
    if len(_tmp):
        latest_trends_date = _tmp.iloc[-1]["date"]

latest_epra_cycle = None
if not epra.empty and "cycle_start" in epra.columns:
    _tmp = epra.dropna(subset=["cycle_start"])
    if len(_tmp):
        latest_epra_cycle = _tmp.iloc[-1]["cycle_start"]

latest_wb_year = int(wb_ctx["year"].max()) if (not wb_ctx.empty and wb_ctx["year"].notna().any()) else None
latest_wb_reg_year = int(wb_reg["year"].max()) if (not wb_reg.empty and "year" in wb_reg.columns and wb_reg["year"].notna().any()) else None


# TRANSPORT SERIES

veh_long = wide_to_long(veh, "Type") if (not veh.empty and "Type" in veh.columns) else pd.DataFrame(columns=["Type", "year", "value"])
lic_long = wide_to_long(lic, "License_Type") if (not lic.empty and "License_Type" in lic.columns) else pd.DataFrame(columns=["License_Type", "year", "value"])

saloon = series_by_label(veh_long, "Type", "Saloon cars")
station = series_by_label(veh_long, "Type", "Station wagons")
matatu = series_by_label(veh_long, "Type", "Mini-buses/Matatu")
buses_coaches = series_by_label(veh_long, "Type", "Buses and Coaches")

motorcycles = series_by_contains(veh_long, "Type", "motor")
total_units = series_by_contains(veh_long, "Type", "total units")

private_pub = None
if (not saloon.empty) and (not station.empty) and (not matatu.empty) and (not buses_coaches.empty):
    combo = pd.merge(saloon.rename(columns={"value": "saloon"}), station.rename(columns={"value": "station"}), on="year", how="outer")
    combo = pd.merge(combo, buses_coaches.rename(columns={"value": "buses"}), on="year", how="outer")
    combo = pd.merge(combo, matatu.rename(columns={"value": "matatu"}), on="year", how="outer")
    combo = combo.sort_values("year")
    combo["Private (Saloon+Station)"] = combo["saloon"].fillna(0) + combo["station"].fillna(0)
    combo["Public (Buses+Matatu)"] = combo["buses"].fillna(0) + combo["matatu"].fillna(0)
    private_pub = combo[["year", "Private (Saloon+Station)", "Public (Buses+Matatu)"]].copy()

psv_total = None
if not lic_long.empty and "License_Type" in lic_long.columns:
    _psv = lic_long[lic_long["License_Type"].astype(str).str.strip().str.lower().eq("total")].copy()
    if not _psv.empty:
        psv_total = (
            _psv.dropna(subset=["year", "value"])
            .groupby("year", as_index=False)["value"].sum()
            .sort_values("year")
        )

latest_year = int(veh_long["year"].max()) if (not veh_long.empty and veh_long["year"].notna().any()) else None


# SIDEBAR

with st.sidebar:
    st.markdown("### Data")
    st.caption("Downloadable Datasets.")

    def download_btn(label: str, df: pd.DataFrame, filename: str):
        if df is None or df.empty:
            st.button(label, disabled=True)
            return
        st.download_button(
            label=label,
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
            use_container_width=True,
        )

    download_btn("CPI", cpi, "cpi_inflation_clean.csv")
    download_btn("FX", fx, "fx_monthly_clean.csv")
    download_btn("Rates", rates, "cbk_rates_clean.csv")
    download_btn("Vehicles", veh, "knbs_vehicle_registrations_clean.csv")
    download_btn("Licenses", lic, "knbs_transport_licenses_clean.csv")
    download_btn("Google Trends", trends, "demand_google_trends.csv")
    download_btn("Demand Context", wb_ctx, "worldbank_demand_context.csv")
    download_btn("Pump Prices", epra, "epra_pump_prices.csv")
    download_btn("Regional Context", wb_reg, "worldbank_regional_context.csv")
    download_btn("CPIx (Compliance Index)", cpix, "compliance_pressure_index.csv")
    download_btn("KRA Events", kra_events, "kra_events.csv")
    download_btn("Friction Map", friction, "friction_map.csv")
    download_btn("KRA Revenue KPIs", kra_rev, "kpi_kra_revenue.csv")
    download_btn("Energy Stress Index", esi, "energy_stress_index.csv")

    show_tables = st.toggle("Display tables", value=False)


# TABS

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "Macro Conditions",
        "Transport & Mobility",
        "Demand Proxies",
        "EAC Regional Context",
        "Regulatory Pressure",
        "Energy & Cost",
        "Signals Map",
        "Opportunity Map",
    ]
)


# TAB 1: MACRO

with tab1:
    st.subheader("Key Indicators")
    st.caption("Source: CBK/KNBS.")
    k1, k2, k3, k4 = st.columns(4)

    if latest_cpi is not None:
        k1.metric("Inflation (YoY, Annual)", f"{float(latest_cpi['12-Month Inflation']):.2f}%")
    else:
        k1.metric("Inflation (YoY, Annual)", "NA")

    if latest_fx is not None:
        k2.metric("KES/USD (Current Monthly Avg)", f"{float(latest_fx['United States dollar']):.2f}")
    else:
        k2.metric("KES/USD (Current Monthly Avg)", "NA")

    if latest_rates is not None:
        k3.metric("CBR", f"{float(latest_rates['Central Bank Rate']):.2f}%")
        if "91-Day Tbill" in latest_rates.index:
            k4.metric("91-Day T-bill", f"{float(latest_rates['91-Day Tbill']):.2f}%")
        else:
            k4.metric("91-Day T-bill", "NA")
    else:
        k3.metric("CBR", "NA")
        k4.metric("91-Day T-bill", "NA")

    st.divider()

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="chart-card"><div class="chart-title">Inflation Trend</div>', unsafe_allow_html=True)
        if (not cpi.empty) and ("date" in cpi.columns) and ("12-Month Inflation" in cpi.columns):
            fig = px.line(cpi, x="date", y="12-Month Inflation", markers=False)
            fig.update_layout(height=440)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("CPI dataset missing required columns.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Exchange Rate(KES/USD)</div>', unsafe_allow_html=True)
        if (not fx.empty) and ("date" in fx.columns) and ("United States dollar" in fx.columns):
            fig = px.line(fx, x="date", y="United States dollar", markers=False)
            fig.update_layout(height=440)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("FX dataset missing required columns.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="chart-card"><div class="chart-title">Central Bank Rate (CBR)</div>', unsafe_allow_html=True)
        if (not rates.empty) and ("date" in rates.columns) and ("Central Bank Rate" in rates.columns):
            fig = px.line(rates, x="date", y="Central Bank Rate", markers=False)
            fig.update_layout(height=440)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("Rates dataset missing required columns.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">91-Day Treasury Bills</div>', unsafe_allow_html=True)
        if (not rates.empty) and ("date" in rates.columns) and ("91-Day Tbill" in rates.columns):
            fig = px.line(rates, x="date", y="91-Day Tbill", markers=False)
            fig.update_layout(height=440)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("91-Day Tbill column not found in rates dataset.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    st.subheader("Snapp Lens")
    st.write(
        "- CPI shows affordability and price sensitivity.\n"
        "- FX signals imported cost pressure and uncertainty.\n"
        "- Rates/yields indicate tighter credit conditions and caution among SMEs/consumers.\n\n"
        "**Implication:** value-first packaging, flexible payment plans, ROI/efficiency."
    )

    st.subheader("Data Lag")
    st.write(f"Latest CPI date: **{pd.to_datetime(latest_cpi['date']).date()}**" if latest_cpi is not None and "date" in latest_cpi else "Latest CPI date: **NA**")
    st.write(f"Latest FX date: **{pd.to_datetime(latest_fx['date']).date()}**" if latest_fx is not None and "date" in latest_fx else "Latest FX date: **NA**")
    st.write(f"Latest Rates date: **{pd.to_datetime(latest_rates['date']).date()}**" if latest_rates is not None and "date" in latest_rates else "Latest Rates date: **NA**")

    if show_tables:
        st.subheader("Cleaned datasets (Macro)")
        st.write("CPI / Inflation (clean)")
        st.dataframe(cpi.tail(25), use_container_width=True)
        st.write("FX (clean)")
        st.dataframe(fx.tail(25), use_container_width=True)
        st.write("CBK Rates (clean)")
        st.dataframe(rates.tail(25), use_container_width=True)


# TAB 2: TRANSPORT + ROAD SAFETY

with tab2:
    st.subheader("Transport Signals")
    st.caption("Source: KNBS Chapter 13 Tables (Registrations, Licenses & Road Safety).")

    if latest_year is not None:
        a, b, c, d = st.columns(4)

        if not total_units.empty:
            tot_latest = total_units.loc[total_units["year"] == latest_year, "value"]
            a.metric("Total units registered", f"{float(tot_latest.values[0]):,.0f}" if len(tot_latest) else "NA", help=f"Year: {latest_year}")
        else:
            a.metric("Total units registered", "NA", help=f"Year: {latest_year}")

        if private_pub is not None:
            priv_latest = private_pub.loc[private_pub["year"] == latest_year, "Private (Saloon+Station)"]
            pub_latest = private_pub.loc[private_pub["year"] == latest_year, "Public (Buses+Matatu)"]
            b.metric("Private registrations", f"{float(priv_latest.values[0]):,.0f}" if len(priv_latest) else "NA", help=f"Year: {latest_year}")
            c.metric("Public registrations", f"{float(pub_latest.values[0]):,.0f}" if len(pub_latest) else "NA", help=f"Year: {latest_year}")
        else:
            b.metric("Private registrations", "NA", help=f"Year: {latest_year}")
            c.metric("Public registrations", "NA", help=f"Year: {latest_year}")

        if not motorcycles.empty:
            moto_latest = motorcycles.loc[motorcycles["year"] == latest_year, "value"]
            d.metric("Motorcycles registered", f"{float(moto_latest.values[0]):,.0f}" if len(moto_latest) else "NA", help=f"Year: {latest_year}")
        else:
            d.metric("Motorcycles registered", "NA", help=f"Year: {latest_year}")

    st.divider()

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="chart-card"><div class="chart-title">Private vs Public Registrations</div>', unsafe_allow_html=True)
        if private_pub is not None:
            plot_df = private_pub.rename(columns={"year": "Year"})
            fig = px.line(plot_df, x="Year", y=["Private (Saloon+Station)", "Public (Buses+Matatu)"], markers=True)
            fig.update_layout(height=520)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.warning("Private/Public series not detected. Check row names in knbs_vehicle_registrations.csv")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Motorcycles ("Boda")</div>', unsafe_allow_html=True)
        if not motorcycles.empty:
            fig = px.line(motorcycles, x="year", y="value", markers=True)
            fig.update_layout(height=520)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.warning("Motorcycles not detected.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="chart-card"><div class="chart-title">Total Units Registered</div>', unsafe_allow_html=True)
        if not total_units.empty:
            fig = px.line(total_units, x="year", y="value", markers=True)
            fig.update_layout(height=520)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.warning("Total Units Registered not detected.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">PSV Licenses Issued (total)</div>', unsafe_allow_html=True)
        if psv_total is not None and not psv_total.empty:
            fig = px.line(psv_total, x="year", y="value", markers=True)
            fig.update_layout(height=520)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("PSV licenses total not clearly available (may include '..' or missing totals).")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Road Safety (NTSA / Police)")
    st.caption("Source: KNBS Chapter 13 — Table 13.6(a) & 13.6(b).")

    acc_ok = (acc_sum is not None) and (not acc_sum.empty) and ("Metric" in acc_sum.columns)
    acc_metrics = {}
    acc_latest_year = None

    if acc_ok:
        acc_long = wide_to_long(acc_sum, "Metric")
        acc_long["metric_norm"] = _norm(acc_long["Metric"])

        acc_metrics["Reported Traffic Accidents"] = acc_long[acc_long["metric_norm"].str.contains("reported traffic accidents", na=False)]
        acc_metrics["Persons Killed or Injured (Total)"] = acc_long[acc_long["metric_norm"].str.contains("persons killed or injured", na=False)]
        acc_metrics["Killed"] = acc_long[acc_long["metric_norm"].eq("killed")]
        acc_metrics["Seriously Injured"] = acc_long[acc_long["metric_norm"].str.contains("seriously injured", na=False)]
        acc_metrics["Slightly Injured"] = acc_long[acc_long["metric_norm"].str.contains("slightly injured", na=False)]

        if acc_long["year"].notna().any():
            acc_latest_year = int(acc_long["year"].max())

    k1, k2, k3, k4 = st.columns(4)

    def _kpi_val(df: pd.DataFrame | None, y: int | None):
        if df is None or df.empty or y is None:
            return None
        v = df.loc[df["year"] == y, "value"]
        return float(v.values[0]) if len(v) and pd.notna(v.values[0]) else None

    if acc_ok and acc_latest_year is not None:
        v_acc = _kpi_val(acc_metrics.get("Reported Traffic Accidents"), acc_latest_year)
        v_total = _kpi_val(acc_metrics.get("Persons Killed or Injured (Total)"), acc_latest_year)
        v_k = _kpi_val(acc_metrics.get("Killed"), acc_latest_year)
        v_si = _kpi_val(acc_metrics.get("Seriously Injured"), acc_latest_year)
        v_sl = _kpi_val(acc_metrics.get("Slightly Injured"), acc_latest_year)

        k1.metric("Reported accidents", f"{v_acc:,.0f}" if v_acc is not None else "NA", help=f"Year: {acc_latest_year}")
        k2.metric("Killed or injured (total)", f"{v_total:,.0f}" if v_total is not None else "NA", help=f"Year: {acc_latest_year}")
        k3.metric("Killed", f"{v_k:,.0f}" if v_k is not None else "NA", help=f"Year: {acc_latest_year}")
        injured = (v_si or 0) + (v_sl or 0) if (v_si is not None or v_sl is not None) else None
        k4.metric("Injured (serious + slight)", f"{injured:,.0f}" if injured is not None else "NA", help=f"Year: {acc_latest_year}")
    else:
        k1.metric("Reported accidents", "NA")
        k2.metric("Killed or injured (total)", "NA")
        k3.metric("Killed", "NA")
        k4.metric("Injured (serious + slight)", "NA")

    st.divider()
    left2, right2 = st.columns(2, gap="large")

    with left2:
        st.markdown('<div class="chart-card"><div class="chart-title">Reported Accidents</div>', unsafe_allow_html=True)
        s = acc_metrics.get("Reported Traffic Accidents")
        if acc_ok and s is not None and not s.empty:
            fig = px.line(s, x="year", y="value", markers=True)
            fig.update_layout(height=520)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("Accidents series not available yet. Ensure knbs_road_accidents_summary.csv exists with a 'Metric' column.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Fatality vs Injured (serious + slight)</div>', unsafe_allow_html=True)
        if acc_ok:
            k = acc_metrics.get("Killed")
            si = acc_metrics.get("Seriously Injured")
            sl = acc_metrics.get("Slightly Injured")

            if k is not None and not k.empty and si is not None and not si.empty and sl is not None and not sl.empty:
                tmp = (
                    k[["year", "value"]].rename(columns={"value": "Killed"})
                    .merge(si[["year", "value"]].rename(columns={"value": "Seriously Injured"}), on="year", how="outer")
                    .merge(sl[["year", "value"]].rename(columns={"value": "Slightly Injured"}), on="year", how="outer")
                    .sort_values("year")
                )
                tmp["Injured (Serious+Slight)"] = tmp["Seriously Injured"].fillna(0) + tmp["Slightly Injured"].fillna(0)
                fig = px.line(tmp, x="year", y=["Killed", "Injured (Serious+Slight)"], markers=True)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("Breakdown rows (Killed/Seriously/Slightly) not detected in Table 13.6(a).")
        else:
            st.info("Load knbs_road_accidents_summary.csv first.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="chart-card"><div class="chart-title">Casualties Breakdown</div>', unsafe_allow_html=True)
        if acc_ok:
            k = acc_metrics.get("Killed")
            si = acc_metrics.get("Seriously Injured")
            sl = acc_metrics.get("Slightly Injured")
            if k is not None and not k.empty and si is not None and not si.empty and sl is not None and not sl.empty:
                tmp = (
                    k[["year", "value"]].rename(columns={"value": "Killed"})
                    .merge(si[["year", "value"]].rename(columns={"value": "Seriously Injured"}), on="year", how="outer")
                    .merge(sl[["year", "value"]].rename(columns={"value": "Slightly Injured"}), on="year", how="outer")
                    .sort_values("year")
                )
                fig = px.line(tmp, x="year", y=["Killed", "Seriously Injured", "Slightly Injured"], markers=True)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("Breakdown rows not detected in Table 13.6(a).")
        else:
            st.info("Load knbs_road_accidents_summary.csv first.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Casualties By Road User Type</div>', unsafe_allow_html=True)
        if acc_class is not None and not acc_class.empty:
            if "Type" not in acc_class.columns or "Class" not in acc_class.columns:
                cols = list(acc_class.columns)
                if len(cols) >= 2:
                    acc_class = acc_class.rename(columns={cols[0]: "Type", cols[1]: "Class"})

            accb_long = wide_years_to_long(acc_class, ["Type", "Class"])
            if not accb_long.empty:
                accb_long["type_norm"] = _norm(accb_long["Type"])
                type_tot = accb_long.groupby(["year", "type_norm"], as_index=False)["value"].sum()

                want = ["pedestrians", "drivers", "passengers", "pillion passengers"]
                keep = type_tot[type_tot["type_norm"].isin(want)].copy()

                if keep.empty and type_tot["year"].notna().any():
                    ly = int(type_tot["year"].max())
                    top_types = (
                        type_tot[type_tot["year"] == ly]
                        .sort_values("value", ascending=False)
                        .head(4)["type_norm"]
                        .tolist()
                    )
                    keep = type_tot[type_tot["type_norm"].isin(top_types)].copy()

                keep["Type"] = keep["type_norm"].str.title()
                fig = px.line(keep, x="year", y="value", color="Type", markers=True)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("13.6(b) loaded but could not detect year columns.")
        else:
            st.info("Optional: generate knbs_road_accidents_by_type_class.csv to unlock this chart.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Snapp Lens")
    st.write(
        "- **Registrations & licensing** proxy mobility demand and affordability.\n"
        "- **Accidents & casualties** proxy road safety risk, productivity loss, and logistics reliability.\n"
        "- Watch **motorcycles** + **accident casualties** together (last-mile growth vs safety stress)."
    )

    st.subheader("Data Lag")
    st.write(f"Latest registrations/licensing year available: **{latest_year if latest_year is not None else 'NA'}**")
    st.write(f"Latest road safety year available: **{acc_latest_year if acc_latest_year is not None else 'NA'}**")

    if show_tables:
        st.subheader("Cleaned datasets (Transport)")
        st.write("Vehicle registrations (clean)")
        st.dataframe(veh.tail(25), use_container_width=True)
        st.write("Transport licenses (clean)")
        st.dataframe(lic.tail(25), use_container_width=True)
        st.write("Road accidents summary (13.6a)")
        st.dataframe(acc_sum, use_container_width=True)
        st.write("Road accidents by type/class (13.6b)")
        st.dataframe(acc_class, use_container_width=True)


# TAB 3: DEMAND PROXIES

with tab3:
    st.subheader("Key Indicators")
    st.caption("Source: Google Trends Scrape / World Bank / EPRA.")

    k1, k2, k3, k4 = st.columns(4)

    if not trends.empty:
        cols = [c for c in trends.columns if c.endswith("_index")]
        if cols and latest_trends_date is not None:
            last_row = trends.dropna(subset=["date"]).iloc[-1]
            v1 = float(last_row[cols[0]]) if pd.notna(last_row[cols[0]]) else None
            v2 = float(last_row[cols[1]]) if len(cols) > 1 and pd.notna(last_row[cols[1]]) else None
            k1.metric(cols[0].replace("_", " ").title(), f"{v1:.1f}" if v1 is not None else "NA", help=f"Date: {pd.to_datetime(latest_trends_date).date()}")
            k2.metric(cols[1].replace("_", " ").title(), f"{v2:.1f}" if (v2 is not None and len(cols) > 1) else "NA", help=f"Date: {pd.to_datetime(latest_trends_date).date()}")
        else:
            k1.metric("Trends index", "NA")
            k2.metric("Trends index", "NA")
    else:
        k1.metric("Trends index", "NA")
        k2.metric("Trends index", "NA")

    if (not epra.empty) and ("super_petrol" in epra.columns):
        _tmp = epra.dropna(subset=["super_petrol"])
        epra_latest = _tmp.iloc[-1] if len(_tmp) else None
        if epra_latest is not None:
            k3.metric(
                "Super Petrol (Latest)",
                f"{float(epra_latest['super_petrol']):.2f}",
                help=f"City: {epra_latest.get('city','NA')} | Cycle: {pd.to_datetime(epra_latest.get('cycle_start')).date() if pd.notna(epra_latest.get('cycle_start')) else 'NA'}",
            )
        else:
            k3.metric("Super Petrol (Latest)", "NA")
    else:
        k3.metric("Super Petrol (Latest)", "NA")

    if not wb_ctx.empty and latest_wb_year is not None:
        wb_candidates = ["private_consumption_growth_pct", "gdp_growth_pct", "unemployment_total_pct", "unemployment_youth_pct"]
        wb_pick = next((c for c in wb_candidates if c in wb_ctx.columns), None)
        if wb_pick is not None:
            wb_latest_val = wb_ctx.loc[wb_ctx["year"] == latest_wb_year, wb_pick]
            if len(wb_latest_val) and pd.notna(wb_latest_val.values[0]):
                k4.metric(wb_pick.replace("_", " ").title(), f"{float(wb_latest_val.values[0]):.2f}", help=f"Year: {latest_wb_year}")
            else:
                k4.metric(wb_pick.replace("_", " ").title(), "NA", help=f"Year: {latest_wb_year}")
        else:
            k4.metric("World Bank (Latest)", "NA")
    else:
        k4.metric("World Bank (Latest)", "NA")

    st.divider()
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown('<div class="chart-card"><div class="chart-title">Google Trends (index)</div>', unsafe_allow_html=True)
        if not trends.empty and "date" in trends.columns:
            idx_cols = [c for c in trends.columns if c.endswith("_index")]
            if idx_cols:
                fig = px.line(trends, x="date", y=idx_cols, markers=False)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("No *_index columns found in demand_google_trends.csv")
        else:
            st.warning("Demand trends dataset not found (Clean_Data/demand_google_trends.csv).")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">EPRA Pump Prices per City</div>', unsafe_allow_html=True)
        if not epra.empty and "city" in epra.columns and "cycle_start" in epra.columns:
            cities = sorted([c for c in epra["city"].dropna().unique().tolist() if str(c).strip()])
            if cities:
                chosen_city = st.selectbox("City", options=cities, index=0, key="epra_city")
                city_df = epra[epra["city"].astype(str).str.strip().eq(str(chosen_city).strip())].copy()
                y_cols = [c for c in ["super_petrol", "diesel", "kerosene"] if c in city_df.columns]
                if (not city_df.empty) and y_cols:
                    fig = px.line(city_df, x="cycle_start", y=y_cols, markers=True)
                    fig.update_layout(height=520)
                    st.plotly_chart(force_light_plotly(fig), use_container_width=True)
                else:
                    st.info("EPRA dataset loaded but required columns are missing/empty.")
            else:
                st.info("EPRA dataset loaded but no cities detected.")
        else:
            st.warning("EPRA dataset not found (Clean_Data/epra_pump_prices.csv).")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="chart-card"><div class="chart-title">World Bank Context (annual)</div>', unsafe_allow_html=True)
        if not wb_ctx.empty and "year" in wb_ctx.columns:
            y_cols = [c for c in wb_ctx.columns if c != "year" and wb_ctx[c].notna().any()]
            if y_cols:
                pick = st.multiselect("Select series", options=y_cols, default=y_cols[:2] if len(y_cols) >= 2 else y_cols[:1], key="wb_series")
                if pick:
                    fig = px.line(wb_ctx, x="year", y=pick, markers=True)
                    fig.update_layout(height=520)
                    st.plotly_chart(force_light_plotly(fig), use_container_width=True)
                else:
                    st.info("Select at least one series.")
            else:
                st.info("World Bank context file has no usable series columns.")
        else:
            st.warning("World Bank context dataset not found (Clean_Data/worldbank_demand_context.csv).")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Keyword-level (if present)</div>', unsafe_allow_html=True)
        if not trends.empty and "date" in trends.columns:
            kw_cols = [c for c in trends.columns if c not in ["date"] and not c.endswith("_index") and trends[c].notna().any()]
            if kw_cols:
                chosen_kw = st.selectbox("Keyword", options=kw_cols, index=0, key="kw_pick")
                fig = px.line(trends, x="date", y=chosen_kw, markers=False)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("No keyword columns detected (only indices available).")
        else:
            st.info("Load trends file to view keyword-level series.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("Snapp Lens")
    st.write(
        "- **Trends baskets** proxy household stress, digital spend appetite, and job-search intensity.\n"
        "- **EPRA pump prices** proxy cost pressure and transport/logistics friction.\n"
        "- **World Bank context** anchors long-run macro demand i.e consumption growth, unemployment, GDP growth.\n\n"
        "**Implication:** anticipate demand shifts earlier than official stats; validate pricing, bundling, and channel strategy."
    )

    st.subheader("Data Lag")
    st.write(f"Latest Trends date: **{pd.to_datetime(latest_trends_date).date()}**" if latest_trends_date is not None else "Latest Trends date: **NA**")
    st.write(f"Latest EPRA cycle start: **{pd.to_datetime(latest_epra_cycle).date()}**" if latest_epra_cycle is not None else "Latest EPRA cycle start: **NA**")
    st.write(f"Latest World Bank year: **{latest_wb_year if latest_wb_year is not None else 'NA'}**")

    if show_tables:
        st.subheader("Cleaned datasets (Demand)")
        st.write("Google Trends (clean)")
        st.dataframe(trends.tail(25), use_container_width=True)
        st.write("World Bank context (clean)")
        st.dataframe(wb_ctx.tail(25), use_container_width=True)
        st.write("EPRA pump prices (clean)")
        st.dataframe(epra.tail(25), use_container_width=True)


# TAB 4: EAC CONTEXT

with tab4:
    st.subheader("Regional Context")
    st.caption("Source: World Bank.")

    if wb_reg.empty:
        st.warning("Regional context dataset not found (Clean_Data/worldbank_regional_context.csv).")
    else:
        reg_long = regional_wide_to_long(wb_reg)

        comparators = ["Kenya", "Rwanda", "Tanzania", "Ethiopia"]

        reg_long["country"] = reg_long["country"].astype(str).str.strip()
        reg_long["indicator"] = reg_long["indicator"].astype(str).str.strip()
        reg_long["year"] = pd.to_numeric(reg_long["year"], errors="coerce")
        reg_long["value"] = pd.to_numeric(reg_long["value"], errors="coerce")
        reg_long = reg_long.dropna(subset=["year"]).copy()
        reg_long["year"] = reg_long["year"].astype(int)

        available_inds = sorted([i for i in reg_long["indicator"].dropna().unique().tolist() if str(i).strip()])

        if not available_inds:
            st.info("Regional file loaded but no indicators detected. Expected: 'Kenya | gdp_growth_pct'.")
        else:
            def _unit_suffix(ind_name: str) -> str:
                s = (ind_name or "").lower()
                if ("pct" in s) or ("growth" in s) or ("unemployment" in s) or ("inflation" in s):
                    return "%"
                return ""

            def _fmt_value(v, ind_name: str) -> str:
                if v is None or pd.isna(v):
                    return "NA"
                suf = _unit_suffix(ind_name)
                return f"{float(v):.2f}{suf}"

            top_left, top_right = st.columns([2.2, 1.1])

            with top_left:
                default_kpi = "gdp_growth_pct" if "gdp_growth_pct" in available_inds else available_inds[0]
                kpi_indicator = st.selectbox("Indicator", options=available_inds, index=available_inds.index(default_kpi), key="reg_kpi_ind")

            with top_right:
                years = sorted(reg_long["year"].dropna().unique().tolist())
                chosen_year = st.selectbox("Year", options=years, index=len(years) - 1 if years else 0, key="reg_kpi_year")

            k1, k2, k3, k4 = st.columns(4)

            kpi_vals = []
            for country, col in zip(comparators, [k1, k2, k3, k4]):
                val = reg_long[
                    (reg_long["year"] == chosen_year)
                    & (reg_long["country"].astype(str).str.strip().str.lower() == country.lower())
                    & (reg_long["indicator"] == kpi_indicator)
                ]["value"]
                v = float(val.values[0]) if len(val) and pd.notna(val.values[0]) else None
                kpi_vals.append({"country": country, "value": v})
                col.metric(country, _fmt_value(v, kpi_indicator), help=f"Year: {chosen_year}")

            rank_df = pd.DataFrame(kpi_vals).dropna(subset=["value"]).sort_values("value", ascending=False).reset_index(drop=True)
            if not rank_df.empty and (rank_df["country"] == "Kenya").any():
                kenya_rank = int(rank_df.index[rank_df["country"] == "Kenya"][0]) + 1
                st.write(f"**Kenya ranks {kenya_rank} of {len(rank_df)}** on this indicator among the selected peers.")

            st.divider()

            st.markdown('<div class="chart-card"><div class="chart-title">Trend — Kenya vs Peers</div>', unsafe_allow_html=True)
            trend_df = reg_long[(reg_long["indicator"] == kpi_indicator) & (reg_long["country"].isin(comparators))].copy()
            trend_df = trend_df.dropna(subset=["value"])
            if trend_df.empty:
                st.info("No trend data available for the selected indicator.")
            else:
                fig = px.line(trend_df, x="year", y="value", color="country", markers=True)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Kenya vs Peer average</div>', unsafe_allow_html=True)
            gap_df = trend_df.copy()
            if gap_df.empty:
                st.info("No data available to compute gap.")
            else:
                peers_only = gap_df[gap_df["country"].str.lower() != "kenya"].copy()
                kenya_only = gap_df[gap_df["country"].str.lower() == "kenya"].copy()

                peer_avg = peers_only.groupby("year", as_index=False)["value"].mean().rename(columns={"value": "peer_avg"})
                kenya_series = kenya_only.groupby("year", as_index=False)["value"].mean().rename(columns={"value": "kenya"})

                merged = pd.merge(kenya_series, peer_avg, on="year", how="inner")
                merged["kenya_minus_peer_avg"] = merged["kenya"] - merged["peer_avg"]

                if merged.empty:
                    st.info("Not enough overlap years to compute gap.")
                else:
                    fig = px.line(merged, x="year", y="kenya_minus_peer_avg", markers=True)
                    fig.update_layout(height=520)
                    st.plotly_chart(force_light_plotly(fig), use_container_width=True)
                    suf = _unit_suffix(kpi_indicator)
                    st.caption(f"Gap is Kenya − average(peers). Units: {suf if suf else 'raw'}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Rank Over Time</div>', unsafe_allow_html=True)
            rank_src = trend_df.copy()
            if rank_src.empty:
                st.info("No data available to compute rank.")
            else:
                pivot = rank_src.pivot_table(index="year", columns="country", values="value", aggfunc="mean")
                if pivot.empty or "Kenya" not in pivot.columns:
                    st.info("Kenya series not available for rank.")
                else:
                    kenya_rank_series = pivot.rank(axis=1, ascending=False, method="min")["Kenya"]
                    rank_plot = kenya_rank_series.reset_index().rename(columns={"Kenya": "Kenya_rank"})
                    rank_plot["Kenya_rank"] = pd.to_numeric(rank_plot["Kenya_rank"], errors="coerce")
                    fig = px.line(rank_plot, x="year", y="Kenya_rank", markers=True)
                    fig.update_layout(height=520)
                    st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.divider()
            st.subheader("Snapp Lens")
            st.write(
                "- The **Trend chart** shows whether Kenya is moving with peers or diverging.\n"
                "- The **Gap chart** isolates Kenya-specific shocks (policy, FX, domestic demand) vs regional forces.\n"
                "- The **Rank chart** gives a simplified Kenyan position for decision making."
            )

            st.subheader("Data Lag")
            latest_wb_reg_year = int(reg_long["year"].max()) if reg_long["year"].notna().any() else None
            st.write(f"Latest Regional Data: **{latest_wb_reg_year if latest_wb_reg_year is not None else 'NA'}**")

            if show_tables:
                st.subheader("Cleaned datasets (Regional)")
                st.write("World Bank regional context (wide)")
                st.dataframe(wb_reg.tail(25), use_container_width=True)


# TAB 5: COMPLIANCE / KRA

with tab5:
    st.subheader("Compliance Signals (KRA)")
    st.caption("Source: KRA.")

    if cpix.empty:
        st.warning("CPIx dataset not found (Clean_Data/compliance_pressure_index.csv).")
    else:
        latest_row = cpix.dropna(subset=["period"]).iloc[-1] if cpix.dropna(subset=["period"]).shape[0] else None

        k1, k2, k3, k4 = st.columns(4)
        if latest_row is not None:
            k1.metric("CPIx (Overall)", f"{latest_row.get('cpix_overall','NA')}")
            k2.metric("SME CPIx", f"{latest_row.get('cpix_sme','NA')}")
            k3.metric("Midmarket CPIx", f"{latest_row.get('cpix_midmarket','NA')}")
            k4.metric("Enterprise CPIx", f"{latest_row.get('cpix_enterprise','NA')}")
        else:
            k1.metric("CPIx (Overall)", "NA")
            k2.metric("SME CPIx", "NA")
            k3.metric("Midmarket CPIx", "NA")
            k4.metric("Enterprise CPIx", "NA")

        st.divider()
        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="chart-card"><div class="chart-title">Compliance Pressure Index (CPIx) — Trend</div>', unsafe_allow_html=True)
            plot_df = cpix.copy()
            for c in ["cpix_overall", "cpix_sme", "cpix_midmarket", "cpix_enterprise"]:
                if c in plot_df.columns:
                    plot_df[c] = pd.to_numeric(plot_df[c], errors="coerce")

            y_cols = [c for c in ["cpix_overall", "cpix_sme", "cpix_midmarket", "cpix_enterprise"] if c in plot_df.columns and plot_df[c].notna().any()]
            if y_cols:
                fig = px.line(plot_df, x="period", y=y_cols, markers=True)
                fig.update_layout(height=520)
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("CPIx file loaded but CPIx columns are missing or empty.")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="chart-card"><div class="chart-title">Friction by Workflow Stage (from Friction Map)</div>', unsafe_allow_html=True)
            if friction.empty:
                st.info("Friction map not found (Clean_Data/friction_map.csv).")
            else:
                fr = friction.copy()
                if "severity" in fr.columns:
                    fr["severity"] = pd.to_numeric(fr["severity"], errors="coerce")

                if "workflow_stage" in fr.columns and fr["workflow_stage"].notna().any():
                    agg = (
                        fr.groupby("workflow_stage", as_index=False)
                        .agg(rows=("friction_id", "count"), avg_severity=("severity", "mean"))
                        .sort_values(["avg_severity", "rows"], ascending=False)
                    )
                    fig = px.bar(agg, x="workflow_stage", y="avg_severity")
                    fig.update_layout(height=520, xaxis_title="Workflow Stage", yaxis_title="Avg Severity (1–5)")
                    st.plotly_chart(force_light_plotly(fig), use_container_width=True)
                    st.caption("Higher avg severity = Higher compliance Friction Intensity.")
                else:
                    st.info("friction_map.csv loaded but workflow_stage column is missing.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="chart-card"><div class="chart-title">Latest KRA Compliance Events (last entries)</div>', unsafe_allow_html=True)
        if kra_events.empty:
            st.info("KRA events not found (Clean_Data/kra_events.csv).")
        else:
            show_cols = [c for c in ["event_date", "event_type", "tax_area", "segment", "severity", "description"] if c in kra_events.columns]
            st.dataframe(kra_events[show_cols].head(12), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">KRA Revenue Collection (Annual)</div>', unsafe_allow_html=True)
        if kra_rev.empty:
            st.info("Revenue KPI file not found (Clean_Data/kpi_kra_revenue.csv).")
        else:
            rev = kra_rev.copy()
            if "total_revenue_collection_ksh_trn" in rev.columns:
                rev["total_revenue_collection_ksh_trn"] = pd.to_numeric(rev["total_revenue_collection_ksh_trn"], errors="coerce")
            if "fiscal_year" in rev.columns and "total_revenue_collection_ksh_trn" in rev.columns and rev["total_revenue_collection_ksh_trn"].notna().any():
                fig = px.line(rev, x="fiscal_year", y="total_revenue_collection_ksh_trn", markers=True)
                fig.update_layout(height=420, xaxis_title="Fiscal Year", yaxis_title="Total Revenue (KSh Trn)")
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.dataframe(kra_rev.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("Snapp Lens")
        st.write(
            "- CPIx summarizes compliance pressure trends.\n"
            "- Friction map shows where the pain sits across the compliance workflow.\n"
            "- Events table provides evidence to support weekly and or monthly narratives.\n\n"
            "**Implication:** package compliance support products/services by segment and workflow stage."
        )

        if show_tables:
            st.subheader("Cleaned datasets (Compliance)")
            st.write("CPIx (clean)")
            st.dataframe(cpix.tail(25), use_container_width=True)
            st.write("Friction map (clean)")
            st.dataframe(friction, use_container_width=True)
            st.write("KRA events (clean)")
            st.dataframe(kra_events.head(25), use_container_width=True)
            st.write("KRA revenue KPI (clean)")
            st.dataframe(kra_rev, use_container_width=True)


# TAB 6: ENERGY

with tab6:
    st.subheader("Energy Stress Index (ESI)")
    st.caption("Source: EPRA, World Bank, IEA")

    if esi.empty:
        st.warning("Energy Stress dataset not found (Clean_Data/energy_stress_index.csv).")
    else:
        if "month" not in esi.columns and "month_key" in esi.columns:
            esi["month"] = pd.to_datetime(esi["month_key"], errors="coerce")
            esi = esi.dropna(subset=["month"]).sort_values("month")

        latest = esi.iloc[-1]

        k1, k2, k3, k4 = st.columns(4)
        if "esi_overall" in esi.columns:
            k1.metric("ESI (Latest)", f"{float(latest['esi_overall']):.1f}", help=f"Month: {pd.to_datetime(latest['month']).date() if 'month' in latest else 'NA'}")
        else:
            k1.metric("ESI (Latest)", "NA")

        k2.metric("Interpretation", str(latest.get("interpretation_band", "NA")))
        k3.metric("Diesel (KES/L)", f"{float(latest['diesel_kes_l']):.2f}" if "diesel_kes_l" in esi.columns and pd.notna(latest.get("diesel_kes_l")) else "NA")
        k4.metric("Brent (USD/bbl)", f"{float(latest['brent_usd_bbl']):.2f}" if "brent_usd_bbl" in esi.columns and pd.notna(latest.get("brent_usd_bbl")) else "NA")

        st.divider()

        st.markdown('<div class="chart-card"><div class="chart-title">ESI Trend</div>', unsafe_allow_html=True)
        if "month" in esi.columns and "esi_overall" in esi.columns:
            fig = px.line(esi, x="month", y="esi_overall", markers=True)
            fig.update_layout(height=450)
            fig.add_hline(y=40, line_dash="dot")
            fig.add_hline(y=60, line_dash="dot")
            fig.add_hline(y=80, line_dash="dot")
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("ESI file missing required columns.")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Component Breakdown (0–100)</div>', unsafe_allow_html=True)
        comp_cols = [c for c in ["pump_index", "fx_index", "brent_index"] if c in esi.columns]
        if "month" in esi.columns and comp_cols:
            fig = px.line(esi, x="month", y=comp_cols, markers=True)
            fig.update_layout(height=450)
            st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        else:
            st.info("Component columns missing (pump_index, fx_index, brent_index).")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card"><div class="chart-title">Sector Exposure Heat Map</div>', unsafe_allow_html=True)

        exposure_rows = [
            {"Sector": "Transport & Logistics", "Fuel_Intensity": 95, "FX_Sensitivity": 60, "PassThrough_Risk": 55},
            {"Sector": "Manufacturing",         "Fuel_Intensity": 75, "FX_Sensitivity": 70, "PassThrough_Risk": 60},
            {"Sector": "Agriculture Value Chain","Fuel_Intensity": 70, "FX_Sensitivity": 55, "PassThrough_Risk": 75},
            {"Sector": "Construction",          "Fuel_Intensity": 65, "FX_Sensitivity": 60, "PassThrough_Risk": 55},
            {"Sector": "FMCG Distribution",     "Fuel_Intensity": 60, "FX_Sensitivity": 50, "PassThrough_Risk": 65},
            {"Sector": "Retail (General)",      "Fuel_Intensity": 45, "FX_Sensitivity": 45, "PassThrough_Risk": 70},
            {"Sector": "Hospitality & Tourism", "Fuel_Intensity": 50, "FX_Sensitivity": 55, "PassThrough_Risk": 50},
            {"Sector": "Financial Services",    "Fuel_Intensity": 20, "FX_Sensitivity": 35, "PassThrough_Risk": 40},
            {"Sector": "Digital / SaaS",        "Fuel_Intensity": 15, "FX_Sensitivity": 30, "PassThrough_Risk": 35},
            {"Sector": "Professional Services", "Fuel_Intensity": 25, "FX_Sensitivity": 25, "PassThrough_Risk": 35},
            {"Sector": "Education",             "Fuel_Intensity": 20, "FX_Sensitivity": 20, "PassThrough_Risk": 30},
        ]
        exposure = pd.DataFrame(exposure_rows)
        exposure["Exposure_Score"] = (
            0.55 * exposure["Fuel_Intensity"]
            + 0.25 * exposure["FX_Sensitivity"]
            + 0.20 * exposure["PassThrough_Risk"]
        )

        def tier(s):
            if s >= 70:
                return "High"
            if s >= 45:
                return "Medium"
            return "Low"

        exposure["Tier"] = exposure["Exposure_Score"].apply(tier)
        exposure = exposure.sort_values("Exposure_Score", ascending=False).reset_index(drop=True)

        heat_cols = ["Fuel_Intensity", "FX_Sensitivity", "PassThrough_Risk", "Exposure_Score"]
        heat_df = exposure.set_index("Sector")[heat_cols]

        fig = px.imshow(
            heat_df,
            aspect="auto",
            labels=dict(x="Metric", y="Sector", color="Score"),
        )
        fig.update_layout(height=560)
        st.plotly_chart(force_light_plotly(fig), use_container_width=True)

        st.caption(
            "Scoring (0–100): 0.55×Fuel Intensity + 0.25×FX Sensitivity + 0.20×Pass-through Risk. "
            "High ≥ 70, Medium 45–69, Low < 45."
        )

        if show_tables:
            st.write("Exposure scoring table")
            st.dataframe(
                exposure[["Sector", "Fuel_Intensity", "FX_Sensitivity", "PassThrough_Risk", "Exposure_Score", "Tier"]],
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.subheader("Snapp Lens")
        st.write(
            "- Elevated ESI indicates rising cost pressure in logistics and supply chains.\n"
            "- Diesel momentum drives first-order stress in transport and distribution.\n"
            "- FX amplifies imported energy costs.\n"
            "- Brent momentum signals upstream global shocks.\n\n"
            "**Implication:** Monitor transport, manufacturing, and agriculture-linked SMEs during Elevated/Severe periods."
        )
        st.subheader("Data Lag")
        st.write(f"Latest ESI month: **{pd.to_datetime(latest['month']).date() if 'month' in esi.columns else 'NA'}**")


# TAB 7: SIGNALS MAP + INSIGHT REGISTRY

with tab7:
    st.markdown(
        """
        <div style="
        background: linear-gradient(135deg, rgba(255,251,235,1), rgba(254,243,199,0.9));
        padding: 22px 28px;
        border-radius: 20px;
        border: 1px solid rgba(245,158,11,0.25);
        margin-bottom: 22px;">
        <h3 style="margin:0;">Signals Map</h3>
        <p style="margin:6px 0 0 0;color:rgba(11,18,32,0.75);">
        Pressure, Demand pulse and Compliance Pressure (monthly).
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    def _to_month(dt):
        return pd.to_datetime(dt, errors="coerce").dt.to_period("M").dt.to_timestamp()

    def _minmax_0_100(s: pd.Series) -> pd.Series:
        s = pd.to_numeric(s, errors="coerce")
        if s.dropna().empty:
            return s
        mn, mx = float(s.min()), float(s.max())
        if mx == mn:
            return s * 0
        return (s - mn) / (mx - mn) * 100

    def _safe_col(df: pd.DataFrame, col: str) -> bool:
        return (df is not None) and (not df.empty) and (col in df.columns)

    base = pd.DataFrame()

    if _safe_col(cpi, "date") and _safe_col(cpi, "12-Month Inflation"):
        tmp = cpi.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["12-Month Inflation"].mean()
        base = tmp.rename(columns={"12-Month Inflation": "infl_yoy"})

    if _safe_col(fx, "date") and _safe_col(fx, "United States dollar"):
        tmp = fx.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["United States dollar"].mean()
        base = base.merge(tmp.rename(columns={"United States dollar": "kes_usd"}), on="month", how="outer") if not base.empty else tmp.rename(columns={"United States dollar": "kes_usd"})

    if _safe_col(rates, "date") and _safe_col(rates, "Central Bank Rate"):
        tmp = rates.copy()
        tmp["month"] = _to_month(tmp["date"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["Central Bank Rate"].mean()
        base = base.merge(tmp.rename(columns={"Central Bank Rate": "cbr"}), on="month", how="outer") if not base.empty else tmp.rename(columns={"Central Bank Rate": "cbr"})

    if (esi is not None) and (not esi.empty) and ("month" in esi.columns) and ("esi_overall" in esi.columns):
        tmp = esi.copy()
        tmp["month"] = _to_month(tmp["month"])
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["esi_overall"].mean()
        base = base.merge(tmp, on="month", how="outer") if not base.empty else tmp

    if (cpix is not None) and (not cpix.empty) and ("period" in cpix.columns) and ("cpix_overall" in cpix.columns):
        tmp = cpix.copy()
        tmp["month"] = _to_month(tmp["period"])
        tmp["cpix_overall"] = pd.to_numeric(tmp["cpix_overall"], errors="coerce")
        tmp = tmp.dropna(subset=["month"]).groupby("month", as_index=False)["cpix_overall"].mean()
        base = base.merge(tmp, on="month", how="outer") if not base.empty else tmp

    if (trends is not None) and (not trends.empty) and ("date" in trends.columns):
        demand_cols = [c for c in trends.columns if c.endswith("_index")]
        if demand_cols:
            tmp = trends.copy()
            tmp["month"] = _to_month(tmp["date"])
            tmp = tmp.dropna(subset=["month"])
            for c in demand_cols:
                tmp[c] = pd.to_numeric(tmp[c], errors="coerce")
            tmp = tmp.groupby("month", as_index=False)[demand_cols].mean()
            tmp["demand_pulse_raw"] = tmp[demand_cols].mean(axis=1, skipna=True)
            base = base.merge(tmp[["month", "demand_pulse_raw"]], on="month", how="outer") if not base.empty else tmp[["month", "demand_pulse_raw"]]

    if base.empty:
        st.warning("Signals Map needs at least one monthly dataset (CPI/FX/Rates/ESI/CPIx/Trends). None detected.")
        st.session_state["signals_base"] = pd.DataFrame()
    else:
        base = base.sort_values("month").reset_index(drop=True)

        if "infl_yoy" in base.columns:
            base["infl_100"] = _minmax_0_100(base["infl_yoy"])
        if "kes_usd" in base.columns:
            base["fx_100"] = _minmax_0_100(base["kes_usd"])
        if "cbr" in base.columns:
            base["cbr_100"] = _minmax_0_100(base["cbr"])
        if "esi_overall" in base.columns:
            base["esi_100"] = _minmax_0_100(base["esi_overall"])
        if "cpix_overall" in base.columns:
            base["cpix_100"] = _minmax_0_100(base["cpix_overall"])
        if "demand_pulse_raw" in base.columns:
            base["demand_100"] = _minmax_0_100(base["demand_pulse_raw"])

        pressure_parts = [c for c in ["infl_100", "fx_100", "cbr_100", "esi_100"] if c in base.columns]
        if pressure_parts:
            base["macro_pressure"] = base[pressure_parts].mean(axis=1, skipna=True)

        compl_parts = [c for c in ["cbr_100", "cpix_100"] if c in base.columns]
        if compl_parts:
            base["compliance_tightness"] = base[compl_parts].mean(axis=1, skipna=True)

        if "esi_100" in base.columns:
            base["energy_stress"] = base["esi_100"]

        st.session_state["signals_base"] = base

        latest_row = base.dropna(subset=["month"]).iloc[-1]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Latest Month", f"{pd.to_datetime(latest_row['month']).strftime('%b %Y')}")
        k2.metric("Macro Pressure", f"{float(latest_row['macro_pressure']):.1f}" if pd.notna(latest_row.get("macro_pressure")) else "NA")
        k3.metric("Compliance Tightness", f"{float(latest_row['compliance_tightness']):.1f}" if pd.notna(latest_row.get("compliance_tightness")) else "NA")
        k4.metric("Demand Pulse", f"{float(latest_row['demand_100']):.1f}" if pd.notna(latest_row.get("demand_100")) else "NA")

        st.divider()

        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="chart-card"><div class="chart-title">Macro Pressure Trend</div>', unsafe_allow_html=True)
            if "macro_pressure" in base.columns:
                fig = px.line(base, x="month", y="macro_pressure", markers=True)
                fig.update_layout(height=450, yaxis_title="0–100")
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("Macro Pressure needs CPI/FX/CBR/ESI (at least one missing).")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Component Breakdown</div>', unsafe_allow_html=True)
            comp_cols = [c for c in ["infl_100", "fx_100", "cbr_100", "esi_100", "cpix_100"] if c in base.columns]
            if comp_cols:
                fig = px.line(base, x="month", y=comp_cols, markers=False)
                fig.update_layout(height=450, yaxis_title="0–100")
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("No normalized components available.")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="chart-card"><div class="chart-title">Demand vs Pressure</div>', unsafe_allow_html=True)
            latest_q = None
            if ("macro_pressure" in base.columns) and ("demand_100" in base.columns):
                q = base.dropna(subset=["macro_pressure", "demand_100"]).copy()
                x_mid = float(q["demand_100"].median())
                y_mid = float(q["macro_pressure"].median())
                q["quadrant"] = "—"
                q.loc[(q["demand_100"] >= x_mid) & (q["macro_pressure"] < y_mid), "quadrant"] = "Growth (Demand↑, Pressure↓)"
                q.loc[(q["demand_100"] >= x_mid) & (q["macro_pressure"] >= y_mid), "quadrant"] = "Overheating (Demand↑, Pressure↑)"
                q.loc[(q["demand_100"] < x_mid) & (q["macro_pressure"] >= y_mid), "quadrant"] = "Stagflation risk (Demand↓, Pressure↑)"
                q.loc[(q["demand_100"] < x_mid) & (q["macro_pressure"] < y_mid), "quadrant"] = "Slowdown (Demand↓, Pressure↓)"

                fig = px.scatter(q, x="demand_100", y="macro_pressure", color="quadrant", hover_data={"month": True})
                fig.add_vline(x=x_mid, line_dash="dot")
                fig.add_hline(y=y_mid, line_dash="dot")
                fig.update_layout(height=450, xaxis_title="Demand Pulse (0–100)", yaxis_title="Macro Pressure (0–100)")
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)

                latest_q = q.iloc[-1]["quadrant"]
                st.caption(f"Latest quadrant: **{latest_q}** (split by median lines).")
            else:
                st.info("Quadrant view requires both Demand Pulse (Trends *_index) and Macro Pressure.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown('<div class="chart-card"><div class="chart-title">Compliance Tightness</div>', unsafe_allow_html=True)
            if "compliance_tightness" in base.columns:
                fig = px.line(base, x="month", y="compliance_tightness", markers=True)
                fig.update_layout(height=450, yaxis_title="0–100")
                st.plotly_chart(force_light_plotly(fig), use_container_width=True)
            else:
                st.info("Compliance Tightness needs CBR and/or CPIx.")
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        st.subheader("Insight Registry (Monthly Log)")
    

        def _safe_read_registry(path: Path) -> pd.DataFrame:
            try:
                if path.exists():
                    df = pd.read_csv(path)
                    if "month" in df.columns:
                        df["month"] = pd.to_datetime(df["month"], errors="coerce")
                    return df
                return pd.DataFrame()
            except Exception:
                return pd.DataFrame()

        def _append_registry(path: Path, row: dict, prevent_duplicate_month: bool = True):
            reg = _safe_read_registry(path)
            new_df = pd.DataFrame([row])

            if prevent_duplicate_month and (not reg.empty) and ("month" in reg.columns):
                same = reg["month"].astype(str).eq(str(row["month"]))
                if same.any():
                    return False, "Entry for this month already exists. Disable duplicate prevention or edit existing row."

            out = pd.concat([reg, new_df], ignore_index=True)
            out.to_csv(path, index=False)
            return True, "Saved to Insight Registry."

        current_month = pd.to_datetime(latest_row["month"]) if "month" in latest_row else None

        macro_pressure = float(latest_row["macro_pressure"]) if pd.notna(latest_row.get("macro_pressure")) else None
        compliance_tightness = float(latest_row["compliance_tightness"]) if pd.notna(latest_row.get("compliance_tightness")) else None
        demand_pulse = float(latest_row["demand_100"]) if pd.notna(latest_row.get("demand_100")) else None

        infl = float(latest_row["infl_yoy"]) if pd.notna(latest_row.get("infl_yoy")) else None
        fxv = float(latest_row["kes_usd"]) if pd.notna(latest_row.get("kes_usd")) else None
        cbrv = float(latest_row["cbr"]) if pd.notna(latest_row.get("cbr")) else None
        esi_raw = float(latest_row["esi_overall"]) if pd.notna(latest_row.get("esi_overall")) else None
        cpix_raw = float(latest_row["cpix_overall"]) if pd.notna(latest_row.get("cpix_overall")) else None

        def _band(v):
            if v is None:
                return None
            if v >= 75:
                return "Severe"
            if v >= 55:
                return "Elevated"
            if v >= 35:
                return "Moderate"
            return "Low"

        b_pressure = _band(macro_pressure)
        b_compliance = _band(compliance_tightness)
        b_demand = _band(demand_pulse)

        suggested_plays: list[str] = []
        if b_pressure in ["Elevated", "Severe"]:
            suggested_plays += [
                "Value-first bundles + smaller packs; emphasize ROI/efficiency",
                "Prioritize transport/manufacturing/agri SMEs (high exposure in pressure regimes)",
            ]
        if b_compliance in ["Elevated", "Severe"]:
            suggested_plays += [
                "Package compliance support by workflow stage (based on friction map)",
            ]
        if (b_demand in ["Low", "Moderate"]) and (b_pressure in ["Elevated", "Severe"]):
            suggested_plays += [
                "Slowdown risk: protect retention, tighten credit terms, reduce CAC waste",
            ]

        c1, c2 = st.columns([1.2, 1.0], gap="large")
        with c1:
            owner = st.text_input("Owner", value="Snapp Research")
            headline = st.text_input("Headline (one-liner)", value="")
        with c2:
            prevent_dupes = st.toggle("Prevent duplicate month entries", value=True)
            confidence = st.selectbox("Confidence", ["High", "Medium", "Low"], index=1)

        notes = st.text_area("Notes (context / evidence / links)", value="", height=110)

        play = st.selectbox(
            "Primary Strategic Play (saved)",
            options=(suggested_plays if suggested_plays else [""]),
            index=0,
        )

        save_col, _, dl_col = st.columns([0.7, 0.1, 0.9])

        with save_col:
            if st.button("✅ Save current month snapshot", use_container_width=True, disabled=(current_month is None)):
                entry = {
                    "month": str(current_month.date()) if current_month is not None else "",
                    "regime": latest_q if latest_q is not None else "",
                    "macro_pressure_0_100": round(macro_pressure, 2) if macro_pressure is not None else "",
                    "compliance_tightness_0_100": round(compliance_tightness, 2) if compliance_tightness is not None else "",
                    "demand_pulse_0_100": round(demand_pulse, 2) if demand_pulse is not None else "",
                    "inflation_yoy_pct": round(infl, 2) if infl is not None else "",
                    "kes_usd": round(fxv, 2) if fxv is not None else "",
                    "cbr_pct": round(cbrv, 2) if cbrv is not None else "",
                    "esi_overall": round(esi_raw, 2) if esi_raw is not None else "",
                    "cpix_overall": round(cpix_raw, 2) if cpix_raw is not None else "",
                    "headline": headline,
                    "primary_play": play,
                    "confidence": confidence,
                    "owner": owner,
                    "notes": notes,
                    "saved_at": pd.Timestamp.now().isoformat(timespec="seconds"),
                }

                ok, msg = _append_registry(INSIGHTS_PATH, entry, prevent_duplicate_month=prevent_dupes)
                if ok:
                    st.success(msg)
                else:
                    st.warning(msg)

        registry = _safe_read_registry(INSIGHTS_PATH)

        with dl_col:
            if registry is None or registry.empty:
                st.button("Download registry CSV", disabled=True, use_container_width=True)
            else:
                st.download_button(
                    "Download registry CSV",
                    data=registry.to_csv(index=False).encode("utf-8"),
                    file_name="insight_registry.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.markdown('<div class="chart-card"><div class="chart-title">Insight Registry — History</div>', unsafe_allow_html=True)
        if registry.empty:
            st.info("No entries yet. Save your first month snapshot above.")
        else:
            show = registry.copy()
            if "month" in show.columns:
                show["month"] = pd.to_datetime(show["month"], errors="coerce")
                show = show.sort_values("month", ascending=False)
            st.dataframe(show, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("Snapp Lens")

        def _band2(v):
            if v is None or pd.isna(v):
                return None
            v = float(v)
            if v >= 75:
                return "Severe"
            if v >= 55:
                return "Elevated"
            if v >= 35:
                return "Moderate"
            return "Low"

        mp = latest_row.get("macro_pressure", None)
        ct = latest_row.get("compliance_tightness", None)
        dp = latest_row.get("demand_100", None)

        b1 = _band2(mp)
        b2 = _band2(ct)
        b3 = _band2(dp)

        bullets = []
        if b1:
            bullets.append(f"- **Macro Pressure is {b1}** → expect tighter consumer budgets + pricing sensitivity.")
        if b2:
            bullets.append(f"- **Compliance Tightness is {b2}** → SME/admin burden risk rises; support + automation sells.")
        if b3:
            bullets.append(f"- **Demand Pulse is {b3}** → indicates whether attention/intent is strengthening or fading.")

        plays = []
        if b1 in ["Elevated", "Severe"]:
            plays.append("- Push **value-first bundles** + smaller pack sizes; emphasize ROI/efficiency.")
            plays.append("- Prioritize **transport/manufacturing/agri** segments (most exposed when pressure is high).")
        if b2 in ["Elevated", "Severe"]:
            plays.append("- Package **compliance support** by workflow stage.")
        if (b3 in ["Low", "Moderate"]) and (b1 in ["Elevated", "Severe"]):
            plays.append("- Treat as **slowdown risk**: protect retention, tighten credit terms, reduce CAC waste.")

        st.write("\n".join(bullets) if bullets else "- Not enough data to generate narrative yet.")
        st.write("**Possible Avenue:**")
        st.write("\n".join(plays) if plays else "- Collect more overlap months across sources to power playbook rules.")

        if show_tables:
            st.subheader("Signals Map table (monthly)")
            st.dataframe(base.tail(24), use_container_width=True)


# TAB 8: OPPORTUNITY MAP

with tab8:
    st.subheader("Snapp 2026 Opportunity Map")


    base = st.session_state.get("signals_base", pd.DataFrame())

    if base is None or base.empty:
        st.warning("Signals Map data not available.")
    else:
        latest = base.iloc[-1]
        demand = float(latest.get("demand_100", 50) or 50)
        pressure = float(latest.get("macro_pressure", 50) or 50)
        compliance = float(latest.get("compliance_tightness", 50) or 50)

        exposure_rows = [
            {"Sector": "Transport & Logistics", "Exposure": 85},
            {"Sector": "Manufacturing", "Exposure": 75},
            {"Sector": "Agriculture Value Chain", "Exposure": 70},
            {"Sector": "Construction", "Exposure": 65},
            {"Sector": "FMCG Distribution", "Exposure": 60},
            {"Sector": "Retail", "Exposure": 55},
            {"Sector": "Hospitality", "Exposure": 50},
            {"Sector": "Financial Services", "Exposure": 35},
            {"Sector": "Digital / SaaS", "Exposure": 25},
            {"Sector": "Professional Services", "Exposure": 30},
        ]
        opp = pd.DataFrame(exposure_rows)

        opp["Opportunity_Score"] = (
            0.50 * demand
            - 0.30 * pressure
            - 0.20 * compliance
            - 0.20 * opp["Exposure"]
        )
        opp = opp.sort_values("Opportunity_Score", ascending=False)

        k1, k2, k3 = st.columns(3)
        k1.metric("Demand Pulse", f"{demand:.1f}")
        k2.metric("Macro Pressure", f"{pressure:.1f}")
        k3.metric("Compliance Tightness", f"{compliance:.1f}")

        st.divider()

        st.markdown('<div class="chart-card"><div class="chart-title">2026 Sector Ranking</div>', unsafe_allow_html=True)
        fig = px.bar(opp, x="Opportunity_Score", y="Sector", orientation="h")
        fig.update_layout(height=500)
        st.plotly_chart(force_light_plotly(fig), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        top3 = opp.head(3)["Sector"].tolist()
        st.subheader("Strategic Recommendation")
        st.write(f"Top opportunity sectors based on current regime: **{', '.join(top3)}**")
        top3 = opp.head(3)["Sector"].tolist()
        st.session_state["opportunity_df"] = opp.copy()
        st.session_state["top3_opportunity"] = top3
        

# SNAPP BOT

dashboard_context = build_dashboard_context(
    latest_cpi=latest_cpi,
    latest_fx=latest_fx,
    latest_rates=latest_rates,
    latest_trends_date=latest_trends_date,
    latest_epra_cycle=latest_epra_cycle,
    latest_wb_year=latest_wb_year,
    latest_year=latest_year,
    acc_latest_year=acc_latest_year if "acc_latest_year" in locals() else None,
    latest_wb_reg_year=latest_wb_reg_year,
    esi=esi,
    cpix=cpix,
    kra_events=kra_events,
    base_signals=st.session_state.get("signals_base", pd.DataFrame()),
    opportunity_df=st.session_state.get("opportunity_df", pd.DataFrame()),
    top3_opportunity=st.session_state.get("top3_opportunity", []),
)

render_snapp_bot_fragment(answer_with_snapp_bot, dashboard_context)