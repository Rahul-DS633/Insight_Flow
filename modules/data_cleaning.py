"""
InsightFlow – Data Cleaning & Power Query Module
Detect/fix data quality issues + Power Query transformations.
"""

import streamlit as st
import pandas as pd
import numpy as np
from config import COLORS


def render():
    """Render the data cleaning & power query page."""
    st.markdown("## 🧹 Data Cleaning & Power Query")

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        _show_empty_state()
        return

    df = st.session_state["current_df"]

    # ── Data Quality Overview ─────────────────────────────────────────
    _render_quality_overview(df)

    st.markdown("---")

    # ── Interactive Data Grid (Excel-like UI) ─────────────────────────
    st.markdown("### 🧮 Interactive Data Grid")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]}; font-size:0.9rem;">'
        "Edit cells directly or add rows/columns like Excel. Changes are saved automatically."
        "</p>",
        unsafe_allow_html=True,
    )
    
    # Store the result of data_editor
    # We must use a unique key and only update session state if the data actually changes
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=350, 
        num_rows="dynamic", 
        key="power_query_editor"
    )
    
    # Check if data was edited
    if not df.equals(edited_df):
        st.session_state["current_df"] = edited_df
        _log_step("Manual edits applied via Data Grid")
        st.rerun()

    st.markdown("---")

    # ── Tabbed Tools ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔲 Missing Values",
        "♻️ Duplicates",
        "🔄 Type Conversion",
        "✂️ Column Manager",
        "🔗 Merge / Join",
        "📊 Group By",
        "🔀 Pivot / Unpivot",
    ])

    with tab1:
        _handle_missing_values(df)
    with tab2:
        _handle_duplicates(df)
    with tab3:
        _handle_type_conversion(df)
    with tab4:
        _handle_column_manager(df)
    with tab5:
        _handle_merge_join(df)
    with tab6:
        _handle_group_by(df)
    with tab7:
        _handle_pivot_unpivot(df)

    # ── Query Steps Log ───────────────────────────────────────────────
    st.markdown("---")
    _render_query_steps()


def _show_empty_state():
    st.markdown(
        f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
        '<p style="font-size:3rem; margin-bottom:8px;">📭</p>'
        "<p>No dataset loaded. Go to <b>Dataset Upload</b> to load a file first.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def _render_quality_overview(df):
    """Show data quality metrics."""
    st.markdown("### 📊 Data Quality Report")

    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 100
    duplicate_rows = int(df.duplicated().sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cells", f"{total_cells:,}")
    with col2:
        st.metric("Missing Cells", f"{missing_cells:,}")
    with col3:
        st.metric("Completeness", f"{completeness:.1f}%")
    with col4:
        st.metric("Duplicate Rows", f"{duplicate_rows:,}")

    # Per-column missing analysis
    missing_per_col = df.isna().sum()
    if missing_per_col.sum() > 0:
        with st.expander("📋 Missing Values by Column", expanded=False):
            missing_df = pd.DataFrame({
                "Column": missing_per_col.index,
                "Missing": missing_per_col.values,
                "Percentage": (missing_per_col.values / len(df) * 100).round(2),
            }).sort_values("Missing", ascending=False)
            missing_df = missing_df[missing_df["Missing"] > 0]
            st.dataframe(missing_df, use_container_width=True, hide_index=True)


def _log_step(description):
    """Log a query transformation step."""
    if "query_steps" not in st.session_state:
        st.session_state["query_steps"] = []
    st.session_state["query_steps"].append(description)


def _render_query_steps():
    """Show the query transformation steps log."""
    steps = st.session_state.get("query_steps", [])
    if not steps:
        return
    st.markdown("### 📜 Applied Query Steps")
    for i, step in enumerate(steps, 1):
        st.markdown(
            f'<div style="background:{COLORS["bg_card"]}; border-left:3px solid {COLORS["accent_gold"]}; '
            f'border-radius:6px; padding:8px 14px; margin:4px 0; font-size:0.85rem;">'
            f'<span style="color:{COLORS["accent_blue"]}; font-weight:600;">Step {i}:</span> '
            f'<span style="color:{COLORS["text_primary"]};">{step}</span></div>',
            unsafe_allow_html=True,
        )
    if st.button("🗑️ Clear Step History", key="clear_steps"):
        st.session_state["query_steps"] = []
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# BASIC CLEANING TOOLS
# ══════════════════════════════════════════════════════════════════════

def _handle_missing_values(df):
    st.markdown("#### Handle Missing Values")
    cols_with_missing = [c for c in df.columns if df[c].isna().sum() > 0]
    if not cols_with_missing:
        st.success("✅ No missing values found!")
        return

    selected_cols = st.multiselect("Select columns to fill", cols_with_missing, default=cols_with_missing[:1], key="missing_cols")
    if not selected_cols:
        return

    strategy = st.selectbox("Fill strategy", [
        "Mean (numeric)", "Median (numeric)", "Mode (most frequent)",
        "Forward Fill", "Backward Fill", "Drop rows with missing", "Custom value"
    ], key="fill_strategy")

    custom_value = None
    if strategy == "Custom value":
        custom_value = st.text_input("Enter custom value", key="custom_fill_val")

    if st.button("🔧 Apply Fix", key="apply_missing_fix"):
        new_df = df.copy()
        for col in selected_cols:
            if strategy == "Mean (numeric)" and pd.api.types.is_numeric_dtype(new_df[col]):
                new_df[col] = new_df[col].fillna(new_df[col].mean())
            elif strategy == "Median (numeric)" and pd.api.types.is_numeric_dtype(new_df[col]):
                new_df[col] = new_df[col].fillna(new_df[col].median())
            elif strategy == "Mode (most frequent)":
                mode_val = new_df[col].mode()
                if len(mode_val) > 0:
                    new_df[col] = new_df[col].fillna(mode_val[0])
            elif strategy == "Forward Fill":
                new_df[col] = new_df[col].ffill()
            elif strategy == "Backward Fill":
                new_df[col] = new_df[col].bfill()
            elif strategy == "Drop rows with missing":
                new_df = new_df.dropna(subset=[col])
            elif strategy == "Custom value" and custom_value is not None:
                new_df[col] = new_df[col].fillna(custom_value)

        before_m = df.isna().sum().sum()
        after_m = new_df.isna().sum().sum()
        st.session_state["current_df"] = new_df
        _log_step(f"Fill missing in {selected_cols} using '{strategy}' ({before_m}→{after_m})")
        st.success(f"✅ Missing values: {before_m:,} → {after_m:,}")
        st.rerun()


def _handle_duplicates(df):
    st.markdown("#### Handle Duplicate Rows")
    n_dupes = int(df.duplicated().sum())
    st.metric("Duplicate Rows Found", f"{n_dupes:,}")
    if n_dupes == 0:
        st.success("✅ No duplicate rows!")
        return
    if st.checkbox("Preview duplicates", key="preview_dupes"):
        st.dataframe(df[df.duplicated(keep=False)].head(50), use_container_width=True)
    if st.button("🗑️ Remove All Duplicates", key="remove_dupes"):
        new_df = df.drop_duplicates()
        st.session_state["current_df"] = new_df
        _log_step(f"Removed {n_dupes} duplicate rows ({len(df)}→{len(new_df)} rows)")
        st.success(f"✅ Removed {n_dupes:,} duplicates.")
        st.rerun()


def _handle_type_conversion(df):
    st.markdown("#### Convert Column Types")
    c1, c2 = st.columns(2)
    with c1:
        col_name = st.selectbox("Select column", df.columns, key="type_conv_col")
    with c2:
        target_type = st.selectbox("Convert to", ["int64", "float64", "string", "datetime64", "category", "bool"], key="target_type")
    if col_name:
        st.caption(f"Current type: **{df[col_name].dtype}**")
    if st.button("🔄 Convert", key="convert_type"):
        try:
            new_df = df.copy()
            if target_type == "datetime64":
                new_df[col_name] = pd.to_datetime(new_df[col_name], errors="coerce")
            elif target_type == "category":
                new_df[col_name] = new_df[col_name].astype("category")
            else:
                new_df[col_name] = new_df[col_name].astype(target_type)
            st.session_state["current_df"] = new_df
            _log_step(f"Converted '{col_name}' to {target_type}")
            st.success(f"✅ Converted **{col_name}** to **{target_type}**")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Conversion failed: {str(e)}")


def _handle_column_manager(df):
    st.markdown("#### Manage Columns")
    cols_to_drop = st.multiselect("Select columns to drop", df.columns.tolist(), key="drop_cols")
    if cols_to_drop and st.button("🗑️ Drop Selected Columns", key="drop_cols_btn"):
        new_df = df.drop(columns=cols_to_drop)
        st.session_state["current_df"] = new_df
        _log_step(f"Dropped columns: {cols_to_drop}")
        st.success(f"✅ Dropped {len(cols_to_drop)} column(s)")
        st.rerun()

    st.markdown("---")
    st.markdown("**Rename a Column**")
    c1, c2 = st.columns(2)
    with c1:
        old_name = st.selectbox("Column to rename", df.columns, key="rename_old")
    with c2:
        new_name = st.text_input("New name", key="rename_new")
    if new_name and st.button("✏️ Rename", key="rename_col_btn"):
        new_df = df.rename(columns={old_name: new_name})
        st.session_state["current_df"] = new_df
        _log_step(f"Renamed '{old_name}' → '{new_name}'")
        st.success(f"✅ Renamed **{old_name}** → **{new_name}**")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
# POWER QUERY – MERGE / JOIN
# ══════════════════════════════════════════════════════════════════════

def _handle_merge_join(df):
    st.markdown("#### 🔗 Merge / Join Datasets")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">Upload a second dataset to merge with the current one (like SQL JOINs or Power Query Merge).</p>',
        unsafe_allow_html=True,
    )

    # Upload second dataset
    second_file = st.file_uploader("Upload second dataset", type=["csv", "xlsx", "xls"], key="merge_file")
    if second_file is None:
        st.info("💡 Upload a second file above to merge with your current dataset.")
        return

    try:
        if second_file.name.endswith(".csv"):
            df2 = pd.read_csv(second_file)
        else:
            df2 = pd.read_excel(second_file)
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return

    st.markdown(f"**Second Dataset:** {second_file.name} — {len(df2):,} rows × {len(df2.columns)} cols")

    c1, c2 = st.columns(2)
    with c1:
        left_key = st.selectbox("Key column (current dataset)", df.columns, key="merge_left_key")
    with c2:
        right_key = st.selectbox("Key column (second dataset)", df2.columns, key="merge_right_key")

    join_type = st.selectbox("Join Type", ["inner", "left", "right", "outer"], key="merge_join_type",
                             help="inner = only matching rows · left = keep all left rows · right = keep all right · outer = keep all")

    with st.expander("👁️ Preview second dataset"):
        st.dataframe(df2.head(10), use_container_width=True)

    if st.button("🔗 Merge Datasets", key="do_merge", use_container_width=True):
        try:
            merged = pd.merge(df, df2, left_on=left_key, right_on=right_key, how=join_type, suffixes=("", "_right"))
            st.session_state["current_df"] = merged
            _log_step(f"Merged with '{second_file.name}' on [{left_key}={right_key}] ({join_type}) → {len(merged):,} rows")
            st.success(f"✅ Merged! Result: {len(merged):,} rows × {len(merged.columns)} columns")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Merge failed: {e}")


# ══════════════════════════════════════════════════════════════════════
# POWER QUERY – GROUP BY
# ══════════════════════════════════════════════════════════════════════

def _handle_group_by(df):
    st.markdown("#### 📊 Group By Aggregation")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">Aggregate your data by grouping columns and applying functions (like Power Query Group By).</p>',
        unsafe_allow_html=True,
    )

    group_cols = st.multiselect("Group By columns", df.columns.tolist(), key="group_cols")
    if not group_cols:
        st.info("💡 Select one or more columns to group by.")
        return

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    remaining_numeric = [c for c in numeric_cols if c not in group_cols]

    if not remaining_numeric:
        st.warning("⚠️ No numeric columns available for aggregation.")
        return

    agg_cols = st.multiselect("Columns to aggregate", remaining_numeric, default=remaining_numeric[:2], key="agg_cols")
    agg_func = st.selectbox("Aggregation function", ["sum", "mean", "median", "min", "max", "count", "std"], key="agg_func")

    if agg_cols:
        try:
            preview = df.groupby(group_cols)[agg_cols].agg(agg_func).reset_index()
            st.markdown("**Preview:**")
            st.dataframe(preview, use_container_width=True)

            if st.button("✅ Apply Group By (replace dataset)", key="apply_groupby", use_container_width=True):
                st.session_state["current_df"] = preview
                _log_step(f"Group By {group_cols} → {agg_func}({agg_cols}) → {len(preview):,} rows")
                st.success(f"✅ Grouped! {len(preview):,} rows")
                st.rerun()
        except Exception as e:
            st.error(f"❌ Group By failed: {e}")


# ══════════════════════════════════════════════════════════════════════
# POWER QUERY – PIVOT / UNPIVOT
# ══════════════════════════════════════════════════════════════════════

def _handle_pivot_unpivot(df):
    st.markdown("#### 🔀 Pivot / Unpivot")

    mode = st.radio("Operation", ["Pivot (wide)", "Unpivot (long/melt)"], key="pivot_mode", horizontal=True)

    if mode == "Pivot (wide)":
        st.markdown(
            f'<p style="color:{COLORS["text_secondary"]};">Reshape your data from long to wide format. Like a Pivot Table.</p>',
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            index_col = st.selectbox("Row Index", df.columns, key="pivot_index")
        with c2:
            columns_col = st.selectbox("Column Headers", [c for c in df.columns if c != index_col], key="pivot_columns")
        with c3:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            values_col = st.selectbox("Values", numeric_cols if numeric_cols else df.columns.tolist(), key="pivot_values")

        agg_func = st.selectbox("Aggregation", ["mean", "sum", "count", "min", "max"], key="pivot_agg")

        if st.button("🔀 Pivot", key="do_pivot", use_container_width=True):
            try:
                pivoted = pd.pivot_table(df, index=index_col, columns=columns_col, values=values_col, aggfunc=agg_func).reset_index()
                pivoted.columns = [str(c) for c in pivoted.columns]
                st.session_state["current_df"] = pivoted
                _log_step(f"Pivoted: index={index_col}, columns={columns_col}, values={values_col}, agg={agg_func}")
                st.success(f"✅ Pivoted! {pivoted.shape[0]} rows × {pivoted.shape[1]} columns")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Pivot failed: {e}")

    else:  # Unpivot / Melt
        st.markdown(
            f'<p style="color:{COLORS["text_secondary"]};">Reshape your data from wide to long format (Unpivot).</p>',
            unsafe_allow_html=True,
        )
        id_cols = st.multiselect("ID columns (keep fixed)", df.columns.tolist(), key="melt_ids")
        value_cols = st.multiselect("Value columns (unpivot these)", [c for c in df.columns if c not in id_cols], key="melt_values")

        if id_cols and value_cols:
            if st.button("🔀 Unpivot", key="do_unpivot", use_container_width=True):
                try:
                    melted = pd.melt(df, id_vars=id_cols, value_vars=value_cols, var_name="Variable", value_name="Value")
                    st.session_state["current_df"] = melted
                    _log_step(f"Unpivoted: id_vars={id_cols}, value_vars={value_cols}")
                    st.success(f"✅ Unpivoted! {len(melted):,} rows")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Unpivot failed: {e}")
