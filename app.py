import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd

CSV_PATH = "hydroponics_data.csv"

df = pd.read_csv(CSV_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp").reset_index(drop=True)
df["date"] = df["timestamp"].dt.date

# columns สำหรับกราฟ (3 อัน)
GRAPH_COLS = ["pH", "TDS", "water_temp"]

# columns สำหรับตารางรายวัน (ทุก column)
TABLE_COLS = ["id", "timestamp", "pH", "TDS", "water_level",
              "DHT_temp", "DHT_humidity", "water_temp",
              "pH_reducer", "add_water", "nutrients_adder", "humidifier", "ex_fan"]

all_dates    = sorted(df["date"].unique())
date_options = [{"label": str(d), "value": str(d)} for d in all_dates]

CHARTS = [
    {"col": "pH",         "color": "#3B82F6", "unit": "",     "label": "pH"},
    {"col": "TDS",        "color": "#F59E0B", "unit": " ppm", "label": "TDS (ppm)"},
    {"col": "water_temp", "color": "#10B981", "unit": " °C",  "label": "Water Temp (°C)"},
]

app = dash.Dash(__name__)
app.title = "Hydro Sensor Dashboard"

app.layout = html.Div(
    style={"fontFamily": "Inter, sans-serif", "background": "#F1F5F9", "minHeight": "100vh", "padding": "32px"},
    children=[
        html.Div(
            style={"maxWidth": "1100px", "margin": "0 auto"},
            children=[

                # ── Header ──────────────────────────────────────────
                html.Div(
                    style={
                        "background": "white", "borderRadius": "16px",
                        "padding": "24px 32px", "marginBottom": "24px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.H1("🌿 Hydro Sensor Dashboard",
                                style={"margin": 0, "fontSize": "24px", "color": "#1E293B"}),
                        html.P(
                            f"ข้อมูล {len(df):,} รายการ  |  "
                            f"{df['timestamp'].min().strftime('%d %b %Y')} – "
                            f"{df['timestamp'].max().strftime('%d %b %Y')}",
                            style={"margin": "6px 0 0", "color": "#64748B", "fontSize": "14px"},
                        ),
                    ],
                ),

                # ── Resample control ────────────────────────────────
                html.Div(
                    style={
                        "background": "white", "borderRadius": "16px",
                        "padding": "20px 32px", "marginBottom": "24px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                        "display": "flex", "alignItems": "center",
                    },
                    children=[
                        html.Label("Resample", style={
                            "fontWeight": "600", "fontSize": "13px",
                            "color": "#374151", "marginRight": "16px",
                        }),
                        dcc.RadioItems(
                            id="resample",
                            options=[
                                {"label": " ทั้งหมด",    "value": "all"},
                                {"label": " รายชั่วโมง", "value": "1h"},
                                {"label": " รายวัน",     "value": "1D"},
                            ],
                            value="all",
                            inline=True,
                            labelStyle={"marginRight": "16px", "fontSize": "14px"},
                        ),
                    ],
                ),

                # ── 3 กราฟ (pH, TDS, water_temp) ───────────────────
                html.Div(id="charts-container"),

                # ── ตารางข้อมูลรายวัน (ทุก column) ─────────────────
                html.Div(
                    style={
                        "background": "white", "borderRadius": "16px",
                        "padding": "20px 32px", "marginTop": "24px",
                        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                    },
                    children=[
                        html.Div(
                            style={
                                "display": "flex", "alignItems": "center",
                                "justifyContent": "space-between",
                                "marginBottom": "16px", "flexWrap": "wrap", "gap": "12px",
                            },
                            children=[
                                html.H3("ข้อมูลรายวัน",
                                        style={"margin": 0, "fontSize": "15px", "color": "#1E293B"}),
                                html.Div(
                                    style={"display": "flex", "alignItems": "center", "gap": "10px"},
                                    children=[
                                        html.Label("เลือกวันที่:", style={
                                            "fontSize": "13px", "color": "#64748B", "fontWeight": "600",
                                        }),
                                        dcc.Dropdown(
                                            id="date-picker",
                                            options=date_options,
                                            value=str(all_dates[0]),
                                            clearable=False,
                                            style={"width": "180px", "fontSize": "13px"},
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        html.Div(id="record-count",
                                 style={"fontSize": "13px", "color": "#64748B", "marginBottom": "10px"}),
                        html.Div(id="date-table"),
                    ],
                ),
            ],
        ),
    ],
)


# ── Callback: กราฟ (ใช้แค่ GRAPH_COLS) ─────────────────────
@app.callback(
    Output("charts-container", "children"),
    Input("resample", "value"),
)
def update_charts(resample):
    if resample == "all":
        plot_df = df[["timestamp"] + GRAPH_COLS].copy()
    else:
        plot_df = (
            df.set_index("timestamp")[GRAPH_COLS]
            .resample(resample).mean().dropna().reset_index()
        )

    charts = []
    for cfg in CHARTS:
        col   = cfg["col"]
        color = cfg["color"]
        unit  = cfg["unit"]
        label = cfg["label"]

        y_vals = plot_df[col]
        y_mean = y_vals.mean()
        y_min  = y_vals.min()
        y_max  = y_vals.max()

        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_df["timestamp"], y=y_vals,
            mode="lines",
            line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{col}</b><br>%{{x|%d %b %Y %H:%M}}<br>%{{y:.2f}}{unit}<extra></extra>",
            fill="tozeroy",
            fillcolor=f"rgba({r},{g},{b},0.08)",
        ))
        fig.add_hline(
            y=y_mean, line_dash="dot", line_color="#94A3B8",
            annotation_text=f"avg {y_mean:.2f}{unit}",
            annotation_font_color="#64748B", annotation_font_size=11,
        )
        fig.update_layout(
            title=dict(
                text=(f"<b>{label}</b>   "
                      f"<span style='font-size:13px;color:#64748B'>"
                      f"min {y_min:.2f}  |  max {y_max:.2f}  |  avg {y_mean:.2f}{unit}</span>"),
                font=dict(size=15, color="#1E293B"), x=0,
            ),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9",
                       tickfont=dict(color="#94A3B8", size=11), linecolor="#E2E8F0"),
            yaxis=dict(
                title=dict(text=label, font=dict(color="#64748B", size=12)),
                showgrid=True, gridcolor="#F1F5F9",
                tickfont=dict(color="#94A3B8", size=11), linecolor="#E2E8F0",
            ),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=60, r=30, t=50, b=40),
            height=260, showlegend=False, hovermode="x unified",
        )
        charts.append(html.Div(
            style={
                "background": "white", "borderRadius": "16px", "marginBottom": "20px",
                "boxShadow": "0 1px 3px rgba(0,0,0,0.08)", "overflow": "hidden",
                "borderLeft": f"4px solid {color}",
            },
            children=[dcc.Graph(figure=fig, config={"displayModeBar": False})],
        ))
    return charts


# ── Callback: ตารางรายวัน (ทุก column) ──────────────────────
@app.callback(
    Output("date-table", "children"),
    Output("record-count", "children"),
    Input("date-picker", "value"),
)
def update_table(selected_date):
    filtered = df[df["date"] == pd.to_datetime(selected_date).date()].copy()
    filtered = filtered[TABLE_COLS].reset_index(drop=True)
    filtered["timestamp"] = filtered["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    count_text = f"พบ {len(filtered):,} รายการ ในวันที่ {selected_date}"

    table = dash_table.DataTable(
        data=filtered.to_dict("records"),
        columns=[{"name": c, "id": c} for c in filtered.columns],
        page_size=25,
        sort_action="native",
        filter_action="native",
        style_table={"overflowX": "auto"},
        style_header={
            "backgroundColor": "#F8FAFC", "fontWeight": "700",
            "fontSize": "13px", "color": "#374151",
            "border": "1px solid #E2E8F0", "padding": "10px 14px",
        },
        style_cell={
            "fontSize": "13px", "color": "#334155",
            "border": "1px solid #F1F5F9", "padding": "9px 14px",
            "fontFamily": "Inter, sans-serif", "whiteSpace": "normal",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#F8FAFC"},
        ],
    )
    return table, count_text


if __name__ == "__main__":
    app.run(debug=True)
