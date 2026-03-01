import pandas as pd
import numpy as np

# Anomaly Detection 

def detect_anomalies(
    df: pd.DataFrame,
    window: int = 30,
    n_std: float = 3.0,
) -> pd.DataFrame:
    out = df.copy()

    mapping = {
        "pH": "pH_anomaly",
        "TDS": "TDS_anomaly",
        "water_temp": "temp_anomaly",
    }

    for col, flag_col in mapping.items():
        if col not in out.columns:
            out[flag_col] = False
            continue

        rolling_mean = out[col].rolling(window=window, min_periods=1).mean()
        rolling_std = out[col].rolling(window=window, min_periods=1).std().fillna(0)

        deviation = (out[col] - rolling_mean).abs()
        out[flag_col] = deviation > (n_std * rolling_std)

    return out


# Health Score 

def health_score(df: pd.DataFrame) -> dict:
    weights = {"pH": 0.40, "TDS": 0.30, "water_temp": 0.30}
    stabilities = {}

    for col, w in weights.items():
        if col not in df.columns or df[col].dropna().empty:
            stabilities[col] = 100.0  # no data → assume stable
            continue

        mean_val = df[col].mean()
        std_val = df[col].std()

        if mean_val == 0:
            cv = 0.0
        else:
            cv = abs(std_val / mean_val)

        # Map CV to 0–100 stability score.
        # CV of 0 → 100 (perfect), CV ≥ 0.5 → 0 (unstable).
        stability = max(0.0, min(100.0, (1 - cv / 0.5) * 100))
        stabilities[col] = stability

    score = round(
        stabilities.get("pH", 100) * weights["pH"]
        + stabilities.get("TDS", 100) * weights["TDS"]
        + stabilities.get("water_temp", 100) * weights["water_temp"],
        1,
    )

    if score >= 80:
        status = "Healthy"
    elif score >= 50:
        status = "Warning"
    else:
        status = "Critical"

    return {
        "score": score,
        "system_status": status,
        "ph_stability": round(stabilities.get("pH", 100), 1),
        "tds_stability": round(stabilities.get("TDS", 100), 1),
        "temp_stability": round(stabilities.get("water_temp", 100), 1),
    }


# AI Insight Generator

def generate_insight(df: pd.DataFrame, health: dict, anomaly_count: int) -> str:
    status = health["system_status"]
    score = health["score"]
    lines = []

    # Overall status
    if status == "Healthy":
        lines.append(
            f"System is operating within normal parameters with a health score of {score}/100."
        )
    elif status == "Warning":
        lines.append(
            f"⚠️ System health is at {score}/100 — some metrics are showing instability."
        )
    else:
        lines.append(
            f"🚨 Critical alert — system health has dropped to {score}/100. Immediate attention recommended."
        )

    # Anomaly summary
    if anomaly_count == 0:
        lines.append("No anomalies detected in the selected time range.")
    elif anomaly_count <= 5:
        lines.append(
            f"{anomaly_count} anomalies detected. Review the flagged events below."
        )
    else:
        lines.append(
            f"{anomaly_count} anomalies detected — elevated sensor deviations observed. "
            "Investigate environmental changes or sensor calibration."
        )

    # Per-metric notes
    if "pH" in df.columns and not df["pH"].dropna().empty:
        ph_mean = df["pH"].mean()
        if ph_mean < 5.5:
            lines.append(f"Average pH ({ph_mean:.2f}) is below optimal range — consider adjusting pH up.")
        elif ph_mean > 7.5:
            lines.append(f"Average pH ({ph_mean:.2f}) is above optimal range — consider adjusting pH down.")
        else:
            lines.append(f"pH levels averaging {ph_mean:.2f} — within optimal hydroponic range.")

    if "water_temp" in df.columns and not df["water_temp"].dropna().empty:
        temp_mean = df["water_temp"].mean()
        if temp_mean < 18:
            lines.append(f"Water temperature ({temp_mean:.1f}°C) is below recommended minimum of 18°C.")
        elif temp_mean > 26:
            lines.append(f"Water temperature ({temp_mean:.1f}°C) is above recommended maximum of 26°C.")

    return " ".join(lines)
