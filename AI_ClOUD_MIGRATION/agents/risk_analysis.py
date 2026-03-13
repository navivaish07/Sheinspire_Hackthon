"""
Module 4 — Risk Analysis Engine
Calculates migration risk score for each service.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from agents.dependency_graph import build_dependency_graph, get_downstream_dependencies
from agents.service_discovery import discover_dependencies
import os


CRITICALITY_WEIGHTS = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.3}


def load_telemetry(telemetry_path: str = None) -> pd.DataFrame:
    """Load telemetry data."""
    if telemetry_path is None:
        telemetry_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "telemetry_data.csv"
        )
    return pd.read_csv(telemetry_path)


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Auto-detect and normalize column names to work with any dataset format.
    Handles variations like: service_name, Service, service, service_id, etc.
    """
    df = df.copy()
    col_mapping = {}
    
    # Standard column names we expect
    expected_cols = {
        "service_name": ["service_name", "service", "Service", "service_id", "ServiceName"],
        "request_volume": ["request_volume", "volume", "requests", "request_count", "rps"],
        "request_latency": ["request_latency", "latency", "response_time", "avg_latency", "latency_ms"],
        "cpu_usage": ["cpu_usage", "cpu", "cpu_percent", "cpu_usage_percent", "cpu_util"],
        "memory_usage": ["memory_usage", "memory", "mem", "memory_percent", "memory_mb"],
        "error_rate": ["error_rate", "errors", "failure_rate", "error_percent", "failure_rate_percent"],
        "service_criticality": ["service_criticality", "criticality", "priority", "importance", "tier"],
    }
    
    # Try to find matches in actual columns (case-insensitive)
    actual_cols_lower = {col.lower(): col for col in df.columns}
    
    for standard_col, variations in expected_cols.items():
        for variation in variations:
            if variation.lower() in actual_cols_lower:
                col_mapping[standard_col] = actual_cols_lower[variation.lower()]
                break
    
    # Rename columns
    reverse_mapping = {v: k for k, v in col_mapping.items()}
    df = df.rename(columns=reverse_mapping)
    
    # Add missing columns with defaults if they don't exist
    if "service_name" not in df.columns:
        if df.shape[0] > 0:
            df["service_name"] = [f"Service_{i}" for i in range(len(df))]
        else:
            df["service_name"] = []
    
    defaults = {
        "request_volume": df["request_volume"].mean() if "request_volume" in df.columns else 1000,
        "request_latency": df["request_latency"].mean() if "request_latency" in df.columns else 100,
        "cpu_usage": df["cpu_usage"].mean() if "cpu_usage" in df.columns else 50,
        "memory_usage": df["memory_usage"].mean() if "memory_usage" in df.columns else 60,
        "error_rate": df["error_rate"].mean() if "error_rate" in df.columns else 0.01,
        "service_criticality": "medium",
    }
    
    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            # Fill NaN values with defaults
            df[col] = df[col].fillna(default_val)
    
    return df


def calculate_risk_scores(telemetry_path: str = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Calculate migration risk score for each service.
    Generalized to work with any dataset format.
    Risk factors: dependencies, request volume, latency, CPU, error rate, criticality
    """
    if df is None:
        df = load_telemetry(telemetry_path)
    
    # Normalize column names to handle different dataset formats
    df = normalize_column_names(df)
    
    G = build_dependency_graph(discover_dependencies(df=df))
    
    # Aggregate metrics per service
    agg = df.groupby("service_name").agg({
        "request_volume": "mean",
        "request_latency": "mean",
        "cpu_usage": "mean",
        "memory_usage": "mean",
        "error_rate": "mean",
        "service_criticality": "first",
    }).reset_index()
    
    results = []
    for _, row in agg.iterrows():
        service = row["service_name"]
        
        # Dependency count (downstream = services this one calls)
        dep_count = len(get_downstream_dependencies(G, service))
        in_degree = G.in_degree(service)
        total_deps = dep_count + in_degree
        
        # Normalize factors (0-1 scale) with safe divisions
        dep_score = min(total_deps / 10, 1.0)
        volume_score = min(max(row["request_volume"], 0) / 5000, 1.0)
        latency_score = min(max(row["request_latency"], 0) / 500, 1.0)
        cpu_score = min(max(row["cpu_usage"], 0) / 80, 1.0)
        error_score = min(max(row["error_rate"], 0) * 50, 1.0)
        
        # Handle criticality with safe dict get
        crit_str = str(row["service_criticality"]).lower() if pd.notna(row["service_criticality"]) else "medium"
        crit_score = CRITICALITY_WEIGHTS.get(crit_str, 0.5)
        
        # Weighted risk score (0-100)
        weights = {"dep": 0.25, "volume": 0.15, "latency": 0.15, "cpu": 0.1, "error": 0.2, "crit": 0.15}
        risk_score = (
            dep_score * weights["dep"] * 100 +
            volume_score * weights["volume"] * 100 +
            latency_score * weights["latency"] * 100 +
            cpu_score * weights["cpu"] * 100 +
            error_score * weights["error"] * 100 +
            crit_score * weights["crit"] * 100
        )
        risk_score = min(100, round(risk_score, 1))
        
        if risk_score >= 70:
            risk_level = "High"
        elif risk_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        results.append({
            "service": service,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "dependency_count": total_deps,
            "request_volume": round(max(row["request_volume"], 0), 0),
            "avg_latency_ms": round(max(row["request_latency"], 0), 2),
            "cpu_usage_pct": round(min(max(row["cpu_usage"], 0), 100), 2),
            "error_rate": round(min(max(row["error_rate"], 0), 1), 4),
            "criticality": crit_str,
        })
    
    return pd.DataFrame(results).sort_values("risk_score", ascending=False)


if __name__ == "__main__":
    df = calculate_risk_scores()
    print(df[["service", "risk_score", "risk_level"]].to_string(index=False))
