"""
Module 1 — Synthetic Telemetry Data Generator
Generates simulated enterprise telemetry data for microservices.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Service definitions with realistic relationships
SERVICES = [
    {"id": "svc_001", "name": "API Gateway", "criticality": "critical", "env": "production"},
    {"id": "svc_002", "name": "Auth Service", "criticality": "critical", "env": "production"},
    {"id": "svc_003", "name": "User Service", "criticality": "high", "env": "production"},
    {"id": "svc_004", "name": "Order Service", "criticality": "critical", "env": "production"},
    {"id": "svc_005", "name": "Payment Service", "criticality": "critical", "env": "production"},
    {"id": "svc_006", "name": "Notification Service", "criticality": "medium", "env": "production"},
    {"id": "svc_007", "name": "Inventory Service", "criticality": "high", "env": "production"},
    {"id": "svc_008", "name": "Catalog Service", "criticality": "high", "env": "production"},
    {"id": "svc_009", "name": "Search Service", "criticality": "medium", "env": "production"},
    {"id": "svc_010", "name": "Analytics Service", "criticality": "low", "env": "production"},
    {"id": "svc_011", "name": "Logging Service", "criticality": "medium", "env": "production"},
    {"id": "svc_012", "name": "Config Service", "criticality": "high", "env": "production"},
    {"id": "svc_013", "name": "Cache Service", "criticality": "high", "env": "production"},
    {"id": "svc_014", "name": "Email Service", "criticality": "medium", "env": "production"},
    {"id": "svc_015", "name": "Report Service", "criticality": "low", "env": "production"},
    {"id": "svc_016", "name": "Billing Service", "criticality": "high", "env": "production"},
    {"id": "svc_017", "name": "Recommendation Service", "criticality": "medium", "env": "production"},
    {"id": "svc_018", "name": "Session Service", "criticality": "high", "env": "production"},
]

# Dependency edges: source -> target
DEPENDENCIES = [
    ("API Gateway", "Auth Service"),
    ("API Gateway", "User Service"),
    ("API Gateway", "Order Service"),
    ("API Gateway", "Search Service"),
    ("Auth Service", "User Service"),
    ("Auth Service", "Session Service"),
    ("Order Service", "Payment Service"),
    ("Order Service", "Inventory Service"),
    ("Order Service", "Notification Service"),
    ("Payment Service", "Notification Service"),
    ("Payment Service", "Billing Service"),
    ("Inventory Service", "Catalog Service"),
    ("Catalog Service", "Search Service"),
    ("Search Service", "Recommendation Service"),
    ("User Service", "Analytics Service"),
    ("Order Service", "Analytics Service"),
    ("API Gateway", "Logging Service"),
    ("Auth Service", "Config Service"),
    ("Order Service", "Config Service"),
    ("User Service", "Config Service"),
    ("Catalog Service", "Cache Service"),
    ("Search Service", "Cache Service"),
    ("Notification Service", "Email Service"),
    ("Billing Service", "Report Service"),
    ("Analytics Service", "Report Service"),
]


def generate_telemetry_data(num_days: int = 7, records_per_edge: int = 50) -> pd.DataFrame:
    """Generate synthetic telemetry data for all service dependencies."""
    records = []
    base_time = datetime.now() - timedelta(days=num_days)
    
    criticality_weights = {"critical": 1.0, "high": 0.8, "medium": 0.6, "low": 0.4}
    
    for source_name, target_name in DEPENDENCIES:
        source_svc = next(s for s in SERVICES if s["name"] == source_name)
        target_svc = next(s for s in SERVICES if s["name"] == target_name)
        
        for _ in range(records_per_edge):
            # Add variance across time
            day_offset = random.randint(0, num_days - 1)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            timestamp = base_time + timedelta(days=day_offset, hours=hour, minutes=minute)
            
            # Realistic metrics based on criticality
            crit_weight = criticality_weights.get(source_svc["criticality"], 0.5)
            base_volume = random.randint(100, 10000) * crit_weight
            request_volume = int(max(10, base_volume + random.gauss(0, 500)))
            request_latency = random.uniform(20, 500) * (1 + 0.2 * (1 - crit_weight))
            cpu_usage = random.uniform(10, 85) * crit_weight
            memory_usage = random.uniform(128, 2048)
            error_rate = random.uniform(0.001, 0.05)
            
            records.append({
                "service_id": target_svc["id"],
                "service_name": target_svc["name"],
                "source_service": source_name,
                "target_service": target_name,
                "request_latency": round(request_latency, 2),
                "request_volume": request_volume,
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": round(memory_usage, 0),
                "error_rate": round(error_rate, 4),
                "service_criticality": target_svc["criticality"],
                "environment": target_svc["env"],
                "timestamp": timestamp.isoformat(),
            })
    
    df = pd.DataFrame(records)
    return df.sort_values("timestamp").reset_index(drop=True)


def main():
    """Generate and save telemetry dataset."""
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "telemetry_data.csv")
    
    df = generate_telemetry_data(num_days=14, records_per_edge=80)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} telemetry records -> {output_path}")
    return df


if __name__ == "__main__":
    main()
