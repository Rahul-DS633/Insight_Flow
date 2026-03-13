"""
InsightFlow – AI-Powered Insights Module
Generate automated insights using Google Gemini AI.
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from config import COLORS, GEMINI_MODEL, MAX_INSIGHT_ROWS

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def render():
    """Render the AI insights page."""
    st.markdown("## 🤖 AI-Powered Insights")
    st.markdown(
        f'<p style="color:{COLORS["text_secondary"]};">'
        "Leverage Google Gemini AI to automatically discover trends, anomalies, and key patterns in your data.</p>",
        unsafe_allow_html=True,
    )

    if "current_df" not in st.session_state or st.session_state["current_df"] is None:
        _show_empty_state()
        return

    if not GENAI_AVAILABLE:
        st.error("❌ `google-generativeai` package is not installed. Run `pip install google-generativeai`.")
        return

    # ── API Key Configuration ─────────────────────────────────────────
    api_key = _get_api_key()
    if not api_key:
        return

    df = st.session_state["current_df"]

    # Apply filters if active
    if "filtered_df" in st.session_state and st.session_state["filtered_df"] is not None:
        df = st.session_state["filtered_df"]
        st.info("📊 Analyzing **filtered** dataset")

    # ── Dataset Summary ───────────────────────────────────────────────
    _show_dataset_summary(df)

    st.markdown("---")

    # ── Insight Generation ────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    with col1:
        analysis_type = st.selectbox(
            "Analysis Focus",
            [
                "🔍 General Overview",
                "📈 Trends & Patterns",
                "⚠️ Anomalies & Outliers",
                "📊 Column Relationships",
                "💡 Business Recommendations",
                "📋 Data Quality Assessment",
            ],
            key="analysis_type",
        )
    with col2:
        detail_level = st.selectbox(
            "Detail Level",
            ["Concise", "Detailed", "Comprehensive"],
            index=1,
            key="detail_level",
        )

    # Custom question
    custom_q = st.text_area(
        "Ask a specific question about your data (optional)",
        placeholder="e.g., Which product category has the highest growth trend?",
        key="custom_question",
    )

    if st.button("🚀 Generate Insights", key="generate_insights", use_container_width=True):
        _generate_insights(api_key, df, analysis_type, detail_level, custom_q)

    # ── Show Previous Insights ────────────────────────────────────────
    if "ai_insights" in st.session_state and st.session_state["ai_insights"]:
        st.markdown("---")
        st.markdown("### 💡 AI Insights")
        _render_insights(st.session_state["ai_insights"])


def _show_empty_state():
    st.markdown(
        f'<div style="text-align:center; padding:60px; color:{COLORS["text_muted"]};">'
        '<p style="font-size:3rem; margin-bottom:8px;">📭</p>'
        "<p>No dataset loaded. Go to <b>Dataset Upload</b> first.</p>"
        "</div>",
        unsafe_allow_html=True,
    )


def _get_api_key():
    """Get Gemini API key from env or user input."""
    api_key = os.getenv("GOOGLE_API_KEY", "")

    if not api_key:
        st.markdown(
            f'<div style="background:{COLORS["bg_card"]}; border:1px solid {COLORS["border"]}; '
            f'border-radius:12px; padding:20px; margin-bottom:20px;">'
            f'<p style="color:{COLORS["accent_gold"]}; font-weight:600;">🔑 API Key Required</p>'
            f'<p style="color:{COLORS["text_secondary"]};">Enter your Google Gemini API key to generate insights.</p>'
            "</div>",
            unsafe_allow_html=True,
        )
        api_key = st.text_input(
            "Google Gemini API Key",
            type="password",
            key="gemini_key_input",
            help="Get your key at https://aistudio.google.com/apikey",
        )

    if not api_key:
        st.warning("⚠️ Please provide a Gemini API key to continue.")
        return None

    return api_key


def _show_dataset_summary(df):
    """Display quick dataset summary."""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", f"{len(df):,}")
    with col2:
        st.metric("Columns", f"{len(df.columns)}")
    with col3:
        numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
        st.metric("Numeric Cols", f"{numeric_cols}")
    with col4:
        cat_cols = len(df.select_dtypes(include=["object", "category"]).columns)
        st.metric("Categorical Cols", f"{cat_cols}")


def _generate_insights(api_key, df, analysis_type, detail_level, custom_question):
    """Generate insights using Gemini AI."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Prepare dataset context
        context = _prepare_data_context(df)

        # Build prompt
        prompt = _build_prompt(context, analysis_type, detail_level, custom_question)

        with st.spinner("🧠 AI is analyzing your data..."):
            response = model.generate_content(prompt)
            insights = response.text

        st.session_state["ai_insights"] = insights
        st.rerun()

    except Exception as e:
        st.error(f"❌ AI generation failed: {str(e)}")


def _prepare_data_context(df):
    """Prepare dataset context for the AI prompt."""
    sample = df.head(MAX_INSIGHT_ROWS)

    context_parts = []

    # Basic info
    context_parts.append(f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    context_parts.append(f"Columns: {', '.join(df.columns.tolist())}")

    # Data types
    dtypes = df.dtypes.astype(str).to_dict()
    context_parts.append(f"Data Types: {dtypes}")

    # Statistical summary
    desc = df.describe(include="all").to_string()
    context_parts.append(f"Statistical Summary:\n{desc}")

    # Missing values
    missing = df.isna().sum()
    if missing.sum() > 0:
        missing_info = missing[missing > 0].to_dict()
        context_parts.append(f"Missing Values: {missing_info}")

    # Correlations (numeric only)
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) >= 2:
        corr = numeric_df.corr().round(3)
        context_parts.append(f"Correlation Matrix:\n{corr.to_string()}")

    # Sample data
    context_parts.append(f"Sample Data (first 5 rows):\n{sample.head().to_string()}")

    return "\n\n".join(context_parts)


def _build_prompt(context, analysis_type, detail_level, custom_question):
    """Build the Gemini prompt."""
    focus_map = {
        "🔍 General Overview": "Provide a general overview of the dataset, highlighting key statistics, distributions, and notable features.",
        "📈 Trends & Patterns": "Focus on identifying trends, patterns, seasonal effects, and temporal relationships in the data.",
        "⚠️ Anomalies & Outliers": "Identify anomalies, outliers, unexpected values, and data points that deviate significantly from the norm.",
        "📊 Column Relationships": "Analyze relationships between columns, correlations, dependencies, and potential causal links.",
        "💡 Business Recommendations": "Provide actionable business recommendations based on the data analysis.",
        "📋 Data Quality Assessment": "Assess the data quality, completeness, consistency, and suggest improvements.",
    }

    detail_map = {
        "Concise": "Keep insights brief — use bullet points, 5-8 key observations.",
        "Detailed": "Provide detailed insights with explanations — 10-15 observations with context.",
        "Comprehensive": "Provide comprehensive analysis with deep insights, supporting evidence, and detailed explanations.",
    }

    prompt = f"""You are an expert data analyst. Analyze the following dataset and provide insights.

{focus_map.get(analysis_type, focus_map["🔍 General Overview"])}

{detail_map.get(detail_level, detail_map["Detailed"])}

Format your response with:
- Use clear headers with emoji icons
- Use bullet points for individual insights
- Highlight key numbers and percentages in bold
- Include actionable takeaways
- Use ⬆️ for increases, ⬇️ for decreases, ⚠️ for warnings, 💡 for recommendations

DATASET CONTEXT:
{context}
"""

    if custom_question:
        prompt += f"\n\nUSER'S SPECIFIC QUESTION:\n{custom_question}\n\nPlease address this question specifically in your analysis."

    return prompt


def _render_insights(insights):
    """Render AI-generated insights in a styled format."""
    st.markdown(
        f'<div style="background: linear-gradient(145deg, {COLORS["bg_card"]}, #242d3d); '
        f'border: 1px solid {COLORS["border"]}; border-left: 4px solid {COLORS["accent_gold"]}; '
        f'border-radius: 12px; padding: 24px; margin: 16px 0;">'
        f'<div style="color: {COLORS["text_primary"]};">'
        f'{insights}'
        '</div></div>',
        unsafe_allow_html=True,
    )

    # Copy button
    st.download_button(
        "📥 Download Insights",
        data=insights,
        file_name="insightflow_ai_insights.txt",
        mime="text/plain",
        key="download_insights",
    )
