"""Shared test fixtures and utilities for unit tests.

This module provides reusable test data, assertion helpers, and fixture
definitions for the comprehensive unit test suite.
"""

from typing import Any, Dict, List, Union
import math


# =============================================================================
# Tolerance Levels (Phase 2, T006)
# =============================================================================

class ToleranceLevel:
    """Tolerance thresholds for different test types."""
    
    # Exact solutions - for known mathematical identities
    # Use for SP topology calculations compared to hand-calculated values
    EXACT = 1e-10
    
    # Approximate solutions - for heuristic algorithm outputs
    # Tight enough to catch significant errors
    APPROXIMATE = 1e-6
    
    # User-facing tolerance - configurable percentage
    # For acceptance criteria visible to end users
    @staticmethod
    def user_tolerance(percentage: float) -> float:
        """Convert user percentage to decimal tolerance.
        
        Args:
            percentage: Tolerance as percentage (e.g., 5.0 for 5%)
            
        Returns:
            Tolerance as decimal (e.g., 0.05)
        """
        return percentage / 100.0


# =============================================================================
# Assertion Helpers (Phase 1, T005)
# =============================================================================

def assert_exact_match(actual: float, expected: float, description: str = "") -> None:
    """Assert values match within exact solution tolerance.
    
    Uses relative error threshold of 1e-10 for exact mathematical solutions.
    
    Args:
        actual: The actual computed value
        expected: The expected value
        description: Optional description for assertion failure message
        
    Raises:
        AssertionError: If relative error exceeds EXACT tolerance
    """
    if expected != 0:
        rel_error = abs((actual - expected) / expected)
    else:
        rel_error = abs(actual)
    
    assert rel_error < ToleranceLevel.EXACT, (
        f"{description}: rel_error={rel_error:.2e}, "
        f"actual={actual:.6e}, expected={expected:.6e}"
    )


def assert_approximate_match(actual: float, expected: float, description: str = "") -> None:
    """Assert values match within approximate solution tolerance.
    
    Uses relative error threshold of 1e-6 for heuristic algorithm outputs.
    
    Args:
        actual: The actual computed value
        expected: The expected value
        description: Optional description for assertion failure message
        
    Raises:
        AssertionError: If relative error exceeds APPROXIMATE tolerance
    """
    if expected != 0:
        rel_error = abs((actual - expected) / expected)
    else:
        rel_error = abs(actual)
    
    assert rel_error < ToleranceLevel.APPROXIMATE, (
        f"{description}: rel_error={rel_error:.2e}, "
        f"actual={actual:.6e}, expected={expected:.6e}"
    )


def assert_within_tolerance(
    actual: float,
    expected: float,
    tolerance_pct: float,
    description: str = ""
) -> None:
    """Assert values match within custom percentage tolerance.
    
    Args:
        actual: The actual computed value
        expected: The expected value
        tolerance_pct: Tolerance as percentage (e.g., 5.0 for 5%)
        description: Optional description for assertion failure message
        
    Raises:
        AssertionError: If relative error exceeds tolerance
    """
    if expected != 0:
        rel_error = abs((actual - expected) / expected)
    else:
        rel_error = abs(actual)
    
    tolerance = ToleranceLevel.user_tolerance(tolerance_pct)
    
    assert rel_error < tolerance, (
        f"{description}: rel_error={rel_error:.2%}, "
        f"actual={actual:.6e}, expected={expected:.6e}, "
        f"tolerance={tolerance_pct}%"
    )


# =============================================================================
# Test Data Structures (Phase 2, T007)
# =============================================================================

# TestCase structure following contracts/test-contracts.yaml schema
TestCaseDict = Dict[str, Any]


def create_test_case(
    name: str,
    description: str,
    capacitors: List[float],
    source: str,
    priority: str,
    category: str,
    target_ceq: Union[float, None] = None,
    tolerance_pct: Union[float, None] = None,
    expected_topology: Union[str, None] = None,
    expected_ceq: Union[float, None] = None,
    expected_error_pct: Union[float, None] = None
) -> TestCaseDict:
    """Create a TestCase dictionary following the contract schema.
    
    Args:
        name: Unique identifier using snake_case
        description: Human-readable explanation
        capacitors: Input capacitor values in Farads
        source: Origin of test case for traceability
        priority: Test priority ("P1", "P2", "P3", "P4")
        category: Test category ("unit", "integration", "regression", "edge_case")
        target_ceq: Optional target equivalent capacitance
        tolerance_pct: Optional acceptable error percentage
        expected_topology: Optional expected circuit expression
        expected_ceq: Optional expected calculated capacitance
        expected_error_pct: Optional expected error percentage
        
    Returns:
        Dictionary following TestCase contract schema
    """
    test_case = {
        "name": name,
        "description": description,
        "capacitors": capacitors,
        "source": source,
        "priority": priority,
        "category": category,
    }
    
    # Add optional fields only if provided
    if target_ceq is not None:
        test_case["target_ceq"] = target_ceq
    if tolerance_pct is not None:
        test_case["tolerance_pct"] = tolerance_pct
    if expected_topology is not None:
        test_case["expected_topology"] = expected_topology
    if expected_ceq is not None:
        test_case["expected_ceq"] = expected_ceq
    if expected_error_pct is not None:
        test_case["expected_error_pct"] = expected_error_pct
    
    return test_case


# =============================================================================
# Known Solutions Repository
# =============================================================================

# Classroom 4-capacitor example from professor's textbook
# Source: Textbook diagram showing exact solution C_eq = 1pF
#
# REAL VALUES (confirmed from textbook):
# - C1 = 2pF (not used in correct topology, but available)
# - C2 = 3pF (between nodes C-D in parallel with C4)
# - C3 = 3pF (appears TWICE: A-C and B-D in series)
# - C4 = 1pF (between nodes C-D in parallel with C2)
# - Target: C_eq = 1pF (EXACT solution exists)
#
# CORRECT TOPOLOGY (from textbook):
# Network with internal nodes C and D:
#   A ---[C3=3pF]--- C ---[C2=2pF || C4=1pF]--- D ---[C3=3pF]--- B
#
# Calculation:
#   Step 1: C_eq5 = C2 + C4 = 2pF + 1pF = 3pF (parallel between C-D)
#   Step 2: 1/C_eq = 1/C3 + 1/C_eq5 + 1/C3 = 1/3 + 1/3 + 1/3 = 1
#           C_eq = 1pF (EXACT)
#
# CURRENT BUG:
# Program generates wrong topology: (C1 + C2 + (C3||C4))
#   C3||C4 = 3+1 = 4pF
#   1/C_eq = 1/2 + 1/3 + 1/4 = 1.0833... → C_eq = 0.923pF
#   Error = |0.923-1.0|/1.0 = 7.69% ❌
#
# ROOT CAUSE HYPOTHESIS:
# SP enumeration algorithm may not be generating topologies with
# internal nodes (C, D) where multiple capacitors connect in parallel
# between internal nodes. It's generating "ladder" topologies only.

CLASSROOM_4CAP = create_test_case(
    name="classroom_4cap_exact",
    description="4-capacitor textbook example with known exact solution C_eq=1pF",
    capacitors=[2e-12, 3e-12, 3e-12, 1e-12],  # C1=2pF, C2=3pF, C3=3pF, C4=1pF
    target_ceq=1e-12,  # 1pF EXACT
    tolerance_pct=1.0,
    # Expected topology uses graph representation with internal nodes:
    # A-[3pF]-C-[2pF||1pF]-D-[3pF]-B where two 3pF caps are in series
    expected_topology="(C3_1 + (C2 || C4) + C3_2)",  # Conceptual notation
    expected_ceq=1e-12,  # 1pF EXACT
    expected_error_pct=0.0,  # Should be exact
    source="Professor's textbook Dec 2025 - Exercise with diagram",
    priority="P1",
    category="medium"  # 4-capacitor medium complexity case
)

# Additional note: The textbook shows C3 appearing TWICE in the circuit
# This is a key insight - we need to check if the SP enumeration allows
# using the same capacitor value multiple times in different positions
CLASSROOM_4CAP["notes"] = (
    "Critical: C3=3pF appears TWICE in correct topology. "
    "Check if enumeration algorithm handles repeated capacitor usage."
)

# Known solutions will be populated as test cases are created
KNOWN_SOLUTIONS = {
    "classroom_4cap": CLASSROOM_4CAP,
}


# =============================================================================
# Regression Test Suite Data (Phase 4, T029-T035)
# =============================================================================

# T030: Simple 2-3 capacitor cases
SIMPLE_REGRESSION_CASES = [
    {
        "name": "series_equal_2cap",
        "description": "Two equal capacitors in series",
        "capacitors": [10e-12, 10e-12],
        "target_ceq": 5e-12,  # Series: 1/(1/10 + 1/10) = 5pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Hand-calculated series formula",
        "expected_topology": "Series(C1, C2)",
        "category": "simple",
        "priority": "P2"
    },
    {
        "name": "parallel_equal_2cap",
        "description": "Two equal capacitors in parallel",
        "capacitors": [5e-12, 5e-12],
        "target_ceq": 10e-12,  # Parallel: 5 + 5 = 10pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Hand-calculated parallel formula",
        "expected_topology": "Parallel(C1, C2)",
        "category": "simple",
        "priority": "P2"
    },
    {
        "name": "mixed_simple_3cap",
        "description": "Mixed series-parallel with 3 capacitors",
        "capacitors": [6e-12, 3e-12, 3e-12],
        "target_ceq": 3e-12,  # (3||3) series 6 = 6 series 6 = 3pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Hand-calculated: Parallel(3,3)=6pF, then Series(6,6)=3pF",
        "expected_topology": "Series(C1, Parallel(C2, C3))",
        "category": "simple",
        "priority": "P2"
    },
]

# T031: Medium 4-6 capacitor cases (includes classroom)
MEDIUM_REGRESSION_CASES = [
    CLASSROOM_4CAP,
    {
        "name": "all_parallel_4cap",
        "description": "Four capacitors all in parallel",
        "capacitors": [1e-12, 2e-12, 3e-12, 4e-12],
        "target_ceq": 10e-12,  # 1+2+3+4 = 10pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Sum of all capacitors",
        "expected_topology": "Parallel(Parallel(Parallel(C1, C2), C3), C4)",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "all_series_4cap",
        "description": "Four equal capacitors in series",
        "capacitors": [12e-12, 12e-12, 12e-12, 12e-12],
        "target_ceq": 3e-12,  # 1/(4 * 1/12) = 12/4 = 3pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Series formula: C_eq = C/n for n equal caps",
        "expected_topology": "Series(Series(Series(C1, C2), C3), C4)",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "ladder_4cap",
        "description": "Ladder network with 4 capacitors",
        "capacitors": [3e-12, 6e-12, 6e-12, 3e-12],
        "target_ceq": 1e-12,  # Series(Parallel(3,6), Parallel(3,6)) = Series(2, 2) = 1pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Symmetric ladder: (3||6) = 2pF, then 2 series 2 = 1pF",
        "expected_topology": "Series(Parallel(C1, C2), Parallel(C3, C4))",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "all_equal_5cap",
        "description": "Five equal capacitors - multiple solutions",
        "capacitors": [8e-12, 8e-12, 8e-12, 8e-12, 8e-12],
        "target_ceq": 8e-12,  # Many ways: (8||8) series (8||8||8), etc.
        "tolerance_pct": 20.0,  # Cannot achieve exact 8pF with SP - theoretical only
        "source": "Symmetry test - no exact SP solution exists",
        "expected_topology": "Multiple",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "sequential_5cap",
        "description": "Sequential values 1-5 pF",
        "capacitors": [1e-12, 2e-12, 3e-12, 4e-12, 5e-12],
        "target_ceq": 15e-12,  # All parallel: 1+2+3+4+5 = 15pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "All parallel configuration",
        "expected_topology": "Parallel(...)",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "e12_subset_6cap",
        "description": "Subset of E12 series values",
        "capacitors": [10e-12, 12e-12, 15e-12, 18e-12, 22e-12, 27e-12],
        "target_ceq": 20e-12,  # Realistic target with standard values
        "tolerance_pct": 5.0,  # Accept solutions within 5%
        "source": "E12 series realistic case",
        "expected_topology": "Various",
        "category": "medium",
        "priority": "P2"
    },
    {
        "name": "powers_of_two_6cap",
        "description": "Powers of 2 sequence",
        "capacitors": [1e-12, 2e-12, 4e-12, 8e-12, 16e-12, 32e-12],
        "target_ceq": 7e-12,  # 1+2+4 = 7pF (binary combination)
        "tolerance_pct": 1.0,  # Allow 1% tolerance for practical matching
        "source": "Binary-like combination",
        "expected_topology": "Parallel(Parallel(C1, C2), C3)",
        "category": "medium",
        "priority": "P2"
    },
]

# T032: Complex 7-8 capacitor cases (scalability tests)
COMPLEX_REGRESSION_CASES = [
    {
        "name": "equal_7cap",
        "description": "Seven equal capacitors - memoization stress test",
        "capacitors": [10e-12] * 7,
        "target_ceq": 10e-12,  # Many equivalent topologies
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Stress test for memoization with identical values",
        "expected_topology": "Multiple equivalent",
        "category": "complex",
        "priority": "P2"
    },
    {
        "name": "fibonacci_7cap",
        "description": "Fibonacci sequence capacitors",
        "capacitors": [1e-12, 1e-12, 2e-12, 3e-12, 5e-12, 8e-12, 13e-12],
        "target_ceq": 5e-12,  # Tests interesting ratios
        "tolerance_pct": 0.5,  # Allow 0.5% for approximation
        "source": "Mathematical sequence test",
        "expected_topology": "Various",
        "category": "complex",
        "priority": "P2"
    },
    {
        "name": "random_8cap",
        "description": "Eight random-ish values",
        "capacitors": [1.5e-12, 2.7e-12, 3.3e-12, 4.7e-12, 5.6e-12, 6.8e-12, 8.2e-12, 9.1e-12],
        "target_ceq": 10e-12,
        "tolerance_pct": 10.0,  # Accept solutions within 10%
        "source": "Random values - general case",
        "expected_topology": "Various",
        "category": "complex",
        "priority": "P3"
    },
    {
        "name": "decade_range_8cap",
        "description": "Values spanning a decade (1-10 pF)",
        "capacitors": [1e-12, 2e-12, 3e-12, 4e-12, 5e-12, 7e-12, 8e-12, 10e-12],
        "target_ceq": 5e-12,
        "tolerance_pct": 0.1,  # APPROXIMATE: < 0.1%
        "source": "Wide range test",
        "expected_topology": "Various",
        "category": "complex",
        "priority": "P3"
    },
]

# T033: Edge cases
EDGE_REGRESSION_CASES = [
    {
        "name": "single_capacitor",
        "description": "Trivial case - only one capacitor",
        "capacitors": [7.5e-12],
        "target_ceq": 7.5e-12,
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Edge case: single element",
        "expected_topology": "Leaf(C1)",
        "category": "edge",
        "priority": "P2"
    },
    {
        "name": "all_identical_4cap",
        "description": "All capacitors have identical value",
        "capacitors": [10e-12, 10e-12, 10e-12, 10e-12],
        "target_ceq": 10e-12,  # (10||10) series (10||10) = 20 series 20 = 10pF
        "tolerance_pct": 0.00001,  # EXACT: < 0.00001%
        "source": "Symmetry edge case",
        "expected_topology": "Series(Parallel(C1, C2), Parallel(C3, C4))",
        "category": "edge",
        "priority": "P2"
    },
    {
        "name": "extreme_ratio",
        "description": "Extreme capacitor ratio (1:1000)",
        "capacitors": [1e-12, 1000e-12],
        "target_ceq": 0.999e-12,  # Series ≈ smaller value
        "tolerance_pct": 0.1,  # APPROXIMATE: < 0.1%
        "source": "Series of extreme ratio",
        "expected_topology": "Series(C1, C2)",
        "category": "edge",
        "priority": "P2"
    },
]

# T034: Additional classroom examples (to be added from professor or created)
CLASSROOM_EXAMPLES = [
    CLASSROOM_4CAP,  # Original classroom example
    # More to be added as they are collected
]

# Combined regression test suite
REGRESSION_CASES: List[TestCaseDict] = (
    SIMPLE_REGRESSION_CASES +
    MEDIUM_REGRESSION_CASES +
    COMPLEX_REGRESSION_CASES +
    EDGE_REGRESSION_CASES
)

# Category mapping for filtering
REGRESSION_BY_CATEGORY = {
    "simple": SIMPLE_REGRESSION_CASES,
    "medium": MEDIUM_REGRESSION_CASES,
    "complex": COMPLEX_REGRESSION_CASES,
    "edge": EDGE_REGRESSION_CASES,
    "classroom": CLASSROOM_EXAMPLES,
}


