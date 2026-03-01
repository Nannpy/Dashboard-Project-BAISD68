# 🌿 Hydroponics AI Monitoring Platform

A production-ready IoT monitoring dashboard for hydroponic systems, built with **Dash** and **Plotly**. Designed with a modern dark-themed Silicon Valley SaaS aesthetic.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Dash](https://img.shields.io/badge/Dash-2.14+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Real-time KPIs** | Health score, anomaly counter, stability index, last reading |
| **Anomaly Detection** | Rolling z-score flagging with visual markers on charts |
| **Health Scoring** | Weighted stability score (pH 40%, TDS 30%, Temp 30%) |
| **AI Insights** | Natural-language system status summary |
| **Interactive Charts** | Three dark-themed line charts with anomaly overlay |
| **Date Filtering** | DateRangePicker for custom time windows |
| **Resampling** | Raw / 5min / 15min / 1H aggregation |
| **Events Table** | Paginated anomaly event log |

---

## 🏗️ Architecture

The platform follows a clean **3-layer separation of concerns**:

```
┌──────────────────────────────────────────┐
│            Presentation Layer            │
│  app.py — Dash layout, callbacks, UI     │
├──────────────────────────────────────────┤
│           Intelligence Layer             │
│  intelligence.py — anomaly detection,    │
│  health score, AI insight generation     │
├──────────────────────────────────────────┤
│              Data Layer                  │
│  data_layer.py — CSV ingestion,          │
│  cleansing, resampling                   │
└──────────────────────────────────────────┘
```

### Data Layer (`data_layer.py`)

- **`clean_data(filepath)`** — Reads the CSV, parses timestamps, drops invalid rows, coerces sensor columns to numeric, applies time-based interpolation, removes pH outliers (< 3 or > 10), and returns a clean datetime-indexed DataFrame.
- **`resample_data(df, frequency)`** — Resamples the sensor data at a given frequency (`5min`, `15min`, `1H`) using mean aggregation. Passing `"raw"` returns the data unchanged.

### Intelligence Layer (`intelligence.py`)

- **`detect_anomalies(df)`** — Uses a rolling window (30 observations) to compute mean ± 3σ boundaries. Rows exceeding these bounds are flagged with boolean columns (`pH_anomaly`, `TDS_anomaly`, `temp_anomaly`).
- **`health_score(df)`** — Computes a 0–100 stability score using the coefficient of variation for each sensor, weighted: pH 40%, TDS 30%, Temp 30%. Returns the score and a status label (`Healthy` / `Warning` / `Critical`).
- **`generate_insight(df, health, anomaly_count)`** — Produces a plain-English summary of the current system state.

### Presentation Layer (`app.py`)

- Pure **Dash** layout with no analytics logic.
- Imports functions from the data and intelligence layers.
- Single unified callback updates all components for consistent state.

---

## 🎨 Design System

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#0F172A` | Page background |
| Card Surface | `#1F2937` | Card panels |
| Primary Green | `#22C55E` | pH line, status indicators |
| Accent Green | `#16A34A` | Hover / accent elements |
| Cyan | `#06B6D4` | TDS chart line |
| Amber | `#F59E0B` | Temperature chart line |
| Red | `#EF4444` | Anomaly markers |
| Muted Text | `#9CA3AF` | Labels, secondary text |
| White | `#F9FAFB` | Primary text |

Typography: **Inter** via Google Fonts.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# Clone / navigate to the project
cd dash_project

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python app.py
```

The app launches at **http://127.0.0.1:8050**.

### Dataset

Place `hydroponics_data.csv` in the project root. Expected columns:

| Column | Type | Description |
|--------|------|-------------|
| `timestamp` | datetime | Reading timestamp |
| `pH` | float | pH level |
| `TDS` | float | Total Dissolved Solids (ppm) |
| `water_temp` | float | Water temperature (°C) |

Additional columns are preserved but not plotted.

---

## 📋 Data Cleaning Process

1. **Timestamp parsing** — `pd.to_datetime` with `errors='coerce'`; invalid rows dropped.
2. **Deduplication** — Duplicate timestamps removed (keep first).
3. **Numeric coercion** — pH, TDS, water_temp forced to numeric; non-numeric → NaN.
4. **Time-based interpolation** — Fills sensor gaps using surrounding timestamps.
5. **Outlier removal** — pH values outside 3–10 are removed.
6. **Chronological sorting** — Data ordered by timestamp ascending.

---

## 📂 Project Structure

```
dash_project/
├── app.py              # Presentation layer (Dash)
├── data_layer.py       # Data ingestion & cleansing
├── intelligence.py     # Anomaly detection & health scoring
├── hydroponics_data.csv
├── requirements.txt
└── README.md
```

---

## 🛡️ License

MIT
