"""
InsightFlow – Interactive Dashboards & Storytelling
Create dashboards with cross-filtering, and present data stories.
Combines Power BI dashboards with Tableau Stories.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import numpy as np
from config import COLORS, CHART_COLORS, PLOTLY_LAYOUT
from database import (
    save_dashboard, get_all_dashboards, get_dashboard,
    delete_dashboard, save_chart, get_charts_for_dashboard, delete_chart,
)


def render():
    """Render the dashboard & storytelling page."""
    st.markdown("## 📈 Dashboards & Stories")

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        st.markdown(
            f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:3rem;">📭</p>'
            "<p>No dataset loaded. Go to <b>Dataset Upload</b> first.</p></div>",
            unsafe_allow_html=True,
        )
        return

    tab1, tab2, tab3 = st.tabs(["🆕 Create Dashboard", "📂 My Dashboards", "📖 Story Mode"])

    with tab1:
        _render_create_dashboard()
    with tab2:
        _render_saved_dashboards()
    with tab3:
        _render_story_mode()


# ══════════════════════════════════════════════════════════════════════
# CREATE DASHBOARD
# ══════════════════════════════════════════════════════════════════════

def _render_create_dashboard():
    st.markdown("### 🎨 Create a New Dashboard")

    saved_charts = st.session_state.get("saved_charts", [])
    if not saved_charts:
        st.info("💡 No charts saved yet. Go to the **Visual Analytics Builder** to create and save charts, then come back here.")
        return

    c1, c2 = st.columns(2)
    with c1:
        dash_name = st.text_input("Dashboard Name", "My Dashboard", key="new_dash_name")
    with c2:
        dash_desc = st.text_input("Description", "", key="new_dash_desc")

    layout_cols = st.selectbox("Layout Columns", [1, 2, 3], index=1, key="dash_layout")

    # Cross-filtering toggle
    cross_filter = st.checkbox("🔗 Enable Cross-Filtering", value=True, key="cross_filter",
                               help="Click on a data point in one chart to filter others")

    st.markdown(f"### 📊 Available Charts ({len(saved_charts)})")

    selected_indices = []
    for i, chart in enumerate(saved_charts):
        cols = st.columns([0.5, 3, 1])
        with cols[0]:
            if st.checkbox("", key=f"sel_chart_{i}", value=True):
                selected_indices.append(i)
        with cols[1]:
            st.markdown(f"**{chart.get('title', 'Untitled')}** — {chart.get('chart_type_name', 'Chart')}")
        with cols[2]:
            dims = chart.get("dims", [])
            meas = chart.get("meas", [])
            info = f"D:{len(dims)} M:{len(meas)}"
            st.caption(info)

    st.markdown("---")

    # Preview
    if selected_indices:
        st.markdown("### 👁️ Dashboard Preview")
        _render_dashboard_grid(
            [saved_charts[i] for i in selected_indices],
            layout_cols,
            st.session_state["current_df"],
        )

    # Save
    if st.button("💾 Save Dashboard", key="save_dashboard_btn", use_container_width=True):
        if not selected_indices:
            st.warning("⚠️ Select at least one chart.")
            return
        dashboard_id = save_dashboard(dash_name, dash_desc)
        for pos, idx in enumerate(selected_indices):
            chart = saved_charts[idx]
            save_chart(dashboard_id, chart.get("chart_type", "bar"), chart.get("title", "Chart"), chart, pos)
        st.success(f"✅ Dashboard **{dash_name}** saved with {len(selected_indices)} chart(s)!")
        st.balloons()


# ══════════════════════════════════════════════════════════════════════
# SAVED DASHBOARDS
# ══════════════════════════════════════════════════════════════════════

def _render_saved_dashboards():
    st.markdown("### 📂 Saved Dashboards")
    dashboards = get_all_dashboards()

    if not dashboards:
        st.markdown(
            f'<div style="text-align:center; padding:40px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:2rem;">📭</p><p>No dashboards saved yet.</p></div>',
            unsafe_allow_html=True,
        )
        return

    for dash in dashboards:
        with st.expander(f"📈 {dash['name']}", expanded=False):
            st.caption(f"Created: {dash['created_at'][:10]} | {dash.get('description', '')}")
            charts = get_charts_for_dashboard(dash["id"])
            if charts and "current_df" in st.session_state:
                chart_configs = [json.loads(c["config_json"]) for c in charts]
                _render_dashboard_grid(chart_configs, 2, st.session_state["current_df"])

            if st.button("🗑️ Delete", key=f"del_dash_{dash['id']}"):
                delete_dashboard(dash["id"])
                st.rerun()


# ══════════════════════════════════════════════════════════════════════
# STORY MODE (Tableau Stories)
# ══════════════════════════════════════════════════════════════════════

def _render_story_mode():
    st.markdown("### 📖 Data Story")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">'
        "Create a presentation-style story by sequencing charts with narrative captions (like Tableau Stories).</p>",
        unsafe_allow_html=True,
    )

    saved_charts = st.session_state.get("saved_charts", [])
    if not saved_charts:
        st.info("💡 Save some charts first in the Visual Analytics Builder.")
        return

    # Initialize story
    if "story_points" not in st.session_state:
        st.session_state["story_points"] = []

    # Add story points
    st.markdown("#### ➕ Add a Story Point")
    c1, c2 = st.columns([2, 1])
    with c1:
        caption = st.text_area("Caption / Narrative", placeholder="Describe what this chart shows and the key insight...",
                               height=80, key="story_caption")
    with c2:
        chart_names = [c.get("title", f"Chart {i}") for i, c in enumerate(saved_charts)]
        sel_chart_idx = st.selectbox("Select Chart", range(len(chart_names)),
                                     format_func=lambda i: chart_names[i], key="story_chart_idx")

    if st.button("➕ Add Story Point", key="add_story_point"):
        st.session_state["story_points"].append({
            "caption": caption,
            "chart_idx": sel_chart_idx,
            "chart_config": saved_charts[sel_chart_idx],
        })
        st.success("✅ Story point added!")
        st.rerun()

    # Story presentation
    story_points = st.session_state.get("story_points", [])
    if story_points:
        st.markdown("---")
        st.markdown("#### 📖 Your Data Story")

        # Navigation
        if "story_page" not in st.session_state:
            st.session_state["story_page"] = 0

        current = st.session_state["story_page"]
        total = len(story_points)

        # Progress bar
        st.progress((current + 1) / total)
        st.markdown(f"**Point {current + 1} of {total}**")

        # Show current story point
        point = story_points[current]

        # Caption
        st.markdown(
            f'<div style="background:linear-gradient(145deg, {COLORS["bg_card"]}, #242d3d); '
            f'border:1px solid {COLORS["border"]}; border-left:4px solid {COLORS["accent_gold"]}; '
            f'border-radius:12px; padding:20px; margin:16px 0;">'
            f'<p style="color:{COLORS["text_primary"]}; font-size:1.05rem; line-height:1.6;">{point["caption"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Chart
        if "current_df" in st.session_state:
            fig = _build_chart_from_config(point["chart_config"], st.session_state["current_df"])
            if fig:
                fig.update_layout(**PLOTLY_LAYOUT)
                fig.update_layout(title=point["chart_config"].get("title", ""), height=420)
                st.plotly_chart(fig, use_container_width=True, key=f"story_chart_{current}")

        # Navigation buttons
        nav_c1, nav_c2, nav_c3 = st.columns([1, 2, 1])
        with nav_c1:
            if current > 0:
                if st.button("⬅️ Previous", key="story_prev"):
                    st.session_state["story_page"] = current - 1
                    st.rerun()
        with nav_c3:
            if current < total - 1:
                if st.button("Next ➡️", key="story_next"):
                    st.session_state["story_page"] = current + 1
                    st.rerun()

        # Clear story
        if st.button("🗑️ Clear Story", key="clear_story"):
            st.session_state["story_points"] = []
            st.session_state["story_page"] = 0
            st.rerun()


# ══════════════════════════════════════════════════════════════════════
# SHARED: DASHBOARD GRID RENDERER
# ══════════════════════════════════════════════════════════════════════

def _render_dashboard_grid(chart_configs, n_cols, df):
    for i in range(0, len(chart_configs), n_cols):
        cols = st.columns(n_cols)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(chart_configs):
                with col:
                    config = chart_configs[idx]
                    try:
                        if config.get("chart_type") == "matrix":
                            _render_matrix_in_dash(config, df, idx)
                        else:
                            fig = _build_chart_from_config(config, df)
                            if fig:
                                fig.update_layout(**PLOTLY_LAYOUT)
                                fig.update_layout(
                                    title_text=config.get("title", "Chart"),
                                    height=350, margin=dict(l=40, r=20, t=50, b=40),
                                )
                                st.plotly_chart(fig, use_container_width=True, key=f"dash_{i}_{j}")
                    except Exception as e:
                        st.error(f"Error: {e}")


def _render_matrix_in_dash(config, df, idx):
    """Render a matrix table inside a dashboard."""
    row_cols = config.get("row_cols", [])
    val_cols = config.get("val_cols", [])
    agg = config.get("agg_func", "sum")
    if row_cols and val_cols:
        try:
            matrix = df.groupby(row_cols)[val_cols].agg(agg).reset_index()
            st.markdown(f"**{config.get('title', 'Table')}**")
            st.dataframe(matrix, use_container_width=True, height=300, hide_index=True)
        except Exception:
            st.warning("⚠️ Could not render table.")


def _build_chart_from_config(config, df):
    """Rebuild a Plotly figure from saved config."""
    chart_type = config.get("chart_type", "bar")
    dims = config.get("dims", [])
    meas = config.get("meas", [])
    x = config.get("x")
    y = config.get("y")
    color = config.get("color")
    if color in ("Auto", "None", None):
        color = None

    try:
        if chart_type == "bar":
            if x and y:
                return px.bar(df, x=x, y=y, color=color, color_discrete_sequence=CHART_COLORS, template="plotly_dark")
            elif x:
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                return px.bar(counts, x=x, y="count", color_discrete_sequence=CHART_COLORS, template="plotly_dark")
        elif chart_type == "line":
            return px.line(df, x=x, y=y, color=color, color_discrete_sequence=CHART_COLORS, template="plotly_dark", markers=True)
        elif chart_type == "scatter":
            return px.scatter(df, x=x, y=y, color=color, color_discrete_sequence=CHART_COLORS, template="plotly_dark", opacity=0.7)
        elif chart_type == "pie":
            if y:
                return px.pie(df, names=x, values=y, color_discrete_sequence=CHART_COLORS, template="plotly_dark", hole=0.4)
            else:
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                return px.pie(counts, names=x, values="count", color_discrete_sequence=CHART_COLORS, template="plotly_dark", hole=0.4)
        elif chart_type == "histogram":
            return px.histogram(df, x=x, color=color, nbins=30, color_discrete_sequence=CHART_COLORS, template="plotly_dark")
        elif chart_type == "heatmap":
            heat_cols = config.get("heatmap_cols", meas)
            if len(heat_cols) >= 2:
                corr = df[heat_cols].corr()
                return go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
                                                  colorscale="Viridis", text=corr.values.round(2), texttemplate="%{text}"))
    except Exception:
        pass
    return None
