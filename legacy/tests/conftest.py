"""Pytest configuration and shared fixtures.

This module provides pytest configuration, shared fixtures, and test setup
for the CapAssigner test suite.
"""

import pytest
import networkx as nx
from tests.unit.test_fixtures import KNOWN_SOLUTIONS, ToleranceLevel


# =============================================================================
# Simple Fixtures (Phase 2, T008)
# =============================================================================

@pytest.fixture
def simple_caps():
    """Simple 2-3 capacitor set for basic unit tests.

    Returns:
        List of 2 capacitor values in Farads for quick tests.
    """
    return [5e-12, 10e-12]


@pytest.fixture
def sample_capacitors():
    """Provide sample capacitor list for tests.

    Returns:
        List of capacitor values in Farads.
    """
    return [1e-12, 2e-12, 5e-12, 10e-12]


@pytest.fixture
def sample_names():
    """Provide sample capacitor names for tests.

    Returns:
        List of capacitor names matching sample_capacitors.
    """
    return ["C1", "C2", "C3", "C4"]


# =============================================================================
# Known Solution Fixtures (Phase 2, T014)
# =============================================================================

@pytest.fixture
def classroom_4cap():
    """The 4-capacitor classroom example from bug report.
    
    ⚠️ WARNING: Contains PLACEHOLDER values - see spec.md Open Questions.
    
    Returns:
        TestCase dictionary with classroom example data.
    """
    return KNOWN_SOLUTIONS["classroom_4cap"]


@pytest.fixture
def get_regression_cases():
    """Factory fixture for regression test cases (Phase 4, T036).
    
    Returns a callable that provides REGRESSION_CASES list.
    This enables pytest.mark.parametrize with lazy fixture evaluation.
    
    Returns:
        Callable that returns list of regression test case dictionaries.
    """
    def _get_cases():
        from tests.unit.test_fixtures import REGRESSION_CASES
        return REGRESSION_CASES
    return _get_cases


# =============================================================================
# Graph Algorithm Fixtures (Phase 2, T009)
# =============================================================================

@pytest.fixture
def sample_graph():
    """Simple graph topology for graph algorithm tests.
    
    Creates a basic graph with 3 nodes and 2 edges for testing
    graph-based capacitance calculations.
    
    Returns:
        NetworkX Graph with capacitance edge attributes.
    """
    G = nx.Graph()
    G.add_edge('A', 'B', capacitance=5e-12)
    G.add_edge('B', 'C', capacitance=10e-12)
    return G


# =============================================================================
# Tolerance Level Access (convenience)
# =============================================================================

@pytest.fixture
def tolerance_levels():
    """Provide access to tolerance level constants.
    
    Returns:
        ToleranceLevel class with EXACT, APPROXIMATE constants.
    """
    return ToleranceLevel


# Add more shared fixtures as needed

