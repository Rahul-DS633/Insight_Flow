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
    theme = "style_light.css" if st.session_state.get("light_mode", False) else "style.css"
    css_path = os.path.join(os.path.dirname(__file__), "assets", theme)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Initialize Database ──────────────────────────────────────────────
from database import init_db
init_db()

# ── Import Modules ────────────────────────────────────────────────────
from modules import data_upload, data_cleaning, chart_builder, dashboard_builder, data_filter, ai_insights, data_modeling
from modules.auth import init_auth_state, render_login_page, render_logout_button

# ── Initialize Auth State ─────────────────────────────────────────────
init_auth_state()

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
if "light_mode" not in st.session_state:
    st.session_state["light_mode"] = False

# Now that state is prepped, check auth and load CSS
load_css()

# ── Floating Theme Button (top-right corner) ─────────────────────────
if st.session_state["light_mode"]:
    _icon, _label, _next = "🌙", "Dark Mode", False
else:
    _icon, _label, _next = "☀️", "Light Mode", True

st.markdown(
    f'<div style="position:fixed;top:14px;right:24px;z-index:999999;">'
    f'</div>',
    unsafe_allow_html=True,
)

# Use a small column trick to put the button top-right
_btn_col1, _btn_col2 = st.columns([10, 1])
with _btn_col2:
    if st.button(f"{_icon}", key="theme_btn", help=f"Switch to {_label}"):
        st.session_state["light_mode"] = _next
        st.rerun()

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR (Always Visible)
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
    if st.session_state.get("user_authenticated", False):
        st.caption(f"Welcome, **{st.session_state.get('username', 'User')}**")
    st.caption("AI-Powered Data Analytics")

    st.markdown("---")

    # Navigation (Only if authenticated)
    if st.session_state.get("user_authenticated", False):
        page = st.radio(
            "Navigation",
            [
                "🏠  Home",
                "📂  Dataset Upload",
                "🧹  Power Query",
                "🧮  DAX & Modeling",
                "📊  Visual Analytics",
                "📈  Dashboards & Stories",
                "🎛️  Data Filtering",
                "🤖  AI Insights",
            ],
            index=0,
            key="nav_radio",
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Active dataset status
        if st.session_state.get("current_df") is not None:
            df = st.session_state["current_df"]
            st.markdown(
                f'<div style="background: var(--glass-bg, rgba(28,35,51,0.65)); '
                f'backdrop-filter: blur(8px); '
                f'border: 1px solid var(--glass-border, rgba(255,255,255,0.08)); border-radius: 12px; padding: 14px;">'
                f'<p style="color: var(--accent-green, #3fb950); font-size: 0.8rem; font-weight: 600; margin:0;">●  ACTIVE DATASET</p>'
                f'<p style="color: var(--text-primary, #e6edf3); font-weight: 600; margin: 4px 0 8px 0;">{st.session_state["current_df_name"]}</p>'
                f'<p style="color: var(--text-secondary, #8b949e); font-size: 0.8rem; margin:0;">📊 {len(df):,} rows × {len(df.columns)} columns</p>'
                f'<p style="color: var(--text-secondary, #8b949e); font-size: 0.8rem; margin:0;">💾 {len(st.session_state.get("saved_charts", []))} charts saved</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="background: var(--glass-bg, rgba(28,35,51,0.65)); '
                'backdrop-filter: blur(8px); '
                'border: 1px solid var(--glass-border, rgba(255,255,255,0.08)); border-radius: 12px; padding: 14px;">'
                '<p style="color: var(--text-muted, #484f58); font-size: 0.8rem; font-weight: 600; margin:0;">○  NO DATASET</p>'
                '<p style="color: var(--text-secondary, #8b949e); font-size: 0.8rem; margin: 4px 0 0 0;">Upload a file to start</p>'
                '</div>',
                unsafe_allow_html=True,
            )

        st.markdown("---")
    
    # Theme toggle is now a floating button at the top-right, not in sidebar
    st.markdown("---")
    
    # Logout Button (only if authenticated)
    if st.session_state.get("user_authenticated", False):
        render_logout_button()
    
    st.caption("v1.0.0 • Built with ❤️")

# ── Authentication Barrier ────────────────────────────────────────────
if not st.session_state.get("user_authenticated", False):
    render_login_page()
    st.stop()


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

    # Feature Cards – using CSS classes for glassmorphism
    features = [
        ("📂", "Dataset Upload", "Upload CSV & Excel files with instant preview and quality stats", "#58a6ff"),
        ("🧹", "Power Query", "Merge, Group By, Pivot/Unpivot + clean missing values & duplicates", "#3fb950"),
        ("🧮", "DAX & Modeling", "Create calculated columns, data relationships, and quick measures", "#f0883e"),
        ("📊", "Visual Analytics", "Tableau-style chart builder with Show Me!, forecasting & clustering", "#f0b429"),
        ("📈", "Dashboards & Stories", "Build interactive dashboards and create data stories", "#bc8cff"),
        ("🤖", "AI Insights", "Gemini AI analyzes your data and surfaces hidden patterns", "#39d2c0"),
    ]

    cols = st.columns(3)
    for i, (icon, title, desc, color) in enumerate(features):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="feature-card" style="--card-accent: {color}; margin: 8px 0;">
                    <p class="card-icon">{icon}</p>
                    <p class="card-title">{title}</p>
                    <p class="card-desc">{desc}</p>
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


# Note: Sidebar logic was moved up above the authentication barrier



# ══════════════════════════════════════════════════════════════════════
# ROUTING
# ══════════════════════════════════════════════════════════════════════

if "Home" in page:
    render_home()
elif "Dataset Upload" in page:
    data_upload.render()
elif "Power Query" in page:
    data_cleaning.render()
elif "DAX" in page:
    data_modeling.render()
elif "Visual Analytics" in page:
    chart_builder.render()
elif "Dashboard" in page or "Stories" in page:
    dashboard_builder.render()
elif "Data Filtering" in page:
    data_filter.render()
elif "AI Insights" in page:
    ai_insights.render()
