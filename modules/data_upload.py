"""
InsightFlow – Data Upload Module
Upload CSV/Excel files, preview data, and manage datasets.
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from config import SUPPORTED_EXTENSIONS, COLORS
from database import save_dataset, get_all_datasets, delete_dataset


def render():
    """Render the data upload page."""
    st.markdown("## 📂 Dataset Upload")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]}; margin-bottom:24px;">'
        "Upload your CSV or Excel files to begin analysis</p>",
        unsafe_allow_html=True,
    )

    # ── File Uploader ─────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=SUPPORTED_EXTENSIONS,
        help="Supported formats: CSV, XLSX, XLS",
        key="file_uploader",
    )

    if uploaded_file is not None:
        _process_upload(uploaded_file)

    st.markdown("---")

    # ── Dataset Manager ───────────────────────────────────────────────
    _render_dataset_manager()


def _process_upload(uploaded_file):
    """Process an uploaded file."""
    try:
        with st.spinner("📊 Loading dataset..."):
            # Read file
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Store in session state
            st.session_state["current_df"] = df
            st.session_state["current_df_name"] = uploaded_file.name
            st.session_state["original_df"] = df.copy()

            # Save metadata to DB
            save_dataset(
                name=os.path.splitext(uploaded_file.name)[0],
                filename=uploaded_file.name,
                row_count=len(df),
                col_count=len(df.columns),
                columns=df.columns.tolist(),
                file_size_bytes=uploaded_file.size,
            )

        # ── Success Banner ────────────────────────────────────────────
        st.success(f"✅ **{uploaded_file.name}** loaded successfully!")

        # ── Quick Stats ───────────────────────────────────────────────
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", f"{len(df.columns):,}")
        with col3:
            st.metric("Missing Cells", f"{df.isna().sum().sum():,}")
        with col4:
            st.metric("Duplicates", f"{df.duplicated().sum():,}")

        # ── Data Preview ──────────────────────────────────────────────
        st.markdown("### 👁️ Data Preview")
        tab1, tab2, tab3 = st.tabs(["📋 First Rows", "📊 Statistics", "🔍 Column Info"])

        with tab1:
            st.dataframe(df.head(20), use_container_width=True, height=400)

        with tab2:
            st.dataframe(df.describe(), use_container_width=True)

        with tab3:
            col_info = pd.DataFrame({
                "Column": df.columns,
                "Type": [str(t) for t in df.dtypes],
                "Non-Null": [f"{df[c].notna().sum():,}" for c in df.columns],
                "Null": [f"{df[c].isna().sum():,}" for c in df.columns],
                "Unique": [f"{df[c].nunique():,}" for c in df.columns],
            })
            st.dataframe(col_info, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")


def _render_dataset_manager():
    """Show uploaded dataset history."""
    st.markdown("### 📁 Uploaded Datasets")

    datasets = get_all_datasets()
    if not datasets:
        st.markdown(
            f'<div style="text-align:center; padding:40px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:3rem; margin-bottom:8px;">📭</p>'
            "<p>No datasets uploaded yet. Upload your first dataset above!</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    for ds in datasets:
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1])
            with c1:
                st.markdown(f"**{ds['name']}**")
                st.caption(f"📄 {ds['filename']}")
            with c2:
                st.markdown(f"🔢 {ds['row_count']:,} rows")
            with c3:
                st.markdown(f"📊 {ds['col_count']} cols")
            with c4:
                size_kb = ds.get("file_size_bytes", 0) / 1024
                st.markdown(f"💾 {size_kb:.1f} KB")
            with c5:
                if st.button("🗑️", key=f"del_{ds['id']}", help="Delete dataset"):
                    delete_dataset(ds["id"])
                    st.rerun()
