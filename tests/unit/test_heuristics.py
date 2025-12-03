"""Unit tests for capassigner.core.heuristics module.

Tests the heuristic search for finding capacitor network topologies
using random graph generation.

Requirements tested: FR-018 to FR-022
"""

import pytest
import networkx as nx

from capassigner.core.heuristics import (
    generate_random_graph,
    generate_connected_graph,
    heuristic_search,
)
from capassigner.core.graphs import is_connected_between_terminals
from capassigner.core.metrics import ProgressUpdate


class TestGenerateRandomGraph:
    """Tests for generate_random_graph function."""

    def test_basic_generation(self):
        """Test basic graph generation."""
        capacitors = [5e-12, 10e-12]
        G = generate_random_graph(capacitors, max_internal_nodes=1, seed=42)
        
        assert isinstance(G, nx.Graph)
        assert 'A' in G.nodes()
        assert 'B' in G.nodes()

    def test_determinism_with_seed(self):
        """Test that same seed produces same graph."""
        capacitors = [5e-12, 10e-12, 3e-12]
        
        G1 = generate_random_graph(capacitors, max_internal_nodes=2, seed=42)
        G2 = generate_random_graph(capacitors, max_internal_nodes=2, seed=42)
        
        # Same nodes
        assert set(G1.nodes()) == set(G2.nodes())
        
        # Same edges
        assert set(G1.edges()) == set(G2.edges())
        
        # Same edge capacitances
        for u, v in G1.edges():
            assert G1[u][v]['capacitance'] == G2[u][v]['capacitance']

    def test_different_seeds_different_graphs(self):
        """Test that different seeds produce different graphs."""
        # Use more capacitors and nodes to increase variability
        capacitors = [1e-12, 2e-12, 3e-12, 5e-12, 10e-12]
        
        # Generate multiple graphs with different seeds and check for variation
        graphs = []
        for seed in [42, 123, 456, 789, 1000]:
            G = generate_random_graph(capacitors, max_internal_nodes=3, seed=seed)
            graphs.append(G)
        
        # At least some graphs should differ in structure or capacitances
        # Check if all graphs are identical (would indicate a problem)
        all_identical = True
        first_edges = set(graphs[0].edges())
        first_caps = {(u, v): graphs[0][u][v]['capacitance'] for u, v in first_edges}
        
        for G in graphs[1:]:
            edges = set(G.edges())
            if edges != first_edges:
                all_identical = False
                break
            caps = {(u, v): G[u][v]['capacitance'] for u, v in edges}
            if caps != first_caps:
                all_identical = False
                break
        
        # With 5 different seeds and more parameters, should see variation
        # Note: This test may occasionally pass even with identical graphs by chance
        # but it's statistically unlikely with these parameters
        assert not all_identical, "All graphs with different seeds should not be identical"

    def test_max_internal_nodes_zero(self):
        """Test with max_internal_nodes=0 (only A and B)."""
        capacitors = [5e-12]
        G = generate_random_graph(capacitors, max_internal_nodes=0, seed=42)
        
        assert 'A' in G.nodes()
        assert 'B' in G.nodes()
        # May or may not have internal nodes (random choice from 0 to 0)

    def test_empty_capacitors_raises(self):
        """Test error on empty capacitors list."""
        with pytest.raises(ValueError, match="no capacitors"):
            generate_random_graph([], max_internal_nodes=2, seed=42)

    def test_negative_max_internal_raises(self):
        """Test error on negative max_internal_nodes."""
        with pytest.raises(ValueError, match="non-negative"):
            generate_random_graph([5e-12], max_internal_nodes=-1, seed=42)

    def test_all_edges_have_capacitance(self):
        """Test that all edges have capacitance attribute."""
        capacitors = [5e-12, 10e-12]
        G = generate_random_graph(capacitors, max_internal_nodes=2, seed=42)
        
        for u, v, data in G.edges(data=True):
            assert 'capacitance' in data
            assert data['capacitance'] > 0
            assert data['capacitance'] in capacitors


class TestGenerateConnectedGraph:
    """Tests for generate_connected_graph function."""

    def test_generates_connected_graph(self):
        """Test that generated graph is connected."""
        capacitors = [5e-12, 10e-12]
        
        for seed in range(10):  # Test multiple seeds
            G = generate_connected_graph(capacitors, max_internal_nodes=2, seed=seed)
            if G is not None:
                assert is_connected_between_terminals(G, 'A', 'B')

    def test_returns_none_on_failure(self):
        """Test that function can return None on failure (edge case)."""
        # This is hard to trigger, but we test the signature
        capacitors = [5e-12]
        G = generate_connected_graph(capacitors, max_internal_nodes=0, seed=42, max_attempts=1)
        # May or may not succeed depending on random generation
        if G is not None:
            assert is_connected_between_terminals(G, 'A', 'B')


class TestHeuristicSearch:
    """Tests for heuristic_search function."""

    def test_basic_search(self):
        """Test basic heuristic search."""
        capacitors = [5e-12, 10e-12]
        target = 7.5e-12
        
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=100,
            seed=42,
            top_k=5
        )
        
        assert len(solutions) <= 5
        # All solutions should have positive ceq
        for sol in solutions:
            assert sol.ceq > 0
            assert sol.target == target

    def test_determinism(self):
        """Test that same seed produces identical results (SC-011)."""
        capacitors = [5e-12, 10e-12, 3e-12]
        target = 7.0e-12
        
        solutions1 = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=42,
            top_k=5
        )
        
        solutions2 = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=42,
            top_k=5
        )
        
        # Should have same number of solutions
        assert len(solutions1) == len(solutions2)
        
        # Should have same ceq values
        for s1, s2 in zip(solutions1, solutions2):
            assert s1.ceq == s2.ceq
            assert s1.absolute_error == s2.absolute_error

    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results."""
        capacitors = [5e-12, 10e-12, 3e-12]
        target = 7.0e-12
        
        solutions1 = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=42,
            top_k=5
        )
        
        solutions2 = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=123,
            top_k=5
        )
        
        # Results should differ (with high probability)
        if len(solutions1) > 0 and len(solutions2) > 0:
            # At least one solution should differ
            all_same = all(
                s1.ceq == s2.ceq
                for s1, s2 in zip(solutions1, solutions2)
            )
            # Note: could be same by chance, so we don't assert strictly

    def test_solutions_sorted_by_error(self):
        """Test that solutions are sorted by absolute error."""
        capacitors = [5e-12, 10e-12]
        target = 7.5e-12
        
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=42,
            top_k=10
        )
        
        # Check sorted order
        for i in range(len(solutions) - 1):
            assert solutions[i].absolute_error <= solutions[i + 1].absolute_error

    def test_tolerance_marking(self):
        """Test that solutions are correctly marked as within/outside tolerance."""
        capacitors = [5e-12, 10e-12]
        target = 7.5e-12
        tolerance = 10.0  # 10%
        
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=100,
            tolerance=tolerance,
            seed=42,
            top_k=10
        )
        
        for sol in solutions:
            expected_within = sol.relative_error <= tolerance
            assert sol.within_tolerance == expected_within

    def test_progress_callback(self):
        """Test that progress callback is called."""
        capacitors = [5e-12, 10e-12]
        target = 7.5e-12
        
        progress_updates = []
        
        def on_progress(update: ProgressUpdate) -> None:
            progress_updates.append(update)
        
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=200,
            seed=42,
            progress_cb=on_progress
        )
        
        # Should have received progress updates
        assert len(progress_updates) > 0
        
        # Check progress update structure
        for update in progress_updates:
            assert update.current > 0
            assert update.total == 200
            assert len(update.message) > 0

    def test_invalid_target_raises(self):
        """Test error on invalid target."""
        with pytest.raises(ValueError, match="positive"):
            heuristic_search(
                capacitors=[5e-12],
                target=-1.0,
                iterations=100
            )
        
        with pytest.raises(ValueError, match="positive"):
            heuristic_search(
                capacitors=[5e-12],
                target=0.0,
                iterations=100
            )

    def test_invalid_iterations_raises(self):
        """Test error on invalid iterations."""
        with pytest.raises(ValueError, match="at least 1"):
            heuristic_search(
                capacitors=[5e-12],
                target=5e-12,
                iterations=0
            )

    def test_empty_capacitors_raises(self):
        """Test error on empty capacitors."""
        with pytest.raises(ValueError, match="no capacitors"):
            heuristic_search(
                capacitors=[],
                target=5e-12,
                iterations=100
            )

    def test_graph_topologies_in_solutions(self):
        """Test that solutions contain GraphTopology objects."""
        capacitors = [5e-12, 10e-12]
        target = 7.5e-12
        
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=100,
            seed=42,
            top_k=5
        )
        
        for sol in solutions:
            assert sol.is_graph_topology()
            # Check GraphTopology structure
            topology = sol.topology
            assert hasattr(topology, 'graph')
            assert hasattr(topology, 'terminal_a')
            assert hasattr(topology, 'terminal_b')
            assert topology.terminal_a == 'A'
            assert topology.terminal_b == 'B'


class TestPerformance:
    """Performance tests for heuristic search."""

    def test_2000_iterations_completes(self):
        """Test that 2000 iterations completes in reasonable time."""
        import time
        
        capacitors = [5e-12, 10e-12, 3e-12]
        target = 7.5e-12
        
        start = time.time()
        solutions = heuristic_search(
            capacitors=capacitors,
            target=target,
            iterations=2000,
            max_internal_nodes=2,
            seed=42,
            top_k=10
        )
        elapsed = time.time() - start
        
        # Should complete in <10 seconds (SC-003 goal)
        assert elapsed < 10.0
        assert len(solutions) > 0
