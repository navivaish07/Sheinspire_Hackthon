"""
Module 2 — Service Discovery Agent
Automatically detects dependencies between services using telemetry data.
"""

import pandas as pd
from typing import List, Tuple
import os


def discover_dependencies(telemetry_path: str = None, df: pd.DataFrame = None) -> List[Tuple[str, str]]:
    """
    Detect service dependencies from telemetry data.
    Returns list of (source_service, target_service) tuples.
    """
    if df is None:
        if telemetry_path is None:
            telemetry_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "telemetry_data.csv"
            )
        df = pd.read_csv(telemetry_path)
    
    # Extract unique source -> target pairs from telemetry
    edges = df[["source_service", "target_service"]].drop_duplicates()
    dependencies = list(zip(edges["source_service"], edges["target_service"]))
    
    return dependencies


def format_dependency_output(dependencies: List[Tuple[str, str]]) -> str:
    """Format dependencies for display."""
    lines = [f"{src} → {tgt}" for src, tgt in dependencies]
    return "\n".join(lines)


def get_dependency_summary(dependencies: List[Tuple[str, str]]) -> dict:
    """Get summary statistics of discovered dependencies."""
    sources = set(d[0] for d in dependencies)
    targets = set(d[1] for d in dependencies)
    all_services = sources | targets
    
    return {
        "total_dependencies": len(dependencies),
        "unique_services": len(all_services),
        "entry_points": list(sources - targets),
        "leaf_services": list(targets - sources),
    }


if __name__ == "__main__":
    deps = discover_dependencies()
    print("Discovered Dependencies:")
    print(format_dependency_output(deps))
    print("\nSummary:", get_dependency_summary(deps))
