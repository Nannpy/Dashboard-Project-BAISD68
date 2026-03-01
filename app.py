import dash
from dash import dcc, html, Input, Output, dash_table, callback
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data_layer import clean_data, resample_data
from intelligence import detect_anomalies, health_score, generate_insight

DATA_FILE = "hydroponics_data.csv"

BG          = "#0F172A"
BG_ALT      = "#111827"
CARD        = "#1F2937"
CARD_BORDER = "#374151"
GREEN       = "#22C55E"
GREEN_ACCENT = "#16A34A"
RED         = "#EF4444"
AMBER       = "#F59E0B"
MUTED       = "#9CA3AF"
WHITE       = "#F9FAFB"
CYAN        = "#06B6D4"

DF_CLEAN = clean_data(DATA_FILE)

app = dash.Dash(
    __name__,
    title="Hydroponics AI Platform",
    update_title="Loading…",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # for production WSGI

card_style = {
    "background": CARD,
    "borderRadius": "16px",
    "padding": "24px",
    "border": f"1px solid {CARD_BORDER}",
}

kpi_card_style = {
    **card_style,
    "flex": "1",
    "minWidth": "200px",
    "textAlign": "center",
}


def _kpi_card(title, value_id, icon="", extra_style=None):
    """Factory for a single KPI card."""
    s = {**kpi_card_style}
    if extra_style:
        s.update(extra_style)
    return html.Div(
        style=s,
        children=[
            html.P(
                f"{icon}  {title}" if icon else title,
                style={"color": MUTED, "fontSize": "13px", "marginBottom": "8px",
                       "letterSpacing": "0.5px", "textTransform": "uppercase"},
            ),
            html.H2(id=value_id, style={"color": WHITE, "margin": "0", "fontSize": "28px",
                                         "fontWeight": "700"}),
        ],
    )

# LAYOUT
app.layout = html.Div(
    style={
        "fontFamily": "'Inter', 'Segoe UI', system-ui, sans-serif",
        "background": BG,
        "minHeight": "100vh",
        "padding": "0",
        "color": WHITE,
    },
    children=[
        html.Link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        ),

        html.Div(
            style={"maxWidth": "1320px", "margin": "0 auto", "padding": "32px 24px"},
            children=[
                html.Div(
                    style={
                        "display": "flex", "alignItems": "center",
                        "justifyContent": "space-between",
                        "marginBottom": "32px", "flexWrap": "wrap", "gap": "16px",
                    },
                    children=[
                        html.Div(children=[
                            html.H1(
                                "Hydroponics AI Monitoring Platform",
                                style={
                                    "margin": "0", "fontSize": "26px",
                                    "fontWeight": "700", "color": WHITE,
                                    "letterSpacing": "-0.5px",
                                },
                            ),
                            html.P(
                                "Real-time sensor analytics & anomaly detection",
                                style={"margin": "4px 0 0", "fontSize": "14px",
                                       "color": MUTED},
                            ),
                        ]),
                        html.Div(
                            style={
                                "display": "flex", "alignItems": "center",
                                "gap": "8px",
                            },
                            children=[
                                html.Div(
                                    style={
                                        "width": "10px", "height": "10px",
                                        "borderRadius": "50%", "background": GREEN,
                                        "boxShadow": f"0 0 8px {GREEN}",
                                    },
                                ),
                                html.Span("System Online", style={"fontSize": "13px",
                                                                    "color": GREEN,
                                                                    "fontWeight": "600"}),
                            ],
                        ),
                    ],
                ),

                html.Div(
                    style={"display": "flex", "gap": "16px", "marginBottom": "24px",
                           "flexWrap": "wrap"},
                    children=[
                        _kpi_card("Health Score", "kpi-health", "💚"),
                        _kpi_card("Active Anomalies", "kpi-anomalies", "🔴"),
                        _kpi_card("Stability Index", "kpi-stability", "📊"),
                        _kpi_card("Last Reading", "kpi-timestamp", "🕐"),
                    ],
                ),

                html.Div(
                    style={
                        **card_style,
                        "marginBottom": "24px",
                        "display": "flex", "alignItems": "center",
                        "gap": "24px", "flexWrap": "wrap",
                    },
                    children=[
                        html.Div(
                            style={"flex": "1", "minWidth": "260px"},
                            children=[
                                html.Label("Date Range", style={
                                    "fontSize": "12px", "color": MUTED,
                                    "textTransform": "uppercase", "letterSpacing": "0.5px",
                                    "marginBottom": "8px", "display": "block",
                                }),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    min_date_allowed=DF_CLEAN.index.min().date(),
                                    max_date_allowed=DF_CLEAN.index.max().date(),
                                    start_date=DF_CLEAN.index.min().date(),
                                    end_date=DF_CLEAN.index.max().date(),
                                    style={"fontSize": "13px"},
                                ),
                            ],
                        ),
                        html.Div(
                            style={"minWidth": "180px"},
                            children=[
                                html.Label("Resampling", style={
                                    "fontSize": "12px", "color": MUTED,
                                    "textTransform": "uppercase", "letterSpacing": "0.5px",
                                    "marginBottom": "8px", "display": "block",
                                }),
                                dcc.Dropdown(
                                    id="resample-freq",
                                    options=[
                                        {"label": "Raw Data", "value": "raw"},
                                        {"label": "5 Minutes", "value": "5min"},
                                        {"label": "15 Minutes", "value": "15min"},
                                        {"label": "1 Hour", "value": "1H"},
                                    ],
                                    value="raw",
                                    clearable=False,
                                    style={
                                        "background": BG_ALT,
                                        "color": WHITE,
                                        "border": "none",
                                        "borderRadius": "8px",
                                        "fontSize": "13px",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),

                dcc.Loading(
                    type="dot",
                    color=GREEN,
                    children=html.Div(id="charts-section"),
                ),

                dcc.Loading(
                    type="dot",
                    color=GREEN,
                    children=html.Div(
                        id="insight-panel",
                        style={
                            **card_style,
                            "marginTop": "24px",
                            "borderLeft": f"4px solid {GREEN}",
                        },
                    ),
                ),

                dcc.Loading(
                    type="dot",
                    color=GREEN,
                    children=html.Div(
                        id="events-section",
                        style={**card_style, "marginTop": "24px"},
                    ),
                ),

                html.Div(
                    style={"textAlign": "center", "padding": "32px 0 8px",
                           "fontSize": "12px", "color": MUTED},
                    children="Hydroponics AI Monitoring Platform · Built with Dash & Plotly",
                ),
            ],
        ),
    ],
)

def _prepare(start_date, end_date, freq):
    """Slice, resample, and detect anomalies — shared by all callbacks."""
    df = DF_CLEAN.copy()
    if start_date:
        df = df[df.index >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df.index <= pd.Timestamp(end_date) + pd.Timedelta(days=1)]
    df = resample_data(df, freq)
    df = detect_anomalies(df)
    return df

# CHART BUILDER
CHART_CONFIG = [
    {"col": "pH",         "title": "pH Level",           "unit": "",    "color": GREEN,  "anomaly": "pH_anomaly"},
    {"col": "TDS",        "title": "TDS (ppm)",          "unit": " ppm","color": CYAN,   "anomaly": "TDS_anomaly"},
    {"col": "water_temp", "title": "Water Temperature",  "unit": " °C", "color": AMBER,  "anomaly": "temp_anomaly"},
]


def _build_chart(df, cfg):
    """Build a single dark-themed time-series chart with anomaly markers."""
    col = cfg["col"]
    if col not in df.columns:
        return html.Div()

    fig = go.Figure()

    # Main line
    fig.add_trace(go.Scatter(
        x=df.index, y=df[col],
        mode="lines",
        name=cfg["title"],
        line=dict(color=cfg["color"], width=2),
        hovertemplate=f"%{{x|%Y-%m-%d %H:%M}}<br>{cfg['title']}: %{{y:.2f}}{cfg['unit']}<extra></extra>",
    ))

    # Anomaly markers
    anomaly_col = cfg["anomaly"]
    if anomaly_col in df.columns:
        anom = df[df[anomaly_col]]
        if not anom.empty:
            fig.add_trace(go.Scatter(
                x=anom.index, y=anom[col],
                mode="markers",
                name="Anomaly",
                marker=dict(color=RED, size=7, symbol="circle",
                            line=dict(color="#fff", width=1)),
                hovertemplate=f"%{{x|%Y-%m-%d %H:%M}}<br>⚠ Anomaly: %{{y:.2f}}{cfg['unit']}<extra></extra>",
            ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(family="Inter, sans-serif", color=MUTED, size=12),
        title=dict(text=cfg["title"], font=dict(size=15, color=WHITE),
                   x=0.02, y=0.95),
        margin=dict(l=48, r=24, t=48, b=40),
        height=280,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1, font=dict(size=11),
        ),
        xaxis=dict(
            gridcolor="#2D3748", gridwidth=0.5,
            showgrid=True, zeroline=False,
        ),
        yaxis=dict(
            gridcolor="#2D3748", gridwidth=0.5,
            showgrid=True, zeroline=False,
            title=dict(text=f"{cfg['title']}{cfg['unit']}", font=dict(size=11)),
        ),
        hovermode="x unified",
    )
    return dcc.Graph(figure=fig, config={"displayModeBar": False})


# CALLBACKS

@app.callback(
    Output("kpi-health", "children"),
    Output("kpi-anomalies", "children"),
    Output("kpi-stability", "children"),
    Output("kpi-timestamp", "children"),
    Output("charts-section", "children"),
    Output("insight-panel", "children"),
    Output("events-section", "children"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("resample-freq", "value"),
)
def update_dashboard(start_date, end_date, freq):
    """Single callback that updates every component for consistent state."""
    df = _prepare(start_date, end_date, freq)

    # ── KPIs ────────────────────────────────────────────────
    health = health_score(df)
    score = health["score"]
    status = health["system_status"]

    # Color based on status
    status_color = GREEN if status == "Healthy" else AMBER if status == "Warning" else RED

    kpi_health_val = html.Span([
        html.Span(f"{score}", style={"color": status_color}),
        html.Span(f" / 100", style={"fontSize": "14px", "color": MUTED}),
    ])

    anomaly_cols = ["pH_anomaly", "TDS_anomaly", "temp_anomaly"]
    total_anomalies = sum(
        int(df[c].sum()) for c in anomaly_cols if c in df.columns
    )
    anom_color = GREEN if total_anomalies == 0 else RED
    kpi_anomalies_val = html.Span(
        str(total_anomalies),
        style={"color": anom_color},
    )

    avg_stability = round(
        (health["ph_stability"] + health["tds_stability"] + health["temp_stability"]) / 3,
        1,
    )
    kpi_stability_val = html.Span([
        html.Span(f"{avg_stability}%", style={"color": WHITE}),
    ])

    last_ts = df.index.max()
    kpi_ts_val = html.Span(
        last_ts.strftime("%b %d, %H:%M") if pd.notna(last_ts) else "—",
        style={"fontSize": "18px", "color": WHITE},
    )

    charts = html.Div(
        style={"display": "grid", "gridTemplateColumns": "1fr",
               "gap": "16px"},
        children=[
            html.Div(style=card_style, children=_build_chart(df, cfg))
            for cfg in CHART_CONFIG
        ],
    )

    insight_text = generate_insight(df, health, total_anomalies)
    insight = [
        html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "10px",
                   "marginBottom": "12px"},
            children=[
                html.Span("🤖", style={"fontSize": "20px"}),
                html.H3("AI System Insight", style={"margin": "0", "fontSize": "16px",
                                                      "color": WHITE, "fontWeight": "600"}),
            ],
        ),
        html.P(insight_text, style={"color": MUTED, "fontSize": "14px",
                                     "lineHeight": "1.7", "margin": "0"}),
    ]

    event_rows = []
    for c, label in [("pH_anomaly", "pH"), ("TDS_anomaly", "TDS"), ("temp_anomaly", "Temp")]:
        if c in df.columns:
            mask = df[c]
            for ts, row in df[mask].iterrows():
                sensor_col = {"pH_anomaly": "pH", "TDS_anomaly": "TDS", "temp_anomaly": "water_temp"}[c]
                event_rows.append({
                    "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "Sensor": label,
                    "Value": round(row.get(sensor_col, 0), 2),
                    "Type": "Anomaly",
                })

    event_rows = sorted(event_rows, key=lambda r: r["Timestamp"], reverse=True)[:50]

    events_header = html.Div(
        style={"display": "flex", "alignItems": "center", "gap": "10px",
               "marginBottom": "16px"},
        children=[
            html.Span("📋", style={"fontSize": "20px"}),
            html.H3("Recent Events", style={"margin": "0", "fontSize": "16px",
                                              "color": WHITE, "fontWeight": "600"}),
            html.Span(
                f"{len(event_rows)} events",
                style={"fontSize": "12px", "color": MUTED,
                       "background": BG_ALT, "padding": "2px 10px",
                       "borderRadius": "12px"},
            ),
        ],
    )

    if event_rows:
        events_table = dash_table.DataTable(
            data=event_rows,
            columns=[
                {"name": "Timestamp", "id": "Timestamp"},
                {"name": "Sensor", "id": "Sensor"},
                {"name": "Value", "id": "Value"},
                {"name": "Type", "id": "Type"},
            ],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_header={
                "backgroundColor": BG_ALT,
                "color": MUTED,
                "fontWeight": "600",
                "fontSize": "12px",
                "textTransform": "uppercase",
                "letterSpacing": "0.5px",
                "border": "none",
                "borderBottom": f"1px solid {CARD_BORDER}",
            },
            style_cell={
                "backgroundColor": CARD,
                "color": WHITE,
                "fontSize": "13px",
                "border": "none",
                "borderBottom": f"1px solid {CARD_BORDER}",
                "padding": "10px 16px",
                "textAlign": "left",
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": '{Type} = "Anomaly"'},
                    "color": RED,
                    "fontWeight": "600",
                },
            ],
        )
    else:
        events_table = html.P(
            "No events in the selected range.",
            style={"color": MUTED, "fontSize": "13px"},
        )

    events_children = [events_header, events_table]

    return (
        kpi_health_val,
        kpi_anomalies_val,
        kpi_stability_val,
        kpi_ts_val,
        charts,
        insight,
        events_children,
    )

if __name__ == "__main__":
    app.run(debug=True, port=8050)