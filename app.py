"""
InsightFlow – AI-Powered Data Analytics Platform
Main Application Entry Point

A modern data analytics and visualization platform inspired by Power BI.
Built with Streamlit, Plotly, Pandas, and Google Gemini AI.
"""

import streamlit as st
import os

# ── Page Config (must be first Streamlit call) ────────────────────────
st.set_page_config(
    page_title="InsightFlow – AI Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Custom CSS ───────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ── Initialize Database ──────────────────────────────────────────────
from database import init_db
init_db()

# ── Import Modules ────────────────────────────────────────────────────
from modules import data_upload, data_cleaning, chart_builder, dashboard_builder, data_filter, ai_insights

# ── Session State Initialization ──────────────────────────────────────
if "current_df" not in st.session_state:
    st.session_state["current_df"] = None
if "current_df_name" not in st.session_state:
    st.session_state["current_df_name"] = None
if "original_df" not in st.session_state:
    st.session_state["original_df"] = None
if "filtered_df" not in st.session_state:
    st.session_state["filtered_df"] = None
if "saved_charts" not in st.session_state:
    st.session_state["saved_charts"] = []
if "ai_insights" not in st.session_state:
    st.session_state["ai_insights"] = ""


# ══════════════════════════════════════════════════════════════════════
# HOME PAGE
# ══════════════════════════════════════════════════════════════════════

def render_home():
    """Render the home / landing page."""
    # Hero Section
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <p style="font-size: 4rem; margin-bottom: 0;">📊</p>
            <h1 style="font-size: 3rem; margin: 10px 0;
                background: linear-gradient(135deg, #f0b429, #58a6ff);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;">
                InsightFlow
            </h1>
            <p style="font-size: 1.2rem; color: #8b949e; max-width: 600px; margin: 0 auto;">
                AI-Powered Data Analytics Platform — Upload, Analyze, Visualize, and
                Discover Insights from Your Data
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature Cards
    features = [
        ("📂", "Dataset Upload", "Upload CSV & Excel files with instant preview and quality stats", "#58a6ff"),
        ("🧹", "Data Cleaning", "Auto-detect and fix missing values, duplicates, and type issues", "#3fb950"),
        ("📊", "Chart Builder", "Build interactive Bar, Line, Scatter, Pie, Histogram & Heatmap charts", "#f0b429"),
        ("📈", "Dashboard", "Combine multiple charts into powerful visual dashboards", "#bc8cff"),
        ("🎛️", "Data Filtering", "Dynamic filters for focused exploration of data subsets", "#f0883e"),
        ("🤖", "AI Insights", "Gemini AI analyzes your data and surfaces hidden patterns", "#39d2c0"),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc, color) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="background: linear-gradient(145deg, #1c2333, #242d3d);
                    border: 1px solid #30363d; border-top: 3px solid {color};
                    border-radius: 12px; padding: 24px; margin: 8px 0; min-height: 160px;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;">
                    <p style="font-size: 2rem; margin-bottom:8px;">{icon}</p>
                    <p style="color: #e6edf3; font-weight: 700; font-size: 1.05rem; margin-bottom: 6px;">{title}</p>
                    <p style="color: #8b949e; font-size: 0.85rem; line-height: 1.5;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick Start
    st.markdown("### 🚀 Quick Start")
    st.markdown(
        """
        1. **📂 Upload** your CSV or Excel dataset
        2. **🧹 Clean** the data — fix missing values and duplicates
        3. **📊 Build** interactive charts with the visual chart builder
        4. **📈 Create** dashboards by combining your charts
        5. **🤖 Generate** AI-powered insights with Gemini
        """
    )

    # Tech Stack
    st.markdown("---")
    st.markdown("### 🛠️ Powered By")
    t1, t2, t3, t4, t5 = st.columns(5)
    with t1:
        st.markdown("🐍 **Python**")
    with t2:
        st.markdown("🎈 **Streamlit**")
    with t3:
        st.markdown("📊 **Plotly**")
    with t4:
        st.markdown("🐼 **Pandas**")
    with t5:
        st.markdown("🤖 **Gemini AI**")


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════

with st.sidebar:
    # Branding
    st.markdown(
        '<div class="brand-header">'
        '<span class="brand-logo">📊</span>'
        '<span class="brand-text">InsightFlow</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.caption("AI-Powered Data Analytics")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        [
            "🏠  Home",
            "📂  Dataset Upload",
            "🧹  Data Cleaning",
            "📊  Chart Builder",
            "📈  Dashboard",
            "🎛️  Data Filtering",
            "🤖  AI Insights",
        ],
        index=0,
        key="nav_radio",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Active dataset status
    if st.session_state["current_df"] is not None:
        df = st.session_state["current_df"]
        st.markdown(
            f'<div style="background: linear-gradient(145deg, #1c2333, #242d3d); '
            f'border: 1px solid #30363d; border-radius: 10px; padding: 14px;">'
            f'<p style="color: #3fb950; font-size: 0.8rem; font-weight: 600; margin:0;">●  ACTIVE DATASET</p>'
            f'<p style="color: #e6edf3; font-weight: 600; margin: 4px 0 8px 0;">{st.session_state["current_df_name"]}</p>'
            f'<p style="color: #8b949e; font-size: 0.8rem; margin:0;">📊 {len(df):,} rows × {len(df.columns)} columns</p>'
            f'<p style="color: #8b949e; font-size: 0.8rem; margin:0;">💾 {len(st.session_state.get("saved_charts", []))} charts saved</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="background: #1c2333; border: 1px solid #30363d; border-radius: 10px; padding: 14px;">'
            '<p style="color: #484f58; font-size: 0.8rem; font-weight: 600; margin:0;">○  NO DATASET</p>'
            '<p style="color: #8b949e; font-size: 0.8rem; margin: 4px 0 0 0;">Upload a file to start</p>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption("v1.0.0 • Built with ❤️")


# ══════════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════════

if "Home" in page:
    render_home()
elif "Dataset Upload" in page:
    data_upload.render()
elif "Data Cleaning" in page:
    data_cleaning.render()
elif "Chart Builder" in page:
    chart_builder.render()
elif "Dashboard" in page:
    dashboard_builder.render()
elif "Data Filtering" in page:
    data_filter.render()
elif "AI Insights" in page:
    ai_insights.render()
