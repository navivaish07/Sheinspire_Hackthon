"""
Module 9 — Interactive Streamlit Dashboard
AI Cloud Migration Copilot - Hackathon Demo
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
from simulation.migration_simulator import compare_strategies, get_recommended_plan
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
        font-size: 3rem;
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
        font-size: 1.35rem;
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
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(240, 246, 252, 0.1);
        position: relative;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 
            0 12px 24px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(56, 139, 253, 0.2);
    }

    .metric-content {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .metric-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        background: linear-gradient(135deg, rgba(56, 139, 253, 0.2), rgba(163, 113, 247, 0.15));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
        border: 1px solid rgba(56, 139, 253, 0.2);
    }

    .metric-text {
        flex: 1;
        min-width: 0;
    }

    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #e6edf3;
        margin-bottom: 0.25rem;
        line-height: 1;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #8b949e;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .metric-subtitle {
        font-size: 0.7rem;
        color: #6e7681;
        font-weight: 400;
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
        font-size: 1.25rem;
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
        font-size: 0.85rem;
        color: #8b949e;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    /* ========================================
       UPLOAD SECTION - Professional Drag & Drop
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
        font-size: 1.1rem;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.5rem;
    }
    
    .upload-subtitle {
        font-size: 0.85rem;
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
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #388bfd;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }

    .step-service {
        font-size: 1rem;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.25rem;
    }

    .step-meta {
        font-size: 0.8rem;
        color: #8b949e;
    }

    /* Risk level indicators */
    .risk-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
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
        font-size: 0.95rem;
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
        padding: 0.6rem 0;
        border-bottom: 1px solid rgba(240, 246, 252, 0.06);
    }

    .recommendation-item:last-child {
        border-bottom: none;
    }

    .item-label {
        font-size: 0.75rem;
        color: #8b949e;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .item-value {
        font-size: 0.85rem;
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
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
        justify-content: flex-start !important;
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
    """Create an interactive PyVis network graph for service dependencies."""
    deps = discover_dependencies(df=df)
    risk_df = calculate_risk_scores(df=df)

    G = build_dependency_graph(dependencies=deps)

    net = Network(height="600px", width="100%", bgcolor="#0d1117", font_color="#e6edf3")

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": {
          "enabled": true,
          "iterations": 1000
        }
      },
      "nodes": {
        "font": {
          "size": 14,
          "color": "#e6edf3",
          "face": "Inter"
        },
        "borderWidth": 2
      },
      "edges": {
        "color": {
          "color": "#388bfd",
          "opacity": 0.6
        },
        "width": 2,
        "smooth": {
          "enabled": true,
          "type": "continuous"
        }
      },
      "interaction": {
        "hover": true,
        "multiselect": true,
        "navigationButtons": true
      }
    }
    """)

    for node in G.nodes():
        risk_data = risk_df[risk_df['service'] == node]
        if not risk_data.empty:
            risk_score = risk_data['risk_score'].iloc[0]
            risk_level = risk_data['risk_level'].iloc[0]
            dep_count = risk_data['dependency_count'].iloc[0]
        else:
            risk_score = 50
            risk_level = "Medium"
            dep_count = G.degree(node)

        size = 20 + (risk_score / 100) * 30

        if risk_level == "High":
            color = "#f85149"
        elif risk_level == "Medium":
            color = "#d29922"
        else:
            color = "#3fb950"

        title = f"""
        <div style="background: rgba(13, 17, 23, 0.95); padding: 10px; border-radius: 8px; border: 1px solid rgba(240,246,252,0.1);">
            <strong>{node}</strong><br>
            Risk Level: <span style="color: {color};">{risk_level}</span><br>
            Risk Score: {risk_score}<br>
            Dependencies: {dep_count}
        </div>
        """

        net.add_node(
            node,
            label=node,
            size=size,
            color=color,
            title=title,
            font={"size": 12, "color": "#e6edf3"}
        )

    for edge in G.edges():
        net.add_edge(edge[0], edge[1])

    net.save_graph("temp_graph.html")

    with open("temp_graph.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    import os
    if os.path.exists("temp_graph.html"):
        os.remove("temp_graph.html")

    return html_content


def render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency):
    """Render KPI metrics row at the top of sections."""
    st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4, gap="large")

    with kpi_col1:
        st.markdown(
            f"""
            <div class="metric-card">
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

    with kpi_col2:
        st.markdown(
            f"""
            <div class="metric-card">
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

    with kpi_col3:
        st.markdown(
            f"""
            <div class="metric-card">
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

    with kpi_col4:
        st.markdown(
            f"""
            <div class="metric-card">
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
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    # Data source: upload or default
    telemetry_df = get_telemetry_data()

    # Pre-compute core analytics for KPIs and sections
    try:
        deps = discover_dependencies(df=telemetry_df)
    except Exception:
        deps = []

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
            ("🕸️ Dependency Graph", "graph"),
            ("⚠️ Risk Analysis", "risk"),
            ("📋 Migration Plan", "plan"),
            ("🎯 Simulation", "simulation"),
            ("📥 Download Report", "download"),
        ]

        if "current_section" not in st.session_state:
            st.session_state.current_section = "dashboard"

        for label, key in nav_options:
            icon = label.split()[0]
            text = " ".join(label.split()[1:])
            if st.button(f"{icon} {text}", key=f"nav_{key}", help=f"Navigate to {text}", width='stretch'):
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
        <div style="text-align: center; padding: 1.5rem 1rem 2rem;">
            <h1 style="font-size: 3rem; font-weight: 700; color: #e6edf3; margin-bottom: 0.75rem; letter-spacing: -0.02em; line-height: 1.2;">🚀 AI Cloud Migration Copilot</h1>
            <p style="font-size: 1.35rem; color: #8b949e; max-width: 900px; margin: 0 auto; line-height: 1.6; white-space: nowrap;">AI-Based Intelligent System for Automated Microservice Dependency Analysis and Cloud Migration Planning</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Drag & Drop CSV Upload Section (Under KPI)
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
        
        # Render KPI Metrics Row
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)

        # MAIN CONTENT AREA - Row 1: Dependency Graph + AI Recommendation
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕸️ Service Dependency Graph</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-subtitle">Interactive topology of microservice dependencies with AI-powered migration recommendations.</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([3, 1], gap="large")

        with col1:
            graph_html = create_dependency_graph(telemetry_df)
            components.html(graph_html, height=500, width=None)

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

        # MAIN CONTENT AREA - Row 2: Risk Heatmap + Migration Strategy Summary
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        row2_col1, row2_col2 = st.columns(2, gap="large")

        with row2_col1:
            st.markdown('<div class="section-title">⚠️ Risk Heatmap</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Service risk distribution by latency and error rate.</div>', unsafe_allow_html=True)
            
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

        # MAIN CONTENT AREA - Row 3: CPU Usage + Error Rate Monitoring Charts
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        
        row3_col1, row3_col2 = st.columns(2, gap="large")

        with row3_col1:
            st.markdown('<div class="section-title">💻 CPU Usage per Service</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">CPU utilization of each microservice.</div>', unsafe_allow_html=True)
            
            if not risk_df.empty:
                if "cpu_usage_pct" not in risk_df.columns and "cpu_usage" in telemetry_df.columns:
                    cpu_data = telemetry_df.groupby("service_name")["cpu_usage"].mean().reset_index()
                    cpu_data.columns = ["service", "cpu_usage_pct"]
                elif "cpu_usage_pct" in risk_df.columns:
                    cpu_data = risk_df[["service", "cpu_usage_pct"]].copy()
                else:
                    cpu_data = risk_df[["service"]].copy()
                    cpu_data["cpu_usage_pct"] = (risk_df["risk_score"] * 0.8 + 10).round(1)
                
                fig_cpu = px.bar(
                    cpu_data,
                    x="service",
                    y="cpu_usage_pct",
                    template="plotly_dark",
                    color="cpu_usage_pct",
                    color_continuous_scale=px.colors.sequential.Blues,
                )
                fig_cpu.update_layout(
                    title="CPU Usage per Service",
                    xaxis_title="Service",
                    yaxis_title="CPU Usage (%)",
                    margin=dict(l=40, r=40, t=40, b=40),
                    height=400,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_cpu, use_container_width=True)

        with row3_col2:
            st.markdown('<div class="section-title">❌ Error Rate per Service</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-subtitle">Failure/error rate of each microservice.</div>', unsafe_allow_html=True)
            
            if not risk_df.empty:
                if "error_rate" in risk_df.columns:
                    error_data = risk_df[["service", "error_rate"]].copy()
                else:
                    error_data = risk_df[["service"]].copy()
                    error_data["error_rate"] = (risk_df["risk_score"] / 100 * 5).round(3)
                
                fig_err = px.bar(
                    error_data,
                    x="service",
                    y="error_rate",
                    template="plotly_dark",
                    color="error_rate",
                    color_continuous_scale=px.colors.sequential.Reds,
                )
                fig_err.update_layout(
                    title="Error Rate per Service",
                    xaxis_title="Service",
                    yaxis_title="Error Rate (%)",
                    margin=dict(l=40, r=40, t=40, b=40),
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
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)
        
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
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)
        
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🕸️ Service Dependency Graph</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Interactive topology of microservice dependencies with AI-powered migration recommendations.</div>', unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1], gap="large")

        with col1:
            graph_html = create_dependency_graph(telemetry_df)
            components.html(graph_html, height=650, width=None)

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
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)
        
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
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)
        
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

        st.subheader("Plan Details")
        st.dataframe(pd.DataFrame(plan), use_container_width=True, height=360)

        st.markdown("</div>", unsafe_allow_html=True)

    # ============================================
    # SECTION 7: Migration Simulation
    # ============================================
    elif section == "🎯 Simulation":
        render_kpi_metrics(total_services, total_dependencies, high_risk_services, avg_latency)
        
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
            mime="text/markdown",
        )
        st.code(report[:2000] + "\n...", language="markdown")


if __name__ == "__main__":
    main()

