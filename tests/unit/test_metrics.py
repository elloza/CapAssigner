"""Unit tests for error calculation and metrics.

Tests verify:
- Absolute error calculation
- Relative error calculation
- Tolerance checking
- Solution creation and ranking
- Edge cases (zero target, negative values)

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact error formula verification
"""

from __future__ import annotations
import pytest
from capassigner.core.metrics import (
    ProgressUpdate,
    Solution,
    calculate_absolute_error,
    calculate_relative_error,
    check_within_tolerance,
    create_solution,
    rank_solutions,
    filter_by_tolerance
)
from capassigner.core.sp_structures import Leaf


class TestProgressUpdate:
    """Test ProgressUpdate dataclass."""

    def test_progress_update_creation(self):
        """Test creating ProgressUpdate with all fields."""
        update = ProgressUpdate(
            current=50,
            total=100,
            message="Processing...",
            best_error=0.5
        )

        assert update.current == 50
        assert update.total == 100
        assert update.message == "Processing..."
        assert update.best_error == 0.5

    def test_progress_update_optional_best_error(self):
        """Test ProgressUpdate with None best_error."""
        update = ProgressUpdate(
            current=10,
            total=100,
            message="Starting..."
        )

        assert update.best_error is None


class TestAbsoluteError:
    """Test absolute error calculation: |C_eq - C_target|."""

    def test_absolute_error_positive_difference(self):
        """Test when C_eq > C_target."""
        ceq = 5.2e-12
        target = 5.0e-12

        error = calculate_absolute_error(ceq, target)

        assert abs(error - 0.2e-12) < 1e-20  # Use tolerance for floating-point
        assert error > 0

    def test_absolute_error_negative_difference(self):
        """Test when C_eq < C_target (should still be positive)."""
        ceq = 3.0e-12
        target = 5.0e-12

        error = calculate_absolute_error(ceq, target)

        assert abs(error - 2.0e-12) < 1e-20  # Use tolerance for floating-point
        assert error > 0

    def test_absolute_error_zero(self):
        """Test when C_eq == C_target."""
        ceq = 5.0e-12
        target = 5.0e-12

        error = calculate_absolute_error(ceq, target)

        assert error == 0.0

    def test_absolute_error_large_values(self):
        """Test with large capacitance values."""
        ceq = 1.0  # 1 Farad
        target = 0.5

        error = calculate_absolute_error(ceq, target)

        assert error == 0.5

    def test_absolute_error_small_values(self):
        """Test with very small capacitance values."""
        ceq = 1e-15  # 1 fF
        target = 2e-15

        error = calculate_absolute_error(ceq, target)

        assert abs(error - 1e-15) < 1e-20


class TestRelativeError:
    """Test relative error calculation: (|C_eq - C_target| / C_target) × 100."""

    def test_relative_error_percentage(self):
        """Test relative error returns percentage."""
        ceq = 5.2e-12
        target = 5.0e-12

        rel_error = calculate_relative_error(ceq, target)

        expected = (0.2e-12 / 5.0e-12) * 100  # 4%
        assert abs(rel_error - expected) < 1e-10
        assert abs(rel_error - 4.0) < 1e-10

    def test_relative_error_large_difference(self):
        """Test with large relative error."""
        ceq = 10.0e-12
        target = 5.0e-12

        rel_error = calculate_relative_error(ceq, target)

        expected = (5.0e-12 / 5.0e-12) * 100  # 100%
        assert abs(rel_error - expected) < 1e-10
        assert abs(rel_error - 100.0) < 1e-10

    def test_relative_error_small_difference(self):
        """Test with small relative error."""
        ceq = 5.01e-12
        target = 5.0e-12

        rel_error = calculate_relative_error(ceq, target)

        expected = (0.01e-12 / 5.0e-12) * 100  # 0.2%
        assert abs(rel_error - expected) < 1e-10
        assert abs(rel_error - 0.2) < 1e-10

    def test_relative_error_zero(self):
        """Test when C_eq == C_target."""
        ceq = 5.0e-12
        target = 5.0e-12

        rel_error = calculate_relative_error(ceq, target)

        assert rel_error == 0.0

    def test_relative_error_zero_target_raises(self):
        """Test that zero target raises ValueError."""
        ceq = 5.0e-12
        target = 0.0

        with pytest.raises(ValueError, match="Cannot calculate relative error with zero target"):
            calculate_relative_error(ceq, target)


class TestToleranceChecking:
    """Test tolerance threshold checking."""

    def test_within_tolerance_true(self):
        """Test error within tolerance."""
        rel_error = 3.0  # 3%
        tolerance = 5.0  # ±5%

        result = check_within_tolerance(rel_error, tolerance)

        assert result is True

    def test_within_tolerance_false(self):
        """Test error exceeds tolerance."""
        rel_error = 7.0  # 7%
        tolerance = 5.0  # ±5%

        result = check_within_tolerance(rel_error, tolerance)

        assert result is False

    def test_within_tolerance_exactly_on_boundary(self):
        """Test error exactly equals tolerance."""
        rel_error = 5.0
        tolerance = 5.0

        result = check_within_tolerance(rel_error, tolerance)

        assert result is True  # Should be inclusive (<=)

    def test_within_tolerance_zero_error(self):
        """Test zero error is always within tolerance."""
        rel_error = 0.0
        tolerance = 5.0

        result = check_within_tolerance(rel_error, tolerance)

        assert result is True

    def test_within_tolerance_zero_tolerance(self):
        """Test zero tolerance (only exact match accepted)."""
        rel_error = 0.1
        tolerance = 0.0

        result = check_within_tolerance(rel_error, tolerance)

        assert result is False


class TestSolutionCreation:
    """Test Solution dataclass and create_solution factory."""

    def test_create_solution_all_fields(self):
        """Test that create_solution populates all fields correctly."""
        topology = Leaf(0, 5.2e-12)
        ceq = 5.2e-12
        target = 5.0e-12
        tolerance = 5.0
        expression = "C1"

        solution = create_solution(topology, ceq, target, tolerance, expression)

        assert solution.topology == topology
        assert solution.ceq == ceq
        assert solution.target == target
        assert abs(solution.absolute_error - 0.2e-12) < 1e-15
        assert abs(solution.relative_error - 4.0) < 1e-10
        assert solution.within_tolerance is True
        assert solution.expression == expression
        assert solution.diagram is None  # Initially None

    def test_create_solution_within_tolerance(self):
        """Test solution within tolerance."""
        topology = Leaf(0, 5.1e-12)
        ceq = 5.1e-12
        target = 5.0e-12
        tolerance = 5.0  # ±5%

        solution = create_solution(topology, ceq, target, tolerance, "C1")

        assert solution.within_tolerance is True

    def test_create_solution_exceeds_tolerance(self):
        """Test solution exceeds tolerance."""
        topology = Leaf(0, 6.0e-12)
        ceq = 6.0e-12
        target = 5.0e-12
        tolerance = 5.0  # ±5% (6.0 is +20% error)

        solution = create_solution(topology, ceq, target, tolerance, "C1")

        assert solution.within_tolerance is False

    def test_create_solution_zero_target_raises(self):
        """Test that zero target raises ValueError."""
        topology = Leaf(0, 5.0e-12)
        ceq = 5.0e-12
        target = 0.0
        tolerance = 5.0

        with pytest.raises(ValueError, match="Target capacitance must be positive"):
            create_solution(topology, ceq, target, tolerance, "C1")

    def test_create_solution_negative_target_raises(self):
        """Test that negative target raises ValueError."""
        topology = Leaf(0, 5.0e-12)
        ceq = 5.0e-12
        target = -5.0e-12
        tolerance = 5.0

        with pytest.raises(ValueError, match="Target capacitance must be positive"):
            create_solution(topology, ceq, target, tolerance, "C1")


class TestSolutionRanking:
    """Test solution ranking and sorting."""

    def test_rank_solutions_sorts_by_absolute_error(self):
        """Test that rank_solutions sorts by absolute_error ascending."""
        topology = Leaf(0, 5.0e-12)

        # Create solutions with different errors
        sol1 = create_solution(topology, 5.5e-12, 5.0e-12, 10.0, "C1")  # 0.5pF error
        sol2 = create_solution(topology, 5.1e-12, 5.0e-12, 10.0, "C1")  # 0.1pF error
        sol3 = create_solution(topology, 5.3e-12, 5.0e-12, 10.0, "C1")  # 0.3pF error

        solutions = [sol1, sol2, sol3]
        ranked = rank_solutions(solutions)

        # Should be sorted: sol2 < sol3 < sol1
        assert ranked[0].absolute_error < ranked[1].absolute_error
        assert ranked[1].absolute_error < ranked[2].absolute_error

        assert ranked[0] == sol2
        assert ranked[1] == sol3
        assert ranked[2] == sol1

    def test_rank_solutions_preserves_all(self):
        """Test that ranking doesn't lose solutions."""
        topology = Leaf(0, 5.0e-12)

        solutions = [
            create_solution(topology, 5.5e-12, 5.0e-12, 10.0, f"C{i}")
            for i in range(10)
        ]

        ranked = rank_solutions(solutions)

        assert len(ranked) == len(solutions)

    def test_rank_solutions_empty_list(self):
        """Test ranking empty list."""
        ranked = rank_solutions([])

        assert ranked == []


class TestFilterByTolerance:
    """Test filtering solutions by tolerance."""

    def test_filter_by_tolerance_some_within(self):
        """Test filtering when some solutions are within tolerance."""
        topology = Leaf(0, 5.0e-12)
        target = 5.0e-12
        tolerance = 5.0  # ±5%

        # Create solutions: some within, some exceeding tolerance
        sol1 = create_solution(topology, 5.2e-12, target, tolerance, "C1")  # 4% - within
        sol2 = create_solution(topology, 6.0e-12, target, tolerance, "C1")  # 20% - exceeds
        sol3 = create_solution(topology, 5.1e-12, target, tolerance, "C1")  # 2% - within

        solutions = [sol1, sol2, sol3]
        filtered = filter_by_tolerance(solutions)

        assert len(filtered) == 2
        assert sol1 in filtered
        assert sol3 in filtered
        assert sol2 not in filtered

    def test_filter_by_tolerance_all_within(self):
        """Test filtering when all solutions are within tolerance."""
        topology = Leaf(0, 5.0e-12)
        target = 5.0e-12
        tolerance = 10.0  # ±10%

        solutions = [
            create_solution(topology, 5.2e-12, target, tolerance, "C1"),  # 4%
            create_solution(topology, 5.3e-12, target, tolerance, "C2"),  # 6%
            create_solution(topology, 5.1e-12, target, tolerance, "C3"),  # 2%
        ]

        filtered = filter_by_tolerance(solutions)

        assert len(filtered) == 3

    def test_filter_by_tolerance_none_within(self):
        """Test filtering when no solutions are within tolerance."""
        topology = Leaf(0, 5.0e-12)
        target = 5.0e-12
        tolerance = 1.0  # ±1% (very strict)

        solutions = [
            create_solution(topology, 6.0e-12, target, tolerance, "C1"),  # 20%
            create_solution(topology, 7.0e-12, target, tolerance, "C2"),  # 40%
        ]

        filtered = filter_by_tolerance(solutions)

        assert len(filtered) == 0

    def test_filter_by_tolerance_preserves_order(self):
        """Test that filtering preserves original order."""
        topology = Leaf(0, 5.0e-12)
        target = 5.0e-12
        tolerance = 15.0  # Higher tolerance so all pass

        # All solutions within 15% tolerance
        sol1 = create_solution(topology, 5.5e-12, target, tolerance, "C1")  # 10% error
        sol2 = create_solution(topology, 5.1e-12, target, tolerance, "C2")  # 2% error
        sol3 = create_solution(topology, 5.2e-12, target, tolerance, "C3")  # 4% error

        solutions = [sol1, sol2, sol3]
        filtered = filter_by_tolerance(solutions)

        # All should pass with 15% tolerance
        assert len(filtered) == 3
        
        # Order should be preserved - compare by expression (unique identifier)
        assert filtered[0].expression == sol1.expression
        assert filtered[1].expression == sol2.expression
        assert filtered[2].expression == sol3.expression


class TestEdgeCases:
    """Test edge cases and numerical precision."""

    def test_very_small_capacitances(self):
        """Test with femtofarad-scale capacitances."""
        topology = Leaf(0, 1e-15)
        ceq = 1e-15
        target = 1e-15
        tolerance = 5.0

        solution = create_solution(topology, ceq, target, tolerance, "C1")

        assert solution.absolute_error == 0.0
        assert solution.relative_error == 0.0
        assert solution.within_tolerance is True

    def test_very_large_capacitances(self):
        """Test with Farad-scale capacitances."""
        topology = Leaf(0, 1.0)
        ceq = 1.0
        target = 1.0
        tolerance = 5.0

        solution = create_solution(topology, ceq, target, tolerance, "C1")

        assert solution.absolute_error == 0.0
        assert solution.relative_error == 0.0
        assert solution.within_tolerance is True

    def test_numerical_precision_boundary(self):
        """Test error calculation near floating-point precision limits."""
        topology = Leaf(0, 5.000000000001e-12)
        ceq = 5.000000000001e-12
        target = 5.0e-12
        tolerance = 1.0

        solution = create_solution(topology, ceq, target, tolerance, "C1")

        # Should handle tiny differences gracefully
        assert solution.absolute_error >= 0
        assert solution.relative_error >= 0
