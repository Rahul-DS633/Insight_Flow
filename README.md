# 📊 InsightFlow – AI-Powered Data Analytics Platform

InsightFlow is a modern data analytics and visualization platform inspired by **Microsoft Power BI** and **Tableau**. It allows users to upload datasets, clean and analyze data, build interactive visualizations, and generate AI-driven insights automatically using **Google Gemini AI**.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-blue?logo=plotly&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_AI-Integrated-green?logo=google&logoColor=white)

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 📂 **Dataset Upload** | Upload CSV/Excel files with instant preview |
| 🧹 **Data Cleaning** | Auto-detect missing values, duplicates, type issues |
| 📊 **Chart Builder** | Bar, Line, Scatter, Pie, Histogram, Heatmap (Plotly) |
| 📈 **Dashboard** | Combine charts into multi-chart dashboards |
| 🎛️ **Data Filtering** | Dynamic filters (numeric ranges, categories, dates) |
| 🤖 **AI Insights** | Gemini AI analyzes data for trends & anomalies |

---

## 🛠️ Tech Stack

- **Backend**: Python, Pandas, NumPy
- **Visualization**: Plotly
- **Frontend**: Streamlit
- **AI**: Google Gemini API
- **Database**: SQLite

---

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Rahul-DS633/Insight_Flow.git
cd InsightFlow
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure AI (Optional)

Copy `.env.example` to `.env` and add your Google Gemini API key:

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 📂 Project Structure

```
InsightFlow/
├── app.py                  # Main Streamlit application
├── config.py               # Configuration & constants
├── database.py             # SQLite database manager
├── requirements.txt        # Python dependencies
├── .env.example            # API key template
├── assets/
│   └── style.css           # Power BI-inspired dark theme
└── modules/
    ├── data_upload.py      # Dataset upload & preview
    ├── data_cleaning.py    # Data cleaning tools
    ├── chart_builder.py    # Interactive chart builder
    ├── dashboard_builder.py # Dashboard creation
    ├── data_filter.py      # Dynamic data filtering
    └── ai_insights.py      # AI-powered insights (Gemini)
```

---

## 🤖 AI Insights

InsightFlow integrates **Google Gemini AI** to automatically analyze your dataset and generate insights including:

- 📈 **Trends** – Revenue growth, seasonal patterns
- ⚠️ **Anomalies** – Unusual data points and outliers
- 💡 **Recommendations** – Actionable business insights
- 📊 **Relationships** – Column correlations and dependencies

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
