"""
InsightFlow – Configuration & Constants
"""

# ──────────────────────────── App Metadata ────────────────────────────
APP_NAME = "InsightFlow"
APP_ICON = "📊"
APP_TAGLINE = "AI-Powered Data Analytics Platform"
VERSION = "1.0.0"

# ──────────────────────────── Color Palette (Power BI inspired) ──────
COLORS = {
    "bg_primary": "#0d1117",
    "bg_secondary": "#161b22",
    "bg_card": "#1c2333",
    "bg_sidebar": "#0d1117",
    "accent_gold": "#f0b429",
    "accent_blue": "#58a6ff",
    "accent_green": "#3fb950",
    "accent_red": "#f85149",
    "accent_purple": "#bc8cff",
    "accent_orange": "#f0883e",
    "accent_teal": "#39d2c0",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "text_muted": "#484f58",
    "border": "#30363d",
}

# Plotly chart color sequence
CHART_COLORS = [
    "#58a6ff", "#f0b429", "#3fb950", "#f85149",
    "#bc8cff", "#f0883e", "#39d2c0", "#79c0ff",
    "#d2a8ff", "#ffa657", "#56d364", "#ff7b72",
]

# ──────────────────────────── Chart Types ─────────────────────────────
CHART_TYPES = {
    "Bar Chart": "bar",
    "Line Chart": "line",
    "Scatter Plot": "scatter",
    "Pie Chart": "pie",
    "Histogram": "histogram",
    "Heatmap": "heatmap",
}

CHART_ICONS = {
    "Bar Chart": "📊",
    "Line Chart": "📈",
    "Scatter Plot": "🔵",
    "Pie Chart": "🥧",
    "Histogram": "📉",
    "Heatmap": "🗺️",
}

# ──────────────────────────── Database ────────────────────────────────
DB_PATH = "insightflow.db"

# ──────────────────────────── Plotly Dark Layout ──────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e6edf3", family="Inter, sans-serif"),
    title_font=dict(size=18, color="#e6edf3"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8b949e"),
    ),
    xaxis=dict(
        gridcolor="#30363d",
        zerolinecolor="#30363d",
        tickfont=dict(color="#8b949e"),
    ),
    yaxis=dict(
        gridcolor="#30363d",
        zerolinecolor="#30363d",
        tickfont=dict(color="#8b949e"),
    ),
    margin=dict(l=60, r=30, t=60, b=50),
    hoverlabel=dict(
        bgcolor="#1c2333",
        font_size=13,
        font_color="#e6edf3",
    ),
)

# ──────────────────────────── Supported File Types ────────────────────
SUPPORTED_EXTENSIONS = ["csv", "xlsx", "xls"]

# ──────────────────────────── AI Config ───────────────────────────────
GEMINI_MODEL = "gemini-2.0-flash"
MAX_INSIGHT_ROWS = 500  # max rows to send to Gemini for analysis
