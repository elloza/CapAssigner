"""Validation tests for test fixtures and utilities.

This test file validates that the new test infrastructure (Phase 1-2)
works correctly before proceeding with Phase 3 implementation.
"""

import pytest
from tests.unit.test_fixtures import (
    ToleranceLevel,
    assert_exact_match,
    assert_approximate_match,
    assert_within_tolerance,
    create_test_case,
    CLASSROOM_4CAP,
)


class TestToleranceLevels:
    """Validate ToleranceLevel constants (T006)."""

    def test_exact_tolerance_value(self):
        """Verify EXACT tolerance is 1e-10."""
        assert ToleranceLevel.EXACT == 1e-10

    def test_approximate_tolerance_value(self):
        """Verify APPROXIMATE tolerance is 1e-6."""
        assert ToleranceLevel.APPROXIMATE == 1e-6

    def test_user_tolerance_conversion(self):
        """Verify user_tolerance converts percentage to decimal."""
        assert ToleranceLevel.user_tolerance(5.0) == 0.05
        assert ToleranceLevel.user_tolerance(1.0) == 0.01
        assert ToleranceLevel.user_tolerance(10.0) == 0.10


class TestAssertionHelpers:
    """Validate assertion helper functions (T005)."""

    def test_assert_exact_match_passes_for_exact_values(self):
        """Verify exact match assertion passes for identical values."""
        assert_exact_match(1.0, 1.0, "identical values")

    def test_assert_exact_match_passes_within_tolerance(self):
        """Verify exact match passes for values within 1e-10."""
        assert_exact_match(1.0, 1.0 + 1e-11, "within tolerance")

    def test_assert_exact_match_fails_outside_tolerance(self):
        """Verify exact match fails for values outside 1e-10."""
        with pytest.raises(AssertionError):
            assert_exact_match(1.0, 1.0 + 1e-9, "outside tolerance")

    def test_assert_approximate_match_passes_within_tolerance(self):
        """Verify approximate match passes for values within 1e-6."""
        assert_approximate_match(1.0, 1.0 + 1e-7, "within tolerance")

    def test_assert_approximate_match_fails_outside_tolerance(self):
        """Verify approximate match fails for values outside 1e-6."""
        with pytest.raises(AssertionError):
            assert_approximate_match(1.0, 1.0 + 1e-5, "outside tolerance")

    def test_assert_within_tolerance_custom_percentage(self):
        """Verify custom tolerance works correctly."""
        assert_within_tolerance(100.0, 105.0, 5.0, "5% tolerance")
        
        with pytest.raises(AssertionError):
            assert_within_tolerance(100.0, 110.0, 5.0, "exceeds 5%")


class TestTestCaseCreation:
    """Validate TestCase creation function (T007)."""

    def test_create_test_case_required_fields(self):
        """Verify create_test_case populates required fields."""
        test_case = create_test_case(
            name="test_example",
            description="Example test case",
            capacitors=[1e-12, 2e-12],
            source="unit test",
            priority="P2",
            category="unit"
        )
        
        assert test_case["name"] == "test_example"
        assert test_case["description"] == "Example test case"
        assert test_case["capacitors"] == [1e-12, 2e-12]
        assert test_case["source"] == "unit test"
        assert test_case["priority"] == "P2"
        assert test_case["category"] == "unit"

    def test_create_test_case_optional_fields(self):
        """Verify optional fields are included when provided."""
        test_case = create_test_case(
            name="test_with_optionals",
            description="Test with all optional fields",
            capacitors=[5e-12],
            source="unit test",
            priority="P1",
            category="regression",
            target_ceq=5e-12,
            tolerance_pct=1.0,
            expected_topology="C0",
            expected_ceq=5e-12,
            expected_error_pct=0.0
        )
        
        assert test_case["target_ceq"] == 5e-12
        assert test_case["tolerance_pct"] == 1.0
        assert test_case["expected_topology"] == "C0"
        assert test_case["expected_ceq"] == 5e-12
        assert test_case["expected_error_pct"] == 0.0

    def test_create_test_case_omits_none_optionals(self):
        """Verify optional fields are omitted when None."""
        test_case = create_test_case(
            name="test_minimal",
            description="Minimal test case",
            capacitors=[1e-12],
            source="unit test",
            priority="P3",
            category="unit"
        )
        
        assert "target_ceq" not in test_case
        assert "tolerance_pct" not in test_case
        assert "expected_topology" not in test_case


class TestFixtureIntegration:
    """Validate pytest fixtures work correctly (T008, T009, T014)."""

    def test_simple_caps_fixture(self, simple_caps):
        """Verify simple_caps fixture provides 2 capacitors."""
        assert len(simple_caps) == 2
        assert simple_caps == [5e-12, 10e-12]

    def test_sample_capacitors_fixture(self, sample_capacitors):
        """Verify sample_capacitors fixture provides 4 capacitors."""
        assert len(sample_capacitors) == 4
        assert sample_capacitors == [1e-12, 2e-12, 5e-12, 10e-12]

    def test_sample_graph_fixture(self, sample_graph):
        """Verify sample_graph fixture creates valid NetworkX graph."""
        assert sample_graph.number_of_nodes() == 3
        assert sample_graph.number_of_edges() == 2
        assert sample_graph.has_edge('A', 'B')
        assert sample_graph['A']['B']['capacitance'] == 5e-12

    def test_classroom_4cap_fixture(self, classroom_4cap):
        """Verify classroom_4cap fixture structure."""
        assert classroom_4cap["name"] == "classroom_4cap_exact"
        assert len(classroom_4cap["capacitors"]) == 4
        assert classroom_4cap["priority"] == "P1"
        assert classroom_4cap["category"] == "medium"  # Updated: 4-cap is medium complexity

    def test_tolerance_levels_fixture(self, tolerance_levels):
        """Verify tolerance_levels fixture provides ToleranceLevel class."""
        assert tolerance_levels.EXACT == 1e-10
        assert tolerance_levels.APPROXIMATE == 1e-6


# Mark as fast tests since they validate infrastructure
pytestmark = pytest.mark.fast
