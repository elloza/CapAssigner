"""Unit tests for capassigner.core.graphs module.

Tests the Laplacian method for calculating equivalent capacitance
of general graph topologies.

Requirements tested: FR-003 to FR-007
"""

import pytest
import networkx as nx
import numpy as np

from capassigner.core.graphs import (
    GraphTopology,
    build_laplacian_matrix,
    is_connected_between_terminals,
    calculate_graph_ceq,
    graph_topology_to_expression,
)


class TestGraphTopology:
    """Tests for GraphTopology dataclass."""

    def test_graph_topology_creation(self):
        """Test basic GraphTopology creation."""
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        
        topology = GraphTopology(
            graph=G,
            terminal_a='A',
            terminal_b='B',
            internal_nodes=[]
        )
        
        assert topology.terminal_a == 'A'
        assert topology.terminal_b == 'B'
        assert len(topology.internal_nodes) == 0
        assert topology.graph.number_of_edges() == 1

    def test_graph_topology_with_internal_nodes(self):
        """Test GraphTopology with internal nodes."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        G.add_edge('n1', 'B', capacitance=10e-12)
        
        topology = GraphTopology(
            graph=G,
            terminal_a='A',
            terminal_b='B',
            internal_nodes=['n1']
        )
        
        assert len(topology.internal_nodes) == 1
        assert 'n1' in topology.internal_nodes


class TestBuildLaplacianMatrix:
    """Tests for build_laplacian_matrix function."""

    def test_simple_two_node_graph(self):
        """Test Laplacian for A--[C]--B."""
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        
        L, nodes = build_laplacian_matrix(G)
        
        # Laplacian should be [[5e-12, -5e-12], [-5e-12, 5e-12]]
        assert len(nodes) == 2
        assert L.shape == (2, 2)
        
        # Check symmetry
        assert np.allclose(L, L.T)
        
        # Check row sums are zero (Laplacian property)
        row_sums = np.sum(L, axis=1)
        assert np.allclose(row_sums, 0)
        
        # Check diagonal is positive
        assert L[0, 0] > 0
        assert L[1, 1] > 0

    def test_three_node_series(self):
        """Test Laplacian for A--[C1]--n1--[C2]--B."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        G.add_edge('n1', 'B', capacitance=10e-12)
        
        L, nodes = build_laplacian_matrix(G)
        
        assert len(nodes) == 3
        assert L.shape == (3, 3)
        
        # Check symmetry
        assert np.allclose(L, L.T)
        
        # Check row sums are zero
        row_sums = np.sum(L, axis=1)
        assert np.allclose(row_sums, 0)

    def test_missing_capacitance_attribute(self):
        """Test error when edge lacks capacitance attribute."""
        G = nx.Graph()
        G.add_edge('A', 'B')  # No capacitance attribute
        
        with pytest.raises(ValueError, match="capacitance"):
            build_laplacian_matrix(G)


class TestIsConnectedBetweenTerminals:
    """Tests for is_connected_between_terminals function."""

    def test_connected_simple(self):
        """Test connected graph A--B."""
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        
        assert is_connected_between_terminals(G, 'A', 'B') is True

    def test_connected_through_internal(self):
        """Test connected through internal node A--n1--B."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        G.add_edge('n1', 'B', capacitance=10e-12)
        
        assert is_connected_between_terminals(G, 'A', 'B') is True

    def test_disconnected(self):
        """Test disconnected graph A--n1, B (no path)."""
        G = nx.Graph()
        G.add_node('A')
        G.add_node('B')
        G.add_edge('A', 'n1', capacitance=5e-12)
        
        assert is_connected_between_terminals(G, 'A', 'B') is False

    def test_terminal_not_in_graph(self):
        """Test when terminal is not in graph."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        
        assert is_connected_between_terminals(G, 'A', 'B') is False


class TestCalculateGraphCeq:
    """Tests for calculate_graph_ceq function."""

    def test_simple_series_two_capacitors(self):
        """Test series: A--[10pF]--n1--[10pF]--B = 5pF."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=10e-12)
        G.add_edge('n1', 'B', capacitance=10e-12)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Series formula: 1/(1/10 + 1/10) = 5pF
        expected = 5e-12
        assert abs(ceq - expected) < 1e-15
        assert warning is None

    def test_simple_parallel_two_capacitors(self):
        """Test parallel: A--[5pF]--B, A--[3pF]--B = 8pF."""
        G = nx.Graph()
        # Note: NetworkX doesn't support multi-edges by default
        # So we add one edge with combined capacitance
        # For true parallel, we'd need MultiGraph
        G.add_edge('A', 'B', capacitance=8e-12)  # 5pF + 3pF pre-combined
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        expected = 8e-12
        assert abs(ceq - expected) < 1e-15
        assert warning is None

    def test_direct_connection(self):
        """Test direct connection A--[5pF]--B."""
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        expected = 5e-12
        assert abs(ceq - expected) < 1e-15
        assert warning is None

    def test_series_three_capacitors(self):
        """Test series: A--[10pF]--n1--[10pF]--n2--[10pF]--B."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=10e-12)
        G.add_edge('n1', 'n2', capacitance=10e-12)
        G.add_edge('n2', 'B', capacitance=10e-12)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Series formula: 1/(1/10 + 1/10 + 1/10) = 10/3 pF
        expected = 10e-12 / 3
        assert abs(ceq - expected) < 1e-15
        assert warning is None

    def test_bridge_network(self):
        """Test bridge (Wheatstone) network.
        
            A
           / \
          5   10  (pF)
         /     \
        n1--1--n2
         \     /
          3   2
           \ /
            B
        
        This is a non-SP network.
        """
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        G.add_edge('A', 'n2', capacitance=10e-12)
        G.add_edge('n1', 'n2', capacitance=1e-12)  # Bridge
        G.add_edge('n1', 'B', capacitance=3e-12)
        G.add_edge('n2', 'B', capacitance=2e-12)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Bridge network should give a valid positive capacitance
        assert ceq > 0
        assert warning is None
        # The exact value depends on the Laplacian solution

    def test_disconnected_network(self):
        """Test disconnected network returns 0."""
        G = nx.Graph()
        G.add_node('A')
        G.add_node('B')
        G.add_edge('A', 'n1', capacitance=5e-12)
        # B is isolated
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        assert ceq == 0.0
        assert "No path" in warning

    def test_terminal_not_in_graph(self):
        """Test error when terminal not in graph."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        
        with pytest.raises(ValueError, match="Terminal"):
            calculate_graph_ceq(G, 'A', 'B')

    def test_missing_capacitance_attribute(self):
        """Test error when edge lacks capacitance."""
        G = nx.Graph()
        G.add_edge('A', 'B')  # No capacitance
        
        with pytest.raises(ValueError, match="capacitance"):
            calculate_graph_ceq(G, 'A', 'B')


class TestGraphTopologyToExpression:
    """Tests for graph_topology_to_expression function."""

    def test_simple_expression(self):
        """Test expression generation for simple graph."""
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        
        topology = GraphTopology(G, 'A', 'B', [])
        expr = graph_topology_to_expression(topology)
        
        assert "2 nodes" in expr
        assert "1 edges" in expr

    def test_complex_expression(self):
        """Test expression for graph with internal nodes."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=5e-12)
        G.add_edge('n1', 'n2', capacitance=10e-12)
        G.add_edge('n2', 'B', capacitance=3e-12)
        
        topology = GraphTopology(G, 'A', 'B', ['n1', 'n2'])
        expr = graph_topology_to_expression(topology)
        
        assert "4 nodes" in expr
        assert "3 edges" in expr
        assert "2 internal" in expr


class TestNumericalStability:
    """Tests for numerical stability edge cases."""

    def test_very_small_capacitances(self):
        """Test with very small capacitance values (femtofarads)."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=1e-15)
        G.add_edge('n1', 'B', capacitance=1e-15)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Should be 0.5fF
        expected = 0.5e-15
        assert abs(ceq - expected) < 1e-18
        # May have warning about small values

    def test_very_large_capacitances(self):
        """Test with large capacitance values (millifarads)."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=1e-3)
        G.add_edge('n1', 'B', capacitance=1e-3)
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Should be 0.5mF
        expected = 0.5e-3
        assert abs(ceq - expected) < 1e-6

    def test_mixed_magnitudes(self):
        """Test with mixed capacitance magnitudes."""
        G = nx.Graph()
        G.add_edge('A', 'n1', capacitance=1e-12)  # 1pF
        G.add_edge('n1', 'B', capacitance=1e-9)   # 1nF
        
        ceq, warning = calculate_graph_ceq(G, 'A', 'B')
        
        # Series: 1/(1/1e-12 + 1/1e-9) ≈ 0.999e-12
        assert ceq > 0
        assert ceq < 1e-12  # Should be less than smallest
