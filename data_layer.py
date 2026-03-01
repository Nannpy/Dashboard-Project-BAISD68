import pandas as pd
import numpy as np


def clean_data(filepath: str) -> pd.DataFrame:

    df = pd.read_csv(filepath)

    # Timestamp handling 
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df.dropna(subset=["timestamp"], inplace=True)
    df.sort_values("timestamp", inplace=True)
    df.drop_duplicates(subset=["timestamp"], keep="first", inplace=True)

    # Numeric coercion
    sensor_cols = ["pH", "TDS", "water_temp"]
    for col in sensor_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Time-based interpolation
    df.set_index("timestamp", inplace=True)
    df[sensor_cols] = df[sensor_cols].interpolate(method="time")

    # Outlier removal (pH outside 3–10) 
    df = df[(df["pH"] >= 3) & (df["pH"] <= 10)]

    # Drop non-sensor helper columns to keep things clean 
    keep_cols = [c for c in sensor_cols if c in df.columns]
    extra_cols = [c for c in df.columns if c not in keep_cols]
    # Keep all columns — caller can select what they need

    df = df.reset_index()
    df.set_index("timestamp", inplace=True)

    return df


def resample_data(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    if frequency == "raw":
        return df

    freq_map = {
        "5min": "5min",
        "15min": "15min",
        "1H": "1h",
    }
    rule = freq_map.get(frequency, frequency)

    sensor_cols = ["pH", "TDS", "water_temp"]
    available = [c for c in sensor_cols if c in df.columns]
    resampled = df[available].resample(rule).mean().dropna(how="all")

    return resampled
