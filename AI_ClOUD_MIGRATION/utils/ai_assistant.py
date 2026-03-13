"""
Module 8 — AI Migration Assistant
Answers questions using system data.
"""

from typing import Optional
import pandas as pd
from agents.risk_analysis import calculate_risk_scores
from agents.migration_planner import get_migration_order, format_migration_plan
from simulation.migration_simulator import compare_strategies, get_recommended_plan
from agents.service_discovery import discover_dependencies, format_dependency_output
from cost.cost_estimator import estimate_cloud_cost, get_total_estimated_cost


def get_context_data() -> dict:
    """Load all context data for the assistant."""
    risk_df = calculate_risk_scores()
    plan = get_migration_order(risk_df=risk_df)
    sims = compare_strategies()
    recommended = get_recommended_plan(sims)
    deps = discover_dependencies()
    cost_df = estimate_cloud_cost()
    total_cost = get_total_estimated_cost(cost_df)
    
    highest_risk = risk_df.iloc[0] if len(risk_df) > 0 else None
    first_migrate = plan[0]["service"] if plan else None
    
    return {
        "risk_df": risk_df,
        "migration_plan": plan,
        "simulations": sims,
        "recommended_plan": recommended,
        "dependencies": deps,
        "cost_df": cost_df,
        "total_cost": total_cost,
        "highest_risk_service": highest_risk["service"] if highest_risk is not None else None,
        "highest_risk_score": highest_risk["risk_score"] if highest_risk is not None else 0,
        "first_to_migrate": first_migrate,
        "safest_strategy": recommended["strategy"],
        "safest_downtime": recommended["downtime_pct"],
        "safest_risk": recommended["risk_level"],
    }


def answer_question(question: str, context: dict = None) -> str:
    """
    Answer user questions using system data.
    """
    if context is None:
        context = get_context_data()
    
    q = question.lower().strip()
    
    if "first" in q and ("migrate" in q or "order" in q):
        return f"**{context['first_to_migrate']}** should migrate first. " \
               f"Our AI planner recommends migrating services with fewer dependencies and lower risk first. " \
               f"Here's the full order:\n\n{format_migration_plan(context['migration_plan'][:5])}\n\n..."
    
    if "highest risk" in q or "most risk" in q:
        return f"**{context['highest_risk_service']}** has the highest migration risk (score: {context['highest_risk_score']}). " \
               f"Consider migrating it later in the plan after dependent services are stabilized."
    
    if "safest" in q and ("strategy" in q or "plan" in q):
        return f"The safest migration strategy is **{context['safest_strategy']}** with " \
               f"estimated downtime of {context['safest_downtime']}% and {context['safest_risk']} risk level."
    
    if "dependencies" in q or "depend" in q:
        return f"Discovered dependencies:\n\n{format_dependency_output(context['dependencies'][:15])}\n\n..."
    
    if "cost" in q:
        return f"Total estimated monthly cloud cost: **${context['total_cost']:.2f}**. " \
               f"Top cost services: " + ", ".join(
            context['cost_df'].head(5)["service"].tolist()
        ) + "."
    
    if "downtime" in q:
        lines = [f"- {s['strategy']}: {s['downtime_pct']}% downtime ({s['risk_level']} risk)" 
                 for s in context['simulations']]
        return "Migration strategy comparison:\n\n" + "\n".join(lines)
    
    return (
        "I can help with: migration order, risk analysis, safest strategy, "
        "dependencies, cost estimation, and downtime comparison. Try asking: "
        "'Which service should migrate first?' or 'What migration strategy is safest?'"
    )
