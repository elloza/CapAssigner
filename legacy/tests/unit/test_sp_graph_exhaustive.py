"""Unit tests for SP Graph Exhaustive module."""

import pytest
import networkx as nx
from capassigner.core.sp_graph_exhaustive import solve, generate_topologies, is_sp_reducible

def test_generate_topologies_n2():
    """Test topology generation for N=2 edges."""
    # N=2 edges.
    # V=2: A=B (parallel)
    # V=3: A-C-B (series)
    topos = generate_topologies(2)
    # Should have 2 topologies: Parallel (2 nodes, 2 edges) and Series (3 nodes, 2 edges)
    assert len(topos) == 2
    
    # Check properties
    nodes_counts = sorted([G.number_of_nodes() for G in topos])
    assert nodes_counts == [2, 3]

def test_is_sp_reducible_series():
    """Test reduction of simple series circuit."""
    G = nx.MultiGraph()
    G.add_edge(0, 1, capacity=2.0)
    G.add_edge(1, 2, capacity=2.0)
    # 2 series 2 = 1
    ceq = is_sp_reducible(G, 0, 2)
    assert ceq == 1.0

def test_is_sp_reducible_parallel():
    """Test reduction of simple parallel circuit."""
    G = nx.MultiGraph()
    G.add_edge(0, 1, key='a', capacity=2.0)
    G.add_edge(0, 1, key='b', capacity=3.0)
    # 2 parallel 3 = 5
    ceq = is_sp_reducible(G, 0, 1)
    assert ceq == 5.0

def test_is_sp_reducible_bridge_fail():
    """Test that Wheatstone bridge is NOT reducible."""
    # Wheatstone bridge: 5 edges, 4 nodes.
    # A-C, A-D, C-B, D-B, C-D
    G = nx.MultiGraph()
    G.add_edge('A', 'C', capacity=1.0)
    G.add_edge('A', 'D', capacity=1.0)
    G.add_edge('C', 'B', capacity=1.0)
    G.add_edge('D', 'B', capacity=1.0)
    G.add_edge('C', 'D', capacity=1.0) # Bridge
    
    ceq = is_sp_reducible(G, 'A', 'B')
    assert ceq is None

def test_solve_simple():
    """Test solve with simple inputs."""
    caps = [2.0, 2.0]
    target = 1.0
    solutions = solve(caps, target)
    
    # Should find series solution (2+2=1)
    assert len(solutions) > 0
    best = solutions[0]
    assert abs(best.ceq - 1.0) < 1e-9
    assert best.absolute_error < 1e-9

def test_classroom_problem_graph_method():
    """Test the Classroom Problem using SP Graph method."""
    capacitors = [3e-12, 2e-12, 3e-12, 1e-12]
    target = 1.0e-12
    
    solutions = solve(capacitors, target)
    
    assert len(solutions) > 0
    best = solutions[0]
    assert best.absolute_error < 1e-15
