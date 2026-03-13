"""
Module 7 — Cloud Cost Estimation
Estimates expected cloud cost after migration.
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import os

# Pricing assumptions (simplified - can be customized)
CPU_COST_PER_VCPU_HOUR = 0.05
MEMORY_COST_PER_GB_HOUR = 0.01
REQUEST_COST_PER_1K = 0.0001
HOURS_PER_MONTH = 730


def load_telemetry(telemetry_path: str = None) -> pd.DataFrame:
    """Load telemetry data."""
    if telemetry_path is None:
        telemetry_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "telemetry_data.csv"
        )
    return pd.read_csv(telemetry_path)


def estimate_cloud_cost(telemetry_path: str = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """
    Estimate monthly cloud cost per service.
    Inputs: CPU usage, memory usage, request volume
    """
    if df is None:
        df = load_telemetry(telemetry_path)
    
    agg = df.groupby("service_name").agg({
        "cpu_usage": "mean",
        "memory_usage": "mean",
        "request_volume": "sum",
    }).reset_index()
    
    results = []
    for _, row in agg.iterrows():
        # Convert to vCPU (assume 100% = 1 vCPU)
        vcpus = max(0.25, row["cpu_usage"] / 100)
        memory_gb = max(0.5, row["memory_usage"] / 1024)
        requests = row["request_volume"] * 30  # Approximate monthly
        
        cpu_cost = vcpus * CPU_COST_PER_VCPU_HOUR * HOURS_PER_MONTH
        mem_cost = memory_gb * MEMORY_COST_PER_GB_HOUR * HOURS_PER_MONTH
        req_cost = (requests / 1000) * REQUEST_COST_PER_1K
        
        total = cpu_cost + mem_cost + req_cost
        
        results.append({
            "service": row["service_name"],
            "estimated_monthly_cost_usd": round(total, 2),
            "cpu_cost": round(cpu_cost, 2),
            "memory_cost": round(mem_cost, 2),
            "request_cost": round(req_cost, 2),
            "vcpus": round(vcpus, 2),
            "memory_gb": round(memory_gb, 2),
        })
    
    return pd.DataFrame(results).sort_values("estimated_monthly_cost_usd", ascending=False)


def get_total_estimated_cost(cost_df: pd.DataFrame = None) -> float:
    """Get total estimated monthly cost."""
    if cost_df is None:
        cost_df = estimate_cloud_cost()
    return cost_df["estimated_monthly_cost_usd"].sum()


if __name__ == "__main__":
    df = estimate_cloud_cost()
    print(df[["service", "estimated_monthly_cost_usd"]].to_string(index=False))
    print(f"\nTotal: ${get_total_estimated_cost(df):.2f}/month")
