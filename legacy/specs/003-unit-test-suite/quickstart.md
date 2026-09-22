# Quickstart: Comprehensive Unit Test Suite

**Feature**: Comprehensive Unit Test Suite for Circuit Algorithms  
**Branch**: `003-unit-test-suite`  
**Date**: 2025-12-12

---

## Quick Reference

### Run All Tests

```bash
# Activate conda environment first
conda activate .\.conda

# Run full test suite
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=capassigner.core --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only (fast, < 10s)
pytest tests/unit/ -v

# Regression tests only
pytest tests/unit/test_regression.py -v

# Specific module tests
pytest tests/unit/test_sp_enumeration.py -v
pytest tests/unit/test_graphs.py -v

# With test selection by keyword
pytest tests/ -v -k "4cap"  # Run tests matching "4cap"
```

### Run Tests with Markers

```bash
# Fast tests only (for TDD)
pytest -m fast -v

# Slow tests
pytest -m slow -v

# Priority 1 tests only
pytest -m P1 -v
```

---

## Project Structure Quick Reference

```text
tests/
├── conftest.py              # pytest configuration and fixtures
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_sp_structures.py    # Series/parallel formula tests
│   ├── test_sp_enumeration.py   # Topology enumeration tests
│   ├── test_graphs.py           # Graph Laplacian tests
│   ├── test_heuristics.py       # Heuristic search tests
│   ├── test_metrics.py          # Error calculation tests
│   ├── test_parsing.py          # Input parsing tests
│   ├── test_regression.py       # 20+ regression test cases (NEW)
│   └── test_fixtures.py         # Shared test data (NEW)
├── integration/             # Integration tests (module interactions)
│   ├── test_workflows.py        # End-to-end workflow tests
│   └── test_end_to_end.py       # Full algorithm pipeline (NEW)
└── contract/                # API contract tests
    └── test_algorithm_contracts.py  # API stability tests (NEW)
```

---

## Key Principles

From the Constitution and Feature Spec:

1. **Modular Testing**: Core algorithm tests have NO Streamlit dependencies
2. **Tolerance-Aware Assertions**: Use appropriate epsilon for test type
   - Exact solutions: 1e-10 relative error
   - Approximate solutions: 1e-6 relative error  
   - User tolerance: Variable (e.g., 5%)
3. **Deterministic Tests**: All randomized algorithms use fixed seeds
4. **Fast Execution**: Full suite < 30s (unit < 10s, regression < 20s)
5. **Clear Failures**: Test names and error messages explain what failed and why

---

## Test Fixtures

### Available Fixtures (defined in conftest.py)

```python
@pytest.fixture
def simple_caps() -> List[float]:
    """2-3 capacitors for basic unit tests."""
    return [5e-12, 10e-12]

@pytest.fixture
def classroom_4cap() -> Dict:
    """The 4-capacitor bug report case."""
    return {
        "capacitors": [1e-12, 2e-12, 5e-12, 10e-12],
        "target_ceq": 3.33e-12,
        # ... full TestCase structure
    }

@pytest.fixture
def sample_graph() -> nx.Graph:
    """Simple graph topology for graph algorithm tests."""
    G = nx.Graph()
    G.add_edge('A', 'B', capacitance=5e-12)
    return G
```

### Using Fixtures in Tests

```python
def test_series_formula(simple_caps):
    """Test using the simple_caps fixture."""
    c1, c2 = simple_caps
    topology = Series(Leaf(0, c1), Leaf(1, c2))
    result = calculate_sp_ceq(topology)
    # assertions...
```

---

## Assertion Helpers

### Tolerance-Aware Assertions

```python
from tests.unit.test_fixtures import assert_exact_match, assert_approximate_match

def test_exact_solution():
    """Use assert_exact_match for known exact solutions."""
    result = calculate_sp_ceq(topology)
    expected = 5e-12
    assert_exact_match(result, expected, "Two 10pF caps in series")

def test_heuristic_solution():
    """Use assert_approximate_match for heuristic outputs."""
    result = heuristic_search(caps, target, seed=42)
    expected = 5.1e-12
    assert_approximate_match(result.ceq, expected, "Heuristic result")
```

### Standard Assertions

```python
# Use pytest.approx for floating-point comparisons
import pytest

def test_with_approx():
    result = calculate_ceq(topology)
    assert result == pytest.approx(5e-12, rel=1e-10)
```

---

## Writing New Tests

### Test Naming Convention

Follow pattern: `test_<component>_<scenario>_<expected_outcome>`

Examples:
- `test_sp_enumeration_n4_generates_40_topologies`
- `test_graph_ceq_disconnected_returns_zero`
- `test_heuristic_search_deterministic_with_seed`

### Test Structure Template

```python
def test_component_scenario_outcome():
    """One-line description of what is tested.
    
    More detailed explanation if needed, including:
    - Why this test exists
    - What constitutional principle it validates
    - Mathematical formula or expected behavior
    """
    # Arrange: Set up test data
    capacitors = [5e-12, 10e-12]
    expected = 3.33e-12  # Hand-calculated
    
    # Act: Execute the function under test
    result = calculate_series_ceq(capacitors)
    
    # Assert: Verify expected outcome
    assert_exact_match(result, expected, "Series of 5pF and 10pF")
```

### Parametrized Test Template

```python
@pytest.mark.parametrize("case", REGRESSION_CASES, ids=lambda c: c["name"])
def test_regression_case(case):
    """Regression test for known solutions."""
    capacitors = case["capacitors"]
    expected_ceq = case["expected_ceq"]
    
    solutions = find_best_sp_solutions(capacitors, expected_ceq, tolerance=1.0)
    
    assert len(solutions) > 0, f"No solutions found for {case['name']}"
    assert_exact_match(solutions[0].ceq, expected_ceq, case['name'])
```

---

## Debugging Failed Tests

### Verbose Output

```bash
# Show full output including print statements
pytest tests/unit/test_sp_enumeration.py -v -s

# Show local variables on failure
pytest tests/unit/ -v --showlocals

# Stop on first failure
pytest tests/unit/ -v -x
```

### Running Single Test

```bash
# Run specific test function
pytest tests/unit/test_sp_enumeration.py::test_classroom_4cap_finds_exact_solution -v

# Run specific test class
pytest tests/unit/test_graphs.py::TestGraphTopology -v
```

### Debugging with pdb

```python
def test_debugging_example():
    """Example of using pdb for debugging."""
    capacitors = [1e-12, 2e-12, 5e-12, 10e-12]
    
    import pdb; pdb.set_trace()  # Breakpoint
    
    result = enumerate_sp_topologies(capacitors)
    assert len(result) == 40
```

---

## Coverage Reports

### Generate Coverage Report

```bash
# Terminal report
pytest tests/ --cov=capassigner.core --cov-report=term

# HTML report (opens in browser)
pytest tests/ --cov=capassigner.core --cov-report=html
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html  # Windows

# Missing lines report
pytest tests/ --cov=capassigner.core --cov-report=term-missing
```

### Target Coverage

- **Core algorithm modules**: 100% coverage (FR-003, SC-004)
- **Overall project**: > 90% coverage (threshold)
- **UI modules**: Coverage optional (out of scope for this feature)

---

## Test Markers

### Available Markers

Defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "fast: Fast unit tests (< 1s each)",
    "slow: Slow tests (> 1s, typically N≥7)",
    "P1: Priority 1 - Critical tests",
    "P2: Priority 2 - Important tests",
    "P3: Priority 3 - Nice-to-have tests",
]
```

### Using Markers

```python
@pytest.mark.fast
@pytest.mark.P1
def test_critical_fast_operation():
    """Critical test that runs quickly."""
    pass

@pytest.mark.slow
@pytest.mark.P3
def test_n8_exhaustive_enumeration():
    """Slow test with lower priority."""
    pass
```

---

## Common Issues and Solutions

### Issue: Tests timeout or run too slow

**Solution**: Check if you're using large N values. Use N≤5 for unit tests, N≤7 for regression tests.

```python
# Bad: Slow for unit test
def test_enumeration():
    caps = list(range(10))  # N=10 is too large!
    result = enumerate_sp_topologies(caps)

# Good: Fast for unit test
def test_enumeration():
    caps = [5e-12, 10e-12, 15e-12]  # N=3 is fine
    result = enumerate_sp_topologies(caps)
```

### Issue: Floating-point assertion failures

**Solution**: Use appropriate tolerance level.

```python
# Bad: Exact equality for floating-point
assert result == 5e-12  # May fail due to rounding

# Good: Tolerance-aware assertion
assert_exact_match(result, 5e-12, "Description")
# or
assert result == pytest.approx(5e-12, rel=1e-10)
```

### Issue: Non-deterministic test failures

**Solution**: Use fixed seeds for random algorithms.

```python
# Bad: Random seed
result = heuristic_search(caps, target)

# Good: Fixed seed for reproducibility
result = heuristic_search(caps, target, seed=42)
```

---

## Integration with Development Workflow

### Test-Driven Development (TDD)

```bash
# 1. Write failing test
vim tests/unit/test_new_feature.py

# 2. Run test to see it fail
pytest tests/unit/test_new_feature.py -v

# 3. Implement feature
vim capassigner/core/module.py

# 4. Run test to see it pass
pytest tests/unit/test_new_feature.py -v

# 5. Refactor and verify tests still pass
pytest tests/unit/test_new_feature.py -v
```

### Pre-Commit Testing

```bash
# Run fast tests before each commit
pytest -m fast -v

# Run full suite before push
pytest tests/ -v --cov=capassigner.core
```

---

## Additional Resources

### Documentation

- **Feature Spec**: [spec.md](./spec.md) - Requirements and user stories
- **Implementation Plan**: [plan.md](./plan.md) - Technical approach
- **Research**: [research.md](./research.md) - Technical decisions and rationale
- **Data Model**: [data-model.md](./data-model.md) - Test entity definitions
- **Contracts**: [contracts/test-contracts.yaml](./contracts/test-contracts.yaml) - Test case schemas

### Related Files

- **Constitution**: `.specify/memory/constitution.md` - Project principles
- **pytest Config**: `pyproject.toml` - pytest settings
- **Coverage Config**: `.coveragerc` (if exists) - Coverage settings

### External References

- pytest documentation: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/how-to/fixtures.html
- pytest markers: https://docs.pytest.org/en/stable/example/markers.html
- pytest-cov: https://pytest-cov.readthedocs.io/

---

## Next Steps After Implementation

1. **Run full test suite**: `pytest tests/ -v --cov=capassigner.core`
2. **Verify P1 bug is fixed**: Check `test_classroom_4cap_*` passes
3. **Check coverage target**: Should be > 90% for core modules
4. **Verify execution time**: Should be < 30 seconds total
5. **Update UI if needed**: If algorithm APIs changed (per FR-009)

---

**Status**: Ready for implementation phase (`/speckit.tasks` to generate tasks)
