"""
Module 5 — AI Migration Planner
Recommends optimal migration order using graph algorithms.
"""

import networkx as nx
from typing import List, Dict
from agents.dependency_graph import build_dependency_graph
from agents.risk_analysis import calculate_risk_scores
import pandas as pd


def get_migration_order(
    strategy: str = "dependency_first",
    risk_df: pd.DataFrame = None
) -> List[Dict]:
    """
    Recommend migration order.
    Rules: fewer dependencies first, critical services later, minimize downtime.
    """
    G = build_dependency_graph()
    
    if risk_df is None:
        risk_df = calculate_risk_scores()
    
    risk_map = dict(zip(risk_df["service"], risk_df["risk_score"]))
    crit_map = dict(zip(risk_df["service"], risk_df["criticality"]))
    
    if strategy == "dependency_first":
        # Topological sort: leaf nodes first (no outgoing deps)
        # Reverse to get migration order: migrate leaves first
        try:
            topo_order = list(nx.topological_sort(G))
            # Leaves (no outgoing) should go first - reverse topo gives us
            # nodes that have no dependents first
            rev_topo = list(reversed(topo_order))
        except nx.NetworkXError:
            rev_topo = list(G.nodes())
        
        # Sort by: 1) fewer downstream deps first, 2) lower risk, 3) lower criticality
        def sort_key(svc):
            out_deg = G.out_degree(svc)
            risk = risk_map.get(svc, 50)
            crit_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            crit = crit_order.get(crit_map.get(svc, "medium"), 1)
            return (out_deg, risk, crit)
        
        ordered = sorted(rev_topo, key=sort_key)
        
    elif strategy == "risk_first":
        # Migrate lowest risk first
        ordered = risk_df.sort_values("risk_score")["service"].tolist()
    else:
        ordered = list(G.nodes())
    
    result = []
    for i, svc in enumerate(ordered, 1):
        result.append({
            "step": i,
            "service": svc,
            "risk_score": risk_map.get(svc, 0),
            "criticality": crit_map.get(svc, "medium"),
        })
    
    return result


def format_migration_plan(plan: List[Dict]) -> str:
    """Format migration plan for display."""
    lines = [f"Step {p['step']} → {p['service']}" for p in plan]
    return "\n".join(lines)


if __name__ == "__main__":
    plan = get_migration_order()
    print("Recommended Migration Order:")
    print(format_migration_plan(plan))
