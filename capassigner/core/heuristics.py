"""Heuristic search for network topology optimization.

This module implements random graph generation and heuristic search
for finding capacitor network topologies that match a target capacitance.
Uses random graph exploration with Laplacian-based C_eq calculation.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Uses validated Laplacian method
    - Principle IV (Modular Architecture): No Streamlit imports
    - Principle V (Performance Awareness): Configurable iterations

Requirements: FR-018 to FR-022
"""

from __future__ import annotations
from typing import List, Optional, Callable

import networkx as nx
import numpy as np

from capassigner.core.graphs import (
    GraphTopology,
    calculate_graph_ceq,
    is_connected_between_terminals,
    graph_topology_to_expression,
)
from capassigner.core.metrics import (
    ProgressUpdate,
    Solution,
    calculate_absolute_error,
    calculate_relative_error,
    check_within_tolerance,
)


def generate_random_graph(
    capacitors: List[float],
    max_internal_nodes: int = 2,
    seed: Optional[int] = None,
    rng: Optional[np.random.Generator] = None
) -> nx.Graph:
    """Generate random graph topology with given parameters.

    Creates a random graph with terminals 'A' and 'B' plus internal nodes,
    then assigns random capacitor values from the inventory to edges.

    Args:
        capacitors: Available capacitance values to sample from (in Farads).
        max_internal_nodes: Maximum number of internal nodes (besides A and B).
        seed: Random seed for determinism (None for random).
        rng: Optional numpy random generator (takes precedence over seed).

    Returns:
        NetworkX graph with terminals 'A', 'B' and internal nodes 'n1', 'n2', etc.
        All edges have 'capacitance' attribute.

    Raises:
        ValueError: If capacitors list is empty.
        ValueError: If max_internal_nodes < 0.

    Example:
        >>> G = generate_random_graph([5e-12, 10e-12], max_internal_nodes=1, seed=42)
        >>> list(G.nodes())
        ['A', 'B', 'n1']
    """
    if not capacitors:
        raise ValueError("Cannot generate graph with no capacitors")
    if max_internal_nodes < 0:
        raise ValueError("max_internal_nodes must be non-negative")

    # Use provided RNG or create new one
    if rng is None:
        rng = np.random.default_rng(seed)

    # Total nodes: A, B + internal nodes
    # Choose random number of internal nodes from 0 to max_internal_nodes
    n_internal = rng.integers(0, max_internal_nodes + 1)
    total_nodes = 2 + n_internal

    # Node labels
    nodes = ['A', 'B'] + [f'n{i+1}' for i in range(n_internal)]

    # Create empty graph and add nodes
    G = nx.Graph()
    G.add_nodes_from(nodes)

    # Generate random edges
    # For N nodes, number of edges between N-1 (minimum connected) and N*(N-1)/2 (complete)
    max_edges = total_nodes * (total_nodes - 1) // 2
    min_edges = total_nodes - 1  # Minimum for connected graph

    n_edges = rng.integers(min_edges, max_edges + 1)

    # Generate all possible edges
    possible_edges = []
    for i, u in enumerate(nodes):
        for j, v in enumerate(nodes):
            if i < j:
                possible_edges.append((u, v))

    # Randomly select edges
    selected_indices = rng.choice(
        len(possible_edges),
        size=min(n_edges, len(possible_edges)),
        replace=False
    )

    # Add edges with random capacitor values
    for idx in selected_indices:
        u, v = possible_edges[idx]
        cap = rng.choice(capacitors)
        G.add_edge(u, v, capacitance=cap)

    return G


def _ensure_connected(
    graph: nx.Graph,
    capacitors: List[float],
    rng: np.random.Generator,
    terminal_a: str = 'A',
    terminal_b: str = 'B'
) -> bool:
    """Ensure graph is connected between terminals, adding edges if needed.

    Modifies the graph in-place to add edges that connect components.

    Args:
        graph: NetworkX graph to potentially modify.
        capacitors: Available capacitance values.
        rng: Random number generator.
        terminal_a: Terminal A node.
        terminal_b: Terminal B node.

    Returns:
        True if graph is connected (possibly after modification), False otherwise.
    """
    # Find connected components
    components = list(nx.connected_components(graph))

    if len(components) == 1:
        return True  # Already connected

    # Find which component contains A and which contains B
    comp_a = None
    comp_b = None

    for i, comp in enumerate(components):
        if terminal_a in comp:
            comp_a = i
        if terminal_b in comp:
            comp_b = i

    if comp_a is None or comp_b is None:
        return False  # Terminals not in graph

    if comp_a == comp_b:
        return True  # Already in same component

    # Connect components by adding an edge between them
    nodes_a = list(components[comp_a])
    nodes_b = list(components[comp_b])

    u = rng.choice(nodes_a)
    v = rng.choice(nodes_b)
    cap = rng.choice(capacitors)
    graph.add_edge(u, v, capacitance=cap)

    return True


def generate_connected_graph(
    capacitors: List[float],
    max_internal_nodes: int = 2,
    seed: Optional[int] = None,
    rng: Optional[np.random.Generator] = None,
    max_attempts: int = 10
) -> Optional[nx.Graph]:
    """Generate a random graph that is guaranteed to be connected.

    Attempts to generate a connected graph, regenerating if necessary.

    Args:
        capacitors: Available capacitance values (in Farads).
        max_internal_nodes: Maximum number of internal nodes.
        seed: Random seed for determinism.
        rng: Optional numpy random generator.
        max_attempts: Maximum attempts to generate connected graph.

    Returns:
        Connected NetworkX graph, or None if max_attempts exceeded.

    Example:
        >>> G = generate_connected_graph([5e-12, 10e-12], max_internal_nodes=2, seed=42)
        >>> nx.is_connected(G)
        True
    """
    if rng is None:
        rng = np.random.default_rng(seed)

    for _ in range(max_attempts):
        G = generate_random_graph(capacitors, max_internal_nodes, rng=rng)

        # Try to ensure connectivity
        if _ensure_connected(G, capacitors, rng, 'A', 'B'):
            if is_connected_between_terminals(G, 'A', 'B'):
                return G

    return None


def heuristic_search(
    capacitors: List[float],
    target: float,
    iterations: int = 2000,
    max_internal_nodes: int = 2,
    seed: int = 0,
    tolerance: float = 5.0,
    top_k: int = 10,
    progress_cb: Optional[Callable[[ProgressUpdate], None]] = None
) -> List[Solution]:
    """Find best solutions using random graph generation.

    Generates random graph topologies, calculates their equivalent capacitance
    using the Laplacian method, and returns the best matches sorted by error.

    Args:
        capacitors: Available capacitance values in Farads.
        target: Target capacitance in Farads.
        iterations: Number of random graphs to generate.
        max_internal_nodes: Maximum internal nodes per graph.
        seed: Random seed for determinism.
        tolerance: Acceptable relative error percentage.
        top_k: Number of best solutions to return.
        progress_cb: Optional callback for progress updates.

    Returns:
        Top-K solutions sorted by absolute error.

    Raises:
        ValueError: If target <= 0.
        ValueError: If iterations < 1.
        ValueError: If capacitors list is empty.

    Example:
        >>> solutions = heuristic_search(
        ...     capacitors=[5e-12, 10e-12],
        ...     target=7.5e-12,
        ...     iterations=1000,
        ...     seed=42,
        ...     top_k=3
        ... )
        >>> len(solutions) <= 3
        True
    """
    # Validate inputs
    if target <= 0:
        raise ValueError("Target capacitance must be positive")
    if iterations < 1:
        raise ValueError("Iterations must be at least 1")
    if not capacitors:
        raise ValueError("Cannot search with no capacitors")

    # Initialize random generator with seed for determinism
    rng = np.random.default_rng(seed)

    # Track all valid solutions
    solutions: List[Solution] = []
    best_error = float('inf')

    for i in range(iterations):
        # Generate connected random graph
        graph = generate_connected_graph(
            capacitors,
            max_internal_nodes,
            rng=rng,
            max_attempts=10
        )

        if graph is None:
            # Failed to generate connected graph, skip this iteration
            continue

        # Calculate equivalent capacitance
        ceq, warning = calculate_graph_ceq(graph, 'A', 'B')

        if ceq <= 0:
            # Invalid or disconnected network
            continue

        # Calculate error metrics
        abs_err = calculate_absolute_error(ceq, target)
        rel_err = calculate_relative_error(ceq, target)
        within_tol = check_within_tolerance(rel_err, tolerance)

        # Track best error
        if abs_err < best_error:
            best_error = abs_err

        # Create topology object
        internal_nodes = [n for n in graph.nodes() if n not in ('A', 'B')]
        topology = GraphTopology(
            graph=graph.copy(),  # Copy to avoid mutation
            terminal_a='A',
            terminal_b='B',
            internal_nodes=internal_nodes
        )

        # Create solution
        expression = graph_topology_to_expression(topology)
        solution = Solution(
            topology=topology,
            ceq=ceq,
            target=target,
            absolute_error=abs_err,
            relative_error=rel_err,
            within_tolerance=within_tol,
            expression=expression,
            diagram=None
        )
        solutions.append(solution)

        # Progress callback every 50 iterations
        if progress_cb is not None and (i + 1) % 50 == 0:
            progress_cb(ProgressUpdate(
                current=i + 1,
                total=iterations,
                message=f"Iteration {i + 1}/{iterations}",
                best_error=best_error
            ))

    # Final progress update
    if progress_cb is not None:
        progress_cb(ProgressUpdate(
            current=iterations,
            total=iterations,
            message=f"Completed {iterations} iterations",
            best_error=best_error if best_error < float('inf') else None
        ))

    # Sort solutions by absolute error and return top K
    solutions.sort(key=lambda s: s.absolute_error)
    return solutions[:top_k]
