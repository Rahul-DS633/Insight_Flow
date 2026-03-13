"""
InsightFlow – Data Modeling & DAX Module
Create relationships between datasets and build calculated fields.
Inspired by Power BI's Data Model + DAX formula bar.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
import operator
from config import COLORS


# ── Supported DAX-like functions ──────────────────────────────────────
DAX_FUNCTIONS = {
    "SUM": "Sum of a column",
    "AVERAGE": "Average of a column",
    "COUNT": "Count non-null values",
    "MIN": "Minimum value",
    "MAX": "Maximum value",
    "ABS": "Absolute value",
    "ROUND": "Round to N decimals",
    "IF": "IF(condition, true_val, false_val)",
    "UPPER": "Convert text to uppercase",
    "LOWER": "Convert text to lowercase",
    "LEN": "Length of text",
    "LEFT": "First N characters",
    "RIGHT": "Last N characters",
    "YEAR": "Extract year from date",
    "MONTH": "Extract month from date",
    "DAY": "Extract day from date",
}


def render():
    """Render the Data Modeling & DAX page."""
    st.markdown("## 🧮 Data Modeling & DAX")

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        st.markdown(
            f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:3rem; margin-bottom:8px;">📭</p>'
            "<p>No dataset loaded. Go to <b>Dataset Upload</b> first.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Interactive Data Grid (Excel-like UI) ─────────────────────────
    st.markdown("### 🧮 Data Model Grid")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]}; font-size:0.9rem;">'
        "View and edit your entire data model here. Changes are saved automatically."
        "</p>",
        unsafe_allow_html=True,
    )
    
    df = st.session_state["current_df"]
    
    edited_df = st.data_editor(
        df, 
        use_container_width=True, 
        height=350, 
        num_rows="dynamic", 
        key="dax_model_editor"
    )
    
    if not df.equals(edited_df):
        st.session_state["current_df"] = edited_df
        st.rerun()

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "🧮 Calculated Columns (DAX)",
        "🔗 Data Relationships",
        "📐 Quick Measures",
    ])

    with tab1:
        _render_calculated_columns()
    with tab2:
        _render_relationships()
    with tab3:
        _render_quick_measures()


# ══════════════════════════════════════════════════════════════════════
# DAX – CALCULATED COLUMNS
# ══════════════════════════════════════════════════════════════════════

def _render_calculated_columns():
    """DAX-like formula bar for creating new columns."""
    st.markdown("### ✨ Create Calculated Columns")

    df = st.session_state["current_df"]

    # Show available columns
    with st.expander("📋 Available Columns & Types", expanded=False):
        col_info = pd.DataFrame({
            "Column": df.columns,
            "Type": [str(t) for t in df.dtypes],
            "Sample": [str(df[c].iloc[0]) if len(df) > 0 else "—" for c in df.columns],
        })
        st.dataframe(col_info, use_container_width=True, hide_index=True)

    # DAX function reference
    with st.expander("📖 DAX Function Reference", expanded=False):
        for func, desc in DAX_FUNCTIONS.items():
            st.markdown(f"- **{func}** — {desc}")

    st.markdown("---")

    # Formula input
    new_col_name = st.text_input(
        "New Column Name",
        placeholder="e.g., Profit",
        key="dax_col_name",
    )

    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]}; font-size:0.85rem;">'
        'Use column names in brackets: <code>[Revenue] - [Cost]</code> &nbsp;|&nbsp; '
        'Functions: <code>IF([Sales] > 100, "High", "Low")</code> &nbsp;|&nbsp; '
        'Math: <code>[Price] * [Quantity] * 1.18</code></p>',
        unsafe_allow_html=True,
    )

    formula = st.text_area(
        "DAX Formula",
        placeholder='e.g., [Revenue] - [Cost]\nor: IF([Sales] > 1000, "High", "Low")\nor: ROUND([Price] * [Quantity], 2)',
        height=80,
        key="dax_formula",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("▶️ Preview Result", key="dax_preview", use_container_width=True):
            if formula and new_col_name:
                result = _evaluate_dax(df, formula, new_col_name, preview_only=True)
                if result is not None:
                    st.markdown("**Preview (first 10 rows):**")
                    preview_df = df.head(10).copy()
                    preview_df[new_col_name] = result.head(10)
                    st.dataframe(preview_df, use_container_width=True)
            else:
                st.warning("⚠️ Enter both a column name and a formula.")

    with c2:
        if st.button("✅ Add Column", key="dax_apply", use_container_width=True):
            if formula and new_col_name:
                result = _evaluate_dax(df, formula, new_col_name, preview_only=False)
                if result is not None:
                    df[new_col_name] = result
                    st.session_state["current_df"] = df
                    st.success(f"✅ Column **{new_col_name}** added!")
                    st.rerun()
            else:
                st.warning("⚠️ Enter both a column name and a formula.")


def _evaluate_dax(df, formula, col_name, preview_only=False):
    """Parse and evaluate a DAX-like formula."""
    try:
        expression = formula.strip()

        # ── Handle IF() ───────────────────────────────────────────────
        if_match = re.match(
            r'IF\s*\(\s*(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s*\)\s*$',
            expression, re.IGNORECASE
        )
        if if_match:
            condition_str = if_match.group(1).strip()
            true_val = if_match.group(2).strip().strip('"').strip("'")
            false_val = if_match.group(3).strip().strip('"').strip("'")

            condition = _parse_condition(df, condition_str)
            # Try to convert to numeric
            try:
                true_val = float(true_val)
                false_val = float(false_val)
            except ValueError:
                pass

            return np.where(condition, true_val, false_val)

        # ── Handle aggregate functions ────────────────────────────────
        func_match = re.match(r'(\w+)\s*\(\s*\[(.+?)\]\s*(?:,\s*(\d+))?\s*\)', expression)
        if func_match:
            func_name = func_match.group(1).upper()
            col = func_match.group(2)
            arg = func_match.group(3)

            if col not in df.columns:
                st.error(f"❌ Column '{col}' not found.")
                return None

            series = df[col]
            if func_name == "SUM":
                return pd.Series([series.sum()] * len(df))
            elif func_name == "AVERAGE":
                return pd.Series([series.mean()] * len(df))
            elif func_name == "COUNT":
                return pd.Series([series.count()] * len(df))
            elif func_name == "MIN":
                return pd.Series([series.min()] * len(df))
            elif func_name == "MAX":
                return pd.Series([series.max()] * len(df))
            elif func_name == "ABS":
                return series.abs()
            elif func_name == "ROUND":
                decimals = int(arg) if arg else 0
                return series.round(decimals)
            elif func_name == "UPPER":
                return series.astype(str).str.upper()
            elif func_name == "LOWER":
                return series.astype(str).str.lower()
            elif func_name == "LEN":
                return series.astype(str).str.len()
            elif func_name == "LEFT":
                n = int(arg) if arg else 1
                return series.astype(str).str[:n]
            elif func_name == "RIGHT":
                n = int(arg) if arg else 1
                return series.astype(str).str[-n:]
            elif func_name == "YEAR":
                return pd.to_datetime(series, errors="coerce").dt.year
            elif func_name == "MONTH":
                return pd.to_datetime(series, errors="coerce").dt.month
            elif func_name == "DAY":
                return pd.to_datetime(series, errors="coerce").dt.day
            else:
                st.error(f"❌ Unknown function: {func_name}")
                return None

        # ── Handle simple math expressions ────────────────────────────
        eval_expr = expression
        # Replace [ColumnName] with df["ColumnName"]
        for col in df.columns:
            eval_expr = eval_expr.replace(f"[{col}]", f'__df__["{col}"]')

        result = eval(eval_expr, {"__builtins__": {}, "__df__": df, "np": np, "pd": pd,
                                   "abs": abs, "round": round, "min": min, "max": max})
        return result

    except Exception as e:
        st.error(f"❌ Formula error: {str(e)}")
        return None


def _parse_condition(df, condition_str):
    """Parse a simple condition like [Sales] > 100."""
    ops = {
        ">=": operator.ge, "<=": operator.le,
        "!=": operator.ne, ">": operator.gt,
        "<": operator.lt, "==": operator.eq, "=": operator.eq,
    }
    for op_str, op_func in ops.items():
        if op_str in condition_str:
            parts = condition_str.split(op_str, 1)
            left = parts[0].strip()
            right = parts[1].strip()

            # Resolve column references
            col_match = re.match(r'\[(.+?)\]', left)
            if col_match:
                left_val = df[col_match.group(1)]
            else:
                left_val = float(left)

            # Resolve right side
            col_match_r = re.match(r'\[(.+?)\]', right)
            if col_match_r:
                right_val = df[col_match_r.group(1)]
            else:
                try:
                    right_val = float(right)
                except ValueError:
                    right_val = right.strip('"').strip("'")

            return op_func(left_val, right_val)

    raise ValueError(f"Cannot parse condition: {condition_str}")


# ══════════════════════════════════════════════════════════════════════
# DATA RELATIONSHIPS (Star Schema)
# ══════════════════════════════════════════════════════════════════════

def _render_relationships():
    """Create relationships between datasets."""
    st.markdown("### 🔗 Data Relationships")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">'
        "Upload a second dataset and define a Primary/Foreign key relationship (like Power BI's Model view).</p>",
        unsafe_allow_html=True,
    )

    df = st.session_state["current_df"]

    # Upload related dataset
    related_file = st.file_uploader("Upload related dataset", type=["csv", "xlsx", "xls"], key="rel_file")
    if related_file is None:
        st.info("💡 Upload a second dataset to create a relationship.")

        # Show existing relationships
        rels = st.session_state.get("relationships", [])
        if rels:
            st.markdown("#### Existing Relationships")
            for r in rels:
                st.markdown(
                    f'<div style="background:{COLORS["bg_card"]}; border:1px solid {COLORS["border"]}; '
                    f'border-radius:8px; padding:12px; margin:6px 0;">'
                    f'🔗 <b>{r["left_table"]}</b>.[{r["left_key"]}] ↔ '
                    f'<b>{r["right_table"]}</b>.[{r["right_key"]}] '
                    f'<span style="color:{COLORS["accent_blue"]};">({r["join_type"]})</span></div>',
                    unsafe_allow_html=True,
                )
        return

    try:
        if related_file.name.endswith(".csv"):
            df2 = pd.read_csv(related_file)
        else:
            df2 = pd.read_excel(related_file)
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return

    st.markdown(f"**{related_file.name}**: {len(df2):,} rows × {len(df2.columns)} cols")

    c1, c2 = st.columns(2)
    with c1:
        pk = st.selectbox("Primary Key (current)", df.columns, key="rel_pk")
    with c2:
        fk = st.selectbox("Foreign Key (related)", df2.columns, key="rel_fk")

    join_type = st.selectbox("Relationship Type", ["left", "inner", "outer"], key="rel_type")

    if st.button("🔗 Create Relationship & Merge", key="create_rel", use_container_width=True):
        try:
            merged = pd.merge(df, df2, left_on=pk, right_on=fk, how=join_type, suffixes=("", f"_{related_file.name.split('.')[0]}"))
            st.session_state["current_df"] = merged

            if "relationships" not in st.session_state:
                st.session_state["relationships"] = []
            st.session_state["relationships"].append({
                "left_table": st.session_state.get("current_df_name", "Main"),
                "right_table": related_file.name,
                "left_key": pk,
                "right_key": fk,
                "join_type": join_type,
            })

            st.success(f"✅ Relationship created! Merged: {len(merged):,} rows × {len(merged.columns)} cols")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {e}")


# ══════════════════════════════════════════════════════════════════════
# QUICK MEASURES
# ══════════════════════════════════════════════════════════════════════

def _render_quick_measures():
    """One-click common calculations."""
    st.markdown("### 📐 Quick Measures")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">Pre-built calculations you can apply with one click.</p>',
        unsafe_allow_html=True,
    )

    df = st.session_state["current_df"]
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.warning("⚠️ No numeric columns available.")
        return

    measure_type = st.selectbox("Quick Measure", [
        "Percentage of Total",
        "Running Total (Cumulative Sum)",
        "Difference from Previous Row",
        "Percentage Change",
        "Rank",
        "Z-Score (Standardize)",
        "Bin / Bucket",
    ], key="quick_measure_type")

    col = st.selectbox("Apply to column", numeric_cols, key="qm_col")
    new_name = st.text_input("New column name", f"{col}_{measure_type.split('(')[0].strip().replace(' ', '_').lower()}", key="qm_name")

    if st.button("⚡ Apply Quick Measure", key="apply_qm", use_container_width=True):
        new_df = df.copy()
        try:
            if measure_type == "Percentage of Total":
                total = new_df[col].sum()
                new_df[new_name] = (new_df[col] / total * 100).round(2) if total != 0 else 0

            elif measure_type == "Running Total (Cumulative Sum)":
                new_df[new_name] = new_df[col].cumsum()

            elif measure_type == "Difference from Previous Row":
                new_df[new_name] = new_df[col].diff()

            elif measure_type == "Percentage Change":
                new_df[new_name] = (new_df[col].pct_change() * 100).round(2)

            elif measure_type == "Rank":
                new_df[new_name] = new_df[col].rank(ascending=False).astype(int)

            elif measure_type == "Z-Score (Standardize)":
                mean = new_df[col].mean()
                std = new_df[col].std()
                new_df[new_name] = ((new_df[col] - mean) / std).round(4) if std != 0 else 0

            elif measure_type == "Bin / Bucket":
                n_bins = st.slider("Number of bins", 3, 20, 5, key="qm_bins")
                new_df[new_name] = pd.cut(new_df[col], bins=n_bins, labels=False)

            st.session_state["current_df"] = new_df
            st.success(f"✅ Column **{new_name}** added!")
            st.dataframe(new_df[[col, new_name]].head(10), use_container_width=True)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")
