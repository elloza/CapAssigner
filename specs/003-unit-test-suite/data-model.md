# Data Model: Comprehensive Unit Test Suite

**Feature**: Comprehensive Unit Test Suite for Circuit Algorithms
**Date**: 2025-12-12  
**Purpose**: Define data structures for test cases, fixtures, and test execution entities

---

## Overview

This data model defines the structure of test cases, regression test data, and test execution entities. These are NOT runtime entities for the main application, but rather the structure of test data and test organization.

---

## Entities

### 1. TestCase

**Description**: Represents a single test scenario with inputs, expected outputs, and metadata.

**Attributes**:
- `name`: str - Unique identifier for the test case
- `description`: str - Human-readable explanation of what is being tested
- `capacitors`: List[float] - Input capacitor values in Farads
- `target_ceq`: float | None - Target equivalent capacitance (None for topology generation tests)
- `tolerance_pct`: float | None - Acceptable error percentage (None for exact match tests)
- `expected_topology`: str | None - Expected circuit expression (e.g., "(C1||C2)+C3")
- `expected_ceq`: float | None - Expected calculated capacitance
- `expected_error_pct`: float | None - Expected error percentage for approximate solutions
- `source`: str - Origin of test case (e.g., "classroom example", "hand-calculated", "mathematical proof")
- `priority`: str - Test priority: "P1" (critical), "P2" (important), "P3" (nice-to-have)
- `category`: str - Test category: "unit", "integration", "regression", "edge_case"

**Relationships**:
- Contained in TestFixture collections
- Referenced by test functions via pytest parametrize

**Validation Rules**:
- `capacitors` MUST NOT be empty (unless testing error handling)
- All capacitor values MUST be positive (unless testing error handling)
- `expected_ceq` MUST be positive if provided
- `tolerance_pct` MUST be >= 0 if provided
- `name` MUST be unique within test fixture collection

**Example**:
```python
{
    "name": "classroom_4cap_exact",
    "description": "4-capacitor classroom example with known exact solution",
    "capacitors": [1e-12, 2e-12, 5e-12, 10e-12],
    "target_ceq": 3.33e-12,
    "tolerance_pct": 1.0,
    "expected_topology": "((C1||C2)+C3)+C4",  # TBD from bug analysis
    "expected_ceq": 3.33e-12,
    "expected_error_pct": 0.0,
    "source": "Professor classroom Dec 2025 bug report",
    "priority": "P1",
    "category": "regression"
}
```

---

### 2. RegressionSuite

**Description**: Collection of regression test cases organized by category.

**Attributes**:
- `name`: str - Suite identifier
- `test_cases`: List[TestCase] - All test cases in this suite
- `min_count`: int - Minimum required test cases (20 per clarification)
- `categories`: Dict[str, List[TestCase]] - Test cases grouped by category
- `execution_time_budget_sec`: float - Maximum allowed execution time (20s per clarification)

**Relationships**:
- Contains multiple TestCase entities
- Referenced by pytest test functions

**Validation Rules**:
- MUST contain at least `min_count` test cases
- MUST include at least one P1 priority test case
- SHOULD have balanced distribution across categories
- Total execution time MUST be under budget

**Categories** (20+ cases total):
- `simple_2_3_cap`: 3 cases - Basic series/parallel with N=2-3
- `medium_4_6_cap`: 8 cases - Diverse topologies including bug case
- `complex_7_8_cap`: 4 cases - Ensure enumeration scales
- `edge_cases`: 3 cases - Single capacitor, identical values, extreme ratios
- `classroom_examples`: 2+ cases - Professor-provided examples

---

### 3. AlgorithmComponent

**Description**: Represents a testable algorithmic unit within the core modules.

**Attributes**:
- `module_name`: str - Python module (e.g., "sp_enumeration", "graphs")
- `function_name`: str - Function under test
- `input_schema`: Dict - Expected input types and constraints
- `output_schema`: Dict - Expected output types
- `complexity`: str - Time complexity (e.g., "O(n²)", "O(2ⁿ)")
- `dependencies`: List[str] - Other components this depends on
- `pure_function`: bool - Whether function is pure (no side effects)
- `deterministic`: bool - Whether same inputs always produce same outputs

**Relationships**:
- Maps to test files (e.g., `sp_enumeration` → `test_sp_enumeration.py`)
- Referenced by unit tests and integration tests

**Validation Rules**:
- MUST have corresponding test file in `tests/unit/`
- MUST achieve 100% coverage per FR-003
- Pure functions MUST NOT have side effects in tests

**Core Algorithm Components**:

| Component | Module | Key Functions | Test File |
|-----------|--------|---------------|-----------|
| SP Structures | sp_structures.py | calculate_sp_ceq, sp_node_to_expression | test_sp_structures.py |
| SP Enumeration | sp_enumeration.py | enumerate_sp_topologies, find_best_sp_solutions | test_sp_enumeration.py |
| Graph Topology | graphs.py | calculate_graph_ceq, build_laplacian_matrix | test_graphs.py |
| Heuristic Search | heuristics.py | generate_random_graph, heuristic_search | test_heuristics.py |
| Metrics | metrics.py | calculate_absolute_error, calculate_relative_error | test_metrics.py |
| Parsing | parsing.py | parse_capacitance_value, format_capacitance | test_parsing.py |

---

### 4. ToleranceLevel

**Description**: Defines acceptable error thresholds for different test types.

**Attributes**:
- `name`: str - Tolerance level name
- `relative_error_threshold`: float - Maximum relative error
- `use_case`: str - When to apply this tolerance
- `formula`: str - How to calculate error for this level

**Relationships**:
- Referenced by assertion helper functions
- Used in TestCase validation

**Validation Rules**:
- `relative_error_threshold` MUST be positive
- MUST be used consistently across similar test types

**Defined Tolerance Levels**:

| Name | Threshold | Use Case | Formula |
|------|-----------|----------|---------|
| Exact | 1e-10 | Exact mathematical solutions | &#124;(actual - expected) / expected&#124; < 1e-10 |
| Approximate | 1e-6 | Heuristic algorithm outputs | &#124;(actual - expected) / expected&#124; < 1e-6 |
| User | Variable (e.g., 5%) | User-facing tolerance checks | &#124;(actual - expected) / expected&#124; < tolerance/100 |

---

### 5. TestFixture

**Description**: Reusable test data that can be injected into multiple tests.

**Attributes**:
- `name`: str - Fixture identifier (pytest fixture name)
- `data_type`: str - Type of data ("capacitor_list", "test_case", "known_solution")
- `value`: Any - The actual fixture data
- `scope`: str - pytest scope ("function", "module", "session")
- `description`: str - What this fixture provides

**Relationships**:
- Defined in `conftest.py` or `test_fixtures.py`
- Injected into test functions via pytest dependency injection

**Validation Rules**:
- MUST be defined in conftest.py or imported from test_fixtures
- MUST have matching pytest `@pytest.fixture` decorator
- Scope MUST be appropriate for data mutability

**Common Fixtures**:

```python
@pytest.fixture
def simple_caps() -> List[float]:
    """2-3 capacitors for basic unit tests."""
    return [5e-12, 10e-12]

@pytest.fixture
def classroom_4cap() -> TestCase:
    """The 4-capacitor bug report case."""
    return {
        "capacitors": [1e-12, 2e-12, 5e-12, 10e-12],
        "target_ceq": 3.33e-12,
        # ... rest of TestCase attributes
    }

@pytest.fixture
def sample_graph() -> nx.Graph:
    """Simple graph topology for graph algorithm tests."""
    G = nx.Graph()
    G.add_edge('A', 'B', capacitance=5e-12)
    return G
```

---

### 6. AssertionHelper

**Description**: Utility functions for making tolerance-aware assertions.

**Attributes**:
- `function_name`: str - Helper function name
- `tolerance_level`: ToleranceLevel - Which tolerance to apply
- `parameters`: List[str] - Expected parameters
- `error_message_template`: str - Template for assertion failure messages

**Relationships**:
- Uses ToleranceLevel definitions
- Called by test functions

**Validation Rules**:
- MUST provide clear error messages with actual vs expected values
- MUST include relative error in failure messages
- SHOULD include context (test case name) in messages

**Defined Helpers**:

```python
def assert_exact_match(actual: float, expected: float, description: str = "") -> None:
    """Assert values match within exact solution tolerance (1e-10)."""
    
def assert_approximate_match(actual: float, expected: float, description: str = "") -> None:
    """Assert values match within approximate solution tolerance (1e-6)."""
    
def assert_within_tolerance(actual: float, expected: float, tolerance_pct: float, description: str = "") -> None:
    """Assert values match within user-specified tolerance percentage."""
    
def assert_topologies_equivalent(actual: SPNode, expected: str) -> None:
    """Assert topology expression matches expected string representation."""
```

---

### 7. TestMetrics

**Description**: Tracks test execution metrics for monitoring test suite health.

**Attributes**:
- `total_tests`: int - Number of test cases executed
- `passed`: int - Number of tests passed
- `failed`: int - Number of tests failed
- `skipped`: int - Number of tests skipped
- `execution_time_sec`: float - Total execution time
- `coverage_pct`: float - Code coverage percentage
- `timestamp`: datetime - When tests were run

**Relationships**:
- Generated by pytest execution
- Can be exported for CI/CD reporting

**Validation Rules**:
- `execution_time_sec` SHOULD be < 30 seconds for full suite
- `coverage_pct` TARGET is 100% for core algorithm modules
- `passed / total_tests` SHOULD be > 0.95 (95% pass rate)

**Monitoring Thresholds**:
- ✅ PASS: execution_time < 30s, coverage > 90%, pass_rate > 95%
- ⚠️ WARNING: execution_time 30-45s, coverage 80-90%, pass_rate 90-95%
- ❌ FAIL: execution_time > 45s, coverage < 80%, pass_rate < 90%

---

## Relationships Diagram

```
RegressionSuite
    │
    ├── contains ──> TestCase (20+)
    │                   │
    │                   ├── uses ──> ToleranceLevel
    │                   └── references ──> AlgorithmComponent
    │
    └── execution ──> TestMetrics

TestFixture
    │
    ├── provides ──> TestCase data
    └── injected by ──> pytest

AssertionHelper
    │
    ├── uses ──> ToleranceLevel
    └── called by ──> Test Functions

AlgorithmComponent
    │
    ├── tested by ──> Unit Tests
    └── integrated in ──> Integration Tests
```

---

## Validation Matrix

| Entity | Validation Rule | Test Method |
|--------|----------------|-------------|
| TestCase | `capacitors` non-empty | pytest validates fixture data |
| TestCase | `expected_ceq` positive | Schema validation in fixtures |
| RegressionSuite | Min 20 test cases | Count test cases in test_regression.py |
| AlgorithmComponent | 100% test coverage | pytest-cov measures coverage |
| ToleranceLevel | Consistent application | Code review of assertion usage |
| TestMetrics | Execution < 30s | pytest reports total time |
| TestMetrics | Coverage > 90% | pytest-cov reports percentage |

---

## Implementation Notes

### File Organization

- **test_fixtures.py**: Contains TestCase collections (KNOWN_SOLUTIONS, REGRESSION_CASES)
- **conftest.py**: Contains pytest fixtures that wrap test_fixtures data
- **test_regression.py**: Parametrized tests using RegressionSuite data
- **test_*.py**: Unit tests for AlgorithmComponents

### Data Format Example

```python
# test_fixtures.py
REGRESSION_CASES = [
    {
        "name": "simple_series_2cap",
        "capacitors": [5e-12, 10e-12],
        "expected_ceq": 3.33e-12,  # 1/(1/5 + 1/10) = 3.33pF
        "expected_topology": "C0+C1",  # Series notation
        "category": "simple_2_3_cap",
        "priority": "P2"
    },
    {
        "name": "classroom_4cap_bug",
        "capacitors": [1e-12, 2e-12, 5e-12, 10e-12],
        "target_ceq": 3.33e-12,
        "expected_error_pct": 0.0,  # Should find exact solution
        "category": "medium_4_6_cap",
        "priority": "P1",
        "source": "Bug report PDF Dec 2025"
    },
    # ... 18+ more cases
]
```

---

## Constitutional Compliance

This data model supports constitutional principles:

- **Principle I (Modular Architecture)**: Test data is separated from core algorithms
- **Principle IV (Algorithmic Correctness)**: Explicit validation of mathematical formulas
- **Principle V (Deterministic Reproducibility)**: Fixed test data enables reproducible test runs

---

**Status**: Complete - Ready for Phase 1 contracts generation
