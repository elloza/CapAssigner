"""Unit tests for Series-Parallel data structures and calculations.

Tests verify:
- Series and parallel formula correctness
- Nested topology calculations
- Edge cases (zero values, single capacitor)
- Expression generation

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact formula verification
"""

from __future__ import annotations
import pytest
from capassigner.core.sp_structures import (
    Capacitor,
    Leaf,
    Series,
    Parallel,
    SPNode,
    calculate_sp_ceq,
    sp_node_to_expression
)


class TestCapacitor:
    """Test Capacitor dataclass validation."""

    def test_valid_capacitor(self):
        """Test creating a valid capacitor."""
        cap = Capacitor(index=0, value=5e-12, label="C1")
        assert cap.index == 0
        assert cap.value == 5e-12
        assert cap.label == "C1"

    def test_negative_value_rejected(self):
        """Test that negative capacitance is rejected."""
        with pytest.raises(ValueError, match="Capacitance must be positive"):
            Capacitor(index=0, value=-5e-12, label="C1")

    def test_zero_value_rejected(self):
        """Test that zero capacitance is rejected."""
        with pytest.raises(ValueError, match="Capacitance must be positive"):
            Capacitor(index=0, value=0.0, label="C1")

    def test_immutability(self):
        """Test that Capacitor is immutable (frozen dataclass)."""
        cap = Capacitor(index=0, value=5e-12, label="C1")
        with pytest.raises(AttributeError):
            cap.value = 10e-12  # type: ignore


class TestSeriesFormula:
    """Test series capacitance formula: C_series = 1 / (1/C1 + 1/C2)."""

    def test_series_equal_values(self):
        """Test series of two equal capacitors: C_series = C/2."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        series = Series(c1, c2)

        result = calculate_sp_ceq(series)
        expected = 5e-12  # 10pF in series with 10pF = 5pF

        assert abs(result - expected) < 1e-15

    def test_series_different_values(self):
        """Test series of two different capacitors."""
        c1 = Leaf(0, 5e-12)   # 5pF
        c2 = Leaf(1, 10e-12)  # 10pF
        series = Series(c1, c2)

        # C_series = 1 / (1/5e-12 + 1/10e-12) = 1 / (0.2e12 + 0.1e12) = 1 / 0.3e12 = 3.333...e-12
        result = calculate_sp_ceq(series)
        expected = 1.0 / (1.0 / 5e-12 + 1.0 / 10e-12)

        assert abs(result - expected) < 1e-15

    def test_series_three_capacitors(self):
        """Test series of three capacitors: ((C1+C2)+C3)."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        c3 = Leaf(2, 10e-12)
        series_12 = Series(c1, c2)
        series_123 = Series(series_12, c3)

        result = calculate_sp_ceq(series_123)
        # C_12 = 5pF, then C_123 = 1/(1/5e-12 + 1/10e-12) = 3.333...pF
        expected = 1.0 / (1.0 / 5e-12 + 1.0 / 10e-12)

        assert abs(result - expected) < 1e-15

    def test_series_zero_capacitor_raises_error(self):
        """Test that series with zero-value capacitor raises ZeroDivisionError."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 0.0)  # Invalid but created directly (bypasses Capacitor validation)
        series = Series(c1, c2)

        with pytest.raises(ZeroDivisionError, match="Cannot compute series capacitance"):
            calculate_sp_ceq(series)


class TestParallelFormula:
    """Test parallel capacitance formula: C_parallel = C1 + C2."""

    def test_parallel_equal_values(self):
        """Test parallel of two equal capacitors: C_parallel = 2*C."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        parallel = Parallel(c1, c2)

        result = calculate_sp_ceq(parallel)
        expected = 20e-12  # 10pF || 10pF = 20pF

        assert abs(result - expected) < 1e-15

    def test_parallel_different_values(self):
        """Test parallel of two different capacitors."""
        c1 = Leaf(0, 5e-12)   # 5pF
        c2 = Leaf(1, 10e-12)  # 10pF
        parallel = Parallel(c1, c2)

        result = calculate_sp_ceq(parallel)
        expected = 15e-12  # 5pF || 10pF = 15pF

        assert abs(result - expected) < 1e-15

    def test_parallel_three_capacitors(self):
        """Test parallel of three capacitors: ((C1||C2)||C3)."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        c3 = Leaf(2, 2e-12)
        parallel_12 = Parallel(c1, c2)
        parallel_123 = Parallel(parallel_12, c3)

        result = calculate_sp_ceq(parallel_123)
        expected = 17e-12  # 5 + 10 + 2 = 17pF

        assert abs(result - expected) < 1e-15


class TestMixedTopologies:
    """Test mixed series-parallel topologies."""

    def test_series_of_parallels(self):
        """Test (C1||C2) + (C3||C4)."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        c3 = Leaf(2, 5e-12)
        c4 = Leaf(3, 5e-12)

        parallel_12 = Parallel(c1, c2)  # 20pF
        parallel_34 = Parallel(c3, c4)  # 10pF
        series = Series(parallel_12, parallel_34)

        result = calculate_sp_ceq(series)
        # C_12 = 20pF, C_34 = 10pF
        # C_series = 1 / (1/20e-12 + 1/10e-12) = 1 / (0.05e12 + 0.1e12) = 6.666...pF
        expected = 1.0 / (1.0 / 20e-12 + 1.0 / 10e-12)

        assert abs(result - expected) < 1e-15

    def test_parallel_of_series(self):
        """Test (C1+C2) || (C3+C4)."""
        c1 = Leaf(0, 10e-12)
        c2 = Leaf(1, 10e-12)
        c3 = Leaf(2, 20e-12)
        c4 = Leaf(3, 20e-12)

        series_12 = Series(c1, c2)  # 5pF
        series_34 = Series(c3, c4)  # 10pF
        parallel = Parallel(series_12, series_34)

        result = calculate_sp_ceq(parallel)
        expected = 15e-12  # 5pF || 10pF = 15pF

        assert abs(result - expected) < 1e-15

    def test_complex_nested_topology(self):
        """Test ((C1||C2)+C3) with known result."""
        c1 = Leaf(0, 1e-12)   # 1pF
        c2 = Leaf(1, 2e-12)   # 2pF
        c3 = Leaf(2, 5e-12)   # 5pF

        parallel = Parallel(c1, c2)  # 3pF
        series = Series(parallel, c3)

        result = calculate_sp_ceq(series)
        # C_12 = 3pF, then C_series = 1/(1/3e-12 + 1/5e-12) = 1.875pF
        expected = 1.0 / (1.0 / 3e-12 + 1.0 / 5e-12)

        assert abs(result - expected) < 1e-15


class TestSingleCapacitor:
    """Test leaf node (single capacitor)."""

    def test_leaf_value(self):
        """Test that leaf returns its own value."""
        leaf = Leaf(0, 5.2e-12)
        result = calculate_sp_ceq(leaf)
        assert result == 5.2e-12


class TestExpressionGeneration:
    """Test topology expression string generation."""

    def test_single_capacitor_expression(self):
        """Test expression for single capacitor."""
        leaf = Leaf(0, 5e-12)
        labels = ["C1"]
        expr = sp_node_to_expression(leaf, labels)
        assert expr == "C1"

    def test_series_expression(self):
        """Test expression for series: (C1+C2)."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        series = Series(c1, c2)
        labels = ["C1", "C2"]

        expr = sp_node_to_expression(series, labels)
        assert expr == "(C1+C2)"

    def test_parallel_expression(self):
        """Test expression for parallel: (C1||C2)."""
        c1 = Leaf(0, 5e-12)
        c2 = Leaf(1, 10e-12)
        parallel = Parallel(c1, c2)
        labels = ["C1", "C2"]

        expr = sp_node_to_expression(parallel, labels)
        assert expr == "(C1||C2)"

    def test_complex_expression(self):
        """Test expression for ((C1||C2)+C3)."""
        c1 = Leaf(0, 1e-12)
        c2 = Leaf(1, 2e-12)
        c3 = Leaf(2, 5e-12)
        parallel = Parallel(c1, c2)
        series = Series(parallel, c3)
        labels = ["C1", "C2", "C3"]

        expr = sp_node_to_expression(series, labels)
        assert expr == "((C1||C2)+C3)"

    def test_nested_expression(self):
        """Test expression for (((C1+C2)||C3)+C4)."""
        c1 = Leaf(0, 1e-12)
        c2 = Leaf(1, 2e-12)
        c3 = Leaf(2, 3e-12)
        c4 = Leaf(3, 4e-12)

        series_12 = Series(c1, c2)
        parallel_123 = Parallel(series_12, c3)
        series_1234 = Series(parallel_123, c4)
        labels = ["C1", "C2", "C3", "C4"]

        expr = sp_node_to_expression(series_1234, labels)
        assert expr == "(((C1+C2)||C3)+C4)"


class TestInvalidInput:
    """Test error handling for invalid inputs."""

    def test_unknown_node_type_raises_error(self):
        """Test that unknown node type raises TypeError."""
        # Create a mock object that's not a valid SPNode
        invalid_node = "not a node"  # type: ignore

        with pytest.raises(TypeError, match="Unknown SPNode type"):
            calculate_sp_ceq(invalid_node)  # type: ignore

    def test_expression_unknown_node_type(self):
        """Test that expression generation raises TypeError for unknown node."""
        invalid_node = "not a node"  # type: ignore

        with pytest.raises(TypeError, match="Unknown SPNode type"):
            sp_node_to_expression(invalid_node, ["C1"])  # type: ignore
