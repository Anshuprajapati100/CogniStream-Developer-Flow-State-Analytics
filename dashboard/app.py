from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.insights import generate_insights
from src.live_data import load_combined_data
from database.db import (
    initialize_database,
    add_developer,
    get_developers,
    add_session,
    get_sessions,
    delete_developer,
    delete_session,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "reports/flow_cognitive_analysis.csv"

st.set_page_config(
    page_title="CogniStream | Developer Flow & Cognitive Load Analytics",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# MODERN DESIGN SYSTEM & CSS INJECTION (Animations, Transitions & Glassmorphism)
# ==============================================================================
def inject_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* Root Variables */
        :root {
            --bg-base: #0a0e1a;
            --surface-glass: rgba(18, 25, 43, 0.72);
            --surface-border: rgba(255, 255, 255, 0.08);
            --primary-indigo: #6366f1;
            --primary-violet: #8b5cf6;
            --primary-cyan: #06b6d4;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-subtle: #64748b;
        }

        /* Global Typography & Background */
        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: var(--text-main);
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(99, 102, 241, 0.09) 0%, transparent 40%),
                radial-gradient(circle at 88% 82%, rgba(6, 182, 212, 0.07) 0%, transparent 42%),
                radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.04) 0%, transparent 60%),
                var(--bg-base) !important;
            background-attachment: fixed !important;
        }

        /* Top Header Styling */
        [data-testid="stHeader"] {
            background: rgba(10, 14, 26, 0.75) !important;
            backdrop-filter: blur(16px) !important;
            border-bottom: 1px solid var(--surface-border) !important;
        }

        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(13, 19, 33, 0.94) !important;
            backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        }

        /* Keyframe Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(18px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes liveDotPulse {
            0%, 100% {
                opacity: 1;
                transform: scale(1);
            }
            50% {
                opacity: 0.35;
                transform: scale(0.85);
            }
        }

        /* Hero Container */
        .cogni-hero-card {
            background: linear-gradient(135deg, rgba(26, 35, 62, 0.65) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(99, 102, 241, 0.28);
            border-radius: 20px;
            padding: 26px 32px;
            margin-bottom: 22px;
            backdrop-filter: blur(20px);
            box-shadow: 0 12px 36px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.12);
            animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            position: relative;
            overflow: hidden;
        }

        .cogni-hero-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, #6366f1, #06b6d4, #8b5cf6, transparent);
        }

        .cogni-hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 12px;
        }

        .brand-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(99, 102, 241, 0.14);
            border: 1px solid rgba(99, 102, 241, 0.35);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #a5b4fc;
            text-transform: uppercase;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 0.8rem;
            font-weight: 600;
            color: #34d399;
        }

        .status-dot-active {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #10b981;
            animation: liveDotPulse 2s infinite ease-in-out;
            box-shadow: 0 0 10px #10b981;
        }

        .hero-title {
            font-size: 2.35rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            background: linear-gradient(135deg, #ffffff 40%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 8px 0;
            line-height: 1.15;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: #94a3b8;
            font-weight: 400;
            margin: 0;
            max-width: 850px;
            line-height: 1.55;
        }

        .hero-footnote {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-top: 14px;
            font-size: 0.8rem;
            color: #64748b;
            background: rgba(15, 23, 42, 0.45);
            padding: 6px 14px;
            border-radius: 8px;
            border: 1px dashed rgba(255, 255, 255, 0.1);
        }

        /* KPI Metric Cards */
        .kpi-card {
            background: var(--surface-glass);
            border: 1px solid var(--surface-border);
            border-radius: 16px;
            padding: 20px 22px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.4);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(14px);
            margin-bottom: 8px;
        }

        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 16px 36px -8px rgba(0, 0, 0, 0.6), 0 0 24px rgba(99, 102, 241, 0.22);
            border-color: rgba(99, 102, 241, 0.35);
        }

        .kpi-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .kpi-label {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #94a3b8;
        }

        .kpi-icon-wrap {
            width: 38px;
            height: 38px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            transition: transform 0.3s ease;
        }

        .kpi-card:hover .kpi-icon-wrap {
            transform: scale(1.12) rotate(4deg);
        }

        .kpi-value {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            color: #ffffff;
            font-family: 'Plus Jakarta Sans', sans-serif;
            margin-bottom: 6px;
            line-height: 1.1;
        }

        .kpi-footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 8px;
        }

        .kpi-chip {
            padding: 3px 9px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }

        .chip-indigo { background: rgba(99, 102, 241, 0.16); color: #a5b4fc; }
        .chip-cyan { background: rgba(6, 182, 212, 0.16); color: #67e8f9; }
        .chip-emerald { background: rgba(16, 185, 129, 0.16); color: #6ee7b7; }
        .chip-amber { background: rgba(245, 158, 11, 0.16); color: #fcd34d; }

        .kpi-progress-bg {
            width: 100%;
            height: 5px;
            background: rgba(255, 255, 255, 0.07);
            border-radius: 100px;
            margin-top: 10px;
            overflow: hidden;
        }

        .kpi-progress-fill {
            height: 100%;
            border-radius: 100px;
            transition: width 0.8s ease-in-out;
        }

        /* Tabs Modernization */
        div[data-testid="stTabs"] {
            gap: 8px;
            margin-bottom: 20px;
        }

        button[data-baseweb="tab"] {
            border-radius: 12px !important;
            padding: 10px 18px !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: #94a3b8 !important;
            background: rgba(18, 25, 43, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
            margin-right: 6px !important;
        }

        button[data-baseweb="tab"]:hover {
            color: #ffffff !important;
            background: rgba(30, 41, 69, 0.85) !important;
            border-color: rgba(99, 102, 241, 0.3) !important;
            transform: translateY(-2px) !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.28) 0%, rgba(139, 92, 246, 0.22) 100%) !important;
            border-color: rgba(99, 102, 241, 0.55) !important;
            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.28) !important;
        }

        div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
            display: none !important;
        }

        /* Section Banner */
        .section-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 18px 0 16px 0;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.07);
        }

        .section-pill {
            font-size: 0.74rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 4px 10px;
            border-radius: 6px;
            background: rgba(99, 102, 241, 0.16);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.28);
        }

        .section-heading {
            font-size: 1.3rem;
            font-weight: 700;
            color: #f8fafc;
            margin: 0;
            letter-spacing: -0.015em;
        }

        /* Insight Modern Cards */
        .insight-card {
            background: rgba(18, 25, 43, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 14px;
            backdrop-filter: blur(14px);
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .insight-card:hover {
            transform: translateX(5px);
            background: rgba(26, 36, 62, 0.85);
            box-shadow: 0 8px 26px -6px rgba(0, 0, 0, 0.4), 0 0 18px rgba(99, 102, 241, 0.18);
        }

        .insight-icon-bubble {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
        }

        .insight-body {
            flex: 1;
        }

        .insight-meta {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 4px;
        }

        .insight-tag {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            padding: 2px 8px;
            border-radius: 4px;
        }

        .insight-desc {
            font-size: 0.96rem;
            color: #e2e8f0;
            line-height: 1.5;
            margin: 0;
        }

        /* Interactive Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 10px !important;
            padding: 10px 22px !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(79, 70, 229, 0.55) !important;
            border-color: rgba(255, 255, 255, 0.3) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        .stDownloadButton > button {
            background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
            color: #ffffff !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(16, 185, 129, 0.32) !important;
            transition: all 0.25s ease !important;
        }

        .stDownloadButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.5) !important;
        }

        /* Form Inputs & Controls */
        div[data-baseweb="input"], div[data-baseweb="select"] {
            background-color: rgba(15, 23, 42, 0.7) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            transition: all 0.2s ease !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.28) !important;
        }

        /* Styled Dataframe Card */
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            background: rgba(15, 23, 42, 0.55) !important;
            box-shadow: 0 8px 26px -6px rgba(0, 0, 0, 0.38) !important;
        }

        /* Styled Alerts */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
        }

        /* Sidebar Brand Box */
        .sidebar-brand {
            padding: 16px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.14) 0%, rgba(15, 23, 42, 0.5) 100%);
            border: 1px solid rgba(99, 102, 241, 0.25);
            border-radius: 14px;
            margin-bottom: 20px;
        }

        .sidebar-brand-title {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }

        .filter-stats-pill {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 10px 14px;
            margin-top: 18px;
            font-size: 0.8rem;
            color: #94a3b8;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# PLOTLY MODERN DARK THEME HELPER
# ==============================================================================
def apply_modern_chart_theme(fig, height=390, title=None):
    """Apply a sleek, dark-glass theme with smooth hover and transition styling."""
    layout_update = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif",
            color="#cbd5e1",
            size=12,
        ),
        margin=dict(l=20, r=20, t=55, b=25),
        height=height,
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="rgba(99, 102, 241, 0.5)",
            font=dict(
                family="'JetBrains Mono', 'Plus Jakarta Sans', monospace",
                size=12,
                color="#ffffff",
            ),
        ),
        legend=dict(
            bgcolor="rgba(15, 23, 42, 0.65)",
            bordercolor="rgba(255, 255, 255, 0.08)",
            borderwidth=1,
            font=dict(size=11, color="#cbd5e1"),
        ),
    )
    if title:
        layout_update["title"] = dict(
            text=title,
            font=dict(
                family="'Plus Jakarta Sans', sans-serif",
                size=15,
                color="#f8fafc",
            ),
            x=0.01,
            xanchor="left",
        )
    fig.update_layout(**layout_update)
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zeroline=False,
        tickfont=dict(color="#94a3b8"),
        linecolor="rgba(255, 255, 255, 0.1)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.06)",
        zeroline=False,
        tickfont=dict(color="#94a3b8"),
        linecolor="rgba(255, 255, 255, 0.1)",
    )
    return fig


# Modern color palette for developers and categorical distributions
CYBER_PALETTE = ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]


# ==============================================================================
# DATA INITIALIZATION & LOADING
# ==============================================================================
def load_data():
    return load_combined_data()


@st.cache_resource
def setup_database():
    initialize_database()
    return True


inject_custom_styles()
setup_database()
df = load_data()


# ==============================================================================
# HERO BANNER & HEADER
# ==============================================================================
st.markdown(
    """
    <div class="cogni-hero-card">
        <div class="cogni-hero-header">
            <div class="brand-pill">
                <span>⚡</span>
                <span>CogniStream Intelligence</span>
                <span style="opacity: 0.6;">|</span>
                <span style="color: #c7d2fe;">v4.2 PRO</span>
            </div>
            <div class="status-badge">
                <span class="status-dot-active"></span>
                <span>Live Analytics Engine Active</span>
            </div>
        </div>
        <h1 class="hero-title">CogniStream</h1>
        <p class="hero-subtitle">
            Enterprise Developer Flow-State & Cognitive Workload Telemetry. Real-time insights
            into programming session density, contextual friction, and focus dynamics.
        </p>
        <div class="hero-footnote">
            <span>ℹ️</span>
            <span>Interactive analytics prototype using synthetic & live developer telemetry. Flow indicators are experimental research models.</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df is None:
    st.error(
        "Analysis dataset not found. "
        "Run data collection, cleaning, analytics and cognitive load scripts."
    )
    st.stop()


# ==============================================================================
# SIDEBAR FILTERS
# ==============================================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-title">
                <span style="font-size: 1.4rem;">🌊</span>
                <span style="font-size: 1.25rem; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">CogniStream</span>
            </div>
            <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.4;">
                Flow-State & Cognitive Telemetry Dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Telemetry Controls")
    if st.button("🔄  Refresh Analytics", width="stretch"):
        st.rerun()

    st.markdown("---")
    st.markdown("#### Filter Criteria")

    developers = sorted(df["developer_id"].unique().tolist())
    selected_developers = st.multiselect(
        "Developers",
        developers,
        default=developers,
        help="Select one or more developer IDs to filter telemetry",
    )

    min_date = df["session_date"].min().date()
    max_date = df["session_date"].max().date()

    selected_dates = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter session logs within this temporal window",
    )


# Apply filters
filtered = df[df["developer_id"].isin(selected_developers)].copy()

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    filtered = filtered[
        filtered["session_date"].dt.date.between(start_date, end_date)
    ]

# Display sidebar stats summary
with st.sidebar:
    st.markdown(
        f"""
        <div class="filter-stats-pill">
            <span>Filtered: <strong style="color: #ffffff;">{len(filtered)}</strong> sessions</span>
            <span>&bull;</span>
            <span><strong style="color: #ffffff;">{filtered['developer_id'].nunique() if not filtered.empty else 0}</strong> devs</span>
        </div>
        <div style="font-size: 0.72rem; color: #64748b; margin-top: 28px; text-align: center; line-height: 1.4;">
            Infotact Data Analytics Internship<br>
            <span style="color: #94a3b8; font-weight: 600;">CogniStream Analytics Engine</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

if filtered.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust the sidebar controls.")
    st.stop()


# ==============================================================================
# EXECUTIVE KPI METRICS (Glassmorphism Cards with Hover Animations)
# ==============================================================================
total_sessions = len(filtered)
total_developers = filtered["developer_id"].nunique()
coding_hours = filtered["coding_time_min"].sum() / 60
avg_flow = filtered["flow_indicator_score"].mean()

# Flow score color and status calculation
if avg_flow >= 70:
    flow_status = "High Flow"
    flow_color = "#10b981"
    flow_chip_class = "chip-emerald"
elif avg_flow >= 40:
    flow_status = "Moderate Flow"
    flow_color = "#f59e0b"
    flow_chip_class = "chip-amber"
else:
    flow_status = "Low Flow"
    flow_color = "#f43f5e"
    flow_chip_class = "chip-amber"

kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Developer Sessions</span>
                <div class="kpi-icon-wrap" style="background: rgba(99, 102, 241, 0.16); border: 1px solid rgba(99, 102, 241, 0.3); color: #818cf8;">
                    💻
                </div>
            </div>
            <div class="kpi-value">{total_sessions:,}</div>
            <div class="kpi-footer">
                <span class="kpi-chip chip-indigo">Telemetry Log</span>
                <span>Active Records</span>
            </div>
            <div class="kpi-progress-bg">
                <div class="kpi-progress-fill" style="width: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[1]:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Active Developers</span>
                <div class="kpi-icon-wrap" style="background: rgba(6, 182, 212, 0.16); border: 1px solid rgba(6, 182, 212, 0.3); color: #22d3ee;">
                    👥
                </div>
            </div>
            <div class="kpi-value">{total_developers}</div>
            <div class="kpi-footer">
                <span class="kpi-chip chip-cyan">Cohort Active</span>
                <span>Unique Engineers</span>
            </div>
            <div class="kpi-progress-bg">
                <div class="kpi-progress-fill" style="width: 100%; background: linear-gradient(90deg, #06b6d4, #3b82f6);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[2]:
    avg_per_session = coding_hours / total_sessions if total_sessions else 0
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Coding Hours</span>
                <div class="kpi-icon-wrap" style="background: rgba(16, 185, 129, 0.16); border: 1px solid rgba(16, 185, 129, 0.3); color: #34d399;">
                    ⏱️
                </div>
            </div>
            <div class="kpi-value">{coding_hours:.2f}h</div>
            <div class="kpi-footer">
                <span class="kpi-chip chip-emerald">Deep Work</span>
                <span>~{avg_per_session:.1f}h / session</span>
            </div>
            <div class="kpi-progress-bg">
                <div class="kpi-progress-fill" style="width: 100%; background: linear-gradient(90deg, #10b981, #059669);"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with kpi_cols[3]:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">Average Flow Indicator</span>
                <div class="kpi-icon-wrap" style="background: rgba(245, 158, 11, 0.16); border: 1px solid rgba(245, 158, 11, 0.3); color: #fbbf24;">
                    🌊
                </div>
            </div>
            <div class="kpi-value">{avg_flow:.2f}<span style="font-size: 1.1rem; color: #94a3b8; font-weight: 500;">/100</span></div>
            <div class="kpi-footer">
                <span class="kpi-chip {flow_chip_class}">{flow_status}</span>
                <span>Optimal Index</span>
            </div>
            <div class="kpi-progress-bg">
                <div class="kpi-progress-fill" style="width: {min(max(avg_flow, 0), 100):.1f}%; background: linear-gradient(90deg, #f59e0b, {flow_color});"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# MAIN TAB NAVIGATION
# ==============================================================================
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Overview",
        "👨‍💻 Developer Analytics",
        "🌊 Flow & Cognitive Load",
        "🔍 Session Explorer",
        "💡 Smart Insights",
        "⚙️ Developer Management",
    ]
)


# ==============================================================================
# TAB 1: OVERVIEW
# ==============================================================================
with tab1:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Temporal Telemetry</span>
            <h3 class="section-heading">Daily Developer Activity & Friction Metrics</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    daily = (
        filtered.groupby("session_date", as_index=False)
        .agg(
            coding_minutes=("coding_time_min", "sum"),
            sessions=("session_id", "count"),
        )
    )
    daily["coding_hours"] = daily["coding_minutes"] / 60

    # Line Chart with glowing area fill
    fig_daily = px.area(
        daily,
        x="session_date",
        y="coding_hours",
        markers=True,
        title="Daily Productive Coding Hours Trend",
    )
    fig_daily.update_traces(
        line=dict(color="#6366f1", width=3, shape="spline"),
        marker=dict(size=8, color="#a5b4fc", line=dict(width=2, color="#4338ca")),
        fillcolor="rgba(99, 102, 241, 0.16)",
        hovertemplate="<b>Date:</b> %{x|%b %d, %Y}<br><b>Coding Hours:</b> %{y:.2f} hrs<extra></extra>",
    )
    apply_modern_chart_theme(fig_daily, height=360)
    st.plotly_chart(fig_daily, width="stretch")

    # Secondary charts row
    left, right = st.columns(2)

    with left:
        fig_interrupt = px.histogram(
            filtered,
            x="interruptions",
            title="Interruptions per Session Distribution",
            color_discrete_sequence=["#06b6d4"],
            nbins=12,
        )
        fig_interrupt.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.15)")),
            hovertemplate="<b>Interruptions:</b> %{x}<br><b>Session Count:</b> %{y}<extra></extra>",
        )
        apply_modern_chart_theme(fig_interrupt, height=320)
        st.plotly_chart(fig_interrupt, width="stretch")

    with right:
        fig_switch = px.histogram(
            filtered,
            x="context_switches",
            title="Context Switches per Session Distribution",
            color_discrete_sequence=["#8b5cf6"],
            nbins=12,
        )
        fig_switch.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.15)")),
            hovertemplate="<b>Context Switches:</b> %{x}<br><b>Session Count:</b> %{y}<extra></extra>",
        )
        apply_modern_chart_theme(fig_switch, height=320)
        st.plotly_chart(fig_switch, width="stretch")


# ==============================================================================
# TAB 2: DEVELOPER ANALYTICS
# ==============================================================================
with tab2:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Cohort Benchmarks</span>
            <h3 class="section-heading">Developer Activity & Performance Distribution</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    developer_stats = (
        filtered.groupby("developer_id", as_index=False)
        .agg(
            sessions=("session_id", "count"),
            coding_minutes=("coding_time_min", "sum"),
            avg_flow=("flow_indicator_score", "mean"),
            avg_focus=("focus_rating", "mean"),
            avg_load=("cognitive_load_rating", "mean"),
            interruptions=("interruptions", "sum"),
            context_switches=("context_switches", "sum"),
        )
    )
    developer_stats["coding_hours"] = developer_stats["coding_minutes"] / 60

    st.dataframe(
        developer_stats.round(2),
        width="stretch",
        hide_index=True,
    )

    c_dev1, c_dev2 = st.columns(2)

    with c_dev1:
        fig_dev_hours = px.bar(
            developer_stats,
            x="developer_id",
            y="coding_hours",
            color="developer_id",
            color_discrete_sequence=CYBER_PALETTE,
            title="Total Coding Hours by Developer",
        )
        fig_dev_hours.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.15)")),
            hovertemplate="<b>%{x}:</b> %{y:.2f} coding hours<extra></extra>",
        )
        apply_modern_chart_theme(fig_dev_hours, height=360)
        st.plotly_chart(fig_dev_hours, width="stretch")

    with c_dev2:
        fig_dev_flow = px.bar(
            developer_stats,
            x="developer_id",
            y="avg_flow",
            color="developer_id",
            color_discrete_sequence=CYBER_PALETTE,
            title="Average Flow Indicator Score by Developer",
        )
        fig_dev_flow.add_hline(
            y=70,
            line_dash="dot",
            line_color="#10b981",
            annotation_text="High Flow Benchmark (70+)",
            annotation_position="top right",
            annotation_font=dict(color="#10b981", size=10),
        )
        fig_dev_flow.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.15)")),
            hovertemplate="<b>%{x}:</b> %{y:.2f} flow score<extra></extra>",
        )
        apply_modern_chart_theme(fig_dev_flow, height=360)
        st.plotly_chart(fig_dev_flow, width="stretch")


# ==============================================================================
# TAB 3: FLOW AND COGNITIVE LOAD
# ==============================================================================
with tab3:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Cognitive Dynamics</span>
            <h3 class="section-heading">Flow Indicator & Cognitive Load Distribution</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        flow_counts = (
            filtered["flow_indicator_band"]
            .value_counts()
            .reindex(["Low", "Moderate", "High"], fill_value=0)
            .reset_index()
        )
        flow_counts.columns = ["Flow Indicator", "Sessions"]

        band_colors = {"Low": "#f43f5e", "Moderate": "#f59e0b", "High": "#10b981"}

        fig_flow = px.bar(
            flow_counts,
            x="Flow Indicator",
            y="Sessions",
            color="Flow Indicator",
            color_discrete_map=band_colors,
            title="Flow Indicator Band Distribution",
        )
        fig_flow.update_traces(
            marker=dict(line=dict(width=1, color="rgba(255, 255, 255, 0.15)")),
            hovertemplate="<b>%{x}:</b> %{y} sessions<extra></extra>",
        )
        apply_modern_chart_theme(fig_flow, height=330)
        st.plotly_chart(fig_flow, width="stretch")

    with right:
        load_counts = (
            filtered["cognitive_load_band"]
            .value_counts()
            .reindex(["Low", "Moderate", "High"], fill_value=0)
            .reset_index()
        )
        load_counts.columns = ["Cognitive Load", "Sessions"]

        fig_load = px.pie(
            load_counts,
            names="Cognitive Load",
            values="Sessions",
            hole=0.55,
            color="Cognitive Load",
            color_discrete_map={"Low": "#10b981", "Moderate": "#f59e0b", "High": "#f43f5e"},
            title="Simulated Cognitive Load Distribution",
        )
        fig_load.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#0f172a", width=2)),
            hovertemplate="<b>%{label}:</b> %{value} sessions (%{percent})<extra></extra>",
        )
        apply_modern_chart_theme(fig_load, height=330)
        st.plotly_chart(fig_load, width="stretch")

    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Correlation Matrix</span>
            <h3 class="section-heading">Interruption Rate vs Flow Indicator Correlation</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_scatter = px.scatter(
        filtered,
        x="interruptions_per_hour",
        y="flow_indicator_score",
        color="developer_id",
        color_discrete_sequence=CYBER_PALETTE,
        hover_data=["session_id", "focus_rating", "coding_activity_ratio"],
        title="Interruption Rate vs Flow Indicator Score",
        labels={
            "interruptions_per_hour": "Interruptions per Hour",
            "flow_indicator_score": "Flow Indicator Score (0–100)",
        },
    )
    fig_scatter.update_traces(
        marker=dict(size=10, opacity=0.85, line=dict(width=1.5, color="#ffffff")),
        hovertemplate="<b>Session:</b> %{customdata[0]}<br><b>Interruptions/hr:</b> %{x:.2f}<br><b>Flow Score:</b> %{y:.2f}<extra></extra>",
    )
    apply_modern_chart_theme(fig_scatter, height=390)
    st.plotly_chart(fig_scatter, width="stretch")

    st.info(
        "💡 **Methodology Note:** The flow score formula incorporates interruption frequency as an inverse factor. "
        "Therefore, this negative correlation reflects internal model mechanics rather than independent causal proof."
    )


# ==============================================================================
# TAB 4: SESSION EXPLORER
# ==============================================================================
with tab4:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Raw Telemetry</span>
            <h3 class="section-heading">Developer Session Telemetry Log</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
    )

    csv = filtered.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥  Download Filtered Telemetry Records (CSV)",
        data=csv,
        file_name="cognistream_sessions.csv",
        mime="text/csv",
    )

    st.caption(f"Displaying {len(filtered)} filtered developer sessions.")


# ==============================================================================
# TAB 5: SMART INSIGHTS
# ==============================================================================
with tab5:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Algorithmic Synthesis</span>
            <h3 class="section-heading">Automated Descriptive Activity Insights</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Descriptive insights synthesized automatically from the filtered developer session cohort."
    )

    insights = generate_insights(filtered)

    insight_styles = [
        {"icon": "⚡", "category": "Productive Activity", "color": "#06b6d4", "bg": "rgba(6, 182, 212, 0.12)"},
        {"icon": "🛑", "category": "Interruption Rate", "color": "#f59e0b", "bg": "rgba(245, 158, 11, 0.12)"},
        {"icon": "🔀", "category": "Context Switching", "color": "#8b5cf6", "bg": "rgba(139, 92, 246, 0.12)"},
        {"icon": "🎯", "category": "Simulated Focus", "color": "#10b981", "bg": "rgba(16, 185, 129, 0.12)"},
        {"icon": "🧠", "category": "Cognitive Load", "color": "#6366f1", "bg": "rgba(99, 102, 241, 0.12)"},
        {"icon": "⚠️", "category": "Friction Threshold", "color": "#f43f5e", "bg": "rgba(244, 63, 94, 0.12)"},
    ]

    for index, insight in enumerate(insights):
        style = insight_styles[index % len(insight_styles)]
        st.markdown(
            f"""
            <div class="insight-card" style="border-left: 4px solid {style['color']};">
                <div class="insight-icon-bubble" style="background: {style['bg']}; color: {style['color']}; border: 1px solid {style['color']}40;">
                    {style['icon']}
                </div>
                <div class="insight-body">
                    <div class="insight-meta">
                        <span class="insight-tag" style="background: {style['bg']}; color: {style['color']};">Insight #{index + 1}</span>
                        <span style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">{style['category']}</span>
                    </div>
                    <p class="insight-desc">{insight}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Psychological Proxy</span>
            <h3 class="section-heading">Focus Rating vs Cognitive Load Rating</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig_focus = px.scatter(
        filtered,
        x="cognitive_load_rating",
        y="focus_rating",
        color="developer_id",
        color_discrete_sequence=CYBER_PALETTE,
        hover_data=["session_id", "coding_time_min"],
        title="Simulated Focus and Cognitive Load Ratings Distribution",
        labels={
            "focus_rating": "Focus Rating (1–5)",
            "cognitive_load_rating": "Cognitive Load Rating (1–5)",
        },
    )
    fig_focus.update_traces(
        marker=dict(size=12, opacity=0.85, line=dict(width=1.5, color="#ffffff")),
        hovertemplate="<b>Session:</b> %{customdata[0]}<br><b>Cognitive Load:</b> %{x}<br><b>Focus:</b> %{y}<extra></extra>",
    )
    apply_modern_chart_theme(fig_focus, height=380)
    st.plotly_chart(fig_focus, width="stretch")

    st.info(
        "ℹ️ **Experimental Data Reminder:** Ratings represent synthetic self-report metrics designed "
        "to illustrate dashboard behavior and should not be used as clinical diagnostic measurements."
    )


# ==============================================================================
# TAB 6: DEVELOPER MANAGEMENT
# ==============================================================================
with tab6:
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Administration</span>
            <h3 class="section-heading">Developer Cohort & Session Management</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    management_tab1, management_tab2, management_tab3 = st.tabs(
        ["➕ Add Developer", "🗑️ Delete Developer", "📋 Manage Sessions"]
    )

    with management_tab1:
        st.markdown("#### Register New Developer")
        with st.form("register_developer"):
            new_id = st.text_input(
                "Developer ID",
                placeholder="e.g. DEV007",
                help="Enter a unique alphanumeric identifier for the developer",
            )
            submitted = st.form_submit_button("➕ Register Developer")

        if submitted:
            try:
                add_developer(new_id)
                st.success(f"Developer {new_id} registered successfully!")
                st.rerun()
            except Exception as error:
                st.error(str(error))

        st.markdown("#### Active Registered Developers")
        registered = get_developers()
        if registered:
            st.dataframe(
                pd.DataFrame({"Developer ID": registered}),
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("No registered developers in the database.")

    with management_tab2:
        st.markdown("#### Remove Developer from Registry")
        registered = get_developers()
        if registered:
            developer_to_delete = st.selectbox(
                "Select Developer to Delete",
                registered,
                key="delete_developer_select",
            )
            with st.form("delete_developer_form"):
                confirm = st.checkbox("I confirm that this developer should be permanently removed.")
                delete_clicked = st.form_submit_button("🗑️ Delete Developer")

            if delete_clicked:
                if not confirm:
                    st.warning("Please check the confirmation box before deleting.")
                else:
                    try:
                        delete_developer(developer_to_delete)
                        st.success(f"Developer {developer_to_delete} deleted successfully!")
                        st.rerun()
                    except Exception as error:
                        st.error(str(error))
        else:
            st.info("No developers available for deletion.")

    with management_tab3:
        st.markdown("#### Manually Saved Sessions")
        saved_sessions = get_sessions()
        if saved_sessions:
            sessions_df = pd.DataFrame(saved_sessions)
            st.dataframe(
                sessions_df,
                width="stretch",
                hide_index=True,
            )
            session_ids = sessions_df["session_id"].tolist()
            session_to_delete = st.selectbox(
                "Select Session to Delete",
                session_ids,
            )
            with st.form("delete_session_form"):
                confirm_session = st.checkbox("I confirm that this session record should be deleted.")
                delete_session_clicked = st.form_submit_button("🗑️ Delete Session")

            if delete_session_clicked:
                if not confirm_session:
                    st.warning("Please confirm deletion before proceeding.")
                else:
                    try:
                        delete_session(session_to_delete)
                        st.success(f"Session {session_to_delete} deleted successfully!")
                        st.rerun()
                    except Exception as error:
                        st.error(str(error))
        else:
            st.info("No manually saved sessions found in the SQLite database.")

    # ADD CODING SESSION FORM
    st.markdown("---")
    st.markdown(
        """
        <div class="section-header">
            <span class="section-pill">Manual Ingestion</span>
            <h3 class="section-heading">Log New Coding Session</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    registered = get_developers()

    if not registered:
        st.info("Please register a developer before adding sessions.")
    else:
        with st.form("add_coding_session_form"):
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.markdown("##### 1. Session Information")
                developer = st.selectbox(
                    "Assigned Developer",
                    registered,
                    key="session_developer",
                )
                session_id = st.text_input(
                    "Unique Session ID",
                    placeholder="e.g. MAN001",
                )
                session_date = st.date_input(
                    "Session Date",
                    key="new_session_date",
                )

            with col_b:
                st.markdown("##### 2. Time Breakdown (minutes)")
                duration = st.number_input(
                    "Total Session Duration",
                    min_value=1,
                    value=120,
                    step=1,
                )
                coding = st.number_input(
                    "Coding Time",
                    min_value=0,
                    value=90,
                    step=1,
                )
                idle = st.number_input(
                    "Idle Time",
                    min_value=0,
                    value=15,
                    step=1,
                )
                other = st.number_input(
                    "Other Work Time",
                    min_value=0,
                    value=15,
                    step=1,
                )
                st.caption("ℹ️ Coding + Idle + Other must equal Total Duration")

            with col_c:
                st.markdown("##### 3. Dynamics & Ratings")
                interruptions = st.number_input(
                    "Interruptions Count",
                    min_value=0,
                    value=2,
                    step=1,
                )
                switches = st.number_input(
                    "Context Switches Count",
                    min_value=0,
                    value=3,
                    step=1,
                )
                tasks = st.number_input(
                    "Completed Tasks",
                    min_value=0,
                    value=1,
                    step=1,
                )
                focus = st.slider("Focus Rating (1–5)", 1, 5, 3)
                cognitive_load = st.slider("Cognitive Load Rating (1–5)", 1, 5, 3)

            save_session = st.form_submit_button("💾 Save Telemetry Record", width="stretch")

        if save_session:
            if not session_id.strip():
                st.error("Session ID is required.")
            elif coding + idle + other != duration:
                st.error(
                    f"Session components mismatch: Coding ({coding}) + Idle ({idle}) + Other ({other}) = {coding + idle + other} min, "
                    f"which does not equal Total Duration ({duration} min)."
                )
            elif session_id.strip().upper() in load_combined_data()["session_id"].astype(str).str.strip().str.upper().values:
                st.error(f"Session ID '{session_id.strip()}' already exists in the dataset.")
            else:
                session = {
                    "session_id": session_id.strip(),
                    "developer_id": developer,
                    "session_date": session_date.isoformat(),
                    "session_duration_min": int(duration),
                    "coding_time_min": int(coding),
                    "idle_time_min": int(idle),
                    "other_work_time_min": int(other),
                    "interruptions": int(interruptions),
                    "context_switches": int(switches),
                    "tasks_completed": int(tasks),
                    "focus_rating": int(focus),
                    "cognitive_load_rating": int(cognitive_load),
                }
                try:
                    add_session(session)
                    st.success("Coding session saved successfully!")
                    st.rerun()
                except Exception as error:
                    st.error(f"Could not save session: {error}")


# ==============================================================================
# FOOTER
# ==============================================================================
st.markdown("---")
st.markdown(
    """
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; padding: 12px 0 24px 0; color: #64748b; font-size: 0.8rem;">
        <div>
            <strong style="color: #94a3b8;">CogniStream Analytics</strong> &bull; Infotact Data Analytics Internship
        </div>
        <div>
            Synthetic Dataset &bull; Experimental Cognitive Telemetry Models
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# CogniStream Professional Frontend Styling
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(ellipse at 10% 0%,
        rgba(99,102,241,.13), transparent 38%),
        #090E1B;
    color: #F1F5F9;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11182B, #090E1B);
    border-right: 1px solid rgba(148,163,184,.16);
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #172036, #0D1424);
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,.15);
    transition: transform .25s ease,
                border-color .25s ease,
                box-shadow .25s ease;
    animation: cs-enter .5s ease both;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    border-color: rgba(129,140,248,.65);
    box-shadow: 0 15px 35px rgba(99,102,241,.15);
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-weight: 750;
}

h1, h2, h3 {
    color: #F8FAFC !important;
    letter-spacing: -.03em;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    border: 1px solid rgba(129,140,248,.4);
    background: linear-gradient(115deg, #6366F1, #5145CD);
    color: white;
    font-weight: 650;
    transition: transform .2s ease,
                box-shadow .2s ease,
                filter .2s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px);
    filter: brightness(1.12);
    box-shadow: 0 8px 22px rgba(99,102,241,.25);
}

[data-testid="stTabs"] button[role="tab"] {
    transition: background .2s ease, color .2s ease;
}

[data-testid="stTabs"] button[role="tab"]:hover {
    background: rgba(129,140,248,.12);
    color: #FFFFFF;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 14px;
    transition: border-color .2s ease;
}

[data-testid="stExpander"]:hover {
    border-color: rgba(129,140,248,.5);
}

@keyframes cs-enter {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 768px) {
    [data-testid="stMetric"] {
        padding: 14px;
        border-radius: 13px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)
