"""
Module 6 — Migration Simulation Engine
Simulates different migration strategies and estimates downtime/risk.
"""

import pandas as pd
from typing import List, Dict
from agents.migration_planner import get_migration_order
from agents.risk_analysis import calculate_risk_scores
import random


def simulate_strategy(
    strategy_name: str,
    batch_size: int = 3,
    risk_df: pd.DataFrame = None
) -> Dict:
    """
    Simulate a migration strategy.
    Returns downtime estimate, risk level, and details.
    """
    if risk_df is None:
        risk_df = calculate_risk_scores()
    
    plan = get_migration_order(strategy=strategy_name, risk_df=risk_df)
    
    # Simulate downtime based on risk and batch size
    total_risk = sum(p["risk_score"] for p in plan)
    avg_risk = total_risk / len(plan) if plan else 0
    
    # Downtime model: higher risk + larger batches = more downtime
    base_downtime = 0.5 + (avg_risk / 100) * 3
    batch_penalty = (batch_size - 1) * 0.5
    downtime_pct = min(15, base_downtime + batch_penalty + random.uniform(-0.5, 1.5))
    
    if downtime_pct < 3:
        risk_level = "Low"
    elif downtime_pct < 8:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    return {
        "strategy": strategy_name,
        "downtime_pct": round(downtime_pct, 2),
        "risk_level": risk_level,
        "batch_size": batch_size,
        "total_services": len(plan),
        "avg_risk_score": round(avg_risk, 1),
        "plan": plan,
    }


def compare_strategies(risk_df: pd.DataFrame = None) -> List[Dict]:
    """Compare multiple migration strategies."""
    if risk_df is None:
        risk_df = calculate_risk_scores()
    
    strategies = [
        ("dependency_first", 2),
        ("dependency_first", 4),
        ("risk_first", 2),
        ("risk_first", 5),
    ]
    
    results = []
    for strat, batch in strategies:
        name = f"Plan {chr(65 + len(results))}: {strat.replace('_', ' ').title()} (batch={batch})"
        sim = simulate_strategy(strat, batch_size=batch, risk_df=risk_df)
        sim["strategy"] = name
        results.append(sim)
    
    return results


def get_recommended_plan(simulations: List[Dict] = None) -> Dict:
    """Recommend the safest migration plan."""
    if simulations is None:
        simulations = compare_strategies()
    
    # Score: prefer low downtime, low risk
    def score(s):
        dt = s["downtime_pct"]
        r = 1 if s["risk_level"] == "Low" else (2 if s["risk_level"] == "Medium" else 3)
        return dt + r * 5
    
    best = min(simulations, key=score)
    return best


def create_batch_plan(plan: List[Dict], batch_size: int) -> List[Dict]:
    """
    Create phase-wise batch plan for migration.
    Groups services into batches based on batch size and strategy.
    
    Args:
        plan: Migration plan from get_migration_order
        batch_size: Number of services per batch/phase
    
    Returns:
        List of phases with batched services
    """
    phases = []
    phase_num = 1
    
    for i in range(0, len(plan), batch_size):
        batch_services = plan[i:i+batch_size]
        service_names = [s["service"] for s in batch_services]
        service_risks = [s["risk_score"] for s in batch_services]
        
        avg_risk = sum(service_risks) / len(service_risks) if service_risks else 0
        
        phases.append({
            "phase": phase_num,
            "services": service_names,
            "service_count": len(service_names),
            "avg_risk": round(avg_risk, 1),
            "services_str": ", ".join(service_names)
        })
        phase_num += 1
    
    return phases


def get_detailed_recommendation(best_plan: Dict) -> Dict:
    """
    Get detailed recommendation with batch-wise phases.
    
    Args:
        best_plan: A simulation result from compare_strategies
        
    Returns:
        Enhanced plan with phase-wise batch details
    """
    batch_plan = create_batch_plan(best_plan["plan"], best_plan["batch_size"])
    
    enhanced_plan = best_plan.copy()
    enhanced_plan["phases"] = batch_plan
    enhanced_plan["total_phases"] = len(batch_plan)
    
    return enhanced_plan


if __name__ == "__main__":
    sims = compare_strategies()
    for s in sims:
        print(f"{s['strategy']}: Downtime={s['downtime_pct']}%, Risk={s['risk_level']}")
    
    best = get_recommended_plan(sims)
    print("\nRecommended:", best["strategy"])
    
    detailed = get_detailed_recommendation(best)
    print("\nPhase-wise Migration Plan:")
    for phase in detailed["phases"]:
        print(f"  Phase {phase['phase']}: {phase['services_str']}")
