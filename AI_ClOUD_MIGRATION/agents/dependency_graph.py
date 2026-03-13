"""
Module 3 — Dependency Graph Engine
Converts dependencies into a directed graph using NetworkX.
"""

import networkx as nx
import pandas as pd
from typing import List, Tuple, Dict, Any
from .service_discovery import discover_dependencies
import os


def build_dependency_graph(dependencies: List[Tuple[str, str]] = None) -> nx.DiGraph:
    """Build directed graph from dependency list."""
    if dependencies is None:
        dependencies = discover_dependencies()
    
    G = nx.DiGraph()
    for src, tgt in dependencies:
        G.add_edge(src, tgt)
    
    return G


def get_upstream_dependencies(G: nx.DiGraph, service: str) -> List[str]:
    """Get services that depend on this service (callers)."""
    return list(G.predecessors(service))


def get_downstream_dependencies(G: nx.DiGraph, service: str) -> List[str]:
    """Get services this service depends on (callees)."""
    return list(G.successors(service))


def get_critical_nodes(G: nx.DiGraph, top_n: int = 5) -> List[str]:
    """Identify critical nodes by betweenness centrality."""
    if G.number_of_nodes() == 0:
        return []
    centrality = nx.betweenness_centrality(G)
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return [n[0] for n in sorted_nodes[:top_n]]


def get_dependency_chains(G: nx.DiGraph, max_depth: int = 5) -> List[List[str]]:
    """Find longest dependency chains."""
    chains = []
    for node in G.nodes():
        if G.in_degree(node) == 0:  # Entry point
            for path in nx.all_simple_paths(G, node, list(G.nodes()), cutoff=max_depth):
                if len(path) > 1:
                    chains.append(path)
    
    # Sort by length, return longest
    chains.sort(key=len, reverse=True)
    return chains[:10]


def graph_to_plotly_data(G: nx.DiGraph, layout: str = "spring") -> Dict[str, Any]:
    """Convert graph to Plotly-compatible format for visualization."""
    if layout == "spring":
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    elif layout == "hierarchical":
        pos = nx.planar_layout(G) if nx.is_planar(G) else nx.spring_layout(G, seed=42)
    else:
        pos = nx.spring_layout(G, seed=42)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    
    # Node sizes based on degree
    degrees = dict(G.degree())
    node_sizes = [20 + degrees[n] * 8 for n in G.nodes()]
    
    return {
        "edge_x": edge_x,
        "edge_y": edge_y,
        "node_x": node_x,
        "node_y": node_y,
        "node_labels": list(G.nodes()),
        "node_sizes": node_sizes,
        "edges": list(G.edges()),
    }


def get_graph_metrics(G: nx.DiGraph) -> Dict[str, Any]:
    """Get graph metrics for dashboard."""
    return {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "critical_nodes": get_critical_nodes(G),
        "entry_points": [n for n in G.nodes() if G.in_degree(n) == 0],
        "leaf_services": [n for n in G.nodes() if G.out_degree(n) == 0],
    }


if __name__ == "__main__":
    G = build_dependency_graph()
    print("Graph nodes:", G.number_of_nodes())
    print("Graph edges:", G.number_of_edges())
    print("Critical nodes:", get_critical_nodes(G))
    print("Entry points:", [n for n in G.nodes() if G.in_degree(n) == 0])
