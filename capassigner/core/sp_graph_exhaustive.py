"""SP Graph Exhaustive Enumeration and Reduction.

This module implements the SP Graph Exhaustive method, which enumerates all
connected multigraph topologies with N edges and iteratively reduces them
using Series-Parallel rules. This allows finding solutions for circuits with
internal nodes that are SP-reducible but not representable as simple binary trees.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact graph reduction
    - Principle IV (Modular Architecture): No Streamlit imports
    - Principle V (Performance Awareness): Efficient graph operations
"""

from __future__ import annotations
from typing import List, Optional, Any, Callable
from itertools import combinations, combinations_with_replacement, permutations
import networkx as nx

from capassigner.core.metrics import Solution, ProgressUpdate, ProgressCallback, create_solution, rank_solutions
from capassigner.core.graphs import GraphTopology

def solve(
    capacitors: List[float],
    target: float,
    max_results: int = 10,
    progress_callback: Optional[ProgressCallback] = None
) -> List[Solution]:
    """
    Enumerates all connected multigraph topologies for len(capacitors) edges.
    Assigns capacitors to edges.
    Checks SP-reducibility.
    Returns sorted list of Solutions.
    """
    num_edges = len(capacitors)
    topologies = generate_topologies(num_edges)
    
    solutions = []
    seen_values = set() # To deduplicate by C_eq
    
    total_steps = len(topologies)
    current_step = 0
    
    for G_template in topologies:
        nodes = list(G_template.nodes())
        edges = list(G_template.edges(keys=True)) # (u, v, key)
        
        # Iterate all pairs of terminals
        for term_a, term_b in combinations(nodes, 2):
            
            # Iterate all permutations of capacitors
            for cap_perm in permutations(capacitors):
                # Assign capacitors to edges
                G = G_template.copy()
                for i, (u, v, k) in enumerate(edges):
                    G[u][v][k]['capacity'] = cap_perm[i]
                
                ceq = is_sp_reducible(G, term_a, term_b)
                
                if ceq is not None:
                    # Deduplicate by value (approximate)
                    if any(abs(ceq - v) < 1e-15 for v in seen_values):
                        continue
                    seen_values.add(ceq)
                    
                    # Create internal nodes list
                    internal = [n for n in nodes if n != term_a and n != term_b]
                    
                    topo = GraphTopology(
                        graph=G,
                        terminal_a=term_a,
                        terminal_b=term_b,
                        internal_nodes=internal
                    )
                    
                    # Expression
                    expression = f"Graph(V={len(nodes)}, E={num_edges})"
                    
                    # Use default tolerance 5.0 for creation, can be filtered later
                    sol = create_solution(topo, ceq, target, 5.0, expression)
                    solutions.append(sol)
        
        current_step += 1
        if progress_callback:
             progress_callback(ProgressUpdate(
                current=current_step,
                total=total_steps,
                message=f"Analyzing topology {current_step}/{total_steps}",
                best_error=None
            ))
            
    return rank_solutions(solutions)[:max_results]

def generate_topologies(num_edges: int) -> List[nx.MultiGraph]:
    """
    Generates all unique connected multigraphs with num_edges.
    
    Iterates through possible number of nodes V from 2 to num_edges + 1.
    Generates all multigraphs with num_edges on V nodes.
    Filters for connectivity and isomorphism.
    """
    topologies = []
    # Iterate over possible number of nodes V
    # Minimum 2 nodes (A, B), maximum num_edges + 1 (linear chain)
    for v in range(2, num_edges + 2):
        nodes = range(v)
        # All possible pairs of nodes (potential edge locations)
        possible_pairs = list(combinations(nodes, 2))
        
        # Distribute num_edges into these pairs (multigraph allowed)
        # combinations_with_replacement allows multiple edges between same pair
        for edges in combinations_with_replacement(possible_pairs, num_edges):
            G = nx.MultiGraph()
            G.add_nodes_from(nodes)
            G.add_edges_from(edges)
            
            if not nx.is_connected(G):
                continue
                
            # Check isomorphism against found topologies
            # Note: For larger N, this is slow. But for N<=6 it's acceptable.
            if any(nx.is_isomorphic(G, existing) for existing in topologies):
                continue
                
            topologies.append(G)
    return topologies

def is_sp_reducible(graph: nx.MultiGraph, term_a: Any, term_b: Any) -> Optional[float]:
    """
    Check if graph is SP-reducible and calculate C_eq.
    
    Iteratively applies parallel and series reduction rules.
    Returns equivalent capacitance if graph reduces to a single edge between terminals.
    Returns None if irreducible or disconnected.
    """
    # Work on a copy to avoid modifying the original
    G = graph.copy()
    
    changed = True
    while changed:
        changed = False
        
        # 1. Parallel Reduction
        # Identify edges (u, v) with multiplicity > 1
        parallel_reductions = []
        # Iterate over edges to find parallel bundles
        # We use set of pairs to avoid duplicates
        processed_pairs = set()
        
        for u in list(G.nodes()):
            for v in list(G.neighbors(u)):
                pair = tuple(sorted((u, v)))
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                
                if G.number_of_edges(u, v) > 1:
                    # Found parallel edges
                    total_cap = 0.0
                    for key in G[u][v]:
                        total_cap += G[u][v][key]['capacity']
                    parallel_reductions.append((u, v, total_cap))
        
        for u, v, total_cap in parallel_reductions:
            # Remove all edges between u, v
            keys = list(G[u][v].keys())
            for k in keys:
                G.remove_edge(u, v, key=k)
            # Add single combined edge
            G.add_edge(u, v, capacity=total_cap)
            changed = True
            
        if changed: continue # Restart loop if modified
        
        # 2. Series Reduction
        # Find degree-2 nodes that are not terminals
        series_node = None
        for n in list(G.nodes()):
            if n == term_a or n == term_b:
                continue
            if G.degree(n) == 2:
                series_node = n
                break
        
        if series_node is not None:
            neighbors = list(G.neighbors(series_node))
            # Handle standard series case: u -- n -- v where u != v
            if len(set(neighbors)) == 2:
                u, v = neighbors
                # Get capacitances (assume single edge after parallel reduction)
                # Note: G[u][n] is a dict of edges. We take the first one (key 0 usually)
                # But keys might not be 0 if edges were added/removed.
                # Use list(G[u][n].values())[0]
                c1 = list(G[u][series_node].values())[0]['capacity']
                c2 = list(G[series_node][v].values())[0]['capacity']
                
                c_new = 1.0 / (1.0/c1 + 1.0/c2)
                
                G.remove_node(series_node)
                G.add_edge(u, v, capacity=c_new)
                changed = True
            elif len(set(neighbors)) == 1:
                # u -- n -- u (hanging loop). Remove it?
                # A hanging loop doesn't affect C_eq between A and B unless it's the only path?
                # If it's a dead end, we can remove it.
                # But strictly, series reduction applies to 2 distinct neighbors.
                # If we have a dead end, it's not series in the flow sense.
                # We can prune dead ends (degree 1) but degree 2 loop is weird.
                # Let's ignore for now, or remove node if it's not terminal.
                # If we remove it, we break the loop.
                G.remove_node(series_node)
                changed = True
                
    # Check result
    if G.number_of_nodes() == 2 and G.number_of_edges() == 1:
        if G.has_edge(term_a, term_b):
             return list(G[term_a][term_b].values())[0]['capacity']
    
    return None
