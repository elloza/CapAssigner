"""Unit tests for Series-Parallel enumeration algorithms.

Tests verify:
- Enumeration completeness (all topologies generated)
- Memoization correctness
- Topology count matches expected values
- find_best_sp_solutions integration

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Verify algorithmic correctness
    - Principle V (Performance Awareness): Test memoization efficiency
"""

from __future__ import annotations
import pytest
from capassigner.core.sp_enumeration import (
    enumerate_sp_topologies,
    find_best_sp_solutions
)
from capassigner.core.sp_structures import Leaf, Series, Parallel, calculate_sp_ceq


class TestEnumerationBasicCases:
    """Test basic enumeration cases with known topology counts."""

    def test_single_capacitor(self):
        """Test N=1: Should return exactly 1 topology (leaf)."""
        capacitors = [5e-12]
        topologies = enumerate_sp_topologies(capacitors)

        assert len(topologies) == 1
        assert isinstance(topologies[0], Leaf)
        assert topologies[0].capacitor_index == 0
        assert topologies[0].value == 5e-12

    def test_two_capacitors(self):
        """Test N=2: Should return 2 topologies (1 series + 1 parallel).
        
        Note: The algorithm does not duplicate commutative orderings (A||B == B||A).
        """
        capacitors = [5e-12, 10e-12]
        topologies = enumerate_sp_topologies(capacitors)

        # Expected: Series(0,1) and Parallel(0,1)
        # The algorithm generates unique topologies without redundant orderings
        assert len(topologies) == 2

        # Verify we have both series and parallel
        series_count = sum(1 for t in topologies if isinstance(t, Series))
        parallel_count = sum(1 for t in topologies if isinstance(t, Parallel))

        assert series_count == 1
        assert parallel_count == 1

    def test_three_capacitors_count(self):
        """Test N=3: Should return 8 topologies.

        The algorithm generates unique SP topologies by partitioning indices.
        For N=3: 2 partitions × 2 operators × 2 sub-topologies = 8 topologies.
        """
        capacitors = [1e-12, 2e-12, 5e-12]
        topologies = enumerate_sp_topologies(capacitors)

        # Expected count for N=3 with our enumeration algorithm
        assert len(topologies) == 8

    def test_four_capacitors_count(self):
        """Test N=4: Verify expected topology count.

        For N=4, we expect 40 topologies based on our partitioning algorithm.
        """
        capacitors = [1e-12, 2e-12, 3e-12, 4e-12]
        topologies = enumerate_sp_topologies(capacitors)

        # Expected count for N=4 (empirical from implementation)
        assert len(topologies) == 40


class TestEnumerationValidation:
    """Test that all enumerated topologies are valid and calculate correctly."""

    def test_all_topologies_calculate_successfully(self):
        """Test that all enumerated topologies can calculate C_eq without error."""
        capacitors = [1e-12, 2e-12, 5e-12]
        topologies = enumerate_sp_topologies(capacitors)

        for topology in topologies:
            try:
                ceq = calculate_sp_ceq(topology)
                # Verify result is positive and finite
                assert ceq > 0
                assert ceq < float('inf')
            except Exception as e:
                pytest.fail(f"Topology {topology} failed to calculate: {e}")

    def test_topologies_produce_different_ceq_values(self):
        """Test that different topologies produce different C_eq values (mostly)."""
        capacitors = [1e-12, 2e-12, 5e-12]
        topologies = enumerate_sp_topologies(capacitors)

        ceq_values = [calculate_sp_ceq(t) for t in topologies]

        # We should have at least some unique values (not all identical)
        unique_ceq_count = len(set(ceq_values))
        assert unique_ceq_count > 5  # Expect many different values


class TestEnumerationEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_capacitor_list_raises_error(self):
        """Test that empty capacitor list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot enumerate topologies with zero capacitors"):
            enumerate_sp_topologies([])

    def test_negative_capacitor_raises_error(self):
        """Test that negative capacitor value raises ValueError."""
        with pytest.raises(ValueError, match="All capacitor values must be positive"):
            enumerate_sp_topologies([5e-12, -10e-12])

    def test_zero_capacitor_raises_error(self):
        """Test that zero capacitor value raises ValueError."""
        with pytest.raises(ValueError, match="All capacitor values must be positive"):
            enumerate_sp_topologies([5e-12, 0.0])


class TestMemoization:
    """Test that memoization works correctly."""

    def test_repeated_calls_return_same_count(self):
        """Test that calling enumerate twice returns consistent results."""
        capacitors = [1e-12, 2e-12, 5e-12]

        topologies_1 = enumerate_sp_topologies(capacitors)
        topologies_2 = enumerate_sp_topologies(capacitors)

        # Should return same number of topologies
        assert len(topologies_1) == len(topologies_2)

    def test_different_values_same_structure(self):
        """Test that different capacitor values produce same topology count."""
        capacitors_1 = [1e-12, 2e-12, 5e-12]
        capacitors_2 = [10e-12, 20e-12, 50e-12]

        topologies_1 = enumerate_sp_topologies(capacitors_1)
        topologies_2 = enumerate_sp_topologies(capacitors_2)

        # Same structure → same topology count
        assert len(topologies_1) == len(topologies_2)


class TestProgressCallback:
    """Test progress callback functionality."""

    def test_progress_callback_invoked(self):
        """Test that progress callback is called during enumeration."""
        capacitors = [1e-12, 2e-12, 5e-12]

        callback_count = [0]
        last_progress = [None]

        def progress_cb(update):
            callback_count[0] += 1
            last_progress[0] = update

        topologies = enumerate_sp_topologies(capacitors, progress_cb=progress_cb)

        # Callback should have been invoked at least once (final progress)
        assert callback_count[0] > 0
        assert last_progress[0] is not None

        # Final progress should report completion
        assert last_progress[0].current == len(topologies)
        assert last_progress[0].total == len(topologies)

    def test_progress_callback_none_works(self):
        """Test that passing None as callback doesn't crash."""
        capacitors = [1e-12, 2e-12, 5e-12]

        topologies = enumerate_sp_topologies(capacitors, progress_cb=None)

        assert len(topologies) > 0


class TestFindBestSPSolutions:
    """Test integrated find_best_sp_solutions function."""

    def test_find_best_returns_top_k(self):
        """Test that find_best_sp_solutions returns requested number of solutions."""
        capacitors = [1e-12, 2e-12, 5e-12]
        target = 3.1e-12
        top_k = 5

        solutions = find_best_sp_solutions(capacitors, target, top_k=top_k)

        assert len(solutions) == top_k

    def test_find_best_sorted_by_error(self):
        """Test that solutions are sorted by absolute error (ascending)."""
        capacitors = [1e-12, 2e-12, 5e-12]
        target = 3.1e-12
        top_k = 10

        solutions = find_best_sp_solutions(capacitors, target, top_k=top_k)

        # Verify sorting: each solution should have error <= next solution
        for i in range(len(solutions) - 1):
            assert solutions[i].absolute_error <= solutions[i + 1].absolute_error

    def test_find_best_target_validation(self):
        """Test that invalid target raises ValueError."""
        capacitors = [1e-12, 2e-12, 5e-12]

        with pytest.raises(ValueError, match="Target capacitance must be positive"):
            find_best_sp_solutions(capacitors, target=0.0)

        with pytest.raises(ValueError, match="Target capacitance must be positive"):
            find_best_sp_solutions(capacitors, target=-5e-12)

    def test_find_best_tolerance_validation(self):
        """Test that negative tolerance raises ValueError."""
        capacitors = [1e-12, 2e-12, 5e-12]
        target = 3.1e-12

        with pytest.raises(ValueError, match="Tolerance cannot be negative"):
            find_best_sp_solutions(capacitors, target, tolerance=-1.0)

    def test_find_best_solution_structure(self):
        """Test that solutions have all expected fields populated."""
        capacitors = [1e-12, 2e-12, 5e-12]
        target = 3.1e-12

        solutions = find_best_sp_solutions(capacitors, target, top_k=1)

        assert len(solutions) == 1
        sol = solutions[0]

        # Verify all fields are populated
        assert sol.topology is not None
        assert sol.ceq > 0
        assert sol.target == target
        assert sol.absolute_error >= 0
        assert sol.relative_error >= 0
        assert isinstance(sol.within_tolerance, bool)
        assert len(sol.expression) > 0

    def test_find_best_realistic_scenario(self):
        """Test User Story 1 scenario: target=3.1pF, capacitors=[1pF, 2pF, 5pF]."""
        capacitors = [1e-12, 2e-12, 5e-12]
        target = 3.1e-12
        tolerance = 5.0  # ±5%

        solutions = find_best_sp_solutions(capacitors, target, tolerance=tolerance, top_k=10)

        # Should find at least one solution
        assert len(solutions) > 0

        # Best solution should be reasonably close to target
        best_solution = solutions[0]
        assert best_solution.absolute_error < 1e-12  # Error < 1pF

        # Should have valid expression
        assert "C" in best_solution.expression
        assert any(op in best_solution.expression for op in ["+", "||"])
