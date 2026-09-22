"""Contract tests for algorithm public API stability.

These tests verify that:
1. Public API signatures remain stable (T088)
2. Input validation works correctly (T089)
3. Documented behaviors are preserved

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Formulas and behaviors match documentation
    - Principle IV (Modular Architecture): Tests don't depend on UI
"""

from __future__ import annotations
import pytest
import inspect
from typing import get_type_hints

# Import all public APIs
from capassigner.core.sp_structures import (
    Capacitor,
    Leaf,
    Series,
    Parallel,
    SPNode,
    calculate_sp_ceq,
    sp_node_to_expression,
)
from capassigner.core.sp_enumeration import (
    enumerate_sp_topologies,
    find_best_sp_solutions,
)
from capassigner.core.graphs import (
    GraphTopology,
    build_laplacian_matrix,
    is_connected_between_terminals,
    calculate_graph_ceq,
    graph_topology_to_expression,
)
from capassigner.core.heuristics import (
    generate_random_graph,
    generate_connected_graph,
    heuristic_search,
)
from capassigner.core.metrics import (
    ProgressUpdate,
    Solution,
    calculate_absolute_error,
    calculate_relative_error,
    check_within_tolerance,
    create_solution,
    rank_solutions,
    filter_by_tolerance,
)
from capassigner.core.parsing import (
    ParsedCapacitance,
    parse_capacitance,
    format_capacitance,
)


class TestSPStructuresAPIContract:
    """Verify SP structures public API remains stable."""

    def test_leaf_has_required_attributes(self):
        """Verify Leaf has capacitor_index and value."""
        leaf = Leaf(capacitor_index=0, value=5e-12)
        assert hasattr(leaf, 'capacitor_index')
        assert hasattr(leaf, 'value')

    def test_series_has_left_right(self):
        """Verify Series has left and right children."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        series = Series(left=c1, right=c2)
        assert hasattr(series, 'left')
        assert hasattr(series, 'right')

    def test_parallel_has_left_right(self):
        """Verify Parallel has left and right children."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        parallel = Parallel(left=c1, right=c2)
        assert hasattr(parallel, 'left')
        assert hasattr(parallel, 'right')

    def test_calculate_sp_ceq_signature(self):
        """Verify calculate_sp_ceq accepts SPNode and returns float."""
        sig = inspect.signature(calculate_sp_ceq)
        params = list(sig.parameters.keys())
        assert 'node' in params

    def test_sp_node_to_expression_signature(self):
        """Verify sp_node_to_expression accepts node and labels."""
        sig = inspect.signature(sp_node_to_expression)
        params = list(sig.parameters.keys())
        assert 'node' in params
        assert 'capacitor_labels' in params


class TestSPEnumerationAPIContract:
    """Verify SP enumeration public API remains stable."""

    def test_enumerate_sp_topologies_signature(self):
        """Verify enumerate_sp_topologies accepts capacitors list."""
        sig = inspect.signature(enumerate_sp_topologies)
        params = list(sig.parameters.keys())
        assert 'capacitors' in params
        # Optional progress callback
        assert 'progress_cb' in params

    def test_find_best_sp_solutions_signature(self):
        """Verify find_best_sp_solutions has required parameters."""
        sig = inspect.signature(find_best_sp_solutions)
        params = list(sig.parameters.keys())
        assert 'capacitors' in params
        assert 'target' in params
        assert 'tolerance' in params
        assert 'top_k' in params


class TestGraphsAPIContract:
    """Verify graphs public API remains stable."""

    def test_graph_topology_has_required_fields(self):
        """Verify GraphTopology has graph, terminals, internal_nodes."""
        import networkx as nx
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        topology = GraphTopology(
            graph=G,
            terminal_a='A',
            terminal_b='B',
            internal_nodes=[]
        )
        assert hasattr(topology, 'graph')
        assert hasattr(topology, 'terminal_a')
        assert hasattr(topology, 'terminal_b')
        assert hasattr(topology, 'internal_nodes')

    def test_calculate_graph_ceq_returns_tuple(self):
        """Verify calculate_graph_ceq returns (ceq, warning) tuple."""
        import networkx as nx
        G = nx.Graph()
        G.add_edge('A', 'B', capacitance=5e-12)
        result = calculate_graph_ceq(G, 'A', 'B')
        assert isinstance(result, tuple)
        assert len(result) == 2
        ceq, warning = result
        assert isinstance(ceq, float)
        assert warning is None or isinstance(warning, str)


class TestHeuristicsAPIContract:
    """Verify heuristics public API remains stable."""

    def test_generate_random_graph_signature(self):
        """Verify generate_random_graph has required parameters."""
        sig = inspect.signature(generate_random_graph)
        params = list(sig.parameters.keys())
        assert 'capacitors' in params
        assert 'max_internal_nodes' in params
        assert 'seed' in params
        assert 'rng' in params  # For dependency injection

    def test_heuristic_search_signature(self):
        """Verify heuristic_search has required parameters."""
        sig = inspect.signature(heuristic_search)
        params = list(sig.parameters.keys())
        assert 'capacitors' in params
        assert 'target' in params
        assert 'iterations' in params
        assert 'seed' in params
        assert 'top_k' in params


class TestMetricsAPIContract:
    """Verify metrics public API remains stable."""

    def test_solution_has_required_fields(self):
        """Verify Solution dataclass has all required fields."""
        from capassigner.core.sp_structures import Leaf
        leaf = Leaf(0, 5e-12)
        solution = Solution(
            topology=leaf,
            ceq=5e-12,
            target=5e-12,
            absolute_error=0.0,
            relative_error=0.0,
            within_tolerance=True,
            expression="C1"
        )
        assert hasattr(solution, 'topology')
        assert hasattr(solution, 'ceq')
        assert hasattr(solution, 'target')
        assert hasattr(solution, 'absolute_error')
        assert hasattr(solution, 'relative_error')
        assert hasattr(solution, 'within_tolerance')
        assert hasattr(solution, 'expression')

    def test_progress_update_has_required_fields(self):
        """Verify ProgressUpdate has all required fields."""
        update = ProgressUpdate(
            current=50,
            total=100,
            message="Testing..."
        )
        assert hasattr(update, 'current')
        assert hasattr(update, 'total')
        assert hasattr(update, 'message')
        assert hasattr(update, 'best_error')  # Optional


class TestParsingAPIContract:
    """Verify parsing public API remains stable."""

    def test_parsed_capacitance_has_required_fields(self):
        """Verify ParsedCapacitance has success, value, error_message."""
        result = parse_capacitance("5pF")
        assert hasattr(result, 'success')
        assert hasattr(result, 'value')
        assert hasattr(result, 'error_message')

    def test_parse_capacitance_returns_parsed_capacitance(self):
        """Verify parse_capacitance returns ParsedCapacitance."""
        result = parse_capacitance("5pF")
        assert isinstance(result, ParsedCapacitance)

    def test_format_capacitance_returns_string(self):
        """Verify format_capacitance returns string."""
        result = format_capacitance(5e-12)
        assert isinstance(result, str)


class TestInputValidationContract:
    """Contract tests for input validation (ValueError for invalid inputs)."""

    @pytest.mark.parametrize("invalid_capacitors", [
        [],  # Empty list
        [5e-12, -10e-12],  # Negative value
        [5e-12, 0.0],  # Zero value
    ])
    def test_enumerate_sp_topologies_rejects_invalid_input(self, invalid_capacitors):
        """Verify enumerate_sp_topologies raises ValueError for invalid input."""
        with pytest.raises(ValueError):
            enumerate_sp_topologies(invalid_capacitors)

    @pytest.mark.parametrize("invalid_target", [0.0, -5e-12])
    def test_find_best_sp_solutions_rejects_invalid_target(self, invalid_target):
        """Verify find_best_sp_solutions raises ValueError for invalid target."""
        with pytest.raises(ValueError, match="Target"):
            find_best_sp_solutions([5e-12, 10e-12], target=invalid_target)

    def test_find_best_sp_solutions_rejects_negative_tolerance(self):
        """Verify find_best_sp_solutions raises ValueError for negative tolerance."""
        with pytest.raises(ValueError, match="[Tt]olerance"):
            find_best_sp_solutions([5e-12, 10e-12], target=5e-12, tolerance=-1.0)

    def test_generate_random_graph_rejects_empty_capacitors(self):
        """Verify generate_random_graph raises ValueError for empty capacitors."""
        with pytest.raises(ValueError, match="capacitors"):
            generate_random_graph([])

    def test_generate_random_graph_rejects_negative_max_nodes(self):
        """Verify generate_random_graph raises ValueError for negative max_internal_nodes."""
        with pytest.raises(ValueError, match="non-negative"):
            generate_random_graph([5e-12], max_internal_nodes=-1)

    def test_heuristic_search_rejects_invalid_target(self):
        """Verify heuristic_search raises ValueError for invalid target."""
        with pytest.raises(ValueError, match="positive"):
            heuristic_search(capacitors=[5e-12], target=0.0, iterations=10)

    def test_heuristic_search_rejects_zero_iterations(self):
        """Verify heuristic_search raises ValueError for zero iterations."""
        with pytest.raises(ValueError, match="at least 1"):
            heuristic_search(capacitors=[5e-12], target=5e-12, iterations=0)

    def test_capacitor_rejects_negative_value(self):
        """Verify Capacitor raises ValueError for negative capacitance."""
        with pytest.raises(ValueError, match="positive"):
            Capacitor(index=0, value=-5e-12, label="C1")

    def test_capacitor_rejects_zero_value(self):
        """Verify Capacitor raises ValueError for zero capacitance."""
        with pytest.raises(ValueError, match="positive"):
            Capacitor(index=0, value=0.0, label="C1")


class TestFormulaContract:
    """Contract tests for formula correctness (Principle I: Scientific Accuracy)."""

    def test_series_formula_two_equal(self):
        """Contract: Series of two equal caps = C/2."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        result = calculate_sp_ceq(Series(c1, c2))
        assert abs(result - 5e-12) < 1e-20

    def test_parallel_formula_two_equal(self):
        """Contract: Parallel of two equal caps = 2*C."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        result = calculate_sp_ceq(Parallel(c1, c2))
        assert abs(result - 20e-12) < 1e-20

    def test_series_formula_general(self):
        """Contract: Series formula = 1/(1/C1 + 1/C2)."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        result = calculate_sp_ceq(Series(c1, c2))
        expected = 1.0 / (1.0/5e-12 + 1.0/10e-12)
        assert abs(result - expected) < 1e-20

    def test_parallel_formula_general(self):
        """Contract: Parallel formula = C1 + C2."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        result = calculate_sp_ceq(Parallel(c1, c2))
        expected = 15e-12
        assert abs(result - expected) < 1e-20

    def test_error_formula_absolute(self):
        """Contract: Absolute error = |C_eq - C_target|."""
        assert calculate_absolute_error(5.2e-12, 5.0e-12) == pytest.approx(0.2e-12)
        assert calculate_absolute_error(3.0e-12, 5.0e-12) == pytest.approx(2.0e-12)

    def test_error_formula_relative(self):
        """Contract: Relative error = (|C_eq - C_target| / C_target) * 100."""
        # 5.5 vs 5.0 = 10% error
        result = calculate_relative_error(5.5e-12, 5.0e-12)
        assert result == pytest.approx(10.0)

    def test_tolerance_check(self):
        """Contract: Within tolerance = relative_error <= tolerance."""
        # 0% error is within 1% tolerance
        assert check_within_tolerance(0.0, 1.0) is True
        # 2% error is NOT within 1% tolerance
        assert check_within_tolerance(2.0, 1.0) is False
        # 1% error is exactly within 1% tolerance
        assert check_within_tolerance(1.0, 1.0) is True
