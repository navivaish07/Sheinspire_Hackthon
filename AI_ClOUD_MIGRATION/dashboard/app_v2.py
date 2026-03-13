"""
Module 9 — Interactive Streamlit Dashboard
AI Cloud Migration Copilot - Hackathon Demo

Version 2 - Enhanced with:
- Improved chart titles
- Hover tooltips with service details
- Section headers for better layout
- AI Insights summary box
"""

import sys
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime

# Import project modules
from data.telemetry_generator import generate_telemetry_data
from agents.service_discovery import discover_dependencies, format_dependency_output
from agents.dependency_graph import build_dependency_graph, graph_to_plotly_data, get_graph_metrics
from agents.risk_analysis import calculate_risk_scores
from agents.migration_planner import get_migration_order, format_migration_plan
from simulation.migration_simulator import compare_strategies, get_recommended_plan, get_detailed_recommendation
from cost.cost_estimator import estimate_cloud_cost, get_total_estimated_cost
from utils.failure_predictor import get_failure_predictions
from utils.ai_assistant import answer_question, get_context_data
from utils.data_loader import normalize_external_csv, validate_uploaded_data

# Add PyVis and streamlit components imports
from pyvis.network import Network
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="AI Cloud Migration Copilot",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Professional Theme - Datadog/Dynatrace Inspired
st.markdown(
    """
<style>
    /* ========================================
       GLOBAL STYLES & FONTS
    ======================================== */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(180deg, #0f1419 0%, #13171c 50%, #0d1117 100%);
        color: #e6edf3;
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        min-height: 100vh;
    }
    
    /* Animated subtle background */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 20%, rgba(56, 139, 253, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(163, 113, 247, 0.04) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(6, 182, 212, 0.03) 0%, transparent 60%);
        pointer-events: none;
        z-index: -1;
    }

    /* ========================================
       HERO SECTION
    ======================================== */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1rem;
        position: relative;
    }
    
    .main-header {
        font-size: 48px !important;
        font-weight: 700;
        text-align: center;
        color: #e6edf3;
        margin-bottom: 0.75rem;
        letter-spacing: -0.02em;
        line-height: 1.2;
        padding: 0 1rem;
    }
    
    .sub-header {
        text-align: center;
        color: #8b949e;
        margin-bottom: 2rem;
        font-size: 18px !important;
        font-weight: 400;
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
        padding: 0 1rem;
    }

    /* ========================================
       KPI CARDS - Professional Style
    ======================================== */
    .kpi-row {
        margin-bottom: 1.5rem;
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.9) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 18px;
        padding: 2.2rem 1.2rem 2.2rem 1.2rem;
        border: 1px solid rgba(240, 246, 252, 0.1);
        position: relative;
        transition: all 0.3s ease;
        min-width: 270px;
        max-width: 290px;
        min-height: 260px;
        max-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
        margin: 0 auto;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(56, 139, 253, 0.2);
    }

    .metric-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 1.1rem;
        width: 100%;
        height: 100%;
        text-align: center;
    }

    .metric-icon {
        width: 70px;
        height: 70px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.25), rgba(163, 113, 247, 0.18));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        flex-shrink: 0;
        border: 1.5px solid rgba(56, 139, 253, 0.25);
        margin-bottom: 0.5rem;
    }

    .metric-text {
        flex: 1;
        min-width: 0;
    }

    .metric-value {
        font-size: 48px !important;
        font-weight: 800;
        color: #e6edf3;
        margin-bottom: 0.3rem;
        line-height: 1.1;
        letter-spacing: -0.01em;
    }

    .metric-label {
        font-size: 18px !important;
        color: #8b949e;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        margin-bottom: 0.2rem;
    }

    .metric-subtitle {
        font-size: 15px !important;
        color: #6e7681;
        font-weight: 400;
        margin-top: 0.1rem;
    }

    /* ========================================
       SECTION CARDS - Professional Style
    ======================================== */
    .section-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.9) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(240, 246, 252, 0.1);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 28px !important;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-title .icon {
        font-size: 1.1rem;
    }

    .section-subtitle {
        font-size: 16px !important;
        color: #8b949e;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* ========================================
       SECTION HEADERS (NEW)
    ======================================== */
    .section-header {
        font-size: 28px !important;
        font-weight: 700;
        color: #e6edf3;
        padding: 1rem 0 0.75rem 0;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
        border-bottom: 2px solid rgba(56, 139, 253, 0.3);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-header-icon {
        font-size: 1.5rem;
    }

    /* ========================================
       AI INSIGHTS BOX (NEW)
    ======================================== */
    .ai-insights-card {
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.1) 0%, rgba(163, 113, 247, 0.08) 100%);
        border-radius: 16px;
        border: 1px solid rgba(56, 139, 253, 0.3);
        overflow: hidden;
        margin-bottom: 1.5rem;
    }

    .ai-insights-header {
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.15) 0%, rgba(163, 113, 247, 0.1) 100%);
        padding: 1rem 1.25rem;
        font-size: 22px !important;
        font-weight: 600;
        color: #e6edf3;
        border-bottom: 1px solid rgba(56, 139, 253, 0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .ai-insights-content {
        padding: 1.25rem;
    }

    .ai-insight-item {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(240, 246, 252, 0.06);
        font-size: 18px !important;
        color: #c9d1d9;
        line-height: 1.5;
    }

    .ai-insight-item:last-child {
        border-bottom: none;
    }

    .ai-insight-bullet {
        color: #388bfd;
        font-weight: bold;
    }

    .ai-insight-highlight {
        color: #f85149;
        font-weight: 600;
    }

    .ai-insight-success {
        color: #3fb950;
        font-weight: 600;
    }

    /* ========================================
       UPLOAD SECTION
    ======================================== */
    .upload-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.9) 100%);
        border-radius: 16px;
        border: 2px dashed rgba(56, 139, 253, 0.3);
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: rgba(56, 139, 253, 0.6);
        background: linear-gradient(135deg, rgba(22, 27, 34, 1) 0%, rgba(33, 38, 45, 0.95) 100%);
    }
    
    .upload-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .upload-title {
        font-size: 22px !important;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 15px !important;
        color: #8b949e;
    }

    /* ========================================
       STEP CARDS - Migration Plan
    ======================================== */
    .step-card {
        background: rgba(22, 27, 34, 0.8);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid rgba(240, 246, 252, 0.08);
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }

    .step-card:hover {
        transform: translateX(4px);
        border-color: rgba(56, 139, 253, 0.3);
    }

    .step-label {
        font-size: 12px !important;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #388bfd;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .step-service {
        font-size: 18px !important;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.25rem;
    }

    .step-meta {
        font-size: 14px !important;
        color: #8b949e;
    }

    /* Risk level indicators */
    .risk-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 12px !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .risk-badge.high {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.3);
    }
    
    .risk-badge.medium {
        background: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.3);
    }
    
    .risk-badge.low {
        background: rgba(63, 185, 80, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.3);
    }

    /* ========================================
       AI RECOMMENDATION CARD
    ======================================== */
    .ai-recommendation-card {
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95) 0%, rgba(33, 38, 45, 0.9) 100%);
        border-radius: 16px;
        border: 1px solid rgba(63, 185, 80, 0.3);
    }

    .ai-recommendation-header {
        background: linear-gradient(135deg, rgba(63, 185, 80, 0.1) 0%, rgba(63, 185, 80, 0.05) 100%);
        padding: 1rem 1.25rem;
        font-size: 22px !important;
        font-weight: 600;
        color: #e6edf3;
        text-align: center;
        border-bottom: 1px solid rgba(63, 185, 80, 0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }

    .ai-recommendation-content {
        padding: 1.25rem;
    }

    .recommendation-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(240, 246, 252, 0.06);
    }

    .recommendation-item:last-child {
        border-bottom: none;
    }

    .item-label {
        font-size: 15px !important;
        color: #8b949e;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .item-value {
        font-size: 20px !important;
        font-weight: 600;
        color: #e6edf3;
        text-align: right;
    }

    .item-value.risk-low {
        color: #3fb950;
    }

    .item-value.risk-medium {
        color: #d29922;
    }

    .item-value.risk-high {
        color: #f85149;
    }

    .item-value.improvement {
        color: #3fb950;
        font-weight: 700;
    }

    /* ========================================
       SIDEBAR STYLING
    ======================================== */
    .stSidebar {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%) !important;
        border-right: 1px solid rgba(240, 246, 252, 0.1);
        padding: 1rem;
    }

    .stSidebar .stButton button {
        display: flex !important;
        align-items: center;
        gap: 0.75rem;
        width: 100% !important;
        padding: 0.75rem 1rem !important;
        margin-bottom: 0.4rem !important;
        background: rgba(22, 27, 34, 0.6) !important;
        border: 1px solid rgba(240, 246, 252, 0.08) !important;
        border-radius: 10px !important;
        color: #c9d1d9 !important;
        font-weight: 500 !important;
        font-size: 16px !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
    }

    .stSidebar .stButton button.sidebar-active {
        background: rgba(56, 139, 253, 0.25) !important;
        border: 1px solid rgba(56, 139, 253, 0.6) !important;
        color: #ffffff !important;
    }

    .stSidebar .stButton button:hover {
        background: rgba(56, 139, 253, 0.15) !important;
        border-color: rgba(56, 139, 253, 0.4) !important;
        color: #ffffff !important;
    }

    .stSidebar .stButton button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
        margin-top: 1rem !important;
        font-weight: 600 !important;
        font-size: 16px !important;
    }

    .stSidebar .stButton button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%) !important;
    }

    /* ========================================
       FORM CONTROLS
    ======================================== */
    .stFileUploader {
        background: rgba(22, 27, 34, 0.5);
        border-radius: 12px;
        padding: 1rem;
    }
    
    .stFileUploader:hover {
        background: rgba(22, 27, 34, 0.7);
    }

    .stRadio label {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(240, 246, 252, 0.08);
        border-radius: 10px;
        padding: 0.6rem 0.85rem;
        transition: all 0.2s ease;
        color: #c9d1d9;
    }

    .stRadio label:hover {
        border-color: rgba(56, 139, 253, 0.4);
        background: rgba(56, 139, 253, 0.1);
    }

    /* DataFrames */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(240, 246, 252, 0.08);
    }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.25rem;
        font-weight: 600;
        font-family: 'Outfit', sans-serif;
        font-size: 16px !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
    }

    /* Success/Error/Info Messages */
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    
    .stSuccess {
        background: rgba(63, 185, 80, 0.15);
        border: 1px solid rgba(63, 185, 80, 0.3);
        color: #3fb950;
    }
    
    .stWarning {
        background: rgba(210, 153, 34, 0.15);
        border: 1px solid rgba(210, 153, 34, 0.3);
        color: #d29922;
    }
    
    .stError {
        background: rgba(248, 81, 73, 0.15);
        border: 1px solid rgba(248, 81, 73, 0.3);
        color: #f85149;
    }

    /* ========================================
       SCROLLBAR
    ======================================== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(22, 27, 34, 0.3);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(139, 148, 158, 0.4);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(139, 148, 158, 0.6);
    }

    /* ========================================
       CHART CONTAINER
    ======================================== */
    .chart-container {
        background: rgba(22, 27, 34, 0.5);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(240, 246, 252, 0.06);
    }

    /* Plotly chart dark theme */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }

    /* ========================================
       CHAT CONTAINER
    ======================================== */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border-radius: 12px;
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(240, 246, 252, 0.08);
    }
    
    .chat-message {
        padding: 0.75rem 1rem;
        border-radius: 12px;
        margin-bottom: 0.75rem;
        font-size: 18px !important;
        line-height: 1.6;
    }
    
    .chat-message.user {
        background: rgba(56, 139, 253, 0.15);
        border: 1px solid rgba(56, 139, 253, 0.2);
    }
    
    .chat-message.assistant {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid rgba(240, 246, 252, 0.08);
    }

    /* ========================================
       METRICS & STATS
    ======================================== */
    .stat-card {
        background: rgba(22, 27, 34, 0.6);
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid rgba(240, 246, 252, 0.06);
    }
    
    .stat-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #e6edf3;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #8b949e;
    }

    /* ========================================
       RESPONSIVE
    ======================================== */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 1.75rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .section-card {
            padding: 1rem;
        }
        
        .section-header {
            font-size: 1.4rem;
        }
    }
</style>
    """,
    unsafe_allow_html=True,
)


def ensure_data():
    """Generate telemetry data if not exists."""
    data_path = os.path.join(PROJECT_ROOT, "data", "telemetry_data.csv")
    if not os.path.exists(data_path):
        df = generate_telemetry_data(num_days=14, records_per_edge=80)
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        df.to_csv(data_path, index=False)
        return df
    return pd.read_csv(data_path)


def get_telemetry_data():
    """Get telemetry data: use uploaded file if present, else default."""
    if "uploaded_telemetry" in st.session_state and st.session_state.uploaded_telemetry is not None:
        return st.session_state.uploaded_telemetry
    return ensure_data()


def generate_migration_batches(services, dependencies):
    """Determine migration batches using topological sorting."""
    import networkx as nx

    G = nx.DiGraph()
    G.add_nodes_from(services)
    G.add_edges_from(dependencies)

    batches = []
    working = G.copy()
    while working.nodes:
        zero_indegree = [n for n, d in working.in_degree() if d == 0]
        if not zero_indegree:
            batches.append(list(working.nodes()))
            break
        batches.append(zero_indegree)
        working.remove_nodes_from(zero_indegree)
    return batches


def create_dependency_graph(df):
    """Create an interactive Plotly network graph for service dependencies with hover tooltips."""
    import networkx as nx

    deps = discover_dependencies(df=df)
    risk_df = calculate_risk_scores(df=df)

    G = build_dependency_graph(dependencies=deps)

    # Get node positions using spring layout
    pos = nx.spring_layout(G, k=1, iterations=50, seed=42)

    # Create figure
    fig = go.Figure()

    # Add edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#388bfd'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    ))

    # Add nodes
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_texts = []
    node_names = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_names.append(node)

        # Get risk data
        risk_data = risk_df[risk_df['service'] == node]
        if not risk_data.empty:
            risk_score = risk_data['risk_score'].iloc[0]
            risk_level = risk_data['risk_level'].iloc[0]
            dep_count = risk_data['dependency_count'].iloc[0]
        else:
            risk_score = 50
            risk_level = "Medium"
            dep_count = G.degree(node)

        # Set color based on risk level
        if risk_level == "High":
            color = "#f85149"
        elif risk_level == "Medium":
            color = "#d29922"
        else:
            color = "#3fb950"

        node_colors.append(color)
        node_sizes.append(20 + (risk_score / 100) * 30)

        # Create hover text
        hover_text = f"""
        <b>{node}</b><br>
        Risk Level: <span style="color: {color};">{risk_level}</span><br>
        Risk Score: {risk_score}<br>
        Dependencies: {dep_count}
        """

        node_texts.append(hover_text)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='rgba(255,255,255,0.3)'),
            sizemode='diameter'
        ),
        text=node_names,
        textposition="top center",
        textfont=dict(size=10, color="#e6edf3"),
        hovertemplate=node_texts,
        hoverlabel=dict(
            bgcolor="rgba(13, 17, 23, 0.95)",
            bordercolor="rgba(240, 246, 252, 0.1)",
            font=dict(size=12, color="#e6edf3")
        ),
        showlegend=False
    ))

    # Update layout
    fig.update_layout(
        plot_bgcolor='rgba(13, 17, 23, 0.95)',
        paper_bgcolor='rgba(13, 17, 23, 0.95)',
        font_color="#e6edf3",
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode='closest'
    )

    return fig


def render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df=None, dependencies_list=None):
    """Render KPI metrics row at the top of sections with expandable details."""
    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="large")

    with kpi_col1:
        # Make the card clickable using a button overlay - toggle on click
        if st.button(
            label=" ",  # Invisible label
            key="total_services_card_btn",
            help="Click to toggle services list",
            args=(),
            kwargs={},
            use_container_width=True,
        ):
            # Toggle the state
            if st.session_state.get("show_services_list"):
                st.session_state["show_services_list"] = False
            else:
                st.session_state["show_services_list"] = True
        st.markdown(
            f"""
            <div class="metric-card" style="position:relative; margin-top:-48px; z-index:1; pointer-events:none;">
                <div class="metric-content">
                    <div class="metric-icon">🏗️</div>
                    <div class="metric-text">
                        <div class="metric-label">Total Services</div>
                        <div class="metric-value">{total_services}</div>
                        <div class="metric-subtitle">Microservices discovered</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Show services list if toggled on
        if st.session_state.get("show_services_list") and risk_df is not None and not risk_df.empty:
            st.markdown("<div class='card-detail-popup'>", unsafe_allow_html=True)
            st.markdown("<b>📋 All Services:</b>", unsafe_allow_html=True)
            services_list = risk_df["service"].tolist()
            for idx, service in enumerate(services_list, 1):
                st.write(f"{idx}. {service}")
            st.markdown("</div>", unsafe_allow_html=True)

    with kpi_col2:
        # Make the card clickable using a button overlay - toggle on click
        if st.button(
            label=" ",  # Invisible label
            key="total_dependencies_card_btn",
            help="Click to toggle dependencies list",
            args=(),
            kwargs={},
            use_container_width=True,
        ):
            # Toggle the state
            if st.session_state.get("show_dependencies_list"):
                st.session_state["show_dependencies_list"] = False
            else:
                st.session_state["show_dependencies_list"] = True
        st.markdown(
            f"""
            <div class="metric-card" style="position:relative; margin-top:-48px; z-index:1; pointer-events:none;">
                <div class="metric-content">
                    <div class="metric-icon">🔗</div>
                    <div class="metric-text">
                        <div class="metric-label">Total Dependencies</div>
                        <div class="metric-value">{total_dependencies}</div>
                        <div class="metric-subtitle">Service interconnections</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Show dependencies list if toggled on
        if st.session_state.get("show_dependencies_list") and dependencies_list is not None and len(dependencies_list) > 0:
            st.markdown("<div class='card-detail-popup'>", unsafe_allow_html=True)
            st.markdown("<b>📊 All Dependencies:</b>", unsafe_allow_html=True)
            deps_display = dependencies_list[:20]  # Show first 20
            for idx, (src, dst) in enumerate(deps_display, 1):
                st.write(f"{idx}. {src} → {dst}")
            if len(dependencies_list) > 20:
                st.info(f"... and {len(dependencies_list) - 20} more dependencies")
            st.markdown("</div>", unsafe_allow_html=True)

    with kpi_col3:
        # Make the card clickable using a button overlay - toggle on click
        if st.button(
            label=" ",  # Invisible label
            key="high_risk_services_card_btn",
            help="Click to toggle high risk services list",
            args=(),
            kwargs={},
            use_container_width=True,
        ):
            # Toggle the state
            if st.session_state.get("show_high_risk_list"):
                st.session_state["show_high_risk_list"] = False
            else:
                st.session_state["show_high_risk_list"] = True
        st.markdown(
            f"""
            <div class="metric-card" style="position:relative; margin-top:-48px; z-index:1; pointer-events:none;">
                <div class="metric-content">
                    <div class="metric-icon">⚠️</div>
                    <div class="metric-text">
                        <div class="metric-label">High Risk Services</div>
                        <div class="metric-value">{high_risk_services}</div>
                        <div class="metric-subtitle">Require immediate attention</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Show high-risk services list if toggled on
        if st.session_state.get("show_high_risk_list") and risk_df is not None and not risk_df.empty:
            st.markdown("<div class='card-detail-popup'>", unsafe_allow_html=True)
            st.markdown("<b>⚠️ High Risk Services:</b>", unsafe_allow_html=True)
            high_risk = risk_df[risk_df["risk_level"] == "High"]
            for idx, (_, row) in enumerate(high_risk.iterrows(), 1):
                st.write(f"{idx}. {row['service']} - Risk: {row['risk_score']}")
            st.markdown("</div>", unsafe_allow_html=True)

    with kpi_col4:
        # Make the card clickable using a button overlay - toggle on click
        if st.button(
            label=" ",  # Invisible label
            key="avg_latency_card_btn",
            help="Click to toggle latency details",
            args=(),
            kwargs={},
            use_container_width=True,
        ):
            # Toggle the state
            if st.session_state.get("show_latency_list"):
                st.session_state["show_latency_list"] = False
            else:
                st.session_state["show_latency_list"] = True
        st.markdown(
            f"""
            <div class="metric-card" style="position:relative; margin-top:-48px; z-index:1; pointer-events:none;">
                <div class="metric-content">
                    <div class="metric-icon">⚡</div>
                    <div class="metric-text">
                        <div class="metric-label">Average Latency</div>
                        <div class="metric-value">{avg_latency:.1f}ms</div>
                        <div class="metric-subtitle">Performance metric</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Show latency details if toggled on
        if st.session_state.get("show_latency_list") and risk_df is not None and not risk_df.empty and "avg_latency_ms" in risk_df.columns:
            st.markdown("<div class='card-detail-popup'>", unsafe_allow_html=True)
            st.markdown("<b>⚡ Top 5 Services by Latency:</b>", unsafe_allow_html=True)
            latency_sorted = risk_df.sort_values("avg_latency_ms", ascending=False).head(5)
            for idx, row in enumerate(latency_sorted.itertuples(), 1):
                st.write(f"{idx}. {row.service} - Latency: {row.avg_latency_ms:.1f}ms")
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def generate_ai_insights(risk_df, recommendation, total_services):
    """Generate AI insights based on current data."""
    insights = []
    
    # High risk services count
    if not risk_df.empty and "risk_level" in risk_df.columns:
        high_risk = risk_df[risk_df["risk_level"] == "High"]
        if len(high_risk) > 0:
            insights.append(f"• <span class='ai-insight-highlight'>{len(high_risk)} services</span> classified as high risk")
    
    # Highest error rate service
    if not risk_df.empty and "error_rate" in risk_df.columns:
        max_error_idx = risk_df["error_rate"].idxmax()
        max_error_service = risk_df.loc[max_error_idx, "service"]
        max_error_rate = risk_df.loc[max_error_idx, "error_rate"]
        insights.append(f"• <span class='ai-insight-highlight'>{max_error_service}</span> has highest error rate ({max_error_rate:.2f}%)")
    
    # Highest CPU load
    if not risk_df.empty and "cpu_usage_pct" in risk_df.columns:
        max_cpu_idx = risk_df["cpu_usage_pct"].idxmax()
        max_cpu_service = risk_df.loc[max_cpu_idx, "service"]
        max_cpu = risk_df.loc[max_cpu_idx, "cpu_usage_pct"]
        insights.append(f"• <span class='ai-insight-highlight'>{max_cpu_service}</span> shows high CPU load ({max_cpu:.1f}%)")
    
    # Highest latency
    if not risk_df.empty and "avg_latency_ms" in risk_df.columns:
        max_lat_idx = risk_df["avg_latency_ms"].idxmax()
        max_lat_service = risk_df.loc[max_lat_idx, "service"]
        max_lat = risk_df.loc[max_lat_idx, "avg_latency_ms"]
        insights.append(f"• <span class='ai-insight-highlight'>{max_lat_service}</span> has highest latency ({max_lat:.1f}ms)")
    
    # Recommended strategy
    if recommendation:
        strategy_name = recommendation.get("strategy", "Unknown").split(": ")[-1] if ": " in recommendation.get("strategy", "") else recommendation.get("strategy", "Unknown")
        insights.append(f"• Recommended migration strategy: <span class='ai-insight-success'>{strategy_name}</span>")
    
    return insights


def render_ai_insights(insights):
    """Render AI insights box."""
    if not insights:
        return
    
    insights_html = """
    <div class="ai-insights-card">
        <div class="ai-insights-header">
            🤖 AI Insights
        </div>
        <div class="ai-insights-content">
    """
    
    for insight in insights:
        insights_html += f'<div class="ai-insight-item"><span class="ai-insight-bullet">▸</span><span>{insight}</span></div>'
    
    insights_html += """
        </div>
    </div>
    """
    
    st.markdown(insights_html, unsafe_allow_html=True)


def main():
    # Data source: upload or default
    telemetry_df = get_telemetry_data()

    # Pre-compute core analytics for KPIs and sections
    try:
        deps = discover_dependencies(df=telemetry_df)
    except Exception:
        deps = []

    # Convert deps to list of (source, destination) tuples for display
    dependencies_list = []
    if isinstance(deps, dict):
        # If deps is a dict of {src: [dst1, dst2, ...]}
        for src, dests in deps.items():
            for dst in dests:
                dependencies_list.append((src, dst))
    elif isinstance(deps, list):
        # If deps is already a list
        dependencies_list = deps

    try:
        risk_df = calculate_risk_scores(df=telemetry_df)
    except Exception:
        risk_df = pd.DataFrame()

    total_services = telemetry_df["service_name"].nunique() if "service_name" in telemetry_df.columns else len(telemetry_df)
    total_dependencies = len(deps)
    high_risk_services = (risk_df["risk_level"] == "High").sum() if not risk_df.empty and "risk_level" in risk_df.columns else 0
    avg_latency = (
        float(telemetry_df["request_latency"].mean())
        if "request_latency" in telemetry_df.columns
        else float(risk_df["avg_latency_ms"].mean()) if "avg_latency_ms" in risk_df.columns else 0.0
    )

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📊 Navigation", unsafe_allow_html=True)

        nav_options = [
            ("📊 Dashboard", "dashboard"),
            ("🤖 AI Assistant", "assistant"),
            ("📁 Dataset", "dataset"),
            ("🔗 Dependency Graph", "graph"),
            ("⚠️ Risk Analysis", "risk"),
            ("📋 Migration Plan", "plan"),
            ("🎯 Simulation", "simulation"),
            ("📥 Download Report", "download"),
        ]

        if "current_section" not in st.session_state:
            st.session_state.current_section = "dashboard"

        for label, key in nav_options:
            is_active = st.session_state.current_section == key
            extra_class = "sidebar-active" if is_active else ""
            
            if st.button(f"{label}", key=f"nav_{key}", help=f"Navigate to {label.split(' ', 1)[1] if ' ' in label else label}", width='stretch'):
                st.session_state.current_section = key
                st.rerun()

        st.markdown("---", unsafe_allow_html=True)
        
        if st.button("🔄 Regenerate Data", key="regenerate_data", width='stretch', type="primary"):
            df = generate_telemetry_data(num_days=14, records_per_edge=80)
            df.to_csv(os.path.join(PROJECT_ROOT, "data", "telemetry_data.csv"), index=False)
            for key in ["uploaded_telemetry"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.upload_key = st.session_state.get("upload_key", 0) + 1
            st.success("Data regenerated!")
            st.rerun()

    # Get current section
    section_map = {
        "dashboard": "📊 Dashboard",
        "assistant": "🤖 AI Assistant",
        "dataset": "📁 Dataset",
        "graph": "🕸️ Dependency Graph",
        "risk": "⚠️ Risk Analysis",
        "plan": "📋 Migration Plan",
        "simulation": "🎯 Simulation",
        "download": "📥 Download Report",
    }
    section = section_map.get(st.session_state.current_section, "📊 Dashboard")

    # ============================================
    # SECTION 1: DASHBOARD (Default/Home)
    # ============================================
    if section == "📊 Dashboard":
        # Hero Section
        st.markdown('''
        <div style="text-align: center; padding: 0.75rem 1rem 1rem;">
            <h1 style="font-size: 3rem; font-weight: 700; color: #e6edf3; margin-bottom: 0.5rem; letter-spacing: -0.02em; line-height: 1.2;">🚀 AI Cloud Migration Copilot</h1>
            <p style="font-size: 1.35rem; color: #8b949e; max-width: 900px; margin: 0 auto; line-height: 1.6; white-space: nowrap;">AI-Based Intelligent System for Automated Microservice Dependency Analysis and Cloud Migration Planning</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Section Header: System Overview
        st.markdown('<div class="section-header"><span class="section-header-icon">📊</span> System Overview</div>', unsafe_allow_html=True)
        
        # Render KPI Metrics Row
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)

        # AI Insights Box
        risk_df_dash = calculate_risk_scores(df=telemetry_df)
        recommendation_dash = get_recommended_plan(compare_strategies(risk_df_dash))
        ai_insights = generate_ai_insights(risk_df_dash, recommendation_dash, total_services)
        render_ai_insights(ai_insights)
        
        # Drag & Drop CSV Upload Section
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📁 Data Source</div>', unsafe_allow_html=True)
        
        upload_col1, upload_col2 = st.columns([2, 1])
        
        with upload_col1:
            st.markdown(
                """
                <div class="upload-card">
                    <div class="upload-icon">📄</div>
                    <div class="upload-title">Drag & Drop CSV File</div>
                    <div class="upload-subtitle">Upload your cloud migration dataset (CSV format)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            
            upload_key = st.session_state.get("upload_key", 0)
            uploaded_file = st.file_uploader(
                "Upload CSV for testing",
                type=["csv"],
                help="Supports formats like cloud_migration_dataset_large.csv",
                key=f"file_upload_{upload_key}",
            )
            if uploaded_file is not None:
                try:
                    raw = pd.read_csv(uploaded_file)
                    valid, msg = validate_uploaded_data(raw)
                    if valid:
                        st.session_state.uploaded_telemetry = normalize_external_csv(raw)
                        st.success(f"✅ Loaded {len(st.session_state.uploaded_telemetry)} rows successfully!")
                    else:
                        st.error(f"❌ {msg}")
                except Exception as e:
                    st.error(f"❌ Upload failed: {e}")
        
        with upload_col2:
            current_source = "Uploaded dataset" if "uploaded_telemetry" in st.session_state else "Synthetic telemetry"
            st.markdown(
                f"""
                <div class="stat-card" style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div class="stat-label">Current Data Source</div>
                    <div class="stat-value" style="font-size: 1rem; margin-top: 0.5rem;">{current_source}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Use Default Data"):
                for key in ["uploaded_telemetry"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.upload_key = st.session_state.get("upload_key", 0) + 1
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Section Header: System Architecture
        st.markdown('<div class="section-header"><span class="section-header-icon">🕸️</span> System Architecture</div>', unsafe_allow_html=True)

        # MAIN CONTENT AREA - Row 1: Dependency Graph + AI Recommendation
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕸️ Service Dependency Graph</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Interactive topology of microservice dependencies with AI-powered migration recommendations.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1], gap="large")

        with col1:
            graph_fig = create_dependency_graph(telemetry_df)
            st.plotly_chart(graph_fig, use_container_width=True, height=500)

        with col2:
            st.markdown(
                """
                <div class="ai-recommendation-card">
                    <div class="ai-recommendation-header">
                        🤖 AI Migration Recommendation
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            risk_df = calculate_risk_scores(df=telemetry_df)
            recommendation = get_recommended_plan(compare_strategies(risk_df))

            all_strategies = compare_strategies(risk_df)
            worst_downtime = max(s["downtime_pct"] for s in all_strategies)
            worst_risk_score = max(s["avg_risk_score"] for s in all_strategies)

            downtime_reduction = ((worst_downtime - recommendation["downtime_pct"]) / worst_downtime * 100) if worst_downtime > 0 else 0
            risk_reduction = ((worst_risk_score - recommendation["avg_risk_score"]) / worst_risk_score * 100) if worst_risk_score > 0 else 0

            st.markdown(
                f"""
                <div class="ai-recommendation-content">
                    <div class="recommendation-item">
                        <span class="item-label">Best Strategy:</span>
                        <span class="item-value">{recommendation["strategy"].split(": ")[1]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Batch Size:</span>
                        <span class="item-value">{recommendation["batch_size"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Score:</span>
                        <span class="item-value risk-{recommendation["risk_level"].lower()}">{recommendation["risk_level"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Est. Downtime Reduction:</span>
                        <span class="item-value improvement">+{downtime_reduction:.0f}%</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Reduction:</span>
                        <span class="item-value improvement">+{risk_reduction:.0f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # Section Header: Risk Analysis
        st.markdown('<div class="section-header"><span class="section-header-icon">⚠️</span> Risk Analysis</div>', unsafe_allow_html=True)

        # MAIN CONTENT AREA - Row 2: Risk Heatmap + Migration Strategy Summary
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        row2_col1, row2_col2 = st.columns(2, gap="large")

        with row2_col1:
            st.markdown('<div class="section-title">⚠️ Service Risk Heatmap (Latency vs Error Rate)</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Service risk distribution by latency and error rate. Hover for details.</div>', unsafe_allow_html=True)
            
            if not risk_df.empty:
                fig_heat = px.scatter(
                    risk_df,
                    x="avg_latency_ms" if "avg_latency_ms" in risk_df.columns else "request_latency",
                    y="error_rate",
                    size="risk_score",
                    color="risk_level",
                    hover_name="service",
                    template="plotly_dark",
                    color_discrete_map={"Low": "#3fb950", "Medium": "#d29922", "High": "#f85149"},
                    size_max=60,
                )
                fig_heat.update_traces(
                    hovertemplate="<b>%{hovertext}</b><br>" +
                                  "Latency: %{x:.1f}ms<br>" +
                                  "Error Rate: %{y:.2f}%<br>" +
                                  "Risk Score: %{marker.size}<extra></extra>"
                )
                fig_heat.update_layout(
                    title="Service Risk Heatmap (Latency vs Error Rate)",
                    xaxis_title="Latency (ms)",
                    yaxis_title="Error Rate (%)",
                    margin=dict(l=40, r=40, t=50, b=40),
                    legend_title="Risk Level",
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_heat, use_container_width=True)

        with row2_col2:
            st.markdown('<div class="section-title">🎯 Migration Strategy Summary</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Compare simulated migration strategies.</div>', unsafe_allow_html=True)
            
            sims = compare_strategies(risk_df=risk_df)
            comp_df = pd.DataFrame([{
                "Strategy": s["strategy"].split(": ")[1] if ": " in s["strategy"] else s["strategy"],
                "Downtime": f"{s['downtime_pct']}%",
                "Risk Level": s["risk_level"],
                "Avg Risk Score": s["avg_risk_score"],
            } for s in sims])
            
            st.dataframe(comp_df, use_container_width=True, height=400)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Section Header: Performance Metrics
        st.markdown('<div class="section-header"><span class="section-header-icon">💻</span> Performance Metrics</div>', unsafe_allow_html=True)

        # MAIN CONTENT AREA - Row 3: CPU Usage + Error Rate Monitoring Charts
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        row3_col1, row3_col2 = st.columns(2, gap="large")

        with row3_col1:
            st.markdown('<div class="section-title">💻 CPU Usage per Service (%)</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">CPU utilization of each microservice. Hover for details.</div>', unsafe_allow_html=True)
            
            if not risk_df.empty:
                if "cpu_usage_pct" not in risk_df.columns and "cpu_usage" in telemetry_df.columns:
                    cpu_data = telemetry_df.groupby("service_name")["cpu_usage"].mean().reset_index()
                    cpu_data.columns = ["service", "cpu_usage_pct"]
                elif "cpu_usage_pct" in risk_df.columns:
                    cpu_data = risk_df[["service", "cpu_usage_pct"]].copy()
                else:
                    cpu_data = risk_df[["service"]].copy()
                    cpu_data["cpu_usage_pct"] = (risk_df["risk_score"] * 0.8 + 10).round(1)
                
                # Add error rate and latency for hover
                if "error_rate" in risk_df.columns:
                    cpu_data = cpu_data.merge(risk_df[["service", "error_rate", "avg_latency_ms"]], on="service", how="left")
                else:
                    cpu_data["error_rate"] = 0
                    cpu_data["avg_latency_ms"] = 0
                
                fig_cpu = px.bar(
                    cpu_data,
                    x="service",
                    y="cpu_usage_pct",
                    template="plotly_dark",
                    color="cpu_usage_pct",
                    color_continuous_scale=px.colors.sequential.Blues,
                )
                fig_cpu.update_traces(
                    hovertemplate="<b>%{x}</b><br>" +
                                  "CPU Usage: %{y:.1f}%<br>" +
                                  "Error Rate: %{customdata[0]:.2f}%<br>" +
                                  "Latency: %{customdata[1]:.1f}ms<extra></extra>"
                )
                fig_cpu.update_layout(
                    title="CPU Usage per Service (%)",
                    xaxis_title="Service",
                    yaxis_title="CPU Usage (%)",
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_cpu, use_container_width=True)

        with row3_col2:
            st.markdown('<div class="section-title">❌ Error Rate per Service (%)</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Failure/error rate of each microservice. Hover for details.</div>', unsafe_allow_html=True)
            
            if not risk_df.empty:
                if "error_rate" in risk_df.columns:
                    error_data = risk_df[["service", "error_rate"]].copy()
                else:
                    error_data = risk_df[["service"]].copy()
                    error_data["error_rate"] = (risk_df["risk_score"] / 100 * 5).round(3)
                
                # Add CPU and latency for hover
                if "cpu_usage_pct" in risk_df.columns:
                    error_data = error_data.merge(risk_df[["service", "cpu_usage_pct", "avg_latency_ms"]], on="service", how="left")
                else:
                    error_data["cpu_usage_pct"] = 0
                    error_data["avg_latency_ms"] = 0
                
                fig_err = px.bar(
                    error_data,
                    x="service",
                    y="error_rate",
                    template="plotly_dark",
                    color="error_rate",
                    color_continuous_scale=px.colors.sequential.Reds,
                )
                fig_err.update_traces(
                    hovertemplate="<b>%{x}</b><br>" +
                                  "Error Rate: %{y:.2f}%<br>" +
                                  "CPU Usage: %{customdata[0]:.1f}%<br>" +
                                  "Latency: %{customdata[1]:.1f}ms<extra></extra>"
                )
                fig_err.update_layout(
                    title="Error Rate per Service (%)",
                    xaxis_title="Service",
                    yaxis_title="Error Rate (%)",
                    margin=dict(l=40, r=40, t=50, b=40),
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_err, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # ============================================
    # SECTION 2: AI ASSISTANT
    # ============================================
    elif section == "🤖 AI Assistant":
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🤖 AI Migration Assistant</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Ask questions about your migration plan, dependencies, risks, and more.</div>', unsafe_allow_html=True)

        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        if not st.session_state.chat_messages:
            st.info("👋 Welcome! I can help you with migration planning. Try asking:")
            st.markdown("""
            - Which service should migrate first?
            - What are the highest risk services?
            - What is the safest migration strategy?
            """)

        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me about your migration plan..."):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        context = get_context_data()
                        response = answer_question(prompt, context)
                        st.markdown(response)
                        st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"I apologize, but I encountered an error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

        if st.session_state.chat_messages:
            if st.button("🗑️ Clear Chat History", key="clear_chat"):
                st.session_state.chat_messages = []
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 3: DATASET
    # ============================================
    elif section == "📁 Dataset":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)
        
        st.markdown(
            '<div class="section-card"><div class="section-title">📁 Dataset Overview</div>'
            '<div class="section-subtitle">Preview the loaded telemetry and basic statistics.</div></div>',
            unsafe_allow_html=True,
        )

        with st.expander("Dataset preview & statistics", expanded=True):
            st.dataframe(telemetry_df.head(150), use_container_width=True)
            st.caption(f"Showing up to 150 of {len(telemetry_df)} rows")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Row Count", len(telemetry_df))
            with col2:
                st.metric("Unique Services", total_services)
            with col3:
                if "timestamp" in telemetry_df.columns:
                    st.metric("Time Range", f"{str(telemetry_df['timestamp'].min())[:10]} → {str(telemetry_df['timestamp'].max())[:10]}")
                else:
                    st.metric("Data Source", "Uploaded dataset" if "uploaded_telemetry" in st.session_state else "Synthetic telemetry")

    # ============================================
    # SECTION 4: Service Dependency Graph
    # ============================================
    elif section == "🕸️ Dependency Graph":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕸️ Service Dependency Graph</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Interactive topology of microservice dependencies with AI-powered migration recommendations.</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1], gap="large")

        with col1:
            graph_fig = create_dependency_graph(telemetry_df)
            st.plotly_chart(graph_fig, use_container_width=True, height=650)

        with col2:
            st.markdown(
                """
                <div class="ai-recommendation-card">
                    <div class="ai-recommendation-header">
                        🤖 AI Migration Recommendation
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            risk_df = calculate_risk_scores(df=telemetry_df)
            recommendation = get_recommended_plan(compare_strategies(risk_df))

            all_strategies = compare_strategies(risk_df)
            worst_downtime = max(s["downtime_pct"] for s in all_strategies)
            worst_risk_score = max(s["avg_risk_score"] for s in all_strategies)

            downtime_reduction = ((worst_downtime - recommendation["downtime_pct"]) / worst_downtime * 100) if worst_downtime > 0 else 0
            risk_reduction = ((worst_risk_score - recommendation["avg_risk_score"]) / worst_risk_score * 100) if worst_risk_score > 0 else 0

            st.markdown(
                f"""
                <div class="ai-recommendation-content">
                    <div class="recommendation-item">
                        <span class="item-label">Best Strategy:</span>
                        <span class="item-value">{recommendation["strategy"].split(": ")[1]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Batch Size:</span>
                        <span class="item-value">{recommendation["batch_size"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Score:</span>
                        <span class="item-value risk-{recommendation["risk_level"].lower()}">{recommendation["risk_level"]}</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Est. Downtime Reduction:</span>
                        <span class="item-value improvement">+{downtime_reduction:.0f}%</span>
                    </div>
                    <div class="recommendation-item">
                        <span class="item-label">Risk Reduction:</span>
                        <span class="item-value improvement">+{risk_reduction:.0f}%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        G = build_dependency_graph(dependencies=deps)
        metrics = get_graph_metrics(G)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Services (Nodes)", metrics["num_nodes"])
        with col2:
            st.metric("Dependencies (Edges)", metrics["num_edges"])
        with col3:
            st.metric("Entry Points", len(metrics["entry_points"]))

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 5: Risk Analysis Dashboard
    # ============================================
    elif section == "⚠️ Risk Analysis":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚠️ Risk Analysis Dashboard</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Risk scores and resource pressure across services.</div>', unsafe_allow_html=True)

        if risk_df.empty:
            st.warning("Risk scores could not be computed for the current dataset.")
        else:
            st.dataframe(risk_df, use_container_width=True, height=380)

            if not risk_df.empty:
                fig_heat = px.scatter(
                    risk_df,
                    x="avg_latency_ms" if "avg_latency_ms" in risk_df.columns else "request_latency",
                    y="error_rate",
                    size="risk_score",
                    color="risk_level",
                    hover_name="service",
                    template="plotly_dark",
                    color_discrete_map={"Low": "#3fb950", "Medium": "#d29922", "High": "#f85149"},
                    size_max=60,
                )
                fig_heat.update_layout(
                    title="Service Risk Heatmap",
                    xaxis_title="Latency (ms)",
                    yaxis_title="Error Rate",
                    margin=dict(l=40, r=40, t=40, b=40),
                    legend_title="Risk Level",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_heat, use_container_width=True)

            cpu_col, err_col = st.columns(2)
            with cpu_col:
                st.subheader("CPU Usage per Service")
                fig_cpu = px.bar(
                    risk_df,
                    x="service",
                    y="cpu_usage_pct",
                    color="risk_level",
                    color_discrete_map={"Low": "#3fb950", "Medium": "#d29922", "High": "#f85149"},
                )
                fig_cpu.update_layout(
                    xaxis_title="Service",
                    yaxis_title="CPU Utilization (%)",
                    margin=dict(l=10, r=10, t=30, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_cpu, use_container_width=True)
            with err_col:
                st.subheader("Error Rate per Service")
                fig_err = px.bar(
                    risk_df,
                    x="service",
                    y="error_rate",
                    color="risk_level",
                    color_discrete_map={"Low": "#3fb950", "Medium": "#d29922", "High": "#f85149"},
                )
                fig_err.update_layout(
                    xaxis_title="Service",
                    yaxis_title="Error Rate",
                    margin=dict(l=10, r=10, t=30, b=40),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_err, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 6: Migration Plan
    # ============================================
    elif section == "📋 Migration Plan":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Migration Plan</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">AI-recommended migration order, optimized for dependencies and risk.</div>', unsafe_allow_html=True)

        plan = get_migration_order(risk_df=risk_df)
        risk_level_map = dict(zip(risk_df["service"], risk_df["risk_level"]))

        cols = st.columns(4)
        for step in plan:
            col = cols[(step["step"] - 1) % 4]
            risk_level = risk_level_map.get(step['service'], 'Medium')
            with col:
                st.markdown(
                    f"""
                    <div class="step-card">
                      <div class="step-label">STEP {step['step']}</div>
                      <div class="step-service">{step['service']}</div>
                      <div class="step-meta">Risk: {risk_level}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.subheader("Phase-wise Migration Plan")
        
        # Get phase-wise batch plan for recommended strategy
        sims = compare_strategies(risk_df=risk_df)
        recommendation = get_recommended_plan(sims)
        detailed_plan = get_detailed_recommendation(recommendation)
        
        # Extract strategy details
        strategy_name = detailed_plan["strategy"].split(": ")[1] if ": " in detailed_plan["strategy"] else detailed_plan["strategy"]
        batch_info = f"Batch Size: {detailed_plan['batch_size']} | Total Phases: {detailed_plan['total_phases']}"
        st.markdown(f'<div style="font-size: 20px; font-weight: 600; color: #22c55e; margin: 1rem 0;">{strategy_name}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size: 18px; color: #8b949e; margin-bottom: 1rem;">{batch_info}</div>', unsafe_allow_html=True)
        
        # Add CSS to enlarge table content
        st.markdown("""
            <style>
                .dataframe {
                    font-size: 18px !important;
                }
                .dataframe td, .dataframe th {
                    font-size: 16px !important;
                    padding: 12px !important;
                    line-height: 1.6 !important;
                }
                .dataframe thead th {
                    font-size: 17px !important;
                    font-weight: 700 !important;
                    background-color: rgba(34, 197, 94, 0.1) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Create phase-wise table
        phases_data = []
        for phase in detailed_plan["phases"]:
            phases_data.append({
                "Phase": f"Phase {phase['phase']}",
                "Services": phase['services_str'],
                "Count": phase['service_count'],
                "Avg Risk": phase['avg_risk'],
            })
        
        phases_df = pd.DataFrame(phases_data)
        st.dataframe(phases_df, use_container_width=True, height=450)

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 7: Migration Simulation
    # ============================================
    elif section == "🎯 Simulation":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency, risk_df, dependencies_list)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Migration Simulation</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Compare simulated migration strategies by downtime and aggregate risk.</div>', unsafe_allow_html=True)

        sims = compare_strategies(risk_df=risk_df)
        recommended = get_recommended_plan(sims)

        st.success(
            f"Recommended: **{recommended['strategy']}** — "
            f"Downtime: **{recommended['downtime_pct']}%**, Risk: **{recommended['risk_level']}**"
        )

        comp_df = pd.DataFrame([{
            "Strategy": s["strategy"],
            "Downtime %": s["downtime_pct"],
            "Risk Level": s["risk_level"],
            "Avg Risk Score": s["avg_risk_score"],
        } for s in sims])

        fig_sim = go.Figure()
        fig_sim.add_trace(
            go.Bar(
                x=comp_df["Strategy"],
                y=comp_df["Downtime %"],
                name="Downtime %",
                marker_color="#388bfd",
            )
        )
        fig_sim.add_trace(
            go.Scatter(
                x=comp_df["Strategy"],
                y=comp_df["Avg Risk Score"],
                name="Avg Risk Score",
                mode="lines+markers",
                yaxis="y2",
                marker=dict(color="#d29922"),
            )
        )
        fig_sim.update_layout(
            yaxis=dict(title="Downtime (%)"),
            yaxis2=dict(title="Avg Risk Score", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=10, r=10, t=30, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig_sim, use_container_width=True)

        st.subheader("Simulation Table")
        st.dataframe(comp_df, use_container_width=True, height=320)
        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 8: Download Report
    # ============================================
    elif section == "📥 Download Report":
        st.header("📥 Download Migration Report")
        try:
            risk_df = calculate_risk_scores(df=telemetry_df)
            plan = get_migration_order(risk_df=risk_df)
            cost_df = estimate_cloud_cost(df=telemetry_df)
            sims = compare_strategies(risk_df=risk_df)
            rec = get_recommended_plan(sims)
            try:
                failure_df = get_failure_predictions(df=telemetry_df)
            except Exception:
                failure_df = risk_df[["service"]].copy()
                failure_df["failure_probability"] = (risk_df["risk_score"] / 100).round(4)
                failure_df["predicted_risk"] = ["High" if r > 0.6 else "Low" for r in failure_df["failure_probability"]]
        except Exception as e:
            import traceback
            st.error(f"Error preparing report: {e}")
            st.code(traceback.format_exc(), language="text")
            st.stop()

        report = f"""
# AI Cloud Migration Copilot - Migration Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Executive Summary
- Total Services: {len(risk_df)}
- Recommended Strategy: {rec['strategy']}
- Estimated Downtime: {rec['downtime_pct']}%
- Total Monthly Cloud Cost: ${get_total_estimated_cost(cost_df):.2f}

## Migration Order
{format_migration_plan(plan)}

## Risk Analysis (Top 10)
{risk_df.head(10).to_string()}

## Cost Estimation
{cost_df.to_string()}

## Failure Predictions
{failure_df.to_string()}
"""
        st.download_button(
            "📥 Download Report (Markdown)",
            report,
            file_name=f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )
        st.code(report[:2000] + "\n...", language="markdown")
    
if __name__ == "__main__":
    main()

