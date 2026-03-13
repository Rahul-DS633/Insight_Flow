"""
InsightFlow – Data Filtering Module
Dynamic filters for focused data exploration.
"""

import streamlit as st
import pandas as pd
import numpy as np
from config import COLORS


def render():
    """Render the data filtering page."""
    st.markdown("## 🎛️ Data Filtering")

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        st.markdown(
            f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:3rem; margin-bottom:8px;">📭</p>'
            "<p>No dataset loaded. Go to <b>Dataset Upload</b> first.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    df = st.session_state["current_df"]

    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">'
        "Apply filters to explore subsets of your data. Filters apply to the Chart Builder automatically.</p>",
        unsafe_allow_html=True,
    )

    # ── Filter Builder ────────────────────────────────────────────────
    col_filters, col_preview = st.columns([1, 2.5])

    with col_filters:
        _render_filter_controls(df)

    with col_preview:
        _render_filtered_preview(df)


def _render_filter_controls(df):
    """Build dynamic filter controls."""
    st.markdown("### 🔧 Filter Controls")

    # Reset button
    if st.button("🔄 Reset All Filters", key="reset_filters", use_container_width=True):
        st.session_state["filtered_df"] = None
        st.session_state["active_filters"] = {}
        st.rerun()

    st.markdown("---")

    # Number of filters
    n_filters = st.number_input(
        "Number of filters", min_value=1, max_value=10, value=1, key="n_filters"
    )

    filters = {}

    for i in range(int(n_filters)):
        st.markdown(f"**Filter {i + 1}**")
        col_name = st.selectbox(
            f"Column",
            df.columns.tolist(),
            key=f"filter_col_{i}",
        )

        if col_name:
            col_data = df[col_name]

            if pd.api.types.is_numeric_dtype(col_data):
                _min = float(col_data.min()) if not col_data.isna().all() else 0.0
                _max = float(col_data.max()) if not col_data.isna().all() else 1.0
                if _min == _max:
                    _max = _min + 1.0

                values = st.slider(
                    f"Range",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    key=f"filter_range_{i}",
                )
                filters[col_name] = {"type": "range", "values": values}

            elif pd.api.types.is_datetime64_any_dtype(col_data):
                _min_date = col_data.min()
                _max_date = col_data.max()
                if pd.isna(_min_date) or pd.isna(_max_date):
                    st.warning("Column has no valid dates")
                    continue
                date_range = st.date_input(
                    f"Date Range",
                    value=(_min_date, _max_date),
                    key=f"filter_date_{i}",
                )
                if len(date_range) == 2:
                    filters[col_name] = {"type": "date_range", "values": date_range}

            else:
                unique_vals = col_data.dropna().unique().tolist()
                if len(unique_vals) > 100:
                    unique_vals = unique_vals[:100]
                selected = st.multiselect(
                    f"Values",
                    unique_vals,
                    default=unique_vals[:min(5, len(unique_vals))],
                    key=f"filter_cat_{i}",
                )
                filters[col_name] = {"type": "category", "values": selected}

        st.markdown("---")

    # Apply filters button
    if st.button("✅ Apply Filters", key="apply_filters", use_container_width=True):
        filtered_df = _apply_filters(df, filters)
        st.session_state["filtered_df"] = filtered_df
        st.session_state["active_filters"] = filters
        st.rerun()


def _render_filtered_preview(df):
    """Preview the filtered data."""
    filtered_df = st.session_state.get("filtered_df")
    active_filters = st.session_state.get("active_filters", {})

    if filtered_df is not None:
        st.markdown("### 📋 Filtered Results")

        # Filter summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Original Rows", f"{len(df):,}")
        with col2:
            st.metric("Filtered Rows", f"{len(filtered_df):,}")
        with col3:
            pct = (len(filtered_df) / len(df) * 100) if len(df) > 0 else 0
            st.metric("Showing", f"{pct:.1f}%")

        # Active filters display
        if active_filters:
            st.markdown("**Active Filters:**")
            for col, filt in active_filters.items():
                if filt["type"] == "range":
                    st.markdown(f"- **{col}**: {filt['values'][0]:.2f} – {filt['values'][1]:.2f}")
                elif filt["type"] == "category":
                    st.markdown(f"- **{col}**: {', '.join(str(v) for v in filt['values'][:5])}{'...' if len(filt['values']) > 5 else ''}")
                elif filt["type"] == "date_range":
                    st.markdown(f"- **{col}**: {filt['values'][0]} – {filt['values'][1]}")

        st.dataframe(filtered_df, use_container_width=True, height=500)

    else:
        st.markdown("### 📋 Data Preview (Unfiltered)")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", f"{len(df.columns):,}")
        st.dataframe(df, use_container_width=True, height=500)


def _apply_filters(df, filters):
    """Apply all filters to the dataframe."""
    filtered = df.copy()

    for col, filt in filters.items():
        if col not in filtered.columns:
            continue

        if filt["type"] == "range":
            low, high = filt["values"]
            filtered = filtered[
                (filtered[col] >= low) & (filtered[col] <= high)
            ]
        elif filt["type"] == "category":
            filtered = filtered[filtered[col].isin(filt["values"])]
        elif filt["type"] == "date_range":
            start, end = filt["values"]
            filtered = filtered[
                (filtered[col] >= pd.Timestamp(start)) &
                (filtered[col] <= pd.Timestamp(end))
            ]

    return filtered
