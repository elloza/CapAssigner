"""Graph-based network analysis using Laplacian methods.

This module implements capacitance calculation for general (non-SP) networks
using nodal analysis with the Laplacian matrix. Handles disconnected networks,
singular matrices, and floating nodes robustly.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact Laplacian formulas Y = s·C
    - Principle IV (Modular Architecture): No Streamlit imports
    - Principle V (Performance Awareness): Efficient matrix operations

Requirements: FR-003 to FR-007
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

import networkx as nx
import numpy as np


@dataclass
class GraphTopology:
    """General graph network representation.

    Represents a network of capacitors as a graph where nodes are connection
    points and edges are capacitors. Terminals A and B are the measurement
    points for equivalent capacitance.

    Attributes:
        graph: NetworkX graph with 'capacitance' edge attribute (in Farads).
        terminal_a: Node identifier for terminal A (typically 'A').
        terminal_b: Node identifier for terminal B (typically 'B').
        internal_nodes: List of internal node identifiers (excluding A and B).

    Example:
        >>> import networkx as nx
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'n1', capacitance=5e-12)
        >>> G.add_edge('n1', 'B', capacitance=10e-12)
        >>> topology = GraphTopology(G, 'A', 'B', ['n1'])
    """
    graph: nx.Graph
    terminal_a: str
    terminal_b: str
    internal_nodes: List[str]


def build_laplacian_matrix(graph: nx.Graph) -> Tuple[np.ndarray, List[str]]:
    """Construct Laplacian matrix from graph.

    The Laplacian matrix L is defined as:
    - L[i][i] = sum of capacitances at node i (diagonal)
    - L[i][j] = -C_ij if edge exists between i and j (off-diagonal)

    Args:
        graph: NetworkX graph with 'capacitance' edge attribute.

    Returns:
        Tuple of (Laplacian matrix as np.ndarray, ordered list of node labels).
        Matrix is NxN where N is number of nodes.

    Raises:
        ValueError: If any edge is missing the 'capacitance' attribute.

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', capacitance=5e-12)
        >>> L, nodes = build_laplacian_matrix(G)
        >>> # L = [[5e-12, -5e-12], [-5e-12, 5e-12]]
    """
    nodes = list(graph.nodes())
    n = len(nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}

    # Initialize Laplacian matrix with zeros
    L = np.zeros((n, n), dtype=np.float64)

    # Build Laplacian from edges
    for u, v, data in graph.edges(data=True):
        if 'capacitance' not in data:
            raise ValueError("All edges must have 'capacitance' attribute")

        cap = data['capacitance']
        i, j = node_to_idx[u], node_to_idx[v]

        # Off-diagonal: -C_ij
        L[i, j] -= cap
        L[j, i] -= cap

        # Diagonal: +C_ij for both nodes
        L[i, i] += cap
        L[j, j] += cap

    return L, nodes


def is_connected_between_terminals(
    graph: nx.Graph,
    terminal_a: str = 'A',
    terminal_b: str = 'B'
) -> bool:
    """Check if path exists between terminals A and B.

    Args:
        graph: NetworkX graph.
        terminal_a: Node identifier for terminal A.
        terminal_b: Node identifier for terminal B.

    Returns:
        True if path exists from A to B, False otherwise.
        Returns False if either terminal is not in the graph.

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'B', capacitance=5e-12)
        >>> is_connected_between_terminals(G, 'A', 'B')
        True
    """
    if terminal_a not in graph or terminal_b not in graph:
        return False

    return nx.has_path(graph, terminal_a, terminal_b)


def calculate_graph_ceq(
    graph: nx.Graph,
    terminal_a: str = 'A',
    terminal_b: str = 'B'
) -> Tuple[float, Optional[str]]:
    """Calculate equivalent capacitance using Laplacian matrix method.

    Uses nodal analysis with boundary conditions V_A = 1, V_B = 0.
    Solves for internal node voltages, then calculates current into A
    to determine equivalent capacitance: C_eq = I_A / (V_A - V_B) = I_A.

    Args:
        graph: NetworkX graph with 'capacitance' edge attribute (in Farads).
        terminal_a: Node identifier for terminal A.
        terminal_b: Node identifier for terminal B.

    Returns:
        Tuple of (C_eq in Farads, warning message or None).
        - Returns (0.0, "No path between A and B") if disconnected.
        - Returns (ceq, "Warning: Singular matrix, using pseudo-inverse")
          if matrix is singular.

    Raises:
        ValueError: If terminal_a or terminal_b not in graph.
        ValueError: If any edge is missing 'capacitance' attribute.

    Example:
        >>> G = nx.Graph()
        >>> G.add_edge('A', 'n1', capacitance=10e-12)
        >>> G.add_edge('n1', 'B', capacitance=10e-12)
        >>> ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        >>> ceq  # Series: 1/(1/10e-12 + 1/10e-12) = 5e-12
        5e-12
    """
    # Validate terminals exist
    if terminal_a not in graph:
        raise ValueError(f"Terminal '{terminal_a}' must be a node in graph")
    if terminal_b not in graph:
        raise ValueError(f"Terminal '{terminal_b}' must be a node in graph")

    # Check connectivity
    if not is_connected_between_terminals(graph, terminal_a, terminal_b):
        return 0.0, "No path between A and B"

    # Handle trivial case: direct edge between A and B only
    nodes = list(graph.nodes())
    if len(nodes) == 2:
        # Direct connection: C_eq is sum of parallel capacitances
        total_cap = 0.0
        for u, v, data in graph.edges(data=True):
            if 'capacitance' not in data:
                raise ValueError("All edges must have 'capacitance' attribute")
            total_cap += data['capacitance']
        return total_cap, None

    # Build Laplacian matrix
    L, node_list = build_laplacian_matrix(graph)
    node_to_idx = {node: i for i, node in enumerate(node_list)}
    n = len(node_list)

    # Get indices for terminals
    idx_a = node_to_idx[terminal_a]
    idx_b = node_to_idx[terminal_b]

    # Find internal nodes (all nodes except A and B)
    internal_indices = [i for i in range(n) if i != idx_a and i != idx_b]

    warning_message = None

    if len(internal_indices) == 0:
        # Only A and B nodes: C_eq is sum of all edge capacitances (parallel)
        total_cap = 0.0
        for u, v, data in graph.edges(data=True):
            total_cap += data['capacitance']
        return total_cap, None

    # Extract reduced Laplacian for internal nodes
    # L_reduced * V_internal = -L_ai * V_a - L_bi * V_b
    # With V_a = 1, V_b = 0:
    # L_reduced * V_internal = -L_ai (column of L for terminal A at internal rows)

    L_reduced = L[np.ix_(internal_indices, internal_indices)]

    # Right-hand side: -L[internal, a] * 1 - L[internal, b] * 0 = -L[internal, a]
    rhs = -L[internal_indices, idx_a]

    # Solve for internal node voltages
    try:
        # Check condition number for numerical stability
        cond = np.linalg.cond(L_reduced)
        if cond > 1e12:
            # Near-singular: add small regularization
            L_reduced += 1e-15 * np.eye(len(internal_indices))
            warning_message = "Warning: Near-singular matrix, using regularization"

        V_internal = np.linalg.solve(L_reduced, rhs)

    except np.linalg.LinAlgError:
        # Singular matrix: use pseudo-inverse
        try:
            V_internal = np.linalg.pinv(L_reduced) @ rhs
            warning_message = "Warning: Singular matrix, using pseudo-inverse"
        except Exception:
            return 0.0, "Error: Cannot solve matrix system"

    # Check for NaN or Inf
    if np.any(np.isnan(V_internal)) or np.any(np.isinf(V_internal)):
        return 0.0, "Error: Numerical instability in solution"

    # Build full voltage vector: V[a]=1, V[b]=0, V[internal] from solution
    V = np.zeros(n)
    V[idx_a] = 1.0
    V[idx_b] = 0.0
    for i, idx in enumerate(internal_indices):
        V[idx] = V_internal[i]

    # Calculate current into terminal A: I_a = sum over neighbors of (C_aj * (V_a - V_j))
    I_a = 0.0
    for neighbor in graph.neighbors(terminal_a):
        cap = graph[terminal_a][neighbor]['capacitance']
        V_neighbor = V[node_to_idx[neighbor]]
        I_a += cap * (V[idx_a] - V_neighbor)

    # C_eq = I_a / (V_a - V_b) = I_a / 1 = I_a
    ceq = I_a

    # Ensure non-negative (should be positive for valid networks)
    ceq = max(0.0, ceq)

    return ceq, warning_message


def graph_topology_to_expression(topology: GraphTopology) -> str:
    """Generate a human-readable expression for a graph topology.

    Args:
        topology: GraphTopology object.

    Returns:
        String describing the topology (e.g., "Graph(4 nodes, 5 edges)").
    """
    n_nodes = topology.graph.number_of_nodes()
    n_edges = topology.graph.number_of_edges()
    n_internal = len(topology.internal_nodes)
    return f"Graph({n_nodes} nodes, {n_edges} edges, {n_internal} internal)"
