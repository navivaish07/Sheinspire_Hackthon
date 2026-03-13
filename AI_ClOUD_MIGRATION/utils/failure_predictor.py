"""
Bonus: Failure Prediction Model using Machine Learning
Predicts likelihood of migration failure per service.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
import pickle


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare features for failure prediction."""
    agg = df.groupby("service_name").agg({
        "request_volume": "mean",
        "request_latency": "mean",
        "cpu_usage": "mean",
        "memory_usage": "mean",
        "error_rate": "mean",
    }).reset_index()
    
    le = LabelEncoder()
    agg["service_encoded"] = le.fit_transform(agg["service_name"])
    
    return agg


def train_failure_model(telemetry_path: str = None, df: pd.DataFrame = None) -> tuple:
    """
    Train a simple failure prediction model.
    Uses synthetic labels based on error_rate and latency for demo.
    """
    if df is None:
        if telemetry_path is None:
            telemetry_path = os.path.join(
                os.path.dirname(__file__), "..", "data", "telemetry_data.csv"
            )
        df = pd.read_csv(telemetry_path)
    
    agg = df.groupby("service_name").agg({
        "request_volume": "mean",
        "request_latency": "mean",
        "cpu_usage": "mean",
        "memory_usage": "mean",
        "error_rate": "mean",
    }).reset_index()
    
    # Synthetic target: high failure risk if error_rate > 0.02 or latency > 300
    agg["failure_risk"] = (
        (agg["error_rate"] > 0.02).astype(int) |
        (agg["request_latency"] > 300).astype(int)
    )
    
    features = ["request_volume", "request_latency", "cpu_usage", "memory_usage", "error_rate"]
    X = agg[features]
    y = agg["failure_risk"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Get probability predictions for all services
    X_all = agg[features]
    try:
        probs_raw = model.predict_proba(X_all)
        n_cols = probs_raw.shape[1]
        if n_cols >= 2:
            idx = list(model.classes_).index(1) if 1 in model.classes_ else 0
            probs = probs_raw[:, min(idx, n_cols - 1)]
        else:
            probs = probs_raw[:, 0] if 1 in model.classes_ else 1 - probs_raw[:, 0]
    except (IndexError, ValueError):
        # Fallback: use simple heuristic when ML fails (e.g., single-class training)
        probs = np.clip((agg["error_rate"] * 50 + agg["request_latency"] / 500) / 2, 0, 1)
    
    result = pd.DataFrame({
        "service": agg["service_name"],
        "failure_probability": np.round(probs, 4),
        "predicted_risk": ["High" if p > 0.5 else "Low" for p in probs],
    })
    
    return result, model


def get_failure_predictions(df: pd.DataFrame = None) -> pd.DataFrame:
    """Get failure predictions for all services."""
    result, _ = train_failure_model(df=df)
    return result.sort_values("failure_probability", ascending=False)
