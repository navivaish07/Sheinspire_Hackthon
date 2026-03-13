"""
Utility to load and normalize external telemetry data.
Supports multiple CSV formats for upload.
"""

import pandas as pd
from typing import Optional, Tuple

# Expected internal columns
REQUIRED_COLUMNS = [
    "service_name", "source_service", "target_service",
    "request_volume", "request_latency", "cpu_usage", "memory_usage",
    "error_rate", "service_criticality"
]


def normalize_external_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize external CSV to internal telemetry format.
    Supports formats like cloud_migration_dataset_large.csv:
    service_id, service_name, depends_on, cpu_usage, memory_usage, request_rate, latency, error_rate, criticality
    """
    df = df.copy()

    # Column mappings: external -> internal
    col_map = {
        "request_rate": "request_volume",
        "latency": "request_latency",
        "criticality": "service_criticality",
    }
    for old, new in col_map.items():
        if old in df.columns and new not in df.columns:
            df[new] = df[old]

    # Build source_service, target_service from service_name + depends_on
    if "source_service" not in df.columns and "service_name" in df.columns:
        df["source_service"] = df["service_name"]
    if "target_service" not in df.columns and "depends_on" in df.columns:
        df["target_service"] = df["depends_on"].astype(str)
        # Filter out None/NaN dependencies
        df = df[~df["target_service"].isin(["None", "nan", ""])].copy()
        df["target_service"] = df["target_service"].str.strip()
    elif "target_service" not in df.columns and "source_service" in df.columns:
        df["target_service"] = df["source_service"]  # fallback

    # Ensure service_name exists (use source or first service column)
    if "service_name" not in df.columns and "source_service" in df.columns:
        df["service_name"] = df["source_service"]

    # Fill missing optional columns with defaults
    defaults = {
        "request_volume": 1000,
        "request_latency": 100,
        "cpu_usage": 50,
        "memory_usage": 512,
        "error_rate": 0.01,
        "service_criticality": "medium",
        "environment": "production",
    }
    for col, default in defaults.items():
        if col not in df.columns:
            df[col] = default
        elif col == "service_criticality" and df[col].dtype == object:
            df[col] = df[col].fillna("medium").str.lower()

    # Ensure numeric types
    for col in ["request_volume", "request_latency", "cpu_usage", "memory_usage", "error_rate"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(defaults.get(col, 0))

    return df


def validate_uploaded_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate uploaded CSV has required structure. Returns (valid, message)."""
    if df is None or df.empty:
        return False, "File is empty."
    if len(df) < 2:
        return False, "Need at least 2 rows of data."
    # Need either (source_service, target_service) or (service_name, depends_on)
    has_deps = ("source_service" in df.columns and "target_service" in df.columns) or (
        "service_name" in df.columns and "depends_on" in df.columns
    )
    if not has_deps:
        return False, "CSV must have (service_name, depends_on) or (source_service, target_service)."
    return True, "OK"
