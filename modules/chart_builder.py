"""
InsightFlow – Visual Analytics Builder (Tableau + Power BI Style)
Build interactive visualizations with smart recommendations,
advanced analytics, and matrix tables.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from config import COLORS, CHART_TYPES, CHART_ICONS, CHART_COLORS, PLOTLY_LAYOUT


# ── Dimension vs Measure classification (Tableau style) ───────────────
def _classify_columns(df):
    """Classify columns into Dimensions (categorical) and Measures (numeric)."""
    dimensions = []
    measures = []
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            measures.append(col)
        else:
            dimensions.append(col)
    return dimensions, measures


def _recommend_chart(n_dims, n_meas):
    """Auto-recommend chart type based on selected dimensions/measures (Show Me!)."""
    if n_dims == 0 and n_meas == 1:
        return "histogram", "📉 Histogram – distribution of a single measure"
    elif n_dims == 1 and n_meas == 0:
        return "bar", "📊 Bar Chart – count of categories"
    elif n_dims == 1 and n_meas == 1:
        return "bar", "📊 Bar Chart – measure by category"
    elif n_dims == 1 and n_meas >= 2:
        return "line", "📈 Line Chart – multiple measures by category"
    elif n_dims == 0 and n_meas == 2:
        return "scatter", "🔵 Scatter Plot – relationship between two measures"
    elif n_dims == 0 and n_meas >= 3:
        return "heatmap", "🗺️ Heatmap – correlations between measures"
    elif n_dims >= 2 and n_meas == 0:
        return "bar", "📊 Grouped Bar – category breakdown"
    elif n_dims >= 2 and n_meas >= 1:
        return "bar", "📊 Grouped Bar – measure by nested categories"
    return "bar", "📊 Bar Chart – default"


# ══════════════════════════════════════════════════════════════════════

def render():
    """Render the visual analytics builder page."""
    st.markdown("## 📊 Visual Analytics Builder")

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        st.markdown(
            f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
            '<p style="font-size:3rem;">📭</p>'
            "<p>No dataset loaded. Go to <b>Dataset Upload</b> first.</p></div>",
            unsafe_allow_html=True,
        )
        return

    df = st.session_state["current_df"]
    if "filtered_df" in st.session_state and st.session_state["filtered_df"] is not None:
        df = st.session_state["filtered_df"]

    tab1, tab2, tab3 = st.tabs(["📊 Chart Builder", "📋 Matrix Table", "📈 Advanced Analytics"])

    with tab1:
        _render_chart_builder(df)
    with tab2:
        _render_matrix_table(df)
    with tab3:
        _render_advanced_analytics(df)


# ══════════════════════════════════════════════════════════════════════
# CHART BUILDER (with Tableau Show Me! + Visual Encodings)
# ══════════════════════════════════════════════════════════════════════

def _render_chart_builder(df):
    dimensions, measures = _classify_columns(df)

    col_config, col_chart = st.columns([1, 2.5])

    with col_config:
        st.markdown("### 🎨 Visual Config")

        # ── Dimensions & Measures (Tableau pills) ────────────────────
        st.markdown(
            f'<p style="font-size:0.8rem; color:{COLORS["accent_blue"]}; font-weight:600;">'
            '🔵 DIMENSIONS (Categories)</p>',
            unsafe_allow_html=True,
        )
        sel_dims = st.multiselect("", dimensions, max_selections=2, key="sel_dims",
                                  label_visibility="collapsed")

        st.markdown(
            f'<p style="font-size:0.8rem; color:{COLORS["accent_green"]}; font-weight:600;">'
            '🟢 MEASURES (Numbers)</p>',
            unsafe_allow_html=True,
        )
        sel_meas = st.multiselect("", measures, max_selections=3, key="sel_meas",
                                  label_visibility="collapsed")

        # ── Show Me! recommendation ──────────────────────────────────
        rec_type, rec_reason = _recommend_chart(len(sel_dims), len(sel_meas))
        st.markdown(
            f'<div style="background:{COLORS["bg_card"]}; border:1px solid {COLORS["border"]}; '
            f'border-radius:8px; padding:10px; margin:8px 0;">'
            f'<p style="color:{COLORS["accent_gold"]}; font-weight:600; font-size:0.8rem; margin:0;">💡 SHOW ME!</p>'
            f'<p style="color:{COLORS["text_secondary"]}; font-size:0.8rem; margin:4px 0 0 0;">{rec_reason}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── Chart type override ──────────────────────────────────────
        all_types = list(CHART_TYPES.keys()) + ["Matrix Table"]
        chart_labels = [f"{CHART_ICONS.get(k, '📋')} {k}" for k in all_types]
        default_idx = 0
        for i, k in enumerate(all_types):
            if CHART_TYPES.get(k) == rec_type:
                default_idx = i
                break

        selected_label = st.selectbox("Chart Type (override)", chart_labels, index=default_idx, key="chart_type_sel")
        chart_type_name = selected_label.split(" ", 1)[1]
        chart_type = CHART_TYPES.get(chart_type_name, rec_type)

        # ── Visual Encodings ─────────────────────────────────────────
        st.markdown("---")
        st.markdown("**Visual Encodings**")
        color_col = st.selectbox("🎨 Color", ["Auto"] + df.columns.tolist(), key="enc_color")
        size_col = st.selectbox("📏 Size", ["None"] + measures, key="enc_size")
        tooltip_cols = st.multiselect("💬 Tooltips", df.columns.tolist(), default=[], key="enc_tooltips")

        st.markdown("---")
        chart_title = st.text_input("Chart Title", chart_type_name, key="chart_title")

        # Save button
        if st.button("💾 Save to Dashboard", key="save_chart", use_container_width=True):
            _save_chart_config(chart_type, chart_type_name, chart_title,
                               sel_dims, sel_meas, color_col, size_col)

    with col_chart:
        if not sel_dims and not sel_meas:
            st.info("👈 Select **Dimensions** and/or **Measures** on the left to build a chart.")
            return

        fig = _build_chart(df, chart_type, sel_dims, sel_meas,
                           color_col, size_col, tooltip_cols, chart_title)
        if fig:
            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(title_text=chart_title, height=520)
            st.plotly_chart(fig, use_container_width=True, key="main_chart")


def _build_chart(df, chart_type, dims, meas, color_col, size_col, tooltips, title):
    """Build a Plotly figure from the configuration."""
    color = None if color_col in ("Auto", "None") else color_col
    size = None if size_col == "None" else size_col

    try:
        if chart_type == "pie":
            x = dims[0] if dims else (meas[0] if meas else df.columns[0])
            y = meas[0] if meas else None
            if y:
                return px.pie(df, names=x, values=y, color_discrete_sequence=CHART_COLORS,
                              template="plotly_dark", hole=0.4)
            else:
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                return px.pie(counts, names=x, values="count", color_discrete_sequence=CHART_COLORS,
                              template="plotly_dark", hole=0.4)

        elif chart_type == "histogram":
            col = meas[0] if meas else (dims[0] if dims else df.columns[0])
            return px.histogram(df, x=col, color=color, nbins=30,
                                color_discrete_sequence=CHART_COLORS, template="plotly_dark")

        elif chart_type == "heatmap":
            cols = meas if meas else df.select_dtypes(include=[np.number]).columns.tolist()
            if len(cols) < 2:
                st.warning("⚠️ Need at least 2 numeric columns for heatmap.")
                return None
            corr = df[cols].corr()
            return go.Figure(data=go.Heatmap(
                z=corr.values, x=corr.columns.tolist(), y=corr.columns.tolist(),
                colorscale="Viridis", text=corr.values.round(2),
                texttemplate="%{text}", textfont={"size": 11},
            ))

        elif chart_type == "scatter":
            x = meas[0] if len(meas) >= 1 else (dims[0] if dims else df.columns[0])
            y = meas[1] if len(meas) >= 2 else (meas[0] if meas else df.columns[1])
            return px.scatter(df, x=x, y=y, color=color, size=size,
                              hover_data=tooltips or None,
                              color_discrete_sequence=CHART_COLORS, template="plotly_dark", opacity=0.7)

        elif chart_type == "line":
            x = dims[0] if dims else (meas[0] if meas else df.columns[0])
            y = meas if meas else [df.columns[1]]
            if len(y) == 1:
                return px.line(df, x=x, y=y[0], color=color,
                               color_discrete_sequence=CHART_COLORS, template="plotly_dark", markers=True)
            else:
                fig = go.Figure()
                for i, m in enumerate(y):
                    fig.add_trace(go.Scatter(x=df[x], y=df[m], mode="lines+markers",
                                             name=m, line=dict(color=CHART_COLORS[i % len(CHART_COLORS)])))
                return fig

        else:  # bar (default)
            x = dims[0] if dims else (meas[0] if meas else df.columns[0])
            y = meas[0] if meas else None
            group = dims[1] if len(dims) >= 2 else color
            if y:
                return px.bar(df, x=x, y=y, color=group,
                              hover_data=tooltips or None,
                              color_discrete_sequence=CHART_COLORS, template="plotly_dark",
                              barmode="group" if group else "relative")
            else:
                counts = df[x].value_counts().reset_index()
                counts.columns = [x, "count"]
                return px.bar(counts, x=x, y="count",
                              color_discrete_sequence=CHART_COLORS, template="plotly_dark")

    except Exception as e:
        st.error(f"❌ Chart error: {e}")
        return None


def _save_chart_config(chart_type, chart_type_name, title, dims, meas, color_col, size_col):
    """Save chart config to session for dashboard use."""
    config = {
        "chart_type": chart_type,
        "chart_type_name": chart_type_name,
        "title": title,
        "dims": dims,
        "meas": meas,
        "color": color_col,
        "size": size_col,
        "x": dims[0] if dims else (meas[0] if meas else None),
        "y": meas[0] if meas else None,
    }
    if "saved_charts" not in st.session_state:
        st.session_state["saved_charts"] = []
    st.session_state["saved_charts"].append(config)
    st.success(f"✅ **{title}** saved! ({len(st.session_state['saved_charts'])} charts)")


# ══════════════════════════════════════════════════════════════════════
# MATRIX TABLE (Power BI style)
# ══════════════════════════════════════════════════════════════════════

def _render_matrix_table(df):
    st.markdown("### 📋 Matrix / Table View")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">Create a sortable table with row grouping and subtotals (like Power BI Table visual).</p>',
        unsafe_allow_html=True,
    )

    dimensions, measures = _classify_columns(df)

    c1, c2 = st.columns(2)
    with c1:
        row_cols = st.multiselect("Row Fields", df.columns.tolist(), key="matrix_rows")
    with c2:
        val_cols = st.multiselect("Value Fields", measures, key="matrix_vals")

    show_totals = st.checkbox("Show Subtotals", value=True, key="matrix_totals")
    agg_func = st.selectbox("Aggregation", ["sum", "mean", "count", "min", "max"], key="matrix_agg")

    if row_cols and val_cols:
        try:
            matrix = df.groupby(row_cols)[val_cols].agg(agg_func).reset_index()

            if show_totals:
                totals = {col: "TOTAL" if col == row_cols[0] else "" for col in row_cols}
                for vc in val_cols:
                    totals[vc] = matrix[vc].sum() if agg_func in ("sum", "count") else matrix[vc].mean()
                totals_df = pd.DataFrame([totals])
                matrix = pd.concat([matrix, totals_df], ignore_index=True)

            # Style the dataframe
            st.dataframe(
                matrix,
                use_container_width=True,
                height=min(600, 50 + len(matrix) * 35),
                hide_index=True,
            )

            if st.button("💾 Save Table to Dashboard", key="save_matrix", use_container_width=True):
                config = {
                    "chart_type": "matrix",
                    "chart_type_name": "Matrix Table",
                    "title": f"Table: {', '.join(row_cols)} × {', '.join(val_cols)}",
                    "row_cols": row_cols,
                    "val_cols": val_cols,
                    "agg_func": agg_func,
                    "show_totals": show_totals,
                    "dims": row_cols,
                    "meas": val_cols,
                    "x": row_cols[0] if row_cols else None,
                    "y": val_cols[0] if val_cols else None,
                }
                if "saved_charts" not in st.session_state:
                    st.session_state["saved_charts"] = []
                st.session_state["saved_charts"].append(config)
                st.success("✅ Table saved to dashboard!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
    elif row_cols or val_cols:
        st.info("👈 Select both Row Fields and Value Fields to create a matrix.")


# ══════════════════════════════════════════════════════════════════════
# ADVANCED ANALYTICS (Tableau style)
# ══════════════════════════════════════════════════════════════════════

def _render_advanced_analytics(df):
    st.markdown("### 📈 Advanced Analytics")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">Add trend lines, forecasting, and clustering to your data.</p>',
        unsafe_allow_html=True,
    )

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 1:
        st.warning("⚠️ Need at least 1 numeric column.")
        return

    analytics_type = st.selectbox("Analytics Type", [
        "📉 Trend Line",
        "🔮 Forecast",
        "🎯 K-Means Clustering",
    ], key="analytics_type")

    if "Trend" in analytics_type:
        _render_trend_line(df, numeric_cols)
    elif "Forecast" in analytics_type:
        _render_forecast(df, numeric_cols)
    elif "Cluster" in analytics_type:
        _render_clustering(df, numeric_cols)


def _render_trend_line(df, numeric_cols):
    c1, c2 = st.columns(2)
    with c1:
        x_col = st.selectbox("X-Axis", df.columns.tolist(), key="trend_x")
    with c2:
        y_col = st.selectbox("Y-Axis", numeric_cols, key="trend_y")

    trendline = st.selectbox("Trend Type", ["ols", "lowess", "expanding"], key="trend_type")

    if x_col and y_col:
        try:
            if trendline == "expanding":
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode="markers",
                                         name="Data", marker=dict(color=CHART_COLORS[0])))
                expanding_mean = df[y_col].expanding().mean()
                fig.add_trace(go.Scatter(x=df[x_col], y=expanding_mean, mode="lines",
                                         name="Expanding Mean", line=dict(color=CHART_COLORS[1], width=2)))
            else:
                fig = px.scatter(df, x=x_col, y=y_col, trendline=trendline,
                                 color_discrete_sequence=CHART_COLORS, template="plotly_dark")

            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(title=f"Trend: {y_col} over {x_col}", height=480)
            st.plotly_chart(fig, use_container_width=True, key="trend_chart")
        except Exception as e:
            st.error(f"❌ Error: {e}")


def _render_forecast(df, numeric_cols):
    y_col = st.selectbox("Column to Forecast", numeric_cols, key="forecast_col")
    periods = st.slider("Forecast Periods", 5, 50, 10, key="forecast_periods")

    if y_col and st.button("🔮 Generate Forecast", key="do_forecast", use_container_width=True):
        try:
            values = df[y_col].dropna().values
            n = len(values)

            # Simple linear regression forecast
            x_vals = np.arange(n)
            coeffs = np.polyfit(x_vals, values, 1)
            poly = np.poly1d(coeffs)

            future_x = np.arange(n, n + periods)
            forecast_vals = poly(future_x)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(range(n)), y=values, mode="lines+markers",
                                     name="Actual", line=dict(color=CHART_COLORS[0])))
            fig.add_trace(go.Scatter(x=list(range(n, n + periods)), y=forecast_vals, mode="lines+markers",
                                     name="Forecast", line=dict(color=CHART_COLORS[1], dash="dash")))

            # Confidence band
            std = np.std(values - poly(x_vals))
            upper = forecast_vals + 1.96 * std
            lower = forecast_vals - 1.96 * std
            fig.add_trace(go.Scatter(x=list(range(n, n + periods)), y=upper, mode="lines",
                                     name="Upper 95% CI", line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=list(range(n, n + periods)), y=lower, mode="lines",
                                     name="Lower 95% CI", line=dict(width=0),
                                     fill="tonexty", fillcolor="rgba(88,166,255,0.15)", showlegend=False))

            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(title=f"Forecast: {y_col} (+{periods} periods)", height=480)
            st.plotly_chart(fig, use_container_width=True, key="forecast_chart")

            st.markdown(f"**Trend slope:** {coeffs[0]:.4f} per period | **R²:** {1 - np.var(values - poly(x_vals)) / np.var(values):.4f}")
        except Exception as e:
            st.error(f"❌ Forecast error: {e}")


def _render_clustering(df, numeric_cols):
    st.markdown("Select 2 numeric columns for K-Means clustering:")
    c1, c2 = st.columns(2)
    with c1:
        x_col = st.selectbox("X", numeric_cols, key="cluster_x")
    with c2:
        y_col = st.selectbox("Y", [c for c in numeric_cols if c != x_col] if len(numeric_cols) > 1 else numeric_cols, key="cluster_y")

    n_clusters = st.slider("Number of Clusters (K)", 2, 8, 3, key="n_clusters")

    if st.button("🎯 Run Clustering", key="do_cluster", use_container_width=True):
        try:
            from sklearn.cluster import KMeans
            data = df[[x_col, y_col]].dropna()
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            data["Cluster"] = kmeans.fit_predict(data[[x_col, y_col]])
            data["Cluster"] = data["Cluster"].astype(str)

            fig = px.scatter(data, x=x_col, y=y_col, color="Cluster",
                             color_discrete_sequence=CHART_COLORS, template="plotly_dark",
                             title=f"K-Means Clustering (K={n_clusters})")

            # Add centroids
            centers = kmeans.cluster_centers_
            fig.add_trace(go.Scatter(x=centers[:, 0], y=centers[:, 1], mode="markers",
                                     name="Centroids", marker=dict(size=15, color="white",
                                     symbol="x", line=dict(width=2))))

            fig.update_layout(**PLOTLY_LAYOUT)
            fig.update_layout(height=480)
            st.plotly_chart(fig, use_container_width=True, key="cluster_chart")

            st.markdown(f"**Inertia:** {kmeans.inertia_:.2f}")

        except ImportError:
            st.error("❌ scikit-learn is required for clustering. Run `pip install scikit-learn`.")
        except Exception as e:
            st.error(f"❌ Clustering error: {e}")
